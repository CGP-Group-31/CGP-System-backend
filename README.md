# CGP

# TrustCare Backend System

FastAPI backend for an elderly care mobile application  
Built with **FastAPI**, **MSSQL**, **SQLAlchemy Core**, and **Firebase Cloud Messaging**


<table>
  <tr>
    <td>
      <img src="1.png" alt="Image 1" width="250"/>
    </td>
    <td>
      <img src="2.png" alt="Image 2" width="250"/>
    </td>
  </tr>
</table>

---

# Tech Stack

- Python 3.14
- FastAPI
- MSSQL (SQLAlchemy Core)
- APScheduler
- Firebase Cloud Messaging (FCM)
- Windows + VS Code

---
#Download the SQL Server ODBC Driver 17  (https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver17)


Windows:   https://go.microsoft.com/fwlink/?linkid=2266337

##  Clone the Repository
in that location
## open the windows terminal

python -m venv venv

.\venv\Scripts\activate

You should see:

(venv)

Install Dependencies
pip install --upgrade pip

pip install -r requirements.txt

## TO RUN the app
.\venv\Scripts\activate

 uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

## open with SWAGGER
http://127.0.0.1:8000/docs