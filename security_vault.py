import argparse
import json
import os
from jose import jwe, jwk
from datetime import datetime, timedelta
import traceback # เพิ่มตัวนี้เพื่อดู error ละเอียด [cite: 2026-02-02]
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_key(owner_name, days_valid=30):
    try:
        print(f"🛠️ Debug: Starting key generation for {owner_name}...")
        
        # 1. สร้างกุญแจ RSA จริงๆ ด้วย cryptography library
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        
        # 2. แปลงเป็น JWK format เพื่อใช้งานกับ jose
        key = jwk.construct(private_key, algorithm='RS256')
        print("🛠️ Debug: RSA Key constructed successfully.")
        
        # ... (ส่วนที่เหลือเหมือนเดิม) ...
        # 1. สร้างกุญแจ RSA [cite: 2026-02-02]
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        key = jwk.construct(private_key, algorithm='RS256')
        
        # 2. คำนวณวันหมดอายุ [cite: 2026-02-02]
        expiry = datetime.now() + timedelta(days=days_valid)

        filename = f"key_{owner_name.lower()}.json"
        # ใช้ os.path.abspath เพื่อดูที่อยู่ไฟล์แบบเต็มๆ [cite: 2026-02-02]
        full_path = os.path.abspath(filename) 
        
        metadata = {
                    "owner": owner_name,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "expires_at": expiry.strftime("%Y-%m-%d %H:%M:%S"),
                    "key_data": key.to_dict()
                }
        
        # 3. บันทึกลงไฟล์
        filename = f"key_{owner_name.lower()}.json"
        full_path = os.path.abspath(filename)
        
        with open(filename, 'w') as f:
            json.dump(metadata, f, indent=4) # ตอนนี้จะมี metadata ให้ dump แล้วครับ
            
        print(f"✅ SUCCESS: Key saved to -> {full_path}")
        
    except Exception as e:
        print(f"❌ ERROR inside generate_key: {str(e)}")
        traceback.print_exc()
            
        print(f"✅ SUCCESS: Key saved to -> {full_path}") # แจ้งที่อยู่ไฟล์ชัดๆ        
        
    except Exception as e:
        print(f"❌ ERROR inside generate_key: {str(e)}")
        traceback.print_exc() # พ่น error ทั้งหมดออกมาให้เราเห็นจุดผิด [cite: 2026-02-02]


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