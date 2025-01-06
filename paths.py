import os
import subprocess
import plistlib

import os

def get_path(partition, extensions=[".txt"], skip_system_paths=True):
    file_paths = []

    system_paths = [
        "/proc", "/sys", "/dev", "/run", "/var/lib", "/var/run",  # Linux
        "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",  # Windows
        "/usr", "/boot", "/etc"  # Linux
    ]

    print(f"[INFO] Searching in the partition: {partition}")

    for root, dirs, files in os.walk(partition):
        if skip_system_paths and any(root.startswith(path) for path in system_paths):
            continue

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


def detect_users(partition_path, os_type):
    users_info = {"status": "ok", "users": []}

    try:
        # Detect Linux users
        if os_type == "Linux":
            passwd_path = os.path.join(partition_path, "etc/passwd")
            if os.path.exists(passwd_path):
                with open(passwd_path, "r") as f:
                    for line in f:
                        parts = line.split(":")
                        if len(parts) > 1:
                            username = parts[0]
                            home_dir = parts[5]
                            if "/home/" in home_dir:
                                users_info["users"].append(username)
            else:
                users_info["status"] = "error"
                users_info["message"] = f"{passwd_path} not found"

        # Detect Windows users
        elif os_type == "Windows":
            users_dir = os.path.join(partition_path, "Users")
            if os.path.exists(users_dir):
                users_info["users"] = [
                    user for user in os.listdir(users_dir) 
                    if os.path.isdir(os.path.join(users_dir, user)) and not user.startswith("Default")
                ]
            else:
                users_info["status"] = "error"
                users_info["message"] = f"{users_dir} not found"

        # Detect macOS users
        elif os_type == "MacOS":
            plist_path = os.path.join(partition_path, "var/db/dslocal/nodes/Default/users")
            if os.path.exists(plist_path):
                for file in os.listdir(plist_path):
                    if file.endswith(".plist"):
                        user_path = os.path.join(plist_path, file)
                        with open(user_path, "rb") as f:
                            plist_data = plistlib.load(f)
                            if "home" in plist_data:
                                users_info["users"].append(file.replace(".plist", ""))
            else:
                users_info["status"] = "error"
                users_info["message"] = f"{plist_path} not found"

        else:
            users_info["status"] = "error"
            users_info["message"] = "Unsupported OS type"

    except Exception as e:
        users_info["status"] = "error"
        users_info["message"] = f"Failed to detect users: {e}"

    return users_info