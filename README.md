# CGP-Elder-backend

# Elder Care Backend API

FastAPI backend for an elderly care mobile application  
Built with **FastAPI**, **MSSQL**, **SQLAlchemy Core**, and **Firebase Cloud Messaging**

---

## Tech Stack

- Python 3.14
- FastAPI
- MSSQL (SQLAlchemy Core)
- APScheduler
- Firebase Cloud Messaging (FCM)
- Windows + VS Code

---

###  Clone the Repository
in that location
# open the windows terminal

python -m venv venv
.\venv\Scripts\activate

You should see:

(venv)

Install Dependencies
pip install --upgrade pip
pip install -r requirements.txt

# TO RUN the app
.\venv\Scripts\activate

 uvicorn app.main:app --reload
# open with SWAGGER
http://127.0.0.1:8000/docs