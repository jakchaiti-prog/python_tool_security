import hashlib
import os
from tqdm import tqdm

def calculate_md5_with_progress(file_path):
    # 1. เตรียมตัวคำนวณ Hash
    md5_hash = hashlib.md5()
    
    # 2. หาขนาดไฟล์ทั้งหมดเพื่อเอาไปทำ Progress Bar
    file_size = os.path.getsize(file_path)
    
    # 3. กำหนดขนาดการอ่านทีละก้อน (64KB เหมือนที่คุณจักร์ชัยเขียนไว้)
    chunk_size = 65536
    
    print(f"กำลังตรวจสอบไฟล์: {os.path.basename(file_path)}")
    
    # 4. ใช้ tqdm สร้าง Progress Bar
    # unit='B' คือบอกว่าเป็น Byte, unit_scale=True จะช่วยปรับเป็น MB, GB ให้อัตโนมัติ
    with tqdm(total=file_size, unit='B', unit_scale=True, desc="Calculating") as pbar:
        with open(file_path, "rb") as f:
            while (data := f.read(chunk_size)):
                md5_hash.update(data)
                # อัปเดตแถบความคืบหน้าตามจำนวน Byte ที่อ่านได้จริง
                pbar.update(len(data))
                
    return md5_hash.hexdigest()

# --- วิธีใช้งาน ---
file_to_check = r"ใส่ที่อยู่ไฟล์ของคุณจักร์ชัยตรงนี้.tar" # เปลี่ยนที่อยู่ไฟล์ด้วยนะครับ
expected_val = "372c0b184e32001137424e395823de3c" # ค่า MD5 จากเว็บ Xilinx

actual_hash = calculate_md5_with_progress(file_to_check)

if actual_hash.lower() == expected_val.lower():
    print("\n✅ [Pass] ไฟล์ถูกต้องสมบูรณ์!")
else:
    print("\n❌ [Fail] ไฟล์ไม่ถูกต้อง! กรุณาเช็คการดาวน์โหลดอีกครั้ง")