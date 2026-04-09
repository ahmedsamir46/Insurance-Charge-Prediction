#!/usr/bin/env python
# coding: utf-8

# ai\Scripts\activate
# python insurance.py

import os
import pandas as pd
import numpy as np
import joblib

from flask import render_template, url_for, flash, redirect, request, jsonify
from flask import Flask

# ─────────────────────────────────────────────────────────────────
# 1. Load dataset (handle missing file gracefully if model exists)
# ─────────────────────────────────────────────────────────────────
DATA_PATH = 'insurance.csv'
data = pd.DataFrame()
data2 = pd.DataFrame()

if os.path.exists(DATA_PATH):
    data = pd.read_csv(DATA_PATH)
    # Numeric-only view for statistics (std, etc.)
    data2 = data.drop(data.select_dtypes(include='object'), axis=1)
    columns = list(data.columns)
else:
    # If missing, we assume the model is already trained
    # or the app will fail gracefully on specific routes
    columns = [
        "age", "sex", "bmi", "children", "smoker", "region", "charges"
    ]

columns_desc = [
    "Age of primary beneficiary",
    "Insurance contractor gender (female / male)",
    ("Body mass index — objective index of body weight (kg/m²). "
     "Ideal range: 18.5 to 24.9"),
    "Number of children covered by health insurance / Number of dependents",
    "Smoking status (yes / no)",
    "The beneficiary's residential area in the US (northeast, southeast, southwest, northwest)",
    "Individual medical costs billed by health insurance (target)"
]

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

MODEL_PATH = 'insurance_model.joblib'

global_score = "87.05%" # Baseline R² score for Random Forest on this dataset

IS_VERCEL = "VERCEL" in os.environ

if os.path.exists(MODEL_PATH):
    model1 = joblib.load(MODEL_PATH)
elif os.path.exists(DATA_PATH):
    # Train only if dataset is present and model is missing
    categorical_features = ['sex', 'smoker', 'region']
    dummies = pd.get_dummies(data, columns=categorical_features)
    x = dummies.drop('charges', axis=1)
    y = dummies['charges']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    
    model1 = RandomForestRegressor(n_estimators=100, random_state=42)
    model1.fit(x_train, y_train)
    
    # DO NOT dump model to disk on Vercel (read-only filesystem)
    if not IS_VERCEL:
        joblib.dump(model1, MODEL_PATH)
    
    # Update score if we just trained
    global_score = f'{model1.score(x_test, y_test) * 100:.2f}%'
else:
    # Critical failure: no model and no data
    raise FileNotFoundError("ERROR: Neither 'insurance_model.joblib' nor 'insurance.csv' was found.")

# ──────────────────────────────────────────────
# 5. Flask application
# ──────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'insurance-secret-key')


@app.route("/")
def Home():
    return render_template('home.html', message='hello from home page', custom='home')


@app.route('/charge', methods=['GET', 'POST'])
def Charges():
    if not data.empty:
        sex_unique    = list(data['sex'].unique())
        region_unique = list(data['region'].unique())
        smoker_unique = list(data['smoker'].unique())
    else:
        # Fallback values if dataset is missing at runtime
        sex_unique    = ['female', 'male']
        region_unique = ['northeast', 'northwest', 'southeast', 'southwest']
        smoker_unique = ['yes', 'no']

    return render_template(
        'charge.html',
        sex_unique=sex_unique,
        region_unique=region_unique,
        smoker_unique=smoker_unique,
        custom="charge"
    )


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    # ── Input collection ──────────────────────
    age     = request.form.get('age', '').strip()
    bmi     = request.form.get('bmi', '').strip()
    sex     = request.form.get('gens', '').strip()
    children = request.form.get('ch', '').strip()
    smoker  = request.form.get('smoker', '').strip()
    region1 = request.form.get('regions', '').strip()

    # ── Input validation ──────────────────────
    errors = []

    # age
    try:
        age_val = float(age)
        if not (0 < age_val <= 120):
            errors.append("Age must be between 1 and 120.")
    except ValueError:
        errors.append("Age must be a valid number.")

    # bmi
    try:
        bmi_val = float(bmi)
        if not (0 < bmi_val <= 100):
            errors.append("BMI must be between 1 and 100.")
    except ValueError:
        errors.append("BMI must be a valid number.")

    # children
    try:
        children_val = int(children)
        if not (0 <= children_val <= 20):
            errors.append("Number of children must be between 0 and 20.")
    except ValueError:
        errors.append("Children must be a valid whole number.")

    # categorical fields
    valid_sexes   = list(data['sex'].unique())
    valid_smokers = list(data['smoker'].unique())
    valid_regions = list(data['region'].unique())

    if sex not in valid_sexes:
        errors.append(f"Sex must be one of: {', '.join(valid_sexes)}.")
    if smoker not in valid_smokers:
        errors.append(f"Smoker must be one of: {', '.join(valid_smokers)}.")
    if region1 not in valid_regions:
        errors.append(f"Region must be one of: {', '.join(valid_regions)}.")

    if errors:
        for err in errors:
            flash(err, 'danger')
        return redirect(url_for('Charges'))

    # ── Encoding ──────────────────────────────
    sex_male   = 1 if sex == 'male'  else 0
    sex_female = 1 if sex == 'female' else 0

    smoker_yes = 1 if smoker == 'yes' else 0
    smoker_no  = 1 if smoker == 'no'  else 0

    region_northeast = 1 if region1 == 'northeast' else 0
    region_northwest = 1 if region1 == 'northwest' else 0
    region_southeast = 1 if region1 == 'southeast' else 0
    region_southwest = 1 if region1 == 'southwest' else 0

    # ── Build feature DataFrame ───────────────
    x_T = pd.DataFrame({
        'age':              [age_val],
        'bmi':              [bmi_val],
        'children':         [children_val],
        'sex_female':       [sex_female],
        'sex_male':         [sex_male],
        'smoker_no':        [smoker_no],
        'smoker_yes':       [smoker_yes],
        'region_northeast': [region_northeast],
        'region_northwest': [region_northwest],
        'region_southeast': [region_southeast],
        'region_southwest': [region_southwest],
    })

    # ── Predict ───────────────────────────────
    y_predict = model1.predict(x_T)
    charge = round(float(y_predict[0]), 2)

    return render_template(
        'predict.html',
        charge=charge,
        custom='predict',
        age=age, bmi=bmi, region1=region1, smoker=smoker, sex=sex
    )


@app.route("/visualization")
def Visualization():
    return render_template(
        'visualization.html',
        message='hello from data visualization',
        custom='visualization'
    )


@app.route("/About")
def About():
    if not data.empty:
        shape   = data.shape
        std     = data2.std()
        max_val = data.max(numeric_only=True)
        min_val = data.min(numeric_only=True)
        nunique = data.nunique()
    else:
        # Fallback stats if CSV is missing
        shape   = (1338, 7)
        std     = {}
        max_val = {}
        min_val = {}
        nunique = {c: "—" for c in columns}

    return render_template(
        'about.html',
        custom="about",
        packed=zip(columns, columns_desc),
        columns=columns,
        columns_desc=columns_desc,
        score=global_score,
        shape=shape,
        std=std,
        max=max_val,
        min=min_val,
        nunique=nunique
    )


if __name__ == '__main__':
    port  = int(os.environ.get('PORT', 9000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', debug=debug, port=port)
