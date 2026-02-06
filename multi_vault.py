import argparse

def setup_cli():
    parser = argparse.ArgumentParser(
        description="🛡️ Secure Data Toolkit - Developed by Jakchai",
        epilog="Note: This tool requires valid security keys with non-expired metadata."
    )
    
    parser.add_argument("action", choices=['encrypt', 'decrypt'], 
                        help="Action to perform on the target file.")
    
    parser.add_argument("-f", "--file", required=True, 
                        help="The full path to the file you want to process.")
    
    parser.add_argument("-k", "--keys", nargs='+', required=True, 
                        help="Security keys for multi-signature decryption (1-3 keys).")
    
    return parser.parse_args()