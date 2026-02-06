import tarfile
import os
import argparse
from tqdm import tqdm

def extract_tar_file(source_file, target_dir):
    # ตรวจสอบว่ามีไฟล์ต้นทางอยู่จริงหรือไม่ เพื่อป้องกัน Error
    if not os.path.exists(source_file):
        print(f"❌ Error: Source file not found: {source_file}")
        return

    # สร้างโฟลเดอร์ปลายทางโดยอัตโนมัติหากยังไม่มี
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    print(f"📦 Extracting from: {os.path.basename(source_file)}")
    print(f"📂 Destination: {target_dir}")

    try:
        with tarfile.open(source_file, "r:gz") as tar:
            # ดึงรายชื่อไฟล์ทั้งหมดออกมาเพื่อใช้คำนวณ Progress Bar
            members = tar.getmembers()
            # ใช้ tqdm ติดตามความคืบหน้าตามจำนวนไฟล์ที่แตกออกมา
            with tqdm(total=len(members), unit="file", desc="Extracting") as pbar:
                for member in members:
                    tar.extract(member, path=target_dir)
                    pbar.update(1)
        print("✅ Extraction completed successfully!")
    except Exception as e:
        # แสดงข้อผิดพลาดหากเกิดปัญหาขึ้นระหว่างการทำงาน
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    # ตั้งค่า argparse เพื่อให้รับค่าแบบ Options (CLI) ผ่าน Terminal ได้
    parser = argparse.ArgumentParser(description="Standalone Tar Extraction Tool")
    
    # กำหนด Option -f สำหรับไฟล์ต้นทาง และ -d สำหรับโฟลเดอร์ปลายทาง
    parser.add_argument("-f", "--file", required=True, help="Path to the .tar.gz file")
    parser.add_argument("-d", "--dest", required=True, help="Path to the destination folder")
    
    args = parser.parse_args()

    # เริ่มกระบวนการแตกไฟล์โดยใช้ค่าที่รับมาจาก CLI
    extract_tar_file(args.file, args.dest)