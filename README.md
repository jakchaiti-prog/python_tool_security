📝 README.md (Professional Security Edition)
Markdown
# 🛡️ Secure Data Toolkit (SDT)
**Developed by: Jakchai**

A robust, modular CLI toolkit designed for high-security data management, integrity verification, and multi-owner encryption. Ideal for engineers and consultants handling sensitive datasets (e.g., FPGA projects, Database Archives). [cite: 2026-01-28, 2026-02-02]

## ✨ Key Features
* **Multi-Owner Encryption (JWE)**: Secure files using RSA-OAEP encryption that supports multi-signature logic (1-3 keys). [cite: 2026-02-02]
* **Key Lifecycle Management**: Generate RSA key pairs with embedded expiration metadata (Expiry Control). [cite: 2026-02-02]
* **Data Integrity Verification**: High-speed MD5/SHA checksums with real-time progress visualization.
* **Large-Scale Extraction**: Optimized for extracting massive archives (100GB+) safely after integrity checks.

## 🚀 Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
2. Generate a Security Key (with 30-day expiry)
Bash
python security_vault.py --gen-key --owner "Jakchai" --days 30
3. Encrypt a Sensitive File
Bash
python security_vault.py encrypt -f "project_data.tar.gz" -k "key_jakchai.json"
4. Verify & Extract Large Files
Bash
python extract_tool.py -f "Vivado_Installer.tar.gz"
🛠️ Requirements
Python 3.11+

python-jose[cryptography]

tqdm