import hashlib
import os
from tqdm import tqdm

def verify_vivado_file(file_path, expected_md5):
    # ตรวจสอบว่าไฟล์มีอยู่จริงไหมก่อนเริ่ม
    if not os.path.exists(file_path):
        print(f"❌ ไม่พบไฟล์: {file_path}")
        return

    file_size = os.path.getsize(file_path)
    md5_hash = hashlib.md5()
    
    print(f"กำลังตรวจสอบไฟล์ขนาด {file_size / (1024**3):.2f} GB...")
    
    # ใช้ tqdm ทำ Progress Bar สำหรับไฟล์ 107GB
    with tqdm(total=file_size, unit='B', unit_scale=True, desc="Checking MD5") as pbar:
        with open(file_path, "rb") as f:
            while (data := f.read(65536)): # แก้ไขช่องว่าง := แล้ว
                md5_hash.update(data)
                pbar.update(len(data))
                
    actual_md5 = md5_hash.hexdigest()
    
    if actual_md5.lower() == expected_md5.lower():
        print("\n✅ [Pass] ไฟล์สมบูรณ์ ตรงกับค่าในเว็บ Xilinx!")
    else:
        print("\n❌ [Fail] ค่า Hash ไม่ตรงกัน ไฟล์อาจจะเสีย")

# ใส่ค่าที่คุณจักร์ชัยโหลดเสร็จมา
vivado_path = r"C:\path\to\your\Xilinx_Unified_2024.1_SFD.tar.gz" 
vivado_md5 = "372c0b184e32001137424e395823de3c" # ค่าสำหรับไฟล์ 107.11 GB

verify_vivado_file(vivado_path, vivado_md5)