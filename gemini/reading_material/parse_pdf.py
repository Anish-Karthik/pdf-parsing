from gemini_utilities import *
import PyPDF2
import fitz


def upload_file(file):
    file = generativeai.upload_file(file)

    prompt = f"""
            Read the attached pdf and return the content as it is.

            Format it better.

            **Don't omit any information.**
        """
    response = model.generate_content([prompt, file])

    print(response.text)
    return response.text


def extract_filename_without_extension(file_path):
    """Extracts the filename without extension from a given file path.

    Args:
      file_path: The full path to the file.

    Returns:
      The filename without extension.
    """
    filename = os.path.basename(file_path)
    filename_without_extension, _ = os.path.splitext(filename)
    return filename_without_extension


def split_pdf(input_pdf_path, output_folder, start_page, end_page):
    """Splits a PDF file into smaller PDF files based on the specified page range.

    Args:
        input_pdf_path (str): The path to the input PDF file.
        output_folder (str): The path to the output folder where the split PDF files will be saved.
        start_page (int): The starting page number (1-based).
        end_page (int): The ending page number (1-based).
    """

    with open(input_pdf_path, 'rb') as input_pdf:
        pdf_reader = PyPDF2.PdfReader(input_pdf)
        num_pages = len(pdf_reader.pages)

        if start_page < 1 or end_page > num_pages or start_page > end_page:
            raise ValueError("Invalid page range.")

        pdf_writer = PyPDF2.PdfWriter()
        for i in range(start_page - 1, end_page):
            pdf_writer.add_page(pdf_reader.pages[i])

        input_file_name = extract_filename_without_extension(input_pdf_path)
        output_pdf_name = "{input_file_name}-{start_page}-{end_page}.pdf".format(
            input_file_name=input_file_name, start_page=start_page, end_page=end_page)
        output_pdf_path = os.path.join(output_folder, output_pdf_name)
        with open(output_pdf_path, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)

    return output_pdf_path


def read_txt_file(path):
    with open(path, "r") as f:
        return f.read()

def read_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    txt = ""
    for page in doc:
        txt += page.get_text()
    return txt


def parse_pdf(pdf_path):
    txt_path = pdf_path[:-4] + ".txt"
    folder_path = pdf_path[:-4]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if os.path.exists(txt_path):
        return read_txt_file(txt_path)

    doc = fitz.open(pdf_path)
    pages = len(doc)
    txt = ""
    for i in range(1, pages + 1):
        page_pdf_path = split_pdf(pdf_path, folder_path, i, i)
        try:
            page_content = upload_file(page_pdf_path)
        except Exception as e:
            print(e)
            page_content = read_pdf(page_pdf_path)
        txt += page_content

    with open(txt_path, "w") as f:
        f.write(txt)

    return txt


def split_content_into_parts(content, delimiter):
    prompt = f"""
      Split each paragraph/distinct sections using the delimiter: {delimiter} and next line.

              **Don't omit any information.**

              **Don't add any information.**

              Content:
              {content}
          """
    response = model.generate_content(prompt)
    return response.text


def remove_empty(parts):
    parts = [part for part in parts if part.strip() != ""]

    if len(parts[-1]) < 35 and len(parts) > 1:
        parts[-2] += parts[-1]
        parts = parts[:-1]

    return parts


def split_ncert_into_parts(folder_path):
    delimiter = "&&PART&&"
    splitted_content = []
    last_part = ""
    for file in sorted(os.listdir(folder_path)):
        if not file.endswith(".txt"):
            continue

        with open(os.path.join(folder_path, file), "r") as f:
            page_content = f.read()

            split_content = split_content_into_parts(last_part + page_content, delimiter)
            split_content = delimiter + split_content
            splitted_content += remove_empty(split_content.split(delimiter))
            print(splitted_content)

            last_part = splitted_content[-1]
            splitted_content = splitted_content[:-1]

    splitted_content.append(last_part)

    with open(os.path.join(folder_path, f"kebo101.txt"), "w") as f:
        f.write(f"\n{delimiter}\n".join(splitted_content))


# parse_pdf("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/ncert_books/biology/kebo101.pdf")
# split_ncert_into_parts("/Users/pranav/GitHub/pdf-parsing/gemini/Neet/ncert_books/biology/kebo101")
