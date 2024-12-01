import os
import subprocess
import plistlib

def get_path(partition, extensions=[".txt"]):
    file_paths = []

    print(f"Searching in the partition: {partition}")
    for root, dirs, files in os.walk(partition):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_paths.append(os.path.join(root, file))

    return file_paths


def detect_operating_system(partition_path):
    if not os.path.exists(partition_path):
        return {"status": "error", "message": "Partition not found"}
    
    os_info = {"status": "ok", "type": "Unknown", "details": {}}

    # Linux
    if os.path.exists(os.path.join(partition_path, "etc/os-release")):
        os_info["type"] = "Linux"
        try:
            with open(os.path.join(partition_path, "etc/os-release")) as f:
                for line in f:
                    key, _, value = line.partition("=")
                    os_info["details"][key.strip()] = value.strip().strip('"')
        except Exception as e:
            os_info["details"]["error"] = f"Failed to read os-release: {e}"
    
    # Windows
    elif os.path.exists(os.path.join(partition_path, "Windows/System32/ntoskrnl.exe")):
        os_info["type"] = "Windows"
        os_info["details"]["hint"] = "System32 detected"
        try:
            # Windows version
            winver_path = os.path.join(partition_path, "Windows/System32/license.rtf")
            if os.path.exists(winver_path):
                with open(winver_path, "r", errors="ignore") as f:
                    for line in f:
                        if "Windows" in line:
                            os_info["details"]["version"] = line.strip()
                            break
        except Exception as e:
            os_info["details"]["error"] = f"Failed to extract Windows version: {e}"

    # macOS
    elif os.path.exists(os.path.join(partition_path, "System/Library/CoreServices/SystemVersion.plist")):
        os_info["type"] = "MacOS"
        try:
            plist_path = os.path.join(partition_path, "System/Library/CoreServices/SystemVersion.plist")
            with open(plist_path, "rb") as f:
                plist_data = plistlib.load(f)
                os_info["details"] = {key: plist_data[key] for key in plist_data}
        except Exception as e:
            os_info["details"]["error"] = f"Failed to read SystemVersion.plist: {e}"
    
    else:
        os_info["status"] = "error"
        os_info["message"] = "No recognizable OS detected on the partition"

    return os_info
