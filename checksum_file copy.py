# https://www.geeksforgeeks.org/python/verify-integrity-of-files-using-digest-in-python/
import argparse
import hashlib
import sys
from colorama import init, Fore
from cryptography.fernet import Fernet
import hashlib

# Initialize colorama for colored terminal text.
init()

# Define a function to calculate SHA-256 hash of a file.

def calculate_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        while (data:= file.read(65536)):
            sha256_hash.update(data)

        return sha256_hash.hexdigest()

# Function to verify hash of a downloaded file.


def verify_hash(downloaded_file, expected_hash):
    calculated_hash = calculate_hash(downloaded_file)
    return calculated_hash == expected_hash


# Command-line argument parsing.
parser = argparse.ArgumentParser(description="Verify downloaded file's hash.")
parser.add_argument("-f", "--file", dest="downloaded_file",
                    required=True, help="Path of the downloaded file")
parser.add_argument("--hash", dest="expected_hash",
                    required=True, help="Expected hash value")


args = parser.parse_args()


# Validate arguments and perform hash verification.
try:
    if not args.downloaded_file or not args.expected_hash:
        print(
            f"{Fore.RED}[-] Please specify the file and its hash for validation.")
    sys.exit()
except:
        print(
            f"{Fore.RED}[-] Please specify the file and its hash for validation.")
        sys.exit()

if verify_hash(args.downloaded_file, args.expected_hash):
    print(
        f"{Fore.GREEN}[+] Hash verification successful. The file is original.")
else:
    print(
        f"{Fore.RED}[-] Hash verification failed. This may indicate tampering or non-original software.")