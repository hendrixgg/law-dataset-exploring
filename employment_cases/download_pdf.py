import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import time
import random

# take in a row to start at
ROW_TO_START = 35

employment_csv_filename = "employment_cases.csv"
table = pd.read_csv(employment_csv_filename)

url_column_name = "URL"
case_id_column_name = "Caseid"

assert url_column_name in table.columns, f"column 'URL' not found in {employment_csv_filename}"
assert case_id_column_name in table.columns, f"column 'Caseid' not found in {employment_csv_filename}"

# directory to store the pdfs
os.makedirs("downloaded_pdfs", exist_ok=True)

results = []

for index, row in table.iterrows():
    if index < ROW_TO_START:
        continue

    url = row[url_column_name]
    case_id = row[case_id_column_name]

    results.append({"Caseid": case_id, "original_url": url,
                    "pdf_url": None, "file_path": None, "status": None})

    if url == "NOT FOUND":
        continue

    while True:
        try:
            # access the web page
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad status codes
            soup = BeautifulSoup(response.text, 'html.parser')

            time.sleep(60 + 10*random.random())

            # find pdf link
            pdf_element = soup.find('a', id='pdf-link')
            if not pdf_element or not pdf_element.get('href'):
                results[-1]["status"] = "No PDF link found"
                print(f"No PDF link found for row={index} {case_id=} {url=}")
                continue
            pdf_link = pdf_element['href']

            # Handle relative URLs
            if not pdf_link.startswith('http'):
                pdf_link = urljoin(url, pdf_link)

            results[-1]["pdf_url"] = pdf_link

            time.sleep(60 + 10*random.random())

            # Download the PDF
            pdf_response = requests.get(pdf_link)
            pdf_response.raise_for_status()

            # Save the PDF
            filename = f"downloaded_pdfs/{case_id}.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_response.content)

            results[-1]["file_path"] = filename
            results[-1]["status"] = "Successfully downloaded"
            print(
                f"Downloaded PDF row={index} {case_id=} from {url} to {filename}")

            break
        except requests.RequestException as e:
            results[-1]["status"] = f"Failed: {str(e)}"
            print(f"Failed to process row={index} {case_id=} {url}: {e}")
            input("you probably need to go on the website and do a captcha, input anythinging here and press ENTER to continue")
        except Exception as e:
            results[-1]["status"] = f"Error: {str(e)}"
            print(f"Error processing row={index} {case_id=} {url}: {e}")

# Create a DataFrame from results
results_df = pd.DataFrame(
    results, columns=["Caseid", "original_url", "pdf_url", "file_path", "status"])

# Save the results to a new CSV
results_df.to_csv("download_results.csv", index=False)
print("Processing complete. Results saved to 'download_results.csv'")
