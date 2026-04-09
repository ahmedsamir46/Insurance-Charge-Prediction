# 🏥 InsureAI — Medical Insurance Charge Predictor

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**InsureAI** is a premium machine-learning powered web application that estimates annual medical insurance charges based on individual health profiles. Built with a modern dark glassmorphism aesthetic, it combines robust data science with a high-end user experience.

---

## 🚀 Key Features

- **🎯 High-Accuracy Prediction**: Uses a Random Forest Regressor trained on 1,300+ medical records to provide reliable cost estimates.
- **✨ Premium UI/UX**: Modern dark-themed interface with glassmorphism, smooth animations, and responsive grid layouts.
- **🛡️ Multi-Layer Validation**: Robust client-side (JavaScript) and server-side (Flask) validation to ensure data integrity.
- **📈 Interactive Insights**: Comprehensive data visualization and statistical overview of the underlying dataset.
- **🐳 Dockerized**: Fully containerized and ready for production deployment with Gunicorn.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11, Flask
- **ML Engine**: Scikit-Learn, Pandas, NumPy, Joblib
- **Frontend**: HTML5, Vanilla CSS3 (Custom Design System), JavaScript (ES6+)
- **Visualization**: Plotly Express (rendered via static images)
- **Deployment**: Docker, Gunicorn

---

## 📦 Getting Started

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)

### Local Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/ahmedsamir46/Insurance-Charge-prediction.git
   cd insurance-project
   ```
2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application**:
   ```bash
   python app.py
   ```
   *The app will be available at `http://localhost:9000`.*

---

## 🐳 Docker Deployment

The application is prepared with a multi-stage `Dockerfile` and production-grade `Gunicorn` configuration.

1. **Build the image**:
   ```bash
   docker build -t insure-ai .
   ```
2. **Run the container**:
   ```bash
   docker run -d -p 8000:8000 --env SECRET_KEY=your_secure_key insure-ai
   ```
   *The app will be available at `http://localhost:8000`.*

---

## 📁 Project Structure

```text
├── app.py              # Main Flask application & ML logic
├── insurance.csv       # Training dataset
├── static/
│   ├── css/            # Modular stylesheets (Glassmorphism)
│   ├── js/             # Client-side validation
│   └── images/         # Charts and visual assets
├── templates/          # Jinja2 templates (Layout, Home, Predict, etc.)
├── Dockerfile          # Multi-stage production container
├── requirements.txt    # Pinned dependencies
└── Procfile            # PaaS deployment config
```

---

## ⚖️ License
Distributed under the MIT License. See `LICENSE` for more information.

---
*Developed with ❤️ for Data Science Excellence.*
