# law-dataset-exploring

these are data sets listed here: https://queensuca-my.sharepoint.com/:x:/r/personal/xz27_queensu_ca/Documents/1_Research/Student_Weekly_Report/Hendrix/Legal%20Research%20Agent%20Datasets.xlsx?d=w67fe80b151bb4516b75e5e65bb7955d6&csf=1&web=1&e=00TT6C

## refugee-law-lab/canadian-legal-data from hugging face
https://huggingface.co/datasets/refugee-law-lab/canadian-legal-data?library=datasets

## judilibre judicial court (court de cassation)

## judlibre administrative court (court d'Etat)

## Courtlistener
to get stuff from courtlistener
```py
import os
import json
import hashlib
import psycopg2
from tqdm.auto import tqdm

# PostgreSQL Connection Details
DB_NAME = "courtlistener"
DB_USER = "pstgresresearch"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"

# Processing Constants
NAMESPACE = "courtlistener_search_opinions"
BATCH_SIZE = 100  # Fetch this many rows at a time
CHECKPOINT_FILE = "checkpoint.json"

texts = []
metadatas = []

# Hash function to generate unique IDs
def generate_unique_id(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# Load checkpoint to resume from last processed row
def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f)
    return {"offset": 0, "chunk_index": 0}

def save_checkpoint(offset, chunk_index):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"offset": offset, "chunk_index": chunk_index}, f)

# Initialize checkpoint
checkpoint = load_checkpoint()
offset = checkpoint["offset"]
chunk_start = checkpoint["chunk_index"]

try:
    # Persistent database connection
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()

    while True:
        cursor.execute(f"""
            SELECT id, plain_text, date_created, date_modified, type, download_url, local_path, author_id, author_str, cluster_id 
            FROM search_opinion 
            WHERE plain_text IS NOT NULL AND plain_text <> '' 
            ORDER BY id 
            LIMIT {BATCH_SIZE} OFFSET {offset};
        """)
        rows = cursor.fetchall()
```

i think you need to download the data from http://courtlistener.com/help/api/bulk-data/ to your local system and then you can scrape the valid rows with this code



## CANLii legal cases in canada
https://www.canlii.org/

## Hudoc ECHR

use https://pypi.org/project/echr-extractor/ to access

https://www.echr.coe.int/hudoc-database

reading this court case: https://hudoc.echr.coe.int/eng#{%22documentcollectionid2%22:[%22GRANDCHAMBER%22,%22CHAMBER%22],%22itemid%22:[%22001-243087%22]}
The INTRODUCTION section contains a mention of an applicable law to the case, but otherwise the FACTS section contains only the general case info, then the RELEVANT LEGAL FRAMEWORK AND PRACTICE section details the laws applied to this scenario covering "relevant domestic law", "relevant administrative practice", and "relevant domestic case-law".
- I would need to have available the source body of Italy domestic law for the automated research function to be able to identify the relevant laws


## CanLII employment law cases with structured data

link to csv file: https://queensuca-my.sharepoint.com/:x:/g/personal/14cfl_queensu_ca/EUQlEhUQZ7tJpgRo3_za-YoBriz--6u6SVQtQYY6Y5AsMQ?e=gmWwWT

csv file stored here: [employment_cases.csv](./employment_cases/employment_cases.csv).

table column headers:
- Caseid
- Name
- Case name and (case citation)
- URL
    - either a url in the format `http://canlii.ca/t/<uid>` where `<uid>` is replaced with some unique id, or
    - `NOT FOUND` in the case there is no URL for this case pdf
- Year
- Court
- Province
- Judge name
- Occupation
- Type of Job
- Industry
- Length of service
- Supervision/review of work
- Ability to hire employees
- Delegation of tasks
- Ownership of tools
- Chance of profit
- Risk of loss
- Exclusivity of services
- Who sets the work hours
- Where the work is performed
- Is the worker required to wear a uniform?
- Outcome
- Notes
- Audited\/Initials 
- Court_type
- Court_loc
- leaf_id
- court_full

more details on the table column header values can be found in [employment_column_value_meanings.xlsx](./employment_cases/employment_column_value_meanings.xlsx)

Need to download all the cases as pdfs with file names being `<Caseid>.pdf`.

Based on the view of the website:

![CanLII](./CanLII%20case%20html%20inspection%20for%20pdf-link.png)

When you navigate to the URL, you can access the pdf from the `<a id="pdf-link" href="..."></a>` html element.

