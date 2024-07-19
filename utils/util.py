import re
def removenextline(text: str) -> str:
    return re.sub(r"\n"," ",text)
def write_text_to_file(text: str, file_path: str) -> None:
    with open(file_path, "w", encoding="UTF-8") as f:
        f.write(text)