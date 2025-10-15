# HTTPS Server Demo

## Quick Start Guide

### 1. Generate SSL Certificates

First, generate the self-signed SSL certificate and private key:

```bash
uv run generate-cert
```

This creates:
- `certs/server.key` - Private key (keep this secret!)
- `certs/server.crt` - Certificate containing public key
- `certs/server.csr` - Certificate signing request (intermediate file)

### 2. Run the HTTPS Server

```bash
python3 src/https_server/https_server.py
```

You should see:
```
🔒 HTTPS Server started at https://127.0.0.1:8443
📜 Using certificate: certs/server.crt
⚠️  Using self-signed certificate - browsers will show security warning
Press Ctrl+C to stop the server
```

### 3. Test with curl

In another terminal, test the encrypted connection:

```bash
# See the full TLS handshake details
curl -k https://127.0.0.1:8443/ --verbose

# Just get the content
curl -k https://127.0.0.1:8443/

# Visit the encryption explanation page
curl -k https://127.0.0.1:8443/encryption
```

The `-k` flag tells curl to accept self-signed certificates.

### 4. Test with a Browser

Open your browser and visit:
```
https://127.0.0.1:8443/
```

You'll see a security warning because the certificate is self-signed. This is expected!

- **Chrome/Edge**: Click "Advanced" → "Proceed to 127.0.0.1 (unsafe)"
- **Firefox**: Click "Advanced" → "Accept the Risk and Continue"
- **Safari**: Click "Show Details" → "visit this website"

Once accepted, you'll see the encrypted welcome page!

## What to Look For

### In curl verbose output

```bash
curl -k https://127.0.0.1:8443/ --verbose
```

Look for these key moments:

1. **TLS Handshake begins:**
   ```
   * (304) (OUT), TLS handshake, Client hello (1):
   * (304) (IN), TLS handshake, Server hello (2):
   ```

2. **Server sends certificate:**
   ```
   * (304) (IN), TLS handshake, Certificate (11):
   * Server certificate:
   *  subject: C=US; ST=California; L=San Francisco; O=My Company; CN=localhost
   ```

3. **Cipher negotiated:**
   ```
   * SSL connection using TLSv1.3 / AEAD-AES256-GCM-SHA384
   ```

4. **Connection is encrypted:**
   ```
   * SSL certificate verify result: self signed certificate (18), continuing anyway.
   ```

### In server logs

When a client connects, you'll see:

```
📨 New connection from ('127.0.0.1', 54321)
🤝 Starting TLS handshake with ('127.0.0.1', 54321)...
✅ TLS handshake complete with ('127.0.0.1', 54321)
   Cipher: ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', 256)
   TLS Version: TLSv1.3
📥 Request: GET / HTTP/1.1
📤 Sent encrypted response to ('127.0.0.1', 54321)
```

This shows:
- When the TLS handshake starts
- Which cipher was chosen (AES-256 in this case)
- Which TLS version (1.3)
- All communication after handshake is encrypted

## Understanding the Encryption

### Key Files

- **server.key** (Private Key): Never shared, used to decrypt the pre-master secret
- **server.crt** (Certificate): Shared with clients, contains the public key

### The Process

1. **Client connects** → TCP connection established
2. **TLS Handshake:**
   - Client says: "I support these ciphers"
   - Server says: "Let's use TLS_AES_256_GCM_SHA384"
   - Server sends certificate (with public key)
   - Client generates random "pre-master secret"
   - Client encrypts it with server's public key, sends to server
   - Server decrypts with private key
   - Both derive identical session keys from the pre-master secret
3. **Encrypted communication:**
   - All HTTP request/response data encrypted with session key (symmetric encryption)
   - Fast AES-256 encryption

### Compare with HTTP

Run the regular HTTP server to see the difference:

```bash
# Terminal 1: Run HTTP server
python3 src/https_server/server.py

# Terminal 2: Test it
curl http://127.0.0.1:8080/ --verbose
```

Notice:
- No TLS handshake
- No certificate exchange
- Data sent in plain text
- Anyone monitoring network can read everything

## Experiments to Try

### 1. View Certificate Details

```bash
openssl x509 -in certs/server.crt -text -noout
```

Look for:
- **Public Key**: The RSA public key shared with clients
- **Subject**: Server identity (CN=localhost)
- **Validity**: When certificate expires

### 2. View Private Key

```bash
openssl rsa -in certs/server.key -text -noout
```

See the private key that must be kept secret!

### 3. Compare Cipher Suites

```python
import ssl
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
print([c['name'] for c in context.get_ciphers()])
```

See all available cipher suites (encryption algorithms).

### 4. Capture Network Traffic

Use Wireshark or tcpdump:

```bash
# Capture HTTPS traffic (you'll see encrypted gibberish)
sudo tcpdump -i lo0 -A 'port 8443'

# Capture HTTP traffic (you'll see plain text!)
sudo tcpdump -i lo0 -A 'port 8080'
```

### 5. Test Different TLS Versions

Modify [https_server.py:59](src/https_server/https_server.py#L59):

```python
# Allow only TLS 1.3 (most secure)
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3

# Or allow older versions (less secure)
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
```

## Troubleshooting

### "Certificate not found" error

Run the certificate generator:
```bash
uv run generate-cert
```

### "Address already in use" error

Another process is using port 8443. Either:
- Kill the existing server: `pkill -f https_server.py`
- Or change the port in the code

### Browser shows "Connection refused"

Make sure the server is running:
```bash
python3 src/https_server/https_server.py
```

### Browser won't accept certificate

This is expected for self-signed certificates! Click "Advanced" and proceed anyway. Self-signed certificates are only for learning/testing, not production.

## Next Steps

1. Read [HTTPS_INTERNALS.md](HTTPS_INTERNALS.md) for deep dive into TLS/SSL
2. Examine the code in [https_server.py](src/https_server/https_server.py) with detailed comments
3. Try implementing client certificate authentication
4. Explore Perfect Forward Secrecy (PFS) with ephemeral keys
5. Learn about certificate chains and Certificate Authorities (CAs)