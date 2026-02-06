import argparse
import json
import os
from jose import jwe, jwk
from datetime import datetime, timedelta
import traceback # เพิ่มตัวนี้เพื่อดู error ละเอียด [cite: 2026-02-02]
from cryptography.hazmat.primitives.asymmetric import rsa

def decrypt_file(vault_path, private_key_path):
    try:
        print(f"🔓 Status: Decrypting {os.path.basename(vault_path)}...")
        
        # 1. โหลดกุญแจ Private จากไฟล์ JSON [cite: 2026-02-02]
        with open(private_key_path, 'r') as f:
            metadata = json.load(f)
        
        # ใช้ข้อมูลกุญแจส่วนตัวเพื่อทำการไขรหัส [cite: 2026-02-02]
        priv_key_dict = metadata['key_data']
        
        # 2. อ่านไฟล์ .vault (รหัสลับ) [cite: 2026-02-07]
        with open(vault_path, 'rb') as f:
            ciphertext = f.read()
            
        # 3. ถอดรหัสด้วยมาตรฐาน JWE โดยใช้กุญแจ Private [cite: 2026-02-02]
        decrypted_data = jwe.decrypt(ciphertext, priv_key_dict)
        
        # 4. บันทึกไฟล์ที่ถอดรหัสแล้ว (เพิ่ม _recovered เพื่อให้เห็นความต่าง)
        recovered_name = vault_path.replace(".vault", "_recovered.txt")
        with open(recovered_name, 'wb') as f:
            f.write(decrypted_data)
            
        print(f"✅ SUCCESS: Data recovered and saved to -> {recovered_name}")
        
    except Exception as e:
        print(f"❌ DECRYPT ERROR: {str(e)}")
        traceback.print_exc()

def generate_key(owner_name, days_valid=30):
    try:
        print(f"🛠️ Debug: Generating asymmetric key pair for {owner_name}...")
        
        # 1. สร้างกุญแจหลัก (Private Key) และ Public Key [cite: 2026-02-02]
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        
        # --- ประกาศตัวแปร pub_jwk ให้ถูกต้อง --- [cite: 2026-02-02]
        pub_jwk = jwk.construct(private_key.public_key(), algorithm='RS256')
        priv_jwk = jwk.construct(private_key, algorithm='RS256')
        
        # 2. ตั้งค่าวันหมดอายุ
        expiry = datetime.now() + timedelta(days=days_valid)
        
        # --- ประกาศตัวแปร expiry_str ให้ถูกต้อง --- [cite: 2026-02-02]
        expiry_str = expiry.strftime("%Y-%m-%d %H:%M:%S")

        # 3. กำหนดชื่อไฟล์ให้ชัดเจน [cite: 2026-02-02]
        priv_filename = f"key_{owner_name.lower()}_private.json"
        pub_filename = f"key_{owner_name.lower()}_public.json"

        # 4. บันทึกไฟล์ Private (เก็บไว้ที่เครื่องเรา) [cite: 2026-02-02]
        with open(priv_filename, 'w') as f:
            json.dump({"owner": owner_name, "expires_at": expiry_str, "key_data": priv_jwk.to_dict()}, f, indent=4)

        # 5. บันทึกไฟล์ Public (ใช้สำหรับ Encrypt) [cite: 2026-02-02]
        with open(pub_filename, 'w') as f:
            json.dump({"owner": owner_name, "expires_at": expiry_str, "key_data": pub_jwk.to_dict()}, f, indent=4)
            
        print(f"✅ SUCCESS: Private Key created -> {priv_filename}")
        print(f"✅ SUCCESS: Public Key created -> {pub_filename}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        traceback.print_exc()


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
# บรรทัดนี้เพิ่มต่อจาก enc_parser ครับ
    dec_parser = subparsers.add_parser("decrypt", help="Decrypt a vaulted file")
    dec_parser.add_argument("-f", "--file", required=True, help="Target .vault file path")
    dec_parser.add_argument("-k", "--key", required=True, help="Private key file (.json)")
    
    args = parser.parse_args()

    try:
        if args.command == "gen-key":
            generate_key(args.owner, args.days)
        elif args.command == "encrypt":
            encrypt_file(args.file, args.key)
        # เพิ่มต่อจาก elif args.command == "encrypt":
        elif args.command == "decrypt":
            decrypt_file(args.file, args.key)            
        else:
            parser.print_help()
    except Exception as e:
        print(f"❌ FATAL ERROR: {str(e)}")


def generate_key(owner_name, days_valid=30):
    try:
        print(f"🛠️ Debug: Generating asymmetric key pair for {owner_name}...")
        
        # 1. สร้างกุญแจหลัก (Private Key)
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        priv_jwk = jwk.construct(private_key, algorithm='RS256')
        
        # 2. สกัดกุญแจสาธารณะ (Public Key) แยกออกมาโดยเฉพาะ
        pub_jwk = jwk.construct(private_key.public_key(), algorithm='RS256')
        
        expiry = datetime.now() + timedelta(days=days_valid)
        expiry_str = expiry.strftime("%Y-%m-%d %H:%M:%S")

        # 3. บันทึกไฟล์ Private (เก็บไว้ที่เครื่องเรา)
        priv_filename = f"key_{owner_name.lower()}_private.json"
        with open(priv_filename, 'w') as f:
            json.dump({"owner": owner_name, "expires_at": expiry_str, "key_data": priv_jwk.to_dict()}, f, indent=4)

        # 4. บันทึกไฟล์ Public (ส่งให้คนอื่นใช้ Encrypt)
        pub_filename = f"key_{owner_name.lower()}_public.json"
        with open(pub_filename, 'w') as f:
            json.dump({"owner": owner_name, "expires_at": expiry_str, "key_data": pub_jwk.to_dict()}, f, indent=4)
            
        print(f"✅ SUCCESS: Private Key -> {priv_filename}")
        print(f"✅ SUCCESS: Public Key -> {pub_filename}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

def encrypt_file(file_path, public_key_path):
    try:
        print(f"🔒 Status: Encrypting with Public Key...")
        
        with open(public_key_path, 'r') as f:
            metadata = json.load(f)
            
        # ใช้ key_data จากไฟล์ Public ที่ไม่มีความลับของ Private ปนอยู่เลย [cite: 2026-02-02]
        pub_key_dict = metadata['key_data']
        
        with open(file_path, 'rb') as f:
            plaintext = f.read()
            
        # เข้ารหัส (JWE จะยอมรับกุญแจนี้เพราะเป็น Public Key แท้ๆ) [cite: 2026-02-02]
        ciphertext = jwe.encrypt(plaintext, pub_key_dict, algorithm='RSA-OAEP', encryption='A256GCM')
        
        vault_name = file_path + ".vault"
        with open(vault_name, 'wb') as f:
            f.write(ciphertext)
            
        print(f"✅ SUCCESS: File secured at -> {vault_name}")
        
    except Exception as e:
        print(f"❌ ENCRYPT ERROR: {str(e)}")      

def decrypt_file(vault_path, private_key_path):
    try:
        print(f"🔓 Status: Decrypting {os.path.basename(vault_path)}...")
        
        # 1. โหลดกุญแจ Private (กุญแจตัวจริงที่ใช้ไข) [cite: 2026-02-02]
        with open(private_key_path, 'r') as f:
            metadata = json.load(f)
        
        priv_key_dict = metadata['key_data']
        
        # 2. อ่านไฟล์ที่ถูกล็อกไว้ [cite: 2026-02-02]
        with open(vault_path, 'rb') as f:
            ciphertext = f.read()
            
        # 3. ถอดรหัสคืนเป็นข้อมูลดิบ (JWE Decrypt) [cite: 2026-02-02]
        decrypted_data = jwe.decrypt(ciphertext, priv_key_dict)
        
        # 4. บันทึกคืนเป็นไฟล์เดิม (ตัดนามสกุล .vault ออก)
        original_name = vault_path.replace(".vault", "_recovered.txt")
        with open(original_name, 'wb') as f:
            f.write(decrypted_data)
            
        print(f"✅ SUCCESS: Data recovered at -> {original_name}")
        
    except Exception as e:
        print(f"❌ DECRYPT ERROR: {str(e)}")
        traceback.print_exc()          