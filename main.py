import argparse
from mount_disc import DiskImageManager
from paths import get_path, detect_operating_system,detect_users
from analyze import analyze_files, count_entities
from generate_report import generate_pdf_report
from email_finder import search_emails_in_files
from social_analyze import extract_social_media_data

def main():
    parser = argparse.ArgumentParser(description="Mount a disk image and process its partitions.")
    parser.add_argument('image_path', type=str, help="Path to the disk image file")
    parser.add_argument('--name', type=str, required=False, help="Name of the person", default='')
    parser.add_argument('--surname', type=str, required=False, help="Surname of the person", default='')
    parser.add_argument('--nr', type=str, required=False, help="Number (identifier)", default='')
    parser.add_argument('-a', '--analyze', action='store_true', required=False, help="Run AI analysis", default=False)
    parser.add_argument('-e', '--emails', action='store_true', required=False, help="Run regex email analysis", default=False)
    parser.add_argument('-o', '--ocr', action='store_true', required=False, help="Run OCR analysis", default=False)
    parser.add_argument('-s', '--social', action='store_true', required=False, help="Run OCR analysis", default=False)
    parser.add_argument('-r', '--require_system_dir_analyse', action='store_false', required=False, help="Run analysis also in system directories", default=True)

    
    args = parser.parse_args()
    extensions = []
    
    if args.analyze:
        extensions.extend(['.txt', '.pdf', '.docx', '.doc', '.html', '.xml', '.log', '.eml', '.csv', 'json', '.pptx', '.odt', '.md', '.msg', '.epub', '.db'])
    if args.ocr:
        extensions.extend(['.png', '.jpeg', '.jpg'])

    disk = DiskImageManager(str(args.image_path))
    
    author = {}
    author['Name'] = args.name
    author['Surname'] = args.surname
    author['Nr'] = args.nr
    
    os_results = {}
    users = {}
    email_results = set()
    analyze_results = {}
    social_results = []
        
    for partition in disk.mount_points:
        os_system = detect_operating_system(partition)
        
        if os_system["status"] == "ok":
            os_type = os_system["type"]
            users_info = detect_users(partition, os_type)
            if users_info["status"] == "ok":
                print("Detected users:", users_info["users"])
            else:
                print("Error:", users_info["message"])
                
            users[partition] = users_info

        else:
            print("OS detection error:", os_system["message"])

        
        os_results[partition] = os_system
        paths = get_path(partition, extensions, args.require_system_dir_analyse)
        
        if args.analyze or args.ocr:
            analyze_results = analyze_files(paths, f"./results/analyze_results_{author['Nr']}.txt")
        if args.emails:
            email_results = search_emails_in_files(paths, f"./results/email_results_{author['Nr']}.txt")
        if args.social:
            social_results.append(extract_social_media_data(partition, f"./results/social_results_{author['Nr']}.txt"))
            
        print(social_results)
    
    generate_pdf_report(os_results, users, str(args.image_path), count_entities(analyze_results), email_results, social_results, author, output_path=f"./results/report_{author['Nr']}.pdf")
    
    disk.cleanup()

if __name__ == '__main__':
    main()