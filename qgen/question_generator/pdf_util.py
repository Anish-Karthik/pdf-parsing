import os
import PyPDF2

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
    # print(f"PDF file split into {end_page - start_page + 1} smaller files.")
