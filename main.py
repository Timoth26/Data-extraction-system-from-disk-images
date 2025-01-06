import argparse
from mount_disc import DiskImageManager
from paths import get_path, detect_operating_system, detect_users
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
    parser.add_argument('-s', '--social', action='store_true', required=False, help="Run social media analysis", default=False)
    parser.add_argument('-r', '--require_system_dir_analyse', action='store_false', required=False, help="Run analysis also in system directories", default=True)

    args = parser.parse_args()
    extensions = []

    if args.analyze:
        extensions.extend(['.txt', '.pdf', '.docx', '.doc', '.html', '.xml', '.log', '.eml', '.csv', 'json', '.pptx', '.odt', '.md', '.msg', '.epub', '.db'])
    if args.ocr:
        extensions.extend(['.png', '.jpeg', '.jpg'])

    disk = DiskImageManager(str(args.image_path))

    author = {
        'Name': args.name,
        'Surname': args.surname,
        'Nr': args.nr
    }

    os_results = {}
    users = {}
    email_results = set()
    analyze_results = {}
    social_results = []

    for partition in disk.mount_points:
        print(f"[INFO] Processing partition: {partition}")

        print("[INFO] Detecting operating system...")
        os_system = detect_operating_system(partition)
        if os_system["status"] == "ok":
            os_type = os_system["type"]
            print(f"[INFO] Detected operating system: {os_type}")

            print("[INFO] Detecting users...")
            users_info = detect_users(partition, os_type)
            if users_info["status"] == "ok":
                print(f"[INFO] Detected users: {', '.join(users_info['users'])}")
            else:
                print(f"[ERROR] User detection error: {users_info['message']}")

            users[partition] = users_info
        else:
            print(f"[ERROR] OS detection error: {os_system['message']}")

        os_results[partition] = os_system

        print("[INFO] Searching for files...")
        paths = get_path(partition, extensions, args.require_system_dir_analyse)

        if args.analyze or args.ocr:
            print("[INFO] Starting file analysis...")
            analyze_results = analyze_files(paths, f"./results/analyze_results_{author['Nr']}.txt")

        if args.emails:
            print("[INFO] Searching for email addresses...")
            email_results = search_emails_in_files(paths, f"./results/email_results_{author['Nr']}.txt")

        if args.social:
            print("[INFO] Extracting social media data...")
            social_results.append(extract_social_media_data(partition, f"./results/social_results_{author['Nr']}.txt"))

    print("[INFO] Generating final report...")
    generate_pdf_report(
        os_results,
        users,
        str(args.image_path),
        count_entities(analyze_results),
        email_results,
        social_results,
        author,
        output_path=f"./results/report_{author['Nr']}.pdf"
    )

    print("[INFO] Cleaning up disk mounts...")
    disk.cleanup()

    print("[INFO] Process completed successfully!")

if __name__ == '__main__':
    main()