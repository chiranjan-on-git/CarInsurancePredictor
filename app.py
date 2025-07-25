from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io
import re
from datetime import datetime
from thefuzz import fuzz # <-- Import the new library

# Tell pytesseract where to find the Tesseract executable (Crucial for Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)

# --- Configuration & Loading ---
MODEL_FILE = 'car_insurance_claim_model.joblib'
DATABASE_FILE = 'database.csv'
EXPECTED_FEATURES = [
    'AGE', 'GENDER', 'DRIVING_EXPERIENCE', 'EDUCATION', 'INCOME',
    'VEHICLE_OWNERSHIP', 'VEHICLE_YEAR', 'MARRIED', 'CHILDREN',
    'DUIS', 'SPEEDING_VIOLATIONS', 'PAST_ACCIDENTS'
]

try:
    model_package = joblib.load(MODEL_FILE)
    model = model_package['model']
    preprocessor = model_package['preprocessor']
    print("Model and preprocessor loaded successfully.")
except Exception as e:
    print(f"Could not load model: {e}")
    model, preprocessor = None, None

try:
    db = pd.read_csv(DATABASE_FILE)
    db['DL_NO'] = db['DL_NO'].astype(str)
    print("User database loaded successfully.")
except Exception as e:
    print(f"Could not load database.csv: {e}")
    db = None

# --- Helper Functions (No changes here) ---
def calculate_age(dob_string):
    try:
        dob = datetime.strptime(dob_string, "%d-%m-%Y")
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if 16 <= age <= 25: return "16-25"
        if 26 <= age <= 39: return "26-39"
        if 40 <= age <= 64: return "40-64"
        if age >= 65: return "65+"
        return None
    except ValueError: return None

def calculate_experience(doi_string):
    try:
        doi = datetime.strptime(doi_string, "%d-%m-%Y")
        today = datetime.today()
        experience = today.year - doi.year - ((today.month, today.day) < (doi.month, doi.day))
        if 0 <= experience <= 9: return "0-9y"
        if 10 <= experience <= 19: return "10-19y"
        if 20 <= experience <= 29: return "20-29y"
        if experience >= 30: return "30+ y"
        return None
    except ValueError: return None

# --- Routes (No changes to home() or predict()) ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not model or not preprocessor:
        return jsonify({'error': 'Model not loaded or is invalid. Check server logs.'}), 500
    try:
        form_data = request.form.to_dict()
        input_df = pd.DataFrame([form_data], columns=EXPECTED_FEATURES)
        numerical_features = ['VEHICLE_OWNERSHIP', 'MARRIED', 'CHILDREN', 'DUIS', 'SPEEDING_VIOLATIONS', 'PAST_ACCIDENTS']
        for col in numerical_features:
            input_df[col] = pd.to_numeric(input_df[col])
        input_processed = preprocessor.transform(input_df)
        prediction_proba = model.predict_proba(input_processed)[0]
        claim_probability = prediction_proba[1]
        prediction_outcome = "Claim Likely" if claim_probability > 0.5 else "Claim Unlikely"
        return jsonify({'probability': f"{claim_probability:.2%}", 'outcome': prediction_outcome})
    except Exception as e:
        return jsonify({'error': f'An error occurred during prediction: {e}'}), 400

@app.route('/scan-license', methods=['POST'])
def scan_license():
    if 'license_image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    file = request.files['license_image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    try:
        image = Image.open(io.BytesIO(file.read()))
        image = image.convert('L').filter(ImageFilter.SHARPEN)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2)

        extracted_text = pytesseract.image_to_string(image, config=r'--oem 3 --psm 6')
        print("--- Extracted OCR Text ---\n", extracted_text, "\n--------------------------")

        # --- DATABASE LOOKUP WITH FUZZY MATCHING (THE NEW LOGIC) ---
        # First, try to find a candidate string for the DL number.
        # This regex is flexible: looks for MH followed by 10 to 15 numbers.
        cleaned_text = re.sub(r'[\s\W]', '', extracted_text.upper().replace('O', '0'))
        dl_match = re.search(r'(MH[0-9]{10,15})', cleaned_text)
        
        if dl_match and db is not None:
            ocr_dl_candidate = dl_match.group(1)
            print(f"Found OCR Candidate for DL Number: '{ocr_dl_candidate}'")

            best_score = 0
            best_match_row = None

            # Iterate through the database and find the best match
            for index, row in db.iterrows():
                db_dl = row['DL_NO']
                score = fuzz.ratio(ocr_dl_candidate, db_dl)
                if score > best_score:
                    best_score = score
                    best_match_row = row
            
            # If the best match is good enough (e.g., > 90% similar), use it!
            print(f"Best fuzzy match score was {best_score}% for DL No. '{best_match_row['DL_NO']}'")
            if best_score > 90:
                print("SUCCESS: Confident match found in database. Returning full data.")
                record_dict = best_match_row.to_dict()
                # Clean up data types for JSON
                for key, value in record_dict.items():
                    if pd.api.types.is_numeric_dtype(value):
                        record_dict[key] = int(value)
                return jsonify({'status': 'db_success', 'parsed_data': record_dict})

        # --- FALLBACK TO NEW USER OCR ---
        print(f"Match score of {best_score} was not high enough. Falling back to live OCR.")
        parsed_data = {}
        date_pattern = r'(\d{2}[-/]\d{2}[-/]\d{4})'
        text_for_dates = extracted_text.replace("O", "0") # Only replace O for dates
        
        dob_match = re.search(r'(?:DOB|D0B)\s*[:;]?\s*' + date_pattern, text_for_dates)
        if dob_match:
            age_category = calculate_age(dob_match.group(1).replace("/", "-"))
            if age_category: parsed_data['AGE'] = age_category
        
        doi_match = re.search(r'(?:DOI|D0I)\s*[:;]?\s*' + date_pattern, text_for_dates)
        if doi_match:
            exp_category = calculate_experience(doi_match.group(1).replace("/", "-"))
            if exp_category: parsed_data['DRIVING_EXPERIENCE'] = exp_category

        if not parsed_data:
            return jsonify({'status': 'ocr_fail', 'error': 'Could not extract a valid DOB or DOI from the image.'}), 400
        return jsonify({'status': 'ocr_success', 'parsed_data': parsed_data})

    except Exception as e:
        print(f"Error during OCR processing: {e}")
        return jsonify({'status': 'error', 'error': 'Failed to process image.'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)