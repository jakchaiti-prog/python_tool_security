import hashlib
import os
import argparse
from tqdm import tqdm

def verify_file(file_path, expected_hash):
    # ตรวจสอบว่ามีไฟล์อยู่จริงหรือไม่
    if not os.path.exists(file_path):
        print(f"❌ Error: ไม่พบไฟล์ที่ตำแหน่ง {file_path}")
        return

    file_size = os.path.getsize(file_path)
    md5_hash = hashlib.md5()
    
    print(f"📦 ไฟล์: {os.path.basename(file_path)}")
    print(f"📏 ขนาด: {file_size / (1024**3):.2f} GB")

    with tqdm(total=file_size, unit='B', unit_scale=True, desc="Verifying") as pbar:
        with open(file_path, "rb") as f:
            while (data := f.read(65536)):
                md5_hash.update(data)
                pbar.update(len(data))
                
    actual_hash = md5_hash.hexdigest()
    
    if actual_hash.lower() == expected_hash.lower():
        print("\n✅ [PASS] ค่า Hash ตรงกัน ไฟล์สมบูรณ์!")
    else:
        print("\n❌ [FAIL] ค่า Hash ไม่ตรงกัน!")
        print(f"   ค่าที่ได้: {actual_hash}")
        print(f"   ค่าที่ควรเป็น: {expected_hash}")

if __name__ == "__main__":
    # ตั้งค่า argparse เพื่อรับ options จาก command line
    parser = argparse.ArgumentParser(description="เครื่องมือตรวจสอบความถูกต้องของไฟล์ (Integrity Tool)")
    
    # เพิ่ม option -f (file) และ -m (md5)
    parser.add_argument("-f", "--file", required=True, help="Path ไปยังไฟล์ที่ต้องการตรวจสอบ")
    parser.add_argument("-m", "--md5", required=True, help="ค่า MD5 SUM ที่ต้องการเปรียบเทียบ")
    
    args = parser.parse_args()

    # เรียกใช้ฟังก์ชันโดยส่งค่าจาก options เข้าไป
    verify_file(args.file, args.md5)