from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from google.cloud import storage
import os
from dotenv import load_dotenv
import json

# Library and dependency for Machine Learning
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from tensorflow.keras.utils import img_to_array
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

label_array = ['Collage', 'Food', 'Friends', 'Memes', 'Pets', 'Selfie']

class HubLayer(tf.keras.layers.Layer):
    def __init__(self, handle, **kwargs):
        self.handle = handle
        super(HubLayer, self).__init__(**kwargs)

    def build(self, input_shape):
        self.hub_layer = hub.KerasLayer(self.handle, trainable=False)
        super(HubLayer, self).build(input_shape)

    def call(self, inputs, **kwargs):
        return self.hub_layer(inputs)

    def get_config(self):
        config = super(HubLayer, self).get_config()
        config.update({"handle": self.handle})
        return config

# Replace 'path/to/your/model.h5' with the actual path to your HDF5 model file
model_path = 'model_artifacts/modeltype1.h5'

# Define a custom object scope to tell TensorFlow about the custom layer
custom_objects = {'HubLayer': HubLayer}

# Load the model using the custom object scope
with tf.keras.utils.custom_object_scope(custom_objects):
    model = tf.keras.models.load_model(model_path)

def prepare_data_for_prediction(img_content):
    img_array = img_to_array(img_content)
    img_array = tf.image.resize(img_array, (128, 128))
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(np.copy(img_array))
    return img_array

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
    picture_extensions = ['jpg', 'jpeg', 'png', 'gif']
    document_extensions = ['pdf', 'doc', 'docx', 'txt']
    video_extensions = ['mp4', 'avi', 'mkv']

    if file_extension.lower() in music_extensions:
        return 'music'
    elif file_extension.lower() in picture_extensions:
        return 'picture'
    elif file_extension.lower() in document_extensions:
        return 'document'
    elif file_extension.lower() in video_extensions:
        return 'video'
    else:
        return 'others'

def upload_file_to_gcs(file: UploadFile, category: str, label: str = None):
    # if category == 'unknown':
    #     return JSONResponse(content={"error": "Unknown file type"}, status_code=400)

    # Upload file to GCS bucket with the determined category as prefix
    if label is not None:
        blob_name = f"{category}/{label}/{file.filename}"
        return {"message": f"File uploaded successfully to {category} category and {label} label"}
    else:
        blob_name = f"{category}/{file.filename}"
    
        blob = client.bucket(bucket_name).blob(blob_name)
        blob.upload_from_file(file.file)
        return {"message": f"File uploaded successfully to {category} category"}

@app.post("/files")
async def upload(files: list[UploadFile] = File(...)):
    messages = []
    for file in files:
        file_extension = file.filename.split('.')[-1]
        category = get_category(file_extension)
        label = None
        if category == 'picture':
            file_content = await file.read()
            img_content = tf.image.decode_image(file_content, channels=3)
            prepare_image = prepare_data_for_prediction(img_content)
            prediction = model.predict(prepare_image)
            label = str(label_array[np.argmax(prediction)])

        messages.append(upload_file_to_gcs(file, category, label))

    return messages
