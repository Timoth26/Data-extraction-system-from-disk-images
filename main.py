import argparse
from mount_disc import DiskImageManager
from paths import get_path
from analyze import analyze_files

def main():
    parser = argparse.ArgumentParser(description="Mount a disk image and process its partitions.")
    parser.add_argument('image_path', type=str, help="Path to the disk image file")
    
    args = parser.parse_args()
    
    extensions = ['.txt', '.pdf', '.docx', '.html', '.xml']

    disk = DiskImageManager(str(args.image_path))
    paths = get_path(disk.mount_points, extensions)
    analyze_files(paths, 'final_results.txt')
    
    disk.cleanup()

if __name__ == '__main__':
    main()