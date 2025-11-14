#!/usr/bin/env python3
import os
import zipfile
import tempfile
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# --- Artifact list, inspired by Cado Security! ---
ARTIFACT_PATHS = [
    # User-level
    os.path.expanduser("~/.bash_history"),
    os.path.expanduser("~/.ssh/known_hosts"),
    "/root/.bash_history",
    "/root/.ssh/known_hosts",

    # /var artifacts
    "/var/adm/wtmp",
    "/var/db/application_usage.sqlite",
    "/var/log",
    "/var/run/utmp",
    "/var/run/wtmp",

    # /etc artifacts
    "/etc/passwd",
    "/etc/group",
    "/etc/hosts",
    "/etc/hosts.allow",
    "/etc/hosts.deny",
    "/etc/rc.d",
    "/etc/utmp",
    "/etc/httpd/logs",

    # macOS/Unix system dirs
    "/System/Library/LaunchAgents",
    "/System/Library/LaunchDaemons",
    "/System/Library/StartupItems",
    "/Library/LaunchAgents",
    "/Library/LaunchDaemons",
    "/Library/Preferences/SystemConfiguration",
    "/Library/Receipts/InstallHistory.plist",
    "/Library/StartupItems",
]

# --- Helper functions ---
def is_regular_file(p):
    """Return True if path exists and is a regular file."""
    return os.path.isfile(p)

def safe_walk(p):
    """Yield (root, dirs, files) for a directory, skipping inaccessible dirs."""
    try:
        for root, dirs, files in os.walk(p, followlinks=False):
            yield root, dirs, files
    except Exception as e:
        print(f"[!] Skipping {p}: {e}")

def zip_artifacts(output_path, paths):
    """Zip only the specified artifact paths."""
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            path_obj = Path(p)
            if not path_obj.exists():
                print(f"[!] Skipping missing path: {p}")
                continue
            if path_obj.is_file():
                try:
                    z.write(p, arcname=path_obj.relative_to("/"))
                except Exception as e:
                    print(f"[!] Skipping {p}: {e}")
            elif path_obj.is_dir():
                for root, dirs, files in safe_walk(p):
                    for f in files:
                        full_path = os.path.join(root, f)
                        try:
                            if not os.path.isfile(full_path):
                                continue
                            z.write(full_path, arcname=os.path.relpath(full_path, "/"))
                        except Exception as e:
                            print(f"[!] Skipping {full_path}: {e}")
            else:
                print(f"[!] Skipping non-regular path: {p}")
    return output_path

def upload_presigned(url, file_path):
    """Upload file to presigned S3 URL via PUT using stdlib."""
    with open(file_path, "rb") as f:
        data = f.read()
    req = Request(url, data=data, method="PUT", headers={"Content-Type": "application/zip"})
    try:
        with urlopen(req) as resp:
            if 200 <= resp.status < 300:
                print("[✓] Upload complete")
            else:
                raise RuntimeError(f"Upload failed with status {resp.status}")
    except HTTPError as e:
        raise RuntimeError(f"HTTPError: {e}")
    except URLError as e:
        raise RuntimeError(f"URLError: {e}")

# --- Main workflow ---
def main():
    if len(sys.argv) != 2:
        print("Usage: collector <presigned-url>")
        sys.exit(1)

    presigned_url = sys.argv[1]

    # Temporary zip location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        zip_path = tmp.name

    print(f"[+] Creating zip archive at {zip_path}")
    zip_artifacts(zip_path, ARTIFACT_PATHS)

    print(f"[+] Uploading archive to S3...")
    upload_presigned(presigned_url, zip_path)

    print(f"[+] Cleaning up temporary archive")
    os.remove(zip_path)

if __name__ == "__main__":
    main()
