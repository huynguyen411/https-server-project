# HTTPS Encryption Internals - Learning Guide

## Overview

This document explains how HTTPS encryption works from scratch, specifically how the encryption and key exchange happens in your HTTPS server implementation.

## The Problem HTTPS Solves

When using regular HTTP:
- All data travels in **plain text** over the network
- Anyone monitoring the network can read passwords, messages, etc.
- No way to verify you're talking to the real server (could be an imposter)

HTTPS solves this with **encryption** and **authentication**.

## Two Types of Encryption Used

### 1. Asymmetric Encryption (Public/Private Key)
- **Used during**: Initial handshake only
- **Two keys**: Public key (shared with everyone) and Private key (kept secret)
- **How it works**:
  - Data encrypted with public key can ONLY be decrypted with private key
  - Server shares its public key with clients
  - Client can encrypt secrets that only the server can decrypt
- **Problem**: Very slow (computationally expensive)

### 2. Symmetric Encryption (Session Key)
- **Used during**: All communication after handshake
- **One key**: Same key encrypts and decrypts
- **How it works**: Both client and server use the same secret key
- **Advantage**: Very fast!
- **Problem**: How do you share the key securely?

## The TLS Handshake - Step by Step

This is the key exchange process that happens when a client connects to your HTTPS server.

### In Your Code
The handshake happens in this line in [src/https_server/https_server.py:96](src/https_server/https_server.py#L96):
```python
secure_socket = ssl_context.wrap_socket(client_socket, server_side=True)
```

Behind the scenes, here's what happens:

### Step 1: ClientHello
```
Client → Server:
  "Hello! I support these encryption algorithms (cipher suites):
   - TLS_AES_256_GCM_SHA384
   - TLS_CHACHA20_POLY1305_SHA256
   - TLS_AES_128_GCM_SHA256
   Here's a random number I generated: [random_bytes]"
```

### Step 2: ServerHello
```
Server → Client:
  "Hello! Let's use: TLS_AES_256_GCM_SHA384
   Here's MY random number: [random_bytes]"
```

### Step 3: Server Certificate
```
Server → Client:
  "Here's my certificate containing:
   - My identity (CN=localhost)
   - My PUBLIC KEY
   - Signature from certificate authority (self-signed in our case)"
```

The certificate is loaded here in [src/https_server/https_server.py:49](src/https_server/https_server.py#L49):
```python
ssl_context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
```

### Step 4: Client Key Exchange
```
Client:
  1. Generates a "pre-master secret" (random bytes)
  2. Encrypts it with server's PUBLIC KEY from certificate
  3. Sends encrypted pre-master secret to server

Client → Server: [encrypted_pre_master_secret]
```

Only the server can decrypt this because only the server has the PRIVATE KEY!

### Step 5: Deriving Session Keys
Both client and server now independently generate the same symmetric encryption keys:

```
Session Keys = Hash(
  client_random +
  server_random +
  pre_master_secret
)
```

They both know:
- `client_random` (from Step 1)
- `server_random` (from Step 2)
- `pre_master_secret` (client generated it, server decrypted it)

This generates several keys:
- **Client Write Key**: Encrypts client → server messages
- **Server Write Key**: Encrypts server → client messages
- **Client MAC Key**: Authenticates client messages
- **Server MAC Key**: Authenticates server messages

### Step 6: Finished Messages
```
Client → Server: [encrypted "Finished" message]
Server → Client: [encrypted "Finished" message]
```

Both test that the encryption works. If either message fails to decrypt, the handshake fails.

## Encrypted Communication Phase

After the handshake completes, all communication uses the symmetric session keys.

### When Client Sends a Request
```python
# Client sends: "GET / HTTP/1.1"
encrypted_data = AES_encrypt("GET / HTTP/1.1", client_write_key)
# Sends encrypted bytes over network
```

### When Server Receives
```python
# In your code (https_server.py:102)
request_data = secure_socket.recv(1024).decode('utf-8')
# Behind the scenes, SSL layer did:
# decrypted_data = AES_decrypt(encrypted_bytes, client_write_key)
```

### When Server Sends Response
```python
# In your code (https_server.py:115)
secure_socket.sendall(response.encode('utf-8'))
# Behind the scenes, SSL layer does:
# encrypted_response = AES_encrypt(response, server_write_key)
```

## What Python's ssl Module Does

The `ssl` module handles all this complexity:

1. **`ssl.SSLContext`**: Configures TLS settings
   - Which TLS versions to support
   - Which cipher suites to allow
   - Where to find certificates

2. **`load_cert_chain()`**: Loads your certificate and private key
   - Certificate contains your public key
   - Private key stays secret, used to decrypt pre-master secret

3. **`wrap_socket()`**: Performs the entire TLS handshake
   - Exchanges hello messages
   - Sends certificate
   - Receives encrypted pre-master secret
   - Decrypts it with private key
   - Derives session keys
   - Tests encryption with Finished messages

4. **`recv()` and `sendall()`**: Automatically encrypt/decrypt
   - You work with plain text
   - SSL layer handles encryption transparently

## Security Properties Achieved

### 1. Confidentiality
- Network eavesdroppers see only encrypted gibberish
- Only client and server can read the data

### 2. Integrity
- MAC (Message Authentication Code) ensures data isn't tampered with
- If someone modifies encrypted data, decryption will detect it

### 3. Authentication
- Certificate proves server identity (if signed by trusted CA)
- Client knows it's talking to the real server, not an imposter

## Try It Yourself

1. **Generate certificates** (if not done):
   ```bash
   uv run generate-cert
   ```

2. **Start HTTPS server**:
   ```bash
   python3 src/https_server/https_server.py
   ```

3. **See the handshake details with curl**:
   ```bash
   curl -k https://127.0.0.1:8443/ --verbose
   ```

   Look for:
   - `TLS handshake, Client hello (1)`
   - `TLS handshake, Server hello (2)`
   - `TLS handshake, Certificate (11)`
   - `SSL connection using TLSv1.3 / AEAD-AES256-GCM-SHA384`

4. **View server logs** to see:
   - When handshake starts
   - Which cipher was negotiated
   - When encrypted data is received/sent

## Key Takeaways

1. **Asymmetric encryption** (public/private key) is used ONLY for the handshake to securely exchange the session key

2. **Symmetric encryption** (session key) is used for all actual data transfer because it's fast

3. **The certificate** contains the server's public key and identity

4. **The private key** must be kept secret - it's used to decrypt the pre-master secret during handshake

5. **Session keys** are derived from random data exchanged during handshake - different for every connection!

6. Python's `ssl` module handles all the crypto complexity - but now you understand what it's doing under the hood!

## Further Learning

To go deeper:
- Read about specific cipher suites (AES-GCM, ChaCha20-Poly1305)
- Learn about Diffie-Hellman key exchange (alternative to RSA)
- Study TLS 1.3 improvements over TLS 1.2
- Understand certificate chains and PKI (Public Key Infrastructure)
- Explore Perfect Forward Secrecy (PFS)
