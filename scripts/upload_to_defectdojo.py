#!/usr/bin/env python3
"""
Utility script to import pipelineguard scan results into DefectDojo.
Requires DEFECTDOJO_URL, DEFECTDOJO_API_TOKEN, and DEFECTDOJO_ENGAGEMENT_ID env vars.
"""

import os
import sys
import glob
import requests

# DefectDojo API settings
DEFECTDOJO_URL = os.getenv("DEFECTDOJO_URL")
API_TOKEN = os.getenv("DEFECTDOJO_API_TOKEN")
ENGAGEMENT_ID = os.getenv("DEFECTDOJO_ENGAGEMENT_ID")

# Mapping of file names in outputs/ to DefectDojo scan types
SCAN_TYPES = {
    "trivy-fs.json": "Trivy Scan",
    "trivy-config.json": "Trivy Scan",
    "gitleaks.json": "Gitleaks Scan",
    "semgrep.json": "Semgrep JSON Report",
    "checkov.json": "Checkov Scan"
}

def upload_file(file_path: str, scan_type: str, service_name: str) -> bool:
    if not os.path.exists(file_path):
        print(f"[-] File not found: {file_path}")
        return False

    # Check if the file is empty or contains an empty array (common for gitleaks/semgrep when no leaks are found)
    if os.path.getsize(file_path) == 0:
        print(f"[!] Skipping empty file: {file_path}")
        return False

    url = f"{DEFECTDOJO_URL.rstrip('/')}/api/v2/import-scan/"
    headers = {
        "Authorization": f"Token {API_TOKEN}"
    }
    
    data = {
        "scan_type": scan_type,
        "engagement": ENGAGEMENT_ID,
        "verified": "true",
        "active": "true",
        "service": service_name,
        "close_old_findings": "true",
        "close_old_findings_product_scope": "true"
    }

    print(f"[+] Importing {scan_type} results for service '{service_name}' from {file_path}...")
    verify_ssl = os.getenv("DEFECTDOJO_VERIFY_SSL", "true").lower() in ("true", "1", "yes")
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/json')}
            response = requests.post(url, headers=headers, data=data, files=files, verify=verify_ssl)
            
        if response.status_code in [200, 201]:
            print(f"[+] Successfully uploaded {file_path} to DefectDojo (Status: {response.status_code})")
            return True
        else:
            print(f"[-] Failed to upload {file_path}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[-] Error uploading {file_path}: {e}")
        return False

def main():
    if not DEFECTDOJO_URL or not API_TOKEN or not ENGAGEMENT_ID:
        print("[-] Error: Missing required environment variables: DEFECTDOJO_URL, DEFECTDOJO_API_TOKEN, DEFECTDOJO_ENGAGEMENT_ID")
        print("[*] Please set them before running the script:")
        print("    export DEFECTDOJO_URL='https://dojo.example.com'")
        print("    export DEFECTDOJO_API_TOKEN='your_api_token_here'")
        print("    export DEFECTDOJO_ENGAGEMENT_ID='1'")
        sys.exit(1)

    outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../outputs"))
    if not os.path.exists(outputs_dir):
        print(f"[-] Outputs directory not found: {outputs_dir}")
        sys.exit(1)

    print(f"[*] Scanning {outputs_dir} for report files...")
    
    success_count = 0
    total_count = 0

    # Walk through each subdirectory in outputs/ (each represent a scanned repo)
    for repo_name in os.listdir(outputs_dir):
        repo_path = os.path.join(outputs_dir, repo_name)
        if not os.path.isdir(repo_path):
            continue

        print(f"\n[*] Processing findings for repo: {repo_name}")
        for file_name, scan_type in SCAN_TYPES.items():
            file_path = os.path.join(repo_path, file_name)
            if os.path.exists(file_path):
                total_count += 1
                if upload_file(file_path, scan_type, repo_name):
                    success_count += 1

    print(f"\n[*] Completed. Uploaded {success_count}/{total_count} files successfully.")

if __name__ == "__main__":
    main()
