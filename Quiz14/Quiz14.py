# Name: Bibek Thapa

import os
import time
import re
import pdfplumber
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

PDF_PATH = r"./sample-tables.pdf"
OUTPUT_DIR = "extracted_tables"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def clean_cell(value):
    if value is None:
        return ""
    value = str(value)
    value = value.replace("\n", " ").strip()
    value = re.sub(r"\s+", " ", value)
    return value


def clean_table(raw_table):
    cleaned_rows = []
    max_cols = 0

    for row in raw_table:
        if row is None:
            continue
        cleaned_row = [clean_cell(cell) for cell in row]

        # skip fully empty rows
        if any(cell != "" for cell in cleaned_row):
            cleaned_rows.append(cleaned_row)
            max_cols = max(max_cols, len(cleaned_row))

    # normalize row lengths
    normalized_rows = []
    for row in cleaned_rows:
        if len(row) < max_cols:
            row = row + [""] * (max_cols - len(row))
        normalized_rows.append(row)

    return normalized_rows


def is_good_table(table_rows):
    """
    Basic rule to decide whether table is worth saving.
    """
    if not table_rows:
        return False

    if len(table_rows) < 2:
        return False

    col_count = max(len(r) for r in table_rows)
    if col_count < 2:
        return False

    # count non-empty cells
    non_empty = sum(1 for row in table_rows for cell in row if str(cell).strip() != "")
    if non_empty < 4:
        return False

    return True


# Step 1: Open the PDF using Selenium
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=chrome_options)

pdf_url = "file:///" + os.path.abspath(PDF_PATH).replace("\\", "/")
driver.get(pdf_url)
time.sleep(3)

# Step 2: Extract tables with pdfplumber and save each good one immediately
saved_files = []

with pdfplumber.open(PDF_PATH) as pdf:
    for page_num, page in enumerate(pdf.pages, start=1):
        tables = page.extract_tables()

        if not tables:
            continue

        for table_index, raw_table in enumerate(tables, start=1):
            cleaned = clean_table(raw_table)

            if not is_good_table(cleaned):
                print(f"Skipped weak table: page {page_num}, table {table_index}")
                continue

            df = pd.DataFrame(cleaned)

            # Save CSV immediately
            csv_name = f"page_{page_num}_table_{table_index}.csv"
            csv_path = os.path.join(OUTPUT_DIR, csv_name)
            df.to_csv(csv_path, index=False, header=False, encoding="utf-8-sig")

            saved_files.append((page_num, table_index, csv_path))
            print(f"Saved good table: page {page_num}, table {table_index}")
            print(df)
            print("-" * 80)

driver.quit()

print("\nSaved files:")
for item in saved_files:
    print(f"Page {item[0]}, Table {item[1]} -> {item[2]}")