# Car Insurance Claim Prediction Web App

This project is an end-to-end machine learning web application that predicts the likelihood of a car insurance claim based on driver and vehicle details. It features an interactive web interface built with Flask and includes an advanced driver's license scanning feature to automate data entry.

<div style="display: flex; gap: 10px;">
  <img src="https://github.com/user-attachments/assets/87812b40-7560-47e5-8bcc-317d742dae93" width="600" />
  <img src="https://github.com/user-attachments/assets/a6346740-52e6-498f-87e7-9d0507ece78c" width="600" />
</div>

## Key Features

-   **Predictive Modeling**: Utilizes a Random Forest Classifier trained on driver data to predict claim probability (Claim Likely / Claim Unlikely).
-   **Interactive Web Interface**: A clean and user-friendly web form built with Flask, HTML, CSS, and JavaScript for manual data entry.
-   **Smart Driver's License Scanner**:
    -   **Database Lookup**: On uploading an Indian Driver's License image, the app uses OCR to extract the DL number and searches a local CSV "database" for a pre-existing record.
    -   **OCR with Fuzzy Logic**: If the driver is not in the database, the app falls back to using OCR and fuzzy logic to parse the **Date of Birth (DOB)** and **Date of Issue (DOI)** from the license, automatically calculating the driver's age and experience.
-   **Dynamic Frontend**: The frontend communicates with the Flask backend asynchronously using `fetch`, providing a smooth user experience without page reloads.

## Technology Stack

-   **Backend**: Python, Flask
-   **Machine Learning**: Scikit-learn, Pandas, imblearn, SHAP
-   **OCR Engine**: Google's Tesseract
-   **Frontend**: HTML, CSS, JavaScript

## Project Structure

```bash
# Simulating the 'tree' command output
CARINSURANCEMODEL-MAIN/
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── templates/
│   └── index.html
├── app.py                      # Main Flask application
├── model_creation.py           # Script to train and save the ML model
├── car_insurance_claim_model.joblib  # The saved model and preprocessor
├── database.csv                # A simple CSV file acting as a user database
├── requirements.txt            # Python dependencies
└── README.md
```

# Setup and Installation

Follow these steps to set up and run the project on your local machine.

## 1. Prerequisites

- **Python** (3.8 or newer)  
- **Git**  
- **Tesseract OCR Engine**: This must be installed on your system.

  - **Windows**: Download and install from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).  
    Important: Note the installation path.

  - **macOS**:  
    ```bash
    brew install tesseract
    ```

  - **Linux (Ubuntu/Debian)**:  
    ```bash
    sudo apt install tesseract-ocr
    ```

## 2. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

## 3. Create a Virtual Environment

It's highly recommended to use a virtual environment.

```bash
# Create the virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

## 4. Install Dependencies

Ensure your `requirements.txt` is up to date:

```bash
pip freeze > requirements.txt
```

Then install packages:

```bash
pip install -r requirements.txt
```

## 5. Configure Tesseract Path (for Windows users)

If you are on Windows, Tesseract might not be in your system's PATH. You need to explicitly tell `pytesseract` where to find it.

Open `app.py` and uncomment/edit the following line with your installation path:

```python
# In app.py
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## 6. Train the Machine Learning Model

Run the model creation script:

```bash
python model_creation.py
```

This generates the `car_insurance_claim_model.joblib` file.

## 7. Run the Flask Application

Start the server:

```bash
python app.py
```

Open your web browser and navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

# How to Use the Application

## 1. Using the License Scanner (Recommended)

- Click **"Choose File"** and select an image of an Indian Driver's License.
- Click **"Scan Image"**.
  - If the DL number is found in `database.csv`, the form will auto-fill.
  - If it's a new user, **"Age"** and **"Driving Experience"** fields will be filled.
- Fill in any remaining fields and click **"Predict"**.

## 2. Manual Entry

- Manually fill out all the fields in the form.
- Click **"Predict"**.
- The prediction result, including the probability of a claim, will be displayed.

---

# Future Improvements

- **Deploy to a Cloud Platform**: Containerize with Docker and deploy on Heroku, AWS, or Google Cloud.
- **Use a Real Database**: Replace `database.csv` with PostgreSQL or SQLite.
- **Improve OCR Accuracy**: Use preprocessing (resizing, grayscaling, thresholding) before OCR.
- **User Authentication**: Add login/signup system to manage user data.
- **Live Webcam Scanning**: Enable direct scanning of licenses using device cameras.
