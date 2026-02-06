import tarfile
import os
import argparse
from tqdm import tqdm

def extract_instant(source_file, target_dir):
    # ตรวจสอบไฟล์ต้นทางก่อนเริ่ม
    if not os.path.exists(source_file):
        print(f"❌ Error: Source file not found: {source_file}")
        return

    # สร้างโฟลเดอร์ปลายทาง
    os.makedirs(target_dir, exist_ok=True)

    print(f"📦 Instant Extracting from: {os.path.basename(source_file)}")
    print(f"📂 Destination: {target_dir}")
    print("🚀 Starting extraction immediately (without pre-scanning)...")

    try:
        with tarfile.open(source_file, "r:gz") as tar:
            # ใช้ tqdm แบบไหลไปเรื่อยๆ ไม่ต้องรอสแกนรายชื่อไฟล์ เพื่อลดอาการค้าง
            with tqdm(unit="file", desc="Extracting") as pbar:
                for member in tar:
                    tar.extract(member, path=target_dir)
                    pbar.update(1)
        print("\n✅ Extraction completed successfully!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Instant Tar Extraction Tool")
    parser.add_argument("-f", "--file", required=True, help="Path to the .tar.gz file")
    parser.add_argument("-d", "--dest", required=True, help="Path to the destination folder")
    
    args = parser.parse_args()
    extract_instant(args.file, args.dest)