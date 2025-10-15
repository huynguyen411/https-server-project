import subprocess
import os
import sys

def generate_certificates():
    """Generate self-signed SSL certificates using OpenSSL"""
    cert_file = "certs/server.crt"
    key_file = "certs/server.key"

    print("Generating self-signed SSL certificates...")

    os.makedirs("certs", exist_ok=True)

    try:

        # Generate the private key
        subprocess.run(["openssl", "genrsa", "-out", key_file, "2048"], check=True)

        # Generate the certificate signing request (CSR)
        subprocess.run(["openssl", "req", "-new", "-key", key_file, "-out", "certs/server.csr",
                        "-subj", "/C=US/ST=California/L=San Francisco/O=My Company/CN=localhost"],
                    check=True)

        # Generate the self-signed certificate
        subprocess.run(["openssl", "x509", "-req", "-days", "365", "-in", "certs/server.csr",
                        "-signkey", key_file, "-out", cert_file], check=True)

        print("Self-signed SSL certificates generated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error generating certificates: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("OpenSSL is not installed or not found in PATH.")
        sys.exit(1)

def main():
    """Entry point for the generate-cert command"""
    generate_certificates()

if __name__ == "__main__":
    main()