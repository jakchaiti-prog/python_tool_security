import hashlib
import os
import argparse
from tqdm import tqdm

def verify_file(file_path, expected_hash):
    # ตรวจสอบว่ามีไฟล์อยู่จริงหรือไม่
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found at {file_path}")
        return

    file_size = os.path.getsize(file_path)
    md5_hash = hashlib.md5()
    
    print(f"📦 File: {os.path.basename(file_path)}")
    print(f"📏 Size: {file_size / (1024**3):.2f} GB")

    with tqdm(total=file_size, unit='B', unit_scale=True, desc="Verifying") as pbar:
        # ปรับขนาด Chunk ให้ใหญ่ขึ้นเป็น 1MB เพื่อลดจำนวนรอบของ Loop และเพิ่มความเสถียร
        chunk_size = 1024 * 1024 
        with open(file_path, "rb") as f:
            # ใช้ iter เพื่อให้การวน Loop ลื่นไหลขึ้น ลดภาระหน่วยความจำ
            for data in iter(lambda: f.read(chunk_size), b""):
                md5_hash.update(data)
                pbar.update(len(data))
                
    actual_hash = md5_hash.hexdigest()
    
    # ส่วนแสดงผลลัพธ์การตรวจสอบ
    if actual_hash.lower() == expected_hash.lower():
        print("\n✅ [PASS] Hash matched! The file is complete.")
    else:
        print("\n❌ [FAIL] Hash mismatch!")
        print(f"   Actual:   {actual_hash}")
        print(f"   Expected: {expected_hash}")

if __name__ == "__main__":
    # ตั้งค่า argparse เพื่อรับ options จาก command line (CLI)
    parser = argparse.ArgumentParser(description="File Integrity Check Tool")
    
    # เพิ่ม option -f (file) และ -m (md5) สำหรับรับค่าจาก Terminal
    parser.add_argument("-f", "--file", required=True, help="Path to the file to check")
    parser.add_argument("-m", "--md5", required=True, help="Expected MD5 checksum value")
    
    args = parser.parse_args()

    # เรียกใช้ฟังก์ชันหลักโดยส่งค่าที่รับมาจาก options เข้าไป
    verify_file(args.file, args.md5)