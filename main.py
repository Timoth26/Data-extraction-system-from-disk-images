import argparse
from mount_disc import DiskImageManager
from paths import get_path, detect_operating_system
from analyze import analyze_files, count_entities
from generate_report import generate_pdf_report

def main():
    parser = argparse.ArgumentParser(description="Mount a disk image and process its partitions.")
    parser.add_argument('image_path', type=str, help="Path to the disk image file")
    parser.add_argument('--name', type=str, required=True, help="Name of the person")
    parser.add_argument('--surname', type=str, required=True, help="Surname of the person")
    parser.add_argument('--nr', type=str, required=True, help="Number (identifier)")
    
    args = parser.parse_args()
    
    extensions = ['.txt', '.pdf', '.docx', '.html', '.xml']

    disk = DiskImageManager(str(args.image_path))
    
    author = {}
    author['Name'] = args.name
    author['Surname'] = args.surname
    author['Nr'] = args.nr
    
    os_results = {}
        
    for partition in disk.mount_points:
        os_system = detect_operating_system(partition)
        os_results[partition] = os_system
        paths = get_path(partition, extensions)
        analyze_results = analyze_files(paths, f"final_results_{author['Nr']}.txt")
    
    generate_pdf_report(os_results, str(args.image_path), count_entities(analyze_results), author)
    
    disk.cleanup()

if __name__ == '__main__':
    main()