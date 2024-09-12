import fitz  # PyMuPDF

# Open the PDF file
pdf_document = "Bank exam parsing/Bank Exam Materials/ibps clerk prelims 2023 shift 1.pdf"
doc = fitz.open(pdf_document)
doc = fitz.open(pdf_document)

# Open a text file in write mode
with open("output.txt", "w", encoding="utf-8") as output_file:
    # Iterate through pages and extract text
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)  # Load each page
        text = page.get_text("text")  # Extract text in simple format
        output_file.write(f"Page {page_num + 1}:\n{text}\n")  # Write to text file