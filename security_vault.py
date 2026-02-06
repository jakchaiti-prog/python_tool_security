import argparse
import json
import os
import datetime
import traceback
from jwcrypto import jwk, jwe, jws

# --- 1. ฟังก์ชันจัดการกุญแจ (Key Management & Conversion) --- [cite: 2026-02-07]
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
        print(f"✅ SUCCESS: Key files created for {owner_name}")
    except Exception as e:
        print(f"❌ GENERATE ERROR: {str(e)}")

def convert_key_format(input_path, to_format='pem'):
    """แปลงกุญแจระหว่าง JWK (JSON) และ PEM [cite: 2026-02-07]"""
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
        key = jwk.JWK(**data['key_data'])
        if to_format == 'pem':
            # ตรวจสอบว่าเป็นกุญแจ Private หรือ Public [cite: 2026-02-07]
            is_private = 'd' in data['key_data']
            pem_data = key.export_to_pem(private_key=is_private, password=None)
            out_file = input_path.replace(".json", ".pem")
            with open(out_file, 'wb') as f:
                f.write(pem_data)
            print(f"📄 Converted to PEM: {out_file}")
    except Exception as e:
        print(f"❌ CONVERT ERROR: {str(e)}")

# --- 2. ฟังก์ชันลายเซ็นดิจิทัล (Digital Signature) --- [cite: 2026-02-07]
def sign_data(payload, private_key_path):
    with open(private_key_path, 'r') as f:
        meta = json.load(f)
    key = jwk.JWK(**meta['key_data'])
    signature = jws.JWS(payload)
    signature.add_signature(key, None, json.dumps({"alg": "RS256"}))
    return signature.serialize()

# --- 3. ฟังก์ชันเข้ารหัสและถอดรหัส (Multi-Recipient) --- [cite: 2026-02-07]
def encrypt_multi_signed(file_path, sign_key_path, pub_key_paths):
    try:
        print(f"\n🔒 [SECURE MODE] Signing and Encrypting for {len(pub_key_paths)} users...")
        with open(file_path, 'rb') as f:
            plaintext = f.read()

        # ขั้นตอน: เซ็นชื่อก่อน แล้วค่อยเข้ารหัส (Sign-then-Encrypt) [cite: 2026-02-07]
        signed_payload = sign_data(plaintext, sign_key_path)
        jwetoken = jwe.JWE(signed_payload, json.dumps({"alg": "RSA-OAEP", "enc": "A256GCM"}))

        for path in pub_key_paths:
            with open(path, 'r') as f:
                meta = json.load(f)
            jwetoken.add_recipient(jwk.JWK(**meta['key_data']))

        ciphertext = jwetoken.serialize()
        vault_name = file_path + ".multi.vault"
        with open(vault_name, 'w') as f:
            f.write(ciphertext)
        print(f"✅ SUCCESS: Created Secure Vault -> {vault_name}")
    except Exception as e:
        print(f"❌ ENCRYPT ERROR: {str(e)}")

def decrypt_and_verify(vault_path, private_key_path, sender_pub_key_path):
    try:
        print(f"\n🔓 [DECRYPT] Opening: {os.path.basename(vault_path)}")
        # 1. ถอดรหัส JWE [cite: 2026-02-07]
        with open(private_key_path, 'r') as f:
            my_meta = json.load(f)
        with open(vault_path, 'r') as f:
            ciphertext = f.read()
        
        jwetoken = jwe.JWE()
        jwetoken.deserialize(ciphertext)
        jwetoken.decrypt(jwk.JWK(**my_meta['key_data']))
        
        # 2. ตรวจสอบลายเซ็น JWS [cite: 2026-02-07]
        with open(sender_pub_key_path, 'r') as f:
            sender_meta = json.load(f)
        jwstoken = jws.JWS()
        jwstoken.deserialize(jwetoken.payload)
        jwstoken.verify(jwk.JWK(**sender_meta['key_data']))
        
        recovered_name = vault_path.replace(".multi.vault", "_recovered.txt")
        with open(recovered_name, 'wb') as f:
            f.write(jwstoken.payload)
        print(f"✅ VERIFIED: Signature by {sender_meta['owner']} is VALID.")
        print(f"✅ SUCCESS: File recovered to -> {recovered_name}")
    except Exception as e:
        print(f"❌ DECRYPT/VERIFY ERROR: {str(e)}")

# --- 4. Main Parser (CLI) --- [cite: 2026-02-07]
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🛡️ Master Security Suite by Jakchai")
    subparsers = parser.add_subparsers(dest="command")

    # Command: gen-key
    p_gen = subparsers.add_parser("gen-key")
    p_gen.add_argument("--owner", required=True)

    # Command: encrypt_multi (Sign & Encrypt)
    p_mul = subparsers.add_parser("encrypt_multi")
    p_mul.add_argument("-f", "--file", required=True)
    p_mul.add_argument("-sk", "--sign_key", required=True, help="Your Private Key")
    p_mul.add_argument("-k", "--keys", required=True, nargs='+', help="Recipients' Public Keys")

    # Command: decrypt (Decrypt & Verify)
    p_dec = subparsers.add_parser("decrypt")
    p_dec.add_argument("-f", "--file", required=True)
    p_dec.add_argument("-k", "--key", required=True, help="Your Private Key")
    p_dec.add_argument("-v", "--verify", required=True, help="Sender's Public Key")

    # Command: convert
    p_con = subparsers.add_parser("convert")
    p_con.add_argument("-i", "--input", required=True)

    args = parser.parse_args()
    if args.command == "gen-key": generate_key(args.owner)
    elif args.command == "encrypt_multi": encrypt_multi_signed(args.file, args.sign_key, args.keys)
    elif args.command == "decrypt": decrypt_and_verify(args.file, args.key, args.verify)
    elif args.command == "convert": convert_key_format(args.input)