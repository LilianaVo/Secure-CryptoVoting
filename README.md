<div align="center">

# 🗳️ Secure Electronic Voting System (CryptoVoting)

### A robust web platform implementing advanced cryptographic standards for secure digital elections.

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Security](https://img.shields.io/badge/Security-AES%20%7C%20RSA-red?style=for-the-badge&logo=security&logoColor=white)
![Deploy](https://img.shields.io/badge/Deploy-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

[View Live Demo] • [Report Bug] • [Request Feature]

</div>

---

## 🔗 Live Demo

* **Public Access:** [https://sistema-de-votacion-de-criptografia.onrender.com](https://sistema-de-votacion-de-criptografia.onrender.com)
    > ⚠️ **Deployment Note:** The server may take **30 to 50 seconds** to wake up and load the first time due to free tier energy-saving policies.

---

## Key Features

The system is built on a **Hybrid Cryptographic Scheme** that ensures the integrity and confidentiality of the voting process:

### 1. 🔑 Public Key Infrastructure (PKI)
* Each voter generates a **2048-bit RSA** key pair.
* The **Public Key** is stored on the server for signature validation.
* The **Private Key** is downloaded to the user's device (`.key` file) and is **strictly required to vote**.

### 2. 🛡️ Vote Security
* **Digital Signature:** A **SHA-256** hash of the vote is generated and signed with the user's **Private Key**, ensuring **Non-Repudiation** and **Integrity**.
* **Hybrid Encryption:** The vote payload is encrypted using **AES-256 CBC** before transmission, guaranteeing **Confidentiality**.

### 3. 📈 Transparency & Auditing
* **Real-Time Results:** Live dashboard with graphical visualization of the election.
* **Audit Module:** Admin interface to inspect and validate digital signatures and hashes.
* **Key Validation:** Tool for voters to verify the status and validity of their key pairs.

---

## 🛠️ Tech Stack

| Component | Technology / Library | Version | Description |
| :--- | :--- | :--- | :--- |
| **Backend** | **Django** | 5.2.8 | Main web framework. |
| **Cryptography** | **PyCryptodome** | 3.23.0 | Implementation of **RSA, AES, and SHA256**. |
| **Config** | **Python-Decouple** | 3.8 | Environment variable management. |
| **Database** | **DJ-Database-URL** | 3.0.1 | Database agnostic connection (SQLite / PostgreSQL). |
| **Static Files** | **WhiteNoise** | 6.11.0 | Static file serving for production. |
| **WSGI Server** | **Gunicorn** | 23.0.0 | WSGI HTTP Server for UNIX. |

---

## 🚀 Local Installation & Execution Guide

Follow these exact steps to get the project running locally using **Visual Studio Code (VS Code)**.

### ⚙️ Prerequisites
Ensure you have the following installed:
1.  **Python 3.10+**: [Download Here](https://www.python.org/downloads/) (Check "Add Python to PATH").
2.  **VS Code**: [Download Here](https://code.visualstudio.com/).
3.  **Python Extension**: Install `Python (Microsoft)` from the VS Code Marketplace.
4.  **Git**: (Optional) [Download Here](https://git-scm.com/downloads).

### Execution Steps

1.  **Clone the Repository**
    ```bash
    git clone [YOUR_REPO_URL]
    cd sistema-de-votacion-electronica
    ```

2.  **Create & Activate Virtual Environment**
    > Django should be installed inside a virtual environment to isolate dependencies.
    ```bash
    # Create environment
    python -m venv venv

    # Activate environment
    # Windows:
    .\venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply Migrations**
    ```bash
    python manage.py migrate
    ```

5.  **Create Admin User**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run Local Server**
    ```bash
    python manage.py runserver
    ```
    * Open browser at: 👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## ☁️ Production Deployment (Render)

### **Build Command**
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
