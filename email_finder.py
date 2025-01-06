import re
import os
import json
import csv
import pdfplumber
import sqlite3
import mailbox
from email import message_from_file

def search_emails_in_files(file_paths, output_file):
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    all_found_emails = set()

    for file_path in file_paths:
        file_extension = file_path.lower().split('.')[-1]
        found_emails = set()
        try:
            if file_extension in ["txt", "log", "eml"]:
                # Text files
                with open(file_path, 'r', errors='ignore') as f:
                    content = f.read()
                    found_emails = set(email_pattern.findall(content))

            elif file_extension == "csv":
                # CSV files
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        line = ' '.join(row)
                        found_emails.update(email_pattern.findall(line))

            elif file_extension == "json":
                # JSON files
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    data = json.load(f)
                    content = json.dumps(data)
                    found_emails.update(email_pattern.findall(content))

            elif file_extension == "xml":
                # XML files
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    found_emails.update(email_pattern.findall(content))

            elif file_extension == "html":
                # HTML files
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    found_emails.update(email_pattern.findall(content))

            elif file_extension == "pdf":
                # PDF files
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        content = page.extract_text() or ""
                        found_emails.update(email_pattern.findall(content))

            elif file_extension == "eml":
                # EML files
                with open(file_path, 'r', errors='ignore') as f:
                    msg = message_from_file(f)
                    content = msg.as_string()
                    found_emails.update(email_pattern.findall(content))

            elif file_extension == "mbox":
                # MBOX files
                mbox = mailbox.mbox(file_path)
                for message in mbox:
                    content = message.as_string()
                    found_emails.update(email_pattern.findall(content))

            elif file_extension in ["sqlite", "db"]:
                # SQLite/DB files
                conn = sqlite3.connect(file_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                for table in tables:
                    table_name = table[0]
                    try:
                        cursor.execute(f"SELECT * FROM {table_name}")
                        rows = cursor.fetchall()
                        for row in rows:
                            line = ' '.join(str(col) for col in row)
                            found_emails.update(email_pattern.findall(line))
                    except sqlite3.DatabaseError:
                        continue
                conn.close()

            elif file_extension == "msg":
                # MSG files
                with open(file_path, 'r', errors='ignore') as f:
                    content = f.read()
                    found_emails.update(email_pattern.findall(content))

            all_found_emails.update(found_emails)

            if found_emails:
                with open(output_file, "a", encoding="utf-8") as result_file:
                    result_file.write(f"Analysis of file: {file_path}\n")
                    for email in sorted(found_emails):
                        result_file.write(f"{email}\n")
                    result_file.write("\n")

        except (IOError, OSError, json.JSONDecodeError, sqlite3.DatabaseError) as e:
            print(f"[ERROR] Cannot open file: {file_path}. Error: {e}")

    return all_found_emails