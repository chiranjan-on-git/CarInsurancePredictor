import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report, roc_auc_score
from imblearn.over_sampling import SMOTE
import joblib
import shap
import matplotlib.pyplot as plt

# --- 1. Sample Data ---
data = {
    'AGE': ['26-39', '16-25', '40-64', '26-39', '65+', '26-39', '40-64', '16-25'],
    'GENDER': ['female', 'male', 'male', 'female', 'male', 'female', 'male', 'male'],
    'DRIVING_EXPERIENCE': ['10-19y', '0-9y', '20-29y', '0-9y', '30+ y', '10-19y', '20-29y', '0-9y'],
    'EDUCATION': ['university', 'high school', 'university', 'none', 'high school', 'university', 'university', 'high school'],
    'INCOME': ['upper class', 'poverty', 'working class', 'middle class', 'upper class', 'middle class', 'upper class', 'working class'],
    'VEHICLE_OWNERSHIP': [1, 0, 1, 1, 0, 1, 1, 1],
    'VEHICLE_YEAR': ['after 2015', 'before 2015', 'after 2015', 'before 2015', 'before 2015', 'after 2015', 'after 2015', 'before 2015'],
    'MARRIED': [1, 0, 1, 0, 1, 1, 0, 0],
    'CHILDREN': [1, 1, 1, 0, 0, 1, 1, 0],
    'DUIS': [0, 1, 0, 0, 0, 0, 1, 0],
    'SPEEDING_VIOLATIONS': [0, 3, 1, 0, 5, 1, 0, 8],
    'PAST_ACCIDENTS': [0, 1, 0, 0, 2, 0, 1, 3],
    'OUTCOME': [0, 1, 0, 0, 1, 0, 1, 1]
}
df = pd.DataFrame(data)

# --- 2. Feature Setup ---
X = df.drop('OUTCOME', axis=1)
y = df['OUTCOME']

# Categorical order
age_order = ['16-25', '26-39', '40-64', '65+']
experience_order = ['0-9y', '10-19y', '20-29y', '30+ y']
vehicle_year_order = ['before 2015', 'after 2015']

# Define feature types
ordinal_features = ['AGE', 'DRIVING_EXPERIENCE', 'VEHICLE_YEAR']
ordinal_encoder = OrdinalEncoder(categories=[age_order, experience_order, vehicle_year_order])

categorical_features = ['GENDER', 'EDUCATION', 'INCOME']
numerical_features = ['VEHICLE_OWNERSHIP', 'MARRIED', 'CHILDREN', 'DUIS', 'SPEEDING_VIOLATIONS', 'PAST_ACCIDENTS']

# Preprocessor
preprocessor = ColumnTransformer(transformers=[
    ('ord', ordinal_encoder, ordinal_features),
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
    ('num', StandardScaler(), numerical_features)
])

# --- 3. Train/Test Split ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# --- 4. Preprocess + SMOTE ---
# Manually preprocess
X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)

# Apply SMOTE to numeric data
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train_processed, y_train)

# --- 5. Train Model with GridSearch ---
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5]
}

clf = RandomForestClassifier(class_weight='balanced', random_state=42)
grid_search = GridSearchCV(clf, param_grid, cv=3, scoring='roc_auc')
grid_search.fit(X_resampled, y_resampled)

best_model = grid_search.best_estimator_

# --- 6. Evaluation ---
y_pred = best_model.predict(X_test_processed)
y_prob = best_model.predict_proba(X_test_processed)[:, 1]

print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("ROC AUC Score:", roc_auc_score(y_test, y_prob))

# --- 7. Save Model + Preprocessor Together ---
model_package = {
    'model': best_model,
    'preprocessor': preprocessor
}
joblib.dump(model_package, 'car_insurance_claim_model.joblib')
print("Model & preprocessor saved as 'car_insurance_claim_model.joblib'")

# --- 8. Explain Model with SHAP ---
print("Generating SHAP values (may take a second)...")
explainer = shap.Explainer(best_model, X_resampled)
shap_values = explainer(X_test_processed)

# SHAP Summary Plot
shap.summary_plot(shap_values, X_test_processed)
