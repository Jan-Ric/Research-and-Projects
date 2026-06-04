import base64
import io
import os
import time
from flask import Flask, render_template, request, jsonify, Response
import cv2
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get Gemini API Key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the Gemini API for pest detection on static images
try:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing. Please set it in the environment or .env file.")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro-vision')
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    model = None


# --- RTMP Stream Configuration ---
camera_url = "rtmp://205.185.126.220/live/stream"
# Initialize VideoCapture object
cap = cv2.VideoCapture(camera_url)

def generate_frames():
    """Reads frames from the RTMP stream and yields them for browser streaming."""
    while True:
        # We need to re-check the capture object state in the loop for reconnection logic
        if not cap.isOpened():
            print("Stream is not open. Attempting to reconnect...")
            time.sleep(5)  # Wait 5 seconds before trying to reconnect
            # Re-initialize the VideoCapture object
            globals()['cap'] = cv2.VideoCapture(camera_url)
            continue  # Go to the next loop iteration

        success, frame = cap.read()
        if not success:
            print("Failed to read frame, stream might have ended or is temporarily down.")
            time.sleep(2)  # Wait a moment before trying to read again
            continue  # Skip this frame and try the next one
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue  # Skip frame if encoding fails
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


### ROUTING FOR HTML PAGES ###
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/livestream')
def livestream():
    return render_template('livestream.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/farms')
def farms():
    return render_template('farms.html')

@app.route('/about')
def about():
    return render_template('about.html')


### API AND FUNCTIONAL ENDPOINTS ###

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Serves frames from the RTMP source."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detect_pests', methods=['POST'])
def detect_pests_static():
    """Handles static image uploads for pest detection using Gemini."""
    if not model:
        return jsonify({'error': 'Gemini API not configured correctly.'}), 500

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            image = Image.open(file.stream)
            prompt = "Analyze this image of a cornfield. Detect all pests present. For each detected pest, provide its name and a bounding box with normalized coordinates [y_min, x_min, y_max, x_max]. Respond with only a valid JSON array of objects. Each object should have 'name' and 'box' keys. If no pests are found, return an empty array."
            response = model.generate_content([prompt, image])

            # Clean up the response to ensure it's valid JSON
            clean_response = response.text.replace("```json", "").replace("```", "").strip()
            return jsonify({'bounding_boxes': clean_response})
        except Exception as e:
            print(f"An error occurred during pest detection: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/get_recommendation', methods=['POST'])
def get_recommendation():
    """Generates a pest control recommendation using Gemini 1.5."""
    if not model:
        return jsonify({'error': 'Gemini API not configured correctly.'}), 500

    data = request.get_json()
    pest_density = data.get('pest_density')

    if not pest_density:
        return jsonify({'error': 'Pest density data is required.'}), 400

    # Formulate a detailed prompt for Gemini 1.5
    prompt = f"""
    You are an agricultural advisor for a corn farm in the Philippines.
    Based on the following data, provide a concise and actionable recommendation for pest control.

    Data:
    - Pest Density Population: {pest_density}

    Your recommendation should:
    1. Be formatted for a farm owner.
    2. Focus on Integrated Pest Management (IPM) strategies.
    3. Suggest specific, practical, and locally relevant steps.
    4. If density is low, recommend monitoring and preventive measures.
    5. If density is moderate to high, suggest appropriate interventions (e.g., biological controls like Trichogramma, specific safer pesticides as a last resort, or cultural practices like crop rotation/timing).
    """

    try:
        response = model.generate_content(prompt)
        return jsonify({'recommendation': response.text})
    except Exception as e:
        print(f"An error occurred while getting recommendation: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run()
