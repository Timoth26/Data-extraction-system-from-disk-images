import re
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from fpdf import FPDF


# Funkcja do wyodrębniania adresów e-mail i domen
def extract_emails_and_domains(content):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, content)
    domains = [email.split('@')[-1] for email in emails]
    return emails, domains


# Funkcja do tworzenia wykresu słupkowego
def plot_bar_chart(data, title, xlabel, ylabel, filename):
    df = pd.DataFrame(data, columns=[xlabel, ylabel])
    plt.figure(figsize=(10, 6))
    sns.barplot(x=ylabel, y=xlabel, data=df, palette="viridis")
    plt.title(title)
    plt.xlabel(ylabel)
    plt.ylabel(xlabel)
    plt.tight_layout()
    plt.savefig(filename)

def plot_histogram(data, title, xlabel, ylabel, filename):
    plt.figure(figsize=(10, 6))
    sns.histplot(data, bins=30, kde=True, color="blue")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(filename)
    
def analyze_cookies(cookie_data):
    browser_counts = Counter()
    host_counts = Counter()

    for browser_data in cookie_data:
        for browser, hosts in browser_data.items():
            browser_counts[browser] += sum(hosts.values())
            for host, count in hosts.items():
                host_counts[host] += count

    browser_data = browser_counts.most_common()
    host_data = host_counts.most_common()

    plot_bar_chart(browser_data, "Number of cookies per browser", 
                   "Browser", "Number of cookies", "browser_cookies.png")
    plot_bar_chart(host_data, "Number of cookies per host", 
                   "Host", "Number of cookies", "host_cookies.png")


# Funkcja do generowania raportu PDF
def generate_statistics_pdf(output_pdf, tables, images):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=False, margin=15)
    pdf.add_page()
    
    # Dodanie tabel
    for table_title, table_data in tables.items():
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(0, 10, table_title, ln=True)
        pdf.set_font("Arial", size=12)
        for row in table_data:
            row_text = " | ".join(map(str, row))
            pdf.cell(0, 10, row_text, ln=True)

    # Dodanie obrazów
    for image in images:
        pdf.add_page()
        pdf.image(image, x=10, y=20, w=190)

    pdf.output(output_pdf)
