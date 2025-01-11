from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from textwrap import wrap

def draw_wrapped_text(pdf, text, x, y, max_width, font_name="Helvetica", font_size=12, line_height=15):
    pdf.setFont(font_name, font_size)

    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        if pdf.stringWidth(current_line + " " + word, font_name, font_size) <= max_width:
            current_line += " " + word if current_line else word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    for line in lines:
        pdf.drawString(x, y, line)
        y -= line_height

    return y


def generate_pdf_report(partition_data, users, disk_image_name, personal_data, email_results, social_results, author, 
                        output_path='./results/report.pdf', start_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
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

        # Title
        pdf.setFont("Helvetica-Bold", 16)
        y_position = draw_wrapped_text(pdf, "Disk Image Analysis Report for Personal Data", 50, y_position, max_width=width - 100)
        
        pdf.setFont("Helvetica", 12)
        y_position = draw_wrapped_text(pdf, f"Author: {author['Name']} {author['Surname']}", 50, y_position, max_width=width - 100)
        y_position = draw_wrapped_text(pdf, f"Nr: {author['Nr']}", 50, y_position, max_width=width - 100)
        y_position = draw_wrapped_text(pdf, f"Disk Image: {disk_image_name}", 50, y_position, max_width=width - 100)
        y_position = draw_wrapped_text(pdf, f"Date and time of start analysis: {start_time}", 50, y_position, max_width=width - 100)
        y_position = draw_wrapped_text(pdf, f"Date and time of end analysis and report generation: {current_time}", 50, y_position, max_width=width - 100)
        y_position = draw_wrapped_text(pdf, "The system performs data analysis by extracting information from documents.\
                                       The detection of personal data is carried out using the NER model lakshyakh93/deberta_finetuned_pii, \
                                       which identifies sensitive information such as names, email addresses, or phone numbers. Additionally, \
                                       user activity is analyzed by searching browsing history and cookie files to identify visited social media \
                                       websites. The system also enables text extraction from images in .png and .jpg formats by leveraging OCR \
                                       technology using EasyOCR and OpenCV. All analytical operations are conducted on a copy of the disk image, \
                                       mounted in read-only mode, ensuring data integrity throughout the entire process.", 50, y_position, max_width=width - 100, font_size=8, line_height=10)
        
        pdf.setLineWidth(1)
        pdf.line(50, y_position-5, width - 50, y_position - 5)
        y_position -= 20

        pdf.setFont("Helvetica-Bold", 14)
        y_position = draw_wrapped_text(pdf, "Partition and Operating System Analysis", 50, y_position, max_width=width - 100)
        
        pdf.setFont("Helvetica", 12)
        for partition, os_info in partition_data.items():
            y_position = draw_wrapped_text(pdf, f"Partition: {partition}", 50, y_position, max_width=width - 100)
            check_page_break()

            if isinstance(os_info, dict):
                for key, value in os_info.items():
                    if isinstance(value, dict):
                        for key1, value1 in value.items():
                            y_position = draw_wrapped_text(pdf, f"{key1}: {value1}", 70, y_position, max_width=width - 120)
                            check_page_break()
                    else:
                        y_position = draw_wrapped_text(pdf, f"{key}: {value}", 70, y_position, max_width=width - 120)
                        check_page_break()
            else:
                y_position = draw_wrapped_text(pdf, f"Operating System: {os_info}", 70, y_position, max_width=width - 120)

            if partition in users:
                user_info = users[partition]
                y_position = draw_wrapped_text(pdf, "USERS: ", 70, y_position, max_width=width - 100)
                check_page_break()

                if user_info["status"] == "ok" and user_info["users"]:
                    users_str = ", ".join(user_info["users"])
                    y_position = draw_wrapped_text(pdf, users_str, 90, y_position, max_width=width - 120)
                else:
                    message = user_info.get("message", "No users found")
                    y_position = draw_wrapped_text(pdf, message, 90, y_position, max_width=width - 120)

        y_position -= 10
        check_page_break()

        # Personal Data section
        if personal_data:
            pdf.setFont("Helvetica-Bold", 14)
            y_position = draw_wrapped_text(pdf, "Personal Data Obtained", 50, y_position, max_width=width - 100)
            pdf.setFont("Helvetica", 12)

            for entity_group, count in personal_data.items():
                check_page_break()
                y_position = draw_wrapped_text(pdf, f"Type: {entity_group}, Found: {count}", 50, y_position, max_width=width - 100)

        y_position -= 10
        check_page_break()


        # Emails section
        if email_results:
            pdf.setFont("Helvetica-Bold", 14)
            y_position = draw_wrapped_text(pdf, "Emails Found", 50, y_position, max_width=width - 100)
            pdf.setFont("Helvetica", 12)
            for email in sorted(email_results):
                check_page_break()
                y_position = draw_wrapped_text(pdf, email, 50, y_position, max_width=width - 100)

        y_position -= 10
        check_page_break()

        # Social Media section
        if social_results:
            pdf.setFont("Helvetica-Bold", 14)
            y_position = draw_wrapped_text(pdf, "Social Media Accounts Found", 50, y_position, max_width=width - 100)
            pdf.setFont("Helvetica", 12)
            for social_data in social_results:
                if social_data:
                    for browser, hosts in social_data.items():
                        if isinstance(hosts, dict):
                            for host, count in hosts.items():
                                display_host = host if len(host) <= 50 else host[:50] + "..."
                                text = f"Browser: {browser}, Host: {display_host}, Count: {count}"
                                
                                check_page_break()
                                y_position = draw_wrapped_text(pdf, text, 50, y_position, max_width=width - 100)

        # Save the PDF
        pdf.save()
        print(f"[INFO] PDF report saved at {output_path}")
    except Exception as e:
        print(f"[ERROR] An error occurred while generating the PDF report: {e}")
        