# main.py - Clean version with your trained model
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import json
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import os

app = FastAPI(title="Dog Breed Predictor - Real Model")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and breeds
model = None
breeds = None
IMG_SIZE = 224

def load_breeds():
    """Load the breeds from JSON file"""
    try:
        with open('breeds.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("breeds.json not found, using fallback breeds")
        return -1

def create_model():
    """Create the same model architecture as your Colab training code"""
    INPUT_SHAPE = [None, IMG_SIZE, IMG_SIZE, 3]
    OUTPUT_SHAPE = len(breeds)
    MODEL_URL = "https://kaggle.com/models/google/mobilenet-v2/TensorFlow2/100-224-feature-vector/1"
    
    print("Building model with:", MODEL_URL)
    
    # EXACT same architecture as your Colab code
    model = tf.keras.Sequential([
        tf.keras.layers.InputLayer(input_shape=INPUT_SHAPE[1:]),
        tf.keras.layers.Lambda(lambda x: hub.KerasLayer(MODEL_URL)(x)),
        tf.keras.layers.Dense(units=OUTPUT_SHAPE, activation="softmax")
    ])
    
    model.compile(
        loss=tf.keras.losses.CategoricalCrossentropy(),
        optimizer=tf.keras.optimizers.Adam(),
        metrics=["accuracy"]
    )
    
    return model

def load_trained_model(weights_path):
    """Load your trained model weights"""
    try:
        print(f"Loading model weights from: {weights_path}")
        model = create_model()
        model.load_weights(weights_path)
        print("Model weights loaded successfully!")
        return model
    except Exception as e:
        print(f"Error loading model weights: {e}")
        return None

def preprocess_image(image: Image.Image):
    """Preprocess image exactly like your Colab training pipeline"""
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Resize to 224x224 (same as training)
    image = image.resize((IMG_SIZE, IMG_SIZE))
    
    # Convert to array and normalize to 0-1 (same as training)
    img_array = np.array(image, dtype=np.float32) / 255.0
    
    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array

def get_pred_label(prediction_probabilities):
    """Get predicted label from probabilities"""
    return breeds[np.argmax(prediction_probabilities)]

def get_top_predictions(prediction_probabilities, top_k=3):
    """Get top K predictions with confidence scores"""
    top_indices = np.argsort(prediction_probabilities[0])[-top_k:][::-1]
    
    predictions = []
    for idx in top_indices:
        predictions.append({
            "breed": breeds[idx].replace("_", " ").title(),
            "confidence": float(prediction_probabilities[0][idx])
        })
    
    return predictions

@app.on_event("startup")
async def startup_event():
    global model, breeds
    
    print("Starting up Dog Breed Predictor...")
    
    breeds = load_breeds()
    print(f"Loaded {len(breeds)} dog breeds")
    
    # Try to load your trained model weights - your exact filename first
    weights_paths = [
        "20250619-08341750322059-full-dataset-dog-mobilenetv2-cj.weights.h5",
    ]
    
    model_loaded = False
    for weights_path in weights_paths:
        if os.path.exists(weights_path):
            model = load_trained_model(weights_path)
            if model is not None:
                model_loaded = True
                print(f"Successfully loaded TRAINED model from: {weights_path}")
                break
        else:
            print(f"❌ Model not found at: {weights_path}")
    
    if not model_loaded:
        print("No trained model found. Creating fresh model...")
        print("Available model files in current directory:")
        for file in os.listdir("."):
            if file.endswith((".h5", ".weights.h5")):
                print(f"  - {file}")
        model = create_model()
        print("WARNING: Using untrained model - predictions will be random!")

@app.get("/")
def read_root():
    return {
        "message": "Dog Breed Predictor API with Real ML Model!",
        "status": "healthy",
        "model_loaded": model is not None,
        "total_breeds": len(breeds) if breeds else 0,
        "version": "2.0.0"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "dog-breed-predictor",
        "model_status": "loaded" if model is not None else "not_loaded",
        "gpu_available": len(tf.config.list_physical_devices('GPU')) > 0,
        "tensorflow_version": tf.__version__
    }

@app.get("/model/info")
def model_info():
    """Get information about the loaded model"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        return {
            "model_loaded": True,
            "input_shape": str(model.input_shape),
            "output_shape": str(model.output_shape),
            "total_parameters": model.count_params(),
            "total_breeds": len(breeds),
            "image_size": IMG_SIZE,
            "sample_breeds": [breed.replace("_", " ").title() for breed in breeds[:10]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")

@app.get("/breeds")
def get_breeds():
    """Get all supported dog breeds"""
    return {
        "total_breeds": len(breeds),
        "breeds": [breed.replace("_", " ").title() for breed in breeds]
    }

@app.post("/predict")
async def predict_breed(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, 
            detail="File must be an image (jpg, png, etc.)"
        )
    
    try:
        # Read and process image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        width, height = image.size
        format_type = image.format
        
        # Preprocess image for model (SAME as Colab)
        processed_image = preprocess_image(image)
        
        # Make prediction
        print("Making prediction...")
        predictions = model.predict(processed_image, verbose=0)
        
        # Get prediction results
        top_breed = get_pred_label(predictions)
        confidence = float(np.max(predictions[0]))
        top_3 = get_top_predictions(predictions, top_k=3)
        
        return {
            "success": True,
            "filename": file.filename,
            "image_info": {
                "width": width,
                "height": height,
                "format": format_type,
                "size_kb": round(len(image_data) / 1024, 2)
            },
            "prediction": {
                "breed": top_breed.replace("_", " ").title(),
                "confidence": confidence,
                "confidence_percentage": round(confidence * 100, 1)
            },
            "top_3_predictions": top_3,
            "model_info": {
                "model_type": "MobileNetV2 + Custom Dense Layer",
                "total_breeds": len(breeds),
                "image_size_used": IMG_SIZE,
                "model_trained": confidence > 0.1  # Indicator if model seems trained
            }
        }
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing image: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)