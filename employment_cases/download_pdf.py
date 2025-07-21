import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import time
import random
import msvcrt


# take in a row to start at
ROW_TO_START = 367

wait_time_seconds = 16

employment_csv_filename = "employment_cases.csv"
table = pd.read_csv(employment_csv_filename)

url_column_name = "URL"
case_id_column_name = "Caseid"

assert url_column_name in table.columns, f"column 'URL' not found in {employment_csv_filename}"
assert case_id_column_name in table.columns, f"column 'Caseid' not found in {employment_csv_filename}"

# directory to store the pdfs
os.makedirs("downloaded_pdfs", exist_ok=True)

results = []


def timed_input(prompt: str, timeout: float) -> bool:
    """Display the prompt then wait until ENTER key is pressed (`\\r` or `\\n`) (only works on windows).
    Returns: True if ENTER key is pressed before `timeout` seconds, False otherwise."""
    print(prompt, end="", flush=True)
    start_time = time.time()

    while True:
        if msvcrt.kbhit():  # Check if a key is pressed
            char = msvcrt.getch()  # Read a character without echoing
            if char in (b'\r', b'\n'):  # Enter key
                print()  # Move to next line
                return True
        if time.time() - start_time > timeout:
            print()  # Move to next line
            return False
        time.sleep(0.01)  # Small sleep to avoid CPU overuse


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

            time.sleep(wait_time_seconds*(1 + .1*random.random()))

            # can just get the case citation by
            if False:
                case_name_citation = soup.find(
                    'h1', class_='main-title solexHlZone mt-0')
                if case_name_citation:
                    case_name_citation = case_name_citation.text.strip()
            # can just get the date by
            if False:
                date_row = soup.find('div', string='Date:')
                if date_row:
                    date_value = date_row.find_next_sibling(
                        'div', class_='col')
                    if date_value:
                        case_date = date_value.text.strip()

            # find pdf link
            pdf_element = soup.find('a', id='pdf-link')
            if not pdf_element or not pdf_element.get('href'):
                results[-1]["status"] = "No PDF link found"
                print(f"No PDF link found for row={index} {case_id=} {url=}")
                break
            pdf_link = pdf_element['href']

            # Handle relative URLs
            if not pdf_link.startswith('http'):
                pdf_link = urljoin(url, pdf_link)

            results[-1]["pdf_url"] = pdf_link

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

            time.sleep(wait_time_seconds*(1 + .1*random.random()))

            break
        except requests.RequestException as e:
            results[-1]["status"] = f"Failed: {str(e)}"
            print(f"Failed to process row={index} {case_id=} {url}: {e}")
            input(
                "you probably need to go on the website and do a captcha, press ENTER to continue")
            # wait_time_seconds *= 2
            print(f"{wait_time_seconds=}")
            # if timed_input(
            #     "you probably need to go on the website and do a captcha, press ENTER to continue", wait_time_seconds
            # ):
            #     print("Continuing after user input...")
            # else:
            #     print("No input received within {} seconds, proceeding...".format(
            #         wait_time_seconds))
            #     wait_time_seconds *= 2
            #     time.sleep(wait_time_seconds)
        except Exception as e:
            results[-1]["status"] = f"Error: {str(e)}"
            print(f"Error processing row={index} {case_id=} {url}: {e}")

# Create a DataFrame from results
results_df = pd.DataFrame(
    results, columns=["Caseid", "original_url", "pdf_url", "file_path", "status"])

# Save the results to a new CSV
results_df.to_csv("download_results.csv", index=False)
print("Processing complete. Results saved to 'download_results.csv'")
