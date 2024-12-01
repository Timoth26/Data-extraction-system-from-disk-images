from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_pdf_report(partition_data, disk_image_name, personal_data, author, output_path='./report.pdf'):
    """
    Generates a PDF report based on the operating systems on the partitions and personal data obtained.

    :param output_path: Path to save the PDF file.
    :param partition_data: Dictionary in the format {partition: operating_system}.
    :param disk_image_name: Name of the disk image being analyzed.
    :param personal_data: Dictionary in the format {entity_group: count}.
    :param author: Dictionary containing the author's details.
    """
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

            y_position -= 10
            check_page_break()

        # Add Personal Data section
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y_position, "Personal Data Obtained")
        y_position -= 20
        check_page_break()

        pdf.setFont("Helvetica", 12)
        for entity_group, count in personal_data.items():
            pdf.drawString(50, y_position, f"Type: {entity_group}, Found: {count}")
            y_position -= 15
            check_page_break()

        # Save the PDF file
        pdf.save()
        print(f"PDF report saved at {output_path}")
    except Exception as e:
        print(f"An error occurred while generating the PDF report: {e}")