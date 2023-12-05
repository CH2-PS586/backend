from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from google.cloud import storage
import os
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Fetch sensitive information from environment variables
# key_json_content = os.getenv('KEY_CONFIG')
bucket_name = os.getenv('BUCKET_NAME')

# Convert the environment variable containing JSON to a Python dictionary
#key_info = json.loads(key_json_content)

# Use the fetched values
client = storage.Client.from_service_account_json("./key.json")

def get_category(file_extension: str):
    music_extensions = ['mp3', 'wav', 'ogg']
    image_extensions = ['jpg', 'jpeg', 'png', 'gif']
    document_extensions = ['pdf', 'doc', 'docx', 'txt']
    video_extensions = ['mp4', 'avi', 'mkv']

    if file_extension.lower() in music_extensions:
        return 'music'
    elif file_extension.lower() in image_extensions:
        return 'image'
    elif file_extension.lower() in document_extensions:
        return 'document'
    elif file_extension.lower() in video_extensions:
        return 'video'
    else:
        return 'unknown'

def upload_file_to_gcs(file: UploadFile):
    file_extension = file.filename.split('.')[-1]
    category = get_category(file_extension)

    if category == 'unknown':
        return JSONResponse(content={"error": "Unknown file type"}, status_code=400)

    # Upload file to GCS bucket with the determined category as prefix
    blob_name = f"{category}/{file.filename}"
    blob = client.bucket(bucket_name).blob(blob_name)
    blob.upload_from_file(file.file)

    return {"message": f"File uploaded successfully to {category} category"}

@app.post("/files")
async def upload(files: list[UploadFile] = File(...)):
    messages = []
    for file in files:
        messages.append(upload_file_to_gcs(file))
        
    return messages