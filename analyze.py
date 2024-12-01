from transformers import pipeline
import pdfplumber
from docx import Document
from bs4 import BeautifulSoup
from lxml import etree
from collections import Counter

def analyze_files(file_paths, output_file, score_threshold=0.80, chunk_size=1000):

    ner_pipeline = pipeline("token-classification", model="iiiorg/piiranha-v1-detect-personal-information", aggregation_strategy="simple")
    results = {}

    with open(output_file, "w", encoding="utf-8") as result_file:
        for file_path in file_paths:
            try:
                if file_path.lower().endswith(".pdf"):
                    print(f"Extracting text from PDF file: {file_path}")
                    text = extract_text_from_pdf(file_path)
                    
                elif file_path.lower().endswith(".txt"):
                    print(f"Analyzing text file: {file_path}")
                    with open(file_path, "r", encoding="utf-8") as file:
                        text = file.read()
                        
                elif file_path.lower().endswith(".docx"):
                    print(f"Extracting text from DOCX file: {file_path}")
                    text = extract_text_from_docx(file_path)
                    
                elif file_path.lower().endswith(".html") or file_path.lower().endswith(".xml"):
                    print(f"Extracting text from HTML/XML file: {file_path}")
                    text = extract_text_from_html(file_path)
                    
                elif file_path.lower().endswith(".xml"):
                    print(f"Extracting text from XML file: {file_path}")
                    text = extract_text_from_xml(file_path)
                    
                else:
                    print(f"Unsupported file format: {file_path}")
                    results[file_path] = None
                    continue

                ner_results = []
                for i in range(0, len(text), chunk_size):
                    chunk = text[i:i+chunk_size]
                    ner_results.extend(ner_pipeline(chunk))
                    
                filtered_results = [entity for entity in ner_results if entity['score'] >= score_threshold]

                result_file.write(f"Analysis of file: {file_path}\n\n")
                if filtered_results:
                    for entity in filtered_results:
                        result_file.write(f"Entity: {entity['word']}\nType: {entity['entity_group']}\nScore: {entity['score']:.4f}\nStart: {entity['start']}\nEnd: {entity['end']}\n\n")
                else:
                    result_file.write("No entities detected above the threshold.\n\n")
                
                result_file.write("-"*50 + "\n\n")
                results[file_path] = filtered_results
            except Exception as e:
                print(f"Error during analysis of file {file_path}: {e}")
                results[file_path] = f"ERROR: {e}"
                result_file.write(f"Analysis of file: {file_path}\n\n")
                result_file.write(results[file_path] + "\n\n")
                result_file.write("-"*50 + "\n\n")
    return results

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(docx_path):
    text = ""
    doc = Document(docx_path)
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_html(html_path):
    with open(html_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
        return soup.get_text()
    
def extract_text_from_xml(xml_path):
    with open(xml_path, "rb") as file:
        tree = etree.parse(file)
    return " ".join(tree.xpath("//text()"))