from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_pdf_report(partition_data, users, disk_image_name, personal_data, email_results, social_results, author, output_path='./results/report.pdf'):
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        pdf = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter

        y_position = height - 50

        def check_page_break():
            nonlocal y_position
            if y_position < 50:
                pdf.showPage()
                pdf.setFont("Helvetica", 12)
                y_position = height - 50

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, y_position, "Disk Image Analysis Report for Personal Data")
        y_position -= 30

        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, y_position, f"Author: {author['Name']} {author['Surname']}")
        y_position -= 20
        pdf.drawString(50, y_position, f"Nr: {author['Nr']}")
        y_position -= 20

        pdf.drawString(50, y_position, f"Disk Image: {disk_image_name}")
        y_position -= 20

        pdf.drawString(50, y_position, f"Date and time of generation: {current_time}")
        y_position -= 30

        pdf.setLineWidth(1)
        pdf.line(50, y_position, width - 50, y_position - 5)
        y_position -= 20

        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y_position, "Partition and Operating System Analysis")
        y_position -= 20

        pdf.setFont("Helvetica", 12)
        for partition, os_info in partition_data.items():
            pdf.drawString(50, y_position, f"Partition: {partition}")
            y_position -= 15
            check_page_break()

            if isinstance(os_info, dict):
                for key, value in os_info.items():
                    if isinstance(value, dict):
                        for key1, value1 in value.items():
                            pdf.drawString(70, y_position, f"{key1}: {value1}")
                            y_position -= 15
                            check_page_break()
                    else:
                        pdf.drawString(70, y_position, f"{key}: {value}")
                        y_position -= 15
                        check_page_break()
            else:
                pdf.drawString(70, y_position, f"Operating System: {os_info}")
                y_position -= 15
                check_page_break()

            if partition in users:
                user_info = users[partition]
                pdf.drawString(70, y_position, "USERS: ")
                y_position -= 15
                check_page_break()

                if user_info["status"] == "ok" and user_info["users"]:
                    users_str = ", ".join(user_info["users"])
                    pdf.drawString(90, y_position, users_str)
                    y_position -= 15
                    check_page_break()
                else:
                    message = user_info.get("message", "No users found")
                    pdf.drawString(90, y_position, message)
                    y_position -= 15
                    check_page_break()

                y_position -= 10
                check_page_break()


        # Add Personal Data section if data exists
        if personal_data:
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(50, y_position, "Personal Data Obtained")
            y_position -= 20
            check_page_break()

            pdf.setFont("Helvetica", 12)
            for entity_group, count in personal_data.items():
                pdf.drawString(50, y_position, f"Type: {entity_group}, Found: {count}")
                y_position -= 15
                check_page_break()

        # Add Emails section if emails are found
        email_results = list(email_results)
        if email_results:
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(50, y_position, "Emails Found")
            y_position -= 20
            check_page_break()

            pdf.setFont("Helvetica", 12)
            for email in sorted(email_results):
                pdf.drawString(50, y_position, email)
                y_position -= 15
                check_page_break()

        # Add Social Media section if data is found
        if social_results:
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(50, y_position, "Social Media Accounts Found")
            y_position -= 20
            check_page_break()

            pdf.setFont("Helvetica", 12)
            for social_data in social_results:
                if social_data:
                    for browser, hosts in social_data.items():
                        if isinstance(hosts, dict):
                            for host, count in hosts.items():
                                pdf.drawString(50, y_position, f"Browser: {browser}, Host: {host}, Count: {count}")
                                y_position -= 15
                                check_page_break()


        # Save the PDF file
        pdf.save()
        print(f"[INFO] PDF report saved at {output_path}")
    except Exception as e:
        print(f"[ERROR] An error occurred while generating the PDF report: {e}")
