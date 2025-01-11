import argparse
import os
from mount_disc import DiskImageManager
from paths import get_path, detect_operating_system, detect_users
from analyze import analyze_files, count_entities
from generate_report import generate_pdf_report
from email_finder import search_emails_in_files
from social_analyze import extract_social_media_data
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(
    description=(
        "This script mounts a disk image and processes its partitions. "
        "It supports detecting operating systems, analyzing files, extracting emails, "
        "running OCR on images, analyzing social media data, and identifying personal data. "
        "The program is designed to detect sensitive personal information such as names, email addresses, and other identifiable data."
    )

    )
    parser.add_argument(
        'image_path', 
        type=str, 
        help="Absolute or relative path to the disk image file. Example: '/path/to/image.img."
    )
    parser.add_argument(
        '--name', 
        type=str, 
        required=False, 
        help="The first name of the person to be included in the metadata for the generated report.", 
        default=''
    )
    parser.add_argument(
        '--surname', 
        type=str, 
        required=False, 
        help="The surname of the person to be included in the metadata for the generated report.", 
        default=''
    )
    parser.add_argument(
        '--nr', 
        type=str, 
        required=False, 
        help="A unique identifier or number for the report. Example: '001', 'A123'.", 
        default=''
    )
    parser.add_argument(
        '-a', '--analyze', 
        action='store_true', 
        help=(
            "Enable AI-powered analysis of text-based files. "
            "Analyzed file types include .txt, .pdf, .docx, .doc"
        )
    )
    parser.add_argument(
        '-x', '--extend', 
        action='store_true', 
        help=(
            "Enable AI-powered analysis of more files. "
            "Analyzed file types include additionally .html, .xml, .log, .eml, .csv, json, .pptx, .odt, .md, .msg, .epub, .db, .sqlite"
        )
    )
    parser.add_argument(
        '-e', '--emails', 
        action='store_true', 
        help=(
            "Enable regex-based extraction of email addresses from files. "
            "Works on text, JSON, XML, CSV, and other supported formats."
        )
    )
    parser.add_argument(
        '-o', '--ocr', 
        action='store_true', 
        help=(
            "Enable Optical Character Recognition (OCR) for analyzing image-based files. "
            "Supported file types: .png, .jpeg, .jpg."
        )
    )
    parser.add_argument(
        '-s', '--social', 
        action='store_true', 
        help=(
            "Enable extraction of social media data from files and directories. "
            "This involves searching for patterns and extracting relevant social media information."
        )
    )
    parser.add_argument(
        '-r', '--sys_dir_analysis', 
        action='store_false', 
        help=(
            "Include system directories in the file search and analysis. "
            "By default, system directories are excluded for efficiency."
        )
    )
    args = parser.parse_args()
    
    extensions = []

    if args.analyze:
        extensions.extend(['.txt', '.pdf', '.docx', '.doc'])
    if args.extend:
        extensions.extend(['.html', '.xml', '.log', '.eml', '.csv', 'json', '.pptx', '.odt', '.md', '.msg', '.epub', '.db', 'sqlite'])
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
    
    if not os.path.exists('./results'):
        os.makedirs('./results')

    files_to_remove = [
        f"./results/analyze_results_{author['Nr']}.txt",
        f"./results/email_results_{author['Nr']}.txt",
        f"./results/social_results_{author['Nr']}.txt",
    ]

    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)

    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
        paths = get_path(partition, extensions, args.sys_dir_analysis)

        if args.analyze or args.ocr:
            print("[INFO] Starting file analysis...")
            analyze_results.update(analyze_files(paths, f"./results/analyze_results_{author['Nr']}.txt"))

        if args.emails:
            print("[INFO] Searching for email addresses...")
            email_results.update(search_emails_in_files(paths, f"./results/email_results_{author['Nr']}.txt"))

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
        output_path=f"./results/report_{author['Nr']}.pdf",
        start_time=start_time
    )

    print("[INFO] Cleaning up disk mounts...")
    disk.cleanup()

    print("[INFO] Process completed successfully!")

if __name__ == '__main__':
    main()