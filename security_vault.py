import argparse
import json
import os
from jose import jwe, jwk
from datetime import datetime, timedelta

# --- Core Functions ---

def generate_key(owner_name, days_valid=30):
    """Generate an RSA key pair with expiration metadata."""
    key = jwk.generate_key('RS256', size=2048)
    expiry = datetime.now() + timedelta(days=days_valid)
    
    metadata = {
        "owner": owner_name,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expires_at": expiry.strftime("%Y-%m-%d %H:%M:%S"),
        "key_data": key.to_dict()
    }
    
    filename = f"key_{owner_name.lower()}.json"
    with open(filename, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"✅ SUCCESS: Key generated for '{owner_name}'")
    print(f"📅 VALID UNTIL: {metadata['expires_at']}")

def check_key_integrity(key_path):
    """Check if the key exists and is not expired."""
    if not os.path.exists(key_path):
        raise FileNotFoundError(f"Key file not found: {key_path}")
    
    with open(key_path, 'r') as f:
        data = json.load(f)
        
    expiry = datetime.strptime(data['expires_at'], "%Y-%m-%d %H:%M:%S")
    if datetime.now() > expiry:
        raise Exception(f"Security key for '{data['owner']}' has EXPIRED on {data['expires_at']}")
    
    return data['key_data']

def encrypt_file(file_path, key_path):
    """Encrypt file using a single public key."""
    print(f"🔒 Status: Encrypting {os.path.basename(file_path)}...")
    key_dict = check_key_integrity(key_path)
    
    with open(file_path, 'rb') as f:
        plaintext = f.read()
    
    ciphertext = jwe.encrypt(plaintext, key_dict, algorithm='RSA-OAEP', encryption='A256GCM')
    
    with open(file_path + ".vault", 'wb') as f:
        f.write(ciphertext)
    print(f"✅ Success: File secured at {file_path}.vault")

# --- CLI Setup ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🛡️ Secure Data Toolkit by Jakchai")
    subparsers = parser.add_subparsers(dest="command")

    # Command: gen-key
    gen_parser = subparsers.add_parser("gen-key", help="Generate a new security key")
    gen_parser.add_argument("--owner", required=True, help="Owner name of the key")
    gen_parser.add_argument("--days", type=int, default=30, help="Validity period in days")

    # Command: encrypt
    enc_parser = subparsers.add_parser("encrypt", help="Encrypt a file")
    enc_parser.add_argument("-f", "--file", required=True, help="Target file path")
    enc_parser.add_argument("-k", "--key", required=True, help="Key file (.json)")

    args = parser.parse_args()

    try:
        if args.command == "gen-key":
            generate_key(args.owner, args.days)
        elif args.command == "encrypt":
            encrypt_file(args.file, args.key)
        else:
            parser.print_help()
    except Exception as e:
        print(f"❌ FATAL ERROR: {str(e)}")