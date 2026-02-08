# Qpurpuse_API

Learning API project for Qpurpose — a Python REST API providing application endpoints.  
This project includes Python setup, Docker support, and example tests.


## About

Qpurpuse_API is a learning project that exposes REST API endpoints in Python.  
The API can be used to perform tasks such as data retrieval, creation, and other application logic you define.  

---

## Requirements

- Python **3.8+**
- pip

---

## Setup — Python Environment

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env

**Clone the repo**
   ```bash
   git clone https://github.com/WinchoCode/Qpurpuse_API.git
   cd Qpurpuse_API

** Run it **
python run.py

** test it **
python run_tests.py