import argparse
import json
import os
import datetime
from jwcrypto import jwk, jwe

# --- 1. ฟังก์ชันสร้างกุญแจ (JWK Format) --- [cite: 2026-02-07]
def generate_key(owner_name, days_valid=30):
    try:
        print(f"🛠️ [JWCrypto] Generating keys for: {owner_name}...")
        key = jwk.JWK.generate(kty='RSA', size=2048)
        
        priv_jwk = json.loads(key.export_private())
        pub_jwk = json.loads(key.export_public())
        
        expiry = datetime.datetime.now() + datetime.timedelta(days=days_valid)
        expiry_str = expiry.strftime("%Y-%m-%d %H:%M:%S")

        with open(f"key_{owner_name.lower()}_private.json", 'w') as f:
            json.dump({"owner": owner_name, "expires_at": expiry_str, "key_data": priv_jwk}, f, indent=4)
        with open(f"key_{owner_name.lower()}_public.json", 'w') as f:
            json.dump({"owner": owner_name, "expires_at": expiry_str, "key_data": pub_jwk}, f, indent=4)
            
        print(f"✅ SUCCESS: Created key files for {owner_name}")
    except Exception as e:
        print(f"❌ GENERATE ERROR: {str(e)}")

# --- 2. ฟังก์ชันเข้ารหัสไฟล์เดียว (Multi-Recipient) --- [cite: 2026-02-07]
def encrypt_for_multiple(file_path, public_key_paths):
    try:
        print(f"\n🔒 [MULTI-KEY] Creating vault for {len(public_key_paths)} users...")
        with open(file_path, 'rb') as f:
            plaintext = f.read()

        jwetoken = jwe.JWE(plaintext, json.dumps({"alg": "RSA-OAEP", "enc": "A256GCM"}))

        for path in public_key_paths:
            with open(path, 'r') as f:
                metadata = json.load(f)
            key = jwk.JWK(**metadata['key_data'])
            jwetoken.add_recipient(key) # เพิ่มกุญแจทุกคนเข้าไฟล์เดียว [cite: 2026-02-07]

        ciphertext = jwetoken.serialize()
        vault_name = file_path + ".multi.vault"
        with open(vault_name, 'w') as f:
            f.write(ciphertext)
        print(f"✅ SUCCESS: Created -> {vault_name}")
    except Exception as e:
        print(f"❌ ENCRYPT ERROR: {str(e)}")

# --- 3. ฟังก์ชันถอดรหัส --- [cite: 2026-02-07]
def decrypt_file(vault_path, private_key_path):
    try:
        print(f"🔓 [DECRYPT] Opening: {os.path.basename(vault_path)}")
        with open(private_key_path, 'r') as f:
            metadata = json.load(f)
        with open(vault_path, 'r') as f:
            ciphertext = f.read()

        key = jwk.JWK(**metadata['key_data'])
        jwetoken = jwe.JWE()
        jwetoken.deserialize(ciphertext)
        jwetoken.decrypt(key) # ไขด้วยกุญแจใครก็ได้ที่มีสิทธิ์ [cite: 2026-02-07]

        recovered_name = vault_path.replace(".multi.vault", "_recovered.txt")
        with open(recovered_name, 'wb') as f:
            f.write(jwetoken.payload)
        print(f"✅ SUCCESS: Recovered to -> {recovered_name}")
    except Exception as e:
        print(f"❌ DECRYPT ERROR: {str(e)}")

# --- 4. Main Parser --- [cite: 2026-02-07]
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🛡️ Multi-User Vault by Jakchai")
    subparsers = parser.add_subparsers(dest="command")

    p_gen = subparsers.add_parser("gen-key")
    p_gen.add_argument("--owner", required=True)
    p_gen.add_argument("--days", type=int, default=30)

    p_mul = subparsers.add_parser("encrypt_multi")
    p_mul.add_argument("-f", "--file", required=True)
    p_mul.add_argument("-k", "--keys", required=True, nargs='+')

    p_dec = subparsers.add_parser("decrypt")
    p_dec.add_argument("-f", "--file", required=True)
    p_dec.add_argument("-k", "--key", required=True)

    args = parser.parse_args()
    if args.command == "gen-key": generate_key(args.owner, args.days)
    elif args.command == "encrypt_multi": encrypt_for_multiple(args.file, args.keys)
    elif args.command == "decrypt": decrypt_file(args.file, args.key)