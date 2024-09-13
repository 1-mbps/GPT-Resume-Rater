from PyPDF2 import PdfReader
import csv
import io
import openpyxl

def build_csv_string(data):
    if not data:
        return ""
    
    # Ensure 'name' is the first key
    fieldnames = ['name'] + [key for key in data[0].keys() if key != 'name']
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    
    return output.getvalue()

def csv_to_excel(csv_string, output_filename):
    # Create a workbook and select the active worksheet
    wb = openpyxl.Workbook()
    ws = wb.active

    # Read the CSV data
    csv_data = csv.reader(csv_string.splitlines())

    # Write the CSV data to the worksheet
    for row in csv_data:
        ws.append(row)

    # Save the workbook
    wb.save(output_filename)

def convert_pdf_to_text(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error converting PDF to text: {str(e)}")
        return None