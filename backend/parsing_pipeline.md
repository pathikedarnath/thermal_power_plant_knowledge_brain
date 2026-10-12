1. Setup & Environment
Python
import os
import requests
import time
import zipfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
os & Path: Navigate through local folders and files regardless of the operating system.

requests: Sends HTTP calls (POST, PUT, GET) to the MinerU web servers.

time: Pauses execution between status checks while waiting for the server to finish parsing.

zipfile: Unpacks the .zip archive returned by MinerU.

load_dotenv(): Reads your hidden .env file and loads variables like MINERU_API into Python's environment.

2. Class Initialization
Python
class MineruParser :
    API_TOKEN = os.getenv('MINERU_API')

    def __init__(self, file_path) :
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.batch_id = None
        self.upload_url = None
        self.zip_url = None
        
        self.headers = {"Authorization": f"Bearer {self.API_TOKEN}"}
        self.payload =  {
            "enable_formula": True,
            "language": "en",
            "enable_table": True,
            "files": [
                {
                    "name": self.filename,
                    "data_id": self.filename
                }
            ]
        }
API_TOKEN: Grabs your MinerU authorization key from the .env file.

__init__: Sets up tracking variables for a single PDF.

headers: Attaches your secret API token to prove your account has access.

payload: Sends configuration settings to MinerU: enables OCR for mathematical formulas (enable_formula), targets English text (language), enables table extraction (enable_table), and declares the filename.

3. Step 1: Getting an Upload Slot
Python
def get_upload_url(self) :
    try :
        response = requests.post(url="https://mineru.net/api/v4/file-urls/batch", headers=self.headers, json=self.payload)
        response.raise_for_status()
        result = response.json()

        self.batch_id = result["data"]["batch_id"]
        self.upload_url = result["data"]["file_urls"][0]
        ...
Sends the payload to MinerU to request a processing job.

MinerU assigns a tracking ID (batch_id) and returns a temporary secure link (upload_url) where your PDF must be uploaded.

4. Step 2: Uploading the PDF
Python
def upload_pdf(self) :
    ...
    with open(self.file_path, 'rb') as f:
        upload_response = requests.put(self.upload_url, data=f)
        upload_response.raise_for_status()
Opens the local PDF in binary read mode ('rb').

Sends the raw file data directly to the temporary URL using an HTTP PUT request.

5. Step 3: Polling for Completion
Python
def get_zip_url(self) :
    while True :
        response = requests.get(url=f"https://mineru.net/api/v4/extract-results/batch/{self.batch_id}", headers=self.headers)
        response.raise_for_status()

        data = response.json()
        extract_result = data["data"]["extract_result"][0]

        if extract_result["state"] == "done":
            self.zip_url = extract_result["full_zip_url"]
            break
        elif extract_result["state"] == "failed":
            raise Exception(extract_result.get("err_msg", "Unknown parsing error"))
        else :
            time.sleep(5)
Queries the MinerU server every 5 seconds using self.batch_id.

Loops continuously until the status shifts from processing to "done".

Once complete, captures self.zip_url, which is the download link for the extracted archive.

6. Step 4: Downloading the Result
Python
def download_zip(self) :
    response = requests.get(self.zip_url)
    response.raise_for_status()
    name = self.filename.rsplit('.', 1)[0] + '.zip'
    
    os.makedirs(os.path.join(os.getcwd(), 'zip_files'), exist_ok=True)

    with open(os.path.join(os.getcwd(), 'zip_files', name), 'wb') as f:
        f.write(response.content)
Downloads the completed ZIP file from self.zip_url.

Creates a local folder named zip_files if it does not already exist.

Saves the file locally as <filename>.zip in binary write mode ('wb').

7. Step 5: Unzipping Output Files
Python
def extract_zip(self) :
    name = self.filename.rsplit('.', 1)[0]
    ZIP_PATH = os.path.join(os.getcwd(), 'zip_files', name + '.zip')
    OUTPUT_PATH = os.path.join(os.getcwd(), 'parsed_files', name)

    os.makedirs(os.path.join(os.getcwd(), 'parsed_files'), exist_ok=True)

    with zipfile.ZipFile(ZIP_PATH, 'r') as zp:
        zp.extractall(OUTPUT_PATH)
Creates a directory inside parsed_files dedicated to this specific document.

Unzips the contents, leaving you with:

full.md: The raw extracted text and Markdown tables.

Extracted image files (diagrams, graphs, and P&ID snippets).

8. Orchestrator: start()
Python
def start(self) :
    name = self.filename.rsplit('.', 1)[0]
    OUTPUT_PATH = os.path.join(os.getcwd(), 'parsed_files', name)
    ZIP_PATH = os.path.join(os.getcwd(), 'zip_files', name + '.zip')

    if not os.path.exists(OUTPUT_PATH) :
        if not os.path.exists(ZIP_PATH):
            self.get_upload_url()
            self.upload_pdf()
            self.get_zip_url()
            self.download_zip()
        self.extract_zip()
Checks if the document was already parsed. If parsed_files/<name> exists, it skips everything.

Checks if the ZIP was already downloaded. If so, it skips API requests and jumps straight to extraction.

9. Recursive Folder Scanner & Batch Execution
Python
if __name__ == '__main__' :
    DATA_PATH = os.path.join(os.getcwd(), 'datasets')
    all_file_paths = []

    def get_paths(root) :
        for content in os.listdir(root) :
            temp = os.path.join(root, content)
            if Path.is_file(temp) :
                all_file_paths.append(temp)
            else :
                get_paths(temp)

    get_paths(DATA_PATH)

    for file_path in all_file_paths :
        MineruParser(file_path).start()
get_paths(DATA_PATH): Recursively scans your entire datasets folder and every subfolder inside it (like equipment/), collecting the paths of all files.

Iterates through the list, instantiating MineruParser on each file and executing the pipeline.