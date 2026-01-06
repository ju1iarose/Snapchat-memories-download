# First run through will take the most time, about 25 files a minute (calculate files/25 for estimate)
# Some files may fail on the first run, run it again to skip files that were successful and retry the failed ones
# Run until the number of downloaded files is 0 and skipped files is your number of files


import json
import os
import urllib.request
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# CHANGE THESE TO CORRECT PATH
JSON_FILE = os.path.join(SCRIPT_DIR, r"C:\Your\Path\Here\memories_history.json")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, r"C:\Your\Path\Here\folder")
#

CHUNK_SIZE = 1024 * 1024 


os.makedirs(OUTPUT_DIR, exist_ok=True)

EXTENSION_MAP = {
    "Video": ".mp4",
    "Image": ".jpg"
}

with open(JSON_FILE, "r", encoding="utf-8") as f:
    raw = json.load(f)

# Access the JSON array
data = raw.get("Saved Media", [])
print(f"Found {len(data)} items")

# Downloading with progress
def download_with_progress(url, output_path, index, total):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        total_size = response.getheader("Content-Length")
        total_size = int(total_size) if total_size else None
        downloaded = 0
        with open(output_path, "wb") as out_file:
            while True:
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                out_file.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    percent = downloaded / total_size * 100
                    print(
                        f"\r[{index}/{total}] {percent:6.2f}% "
                        f"({downloaded // (1024*1024)} / {total_size // (1024*1024)} MB)",
                        end=""
                    )
                else:
                    print(f"\r[{index}/{total}] {downloaded // (1024*1024)} MB downloaded", end="")
        print()

# Download loop
total_files = len(data)
completed = 0
skipped = 0  

for idx, item in enumerate(data, start=1):
    date_str = item.get("Date")
    media_type = item.get("Media Type")
    url = item.get("Media Download Url")

    if not date_str or not media_type or not url:
        continue
    if media_type not in EXTENSION_MAP:
        continue

    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S UTC")
    base_name = dt.strftime("%Y-%m-%d_%H-%M-%S")
    extension = EXTENSION_MAP[media_type]

    output_path = os.path.join(OUTPUT_DIR, base_name + extension)

    # Skip if original file already exists (this is for failed files on first iteration, it will only work on second+ runs)
    if os.path.exists(output_path):
        print(f"\nSkipping existing file: {os.path.basename(output_path)}")
        skipped += 1
        continue

    # Handle timestamp duplicates
    counter = 1
    final_path = output_path
    while os.path.exists(final_path):
        final_path = os.path.join(OUTPUT_DIR, f"{base_name}_{counter}{extension}")
        counter += 1

    print(f"\nDownloading file {idx} of {total_files}: {os.path.basename(final_path)}")
    try:
        download_with_progress(url, final_path, idx, total_files)
        completed += 1
    except Exception as e:
        print(f"Failed: {e}")


print(f"\nFinished: {completed} files downloaded, {skipped} files skipped")

