import os

def get_path(mounted_partitions, extensions=[".txt"]):
    file_paths = []

    for partition in mounted_partitions:
        print(f"Searching in the partition: {partition}")
        for root, dirs, files in os.walk(partition):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_paths.append(os.path.join(root, file))

    return file_paths