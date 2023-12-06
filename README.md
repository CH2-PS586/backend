# FastAPI App Setup and Replication

This guide provides step-by-step instructions for setting up and running a FastAPI app using **virtualenv** for local development and possible deployment.

## Prerequisites

- Python installed on your system
- virtualenv installed (you can install it using **pip install virtualenv**)

## Setup

Clone the Repository:

```bash
git clone https://github.com/CH2-PS586/backend.git
cd backend
```

## Environment Variable

1. Create Google Cloud Storage Bucket

2. Create **.env**

```env
BUCKET_NAME=""
```

3. Create service account on Google Cloud Platform (GCP) with **Storage Object Admin** role and store its key on **./key.json**

## Create a Virtual Environment:

On linux:

```bash
python3 -m virtualenv venv
```

on Windows:

```powershell
virtualenv venv
```

# Activate the Virtual Environment:

On Windows:

```powershell
.\venv\Scripts\activate
```


On Linux:

```bash
source venv/bin/activate
```


## Install Dependencies:

```bash
pip install -r requirements.txt
```

## Running the FastAPI App

Run the FastAPI App:

```bash
uvicorn main:app --reload
```

## Access the FastAPI App:

Open a web browser and navigate to http://127.0.0.1:8000 (or the address specified in your FastAPI app).

## Deactivate the Virtual Environment

Deactivate the Virtual Environment:

```bash
deactivate
```