import argparse
import json
import os
import datetime
import traceback
from jose import jwe, jwk

def encrypt_for_multiple(file_path, public_key_paths):
    try:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print("\n" + "!" * 50)
        print(f"🕒 [SYSTEM] Start Batch Encryption at: {now}")
        print("!" * 50)

        for path in public_key_paths:
            with open(path, 'r') as f:
                metadata = json.load(f)
            owner = metadata.get('owner', 'user').lower()
            key_data = metadata['key_data']

            with open(file_path, 'rb') as f:
                plaintext = f.read()

            ciphertext = jwe.encrypt(plaintext, key_data, algorithm='RSA-OAEP', encryption='A256GCM')
            vault_name = f"{file_path}.{owner}.vault"
            with open(vault_name, 'wb') as f:
                f.write(ciphertext)
            print(f"✅ [{datetime.datetime.now().strftime('%H:%M:%S')}] Created: {vault_name}")
        print("!" * 50 + "\n")
    except Exception as e:
        print(f"❌ ENCRYPT ERROR: {str(e)}")

def decrypt_file(vault_path, private_key_path):
    try:
        print(f"\n🔓 [SYSTEM] Decrypting: {os.path.basename(vault_path)}")
        with open(private_key_path, 'r') as f:
            metadata = json.load(f)
        with open(vault_path, 'rb') as f:
            ciphertext = f.read()

        # ใช้ข้อมูลกุญแจ Private ไขรหัส [cite: 2026-02-02]
        decrypted_data = jwe.decrypt(ciphertext, metadata['key_data'])
        
        recovered_name = vault_path.replace(".vault", "_recovered.txt")
        with open(recovered_name, 'wb') as f:
            f.write(decrypted_data)
        print(f"✅ SUCCESS: File recovered as -> {recovered_name}")
    except Exception as e:
        print(f"❌ DECRYPT ERROR: {str(e)}")
        print("💡 Tip: Make sure you are using the correct PRIVATE key for this vault.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🛡️ Secure Data Toolkit by Jakchai")
    subparsers = parser.add_subparsers(dest="command")

    # Command: encrypt_multi
    p_mul = subparsers.add_parser("encrypt_multi")
    p_mul.add_argument("-f", "--file", required=True)
    p_mul.add_argument("-k", "--keys", required=True, nargs='+')

    # Command: decrypt
    p_dec = subparsers.add_parser("decrypt")
    p_dec.add_argument("-f", "--file", required=True)
    p_dec.add_argument("-k", "--key", required=True)

    args = parser.parse_args()

    if args.command == "encrypt_multi":
        encrypt_for_multiple(args.file, args.keys)
    elif args.command == "decrypt":
        decrypt_file(args.file, args.key)
    else:
        parser.print_help()