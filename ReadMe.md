# CovenantGuard+

## Project Description

CovenantGuard+ is a full-stack covenant risk assessment platform designed for financial compliance monitoring.  
It evaluates covenant performance, detects risk breaches, and produces regulatory-grade reports.

This repository contains the **complete source code** for both frontend and backend.

---

## Technology Stack

### Frontend
- React (Vite)
- Recharts
- Axios
- Electron (Desktop Packaging)

### Backend
- FastAPI
- SQLAlchemy
- SQLite
- ReportLab (PDF Generation)
- OpenPyXL (Excel Export)

---

## Repository Structure

# CovenantGuard+

## Project Description

CovenantGuard+ is a full-stack covenant risk assessment platform designed for financial compliance monitoring.  
It evaluates covenant performance, detects risk breaches, and produces regulatory-grade reports.

This repository contains the **complete source code** for both frontend and backend.

---

## Technology Stack

### Frontend
- React (Vite)
- Recharts
- Axios
- Electron (Desktop Packaging)

### Backend
- FastAPI
- SQLAlchemy
- SQLite
- ReportLab (PDF Generation)
- OpenPyXL (Excel Export)

---

## Repository Structure

# CovenantGuard+

## Project Description

CovenantGuard+ is a full-stack covenant risk assessment platform designed for financial compliance monitoring.  
It evaluates covenant performance, detects risk breaches, and produces regulatory-grade reports.

This repository contains the **complete source code** for both frontend and backend.

---

## Technology Stack

### Frontend
- React (Vite)
- Recharts
- Axios
- Electron (Desktop Packaging)

### Backend
- FastAPI
- SQLAlchemy
- SQLite
- ReportLab (PDF Generation)
- OpenPyXL (Excel Export)

---

## Repository Structure
COVENANTGUARD/
|
+-- backend/
|   |-- app/
|   |   |-- api.py
|   |   |-- security.py
|   |   |-- database.py
|   |   |-- db_models.py
|   |   +-- reports.py
|   |-- main.py
|   +-- requirements.txt
|
+-- frontend/
|   |-- src/
|   |   |-- pages/
|   |   |-- components/
|   |   |-- auth/
|   |   +-- api/
|   |-- main.js
|   +-- package.json
|
+-- README.md

================================================================================

[ BACKEND SETUP ]

1. Create Virtual Environment
   $ python -m venv venv
   $ venv\Scripts\activate

2. Install Dependencies
   $ pip install -r requirements.txt

3. Run Backend Server
   $ python main.py

   * API Base URL: http://127.0.0.1:8000
   * Swagger UI:   http://127.0.0.1:8000/docs

--------------------------------------------------------------------------------

[ FRONTEND SETUP ]

1. Install Dependencies
   $ npm install

2. Start Development Server
   $ npm run dev

--------------------------------------------------------------------------------

[ DESKTOP BUILD (ELECTRON) ]

1. Build Frontend
   $ npm run build

2. Create Desktop Package
   $ npm run dist
   (Installer output will be available in: frontend/dist/)

================================================================================

[ AUTHENTICATION & ROLES ]

Default Roles:
 - admin
 - analyst
 - viewer

Sample User Creation Payload (JSON):
{
  "username": "admin",
  "password": "admin123",
  "role": "admin"
}

================================================================================

[ KEY FEATURES ]

 * Risk Dashboard: Interactive dashboard with KPI cards.
 * Visualization: Risk Distribution and Risk Trend charts.
 * Admin Panel: Dedicated KPI panel for administrators.
 * Dynamic UI: Role-Based UI rendering.
 * Security: Secure Authentication system.
 * Reporting: PDF & Excel Report Export.
 * Deployment: Electron Desktop Packaging.

================================================================================

[ DEVELOPMENT NOTES ]

 * All charts are dynamically driven by evaluation data.
 * Risk normalization is handled via centralized utility mapping.
 * Backend is packaged into a standalone executable for desktop use.

================================================================================

[ SECURITY CONSIDERATIONS ]

 * Credentials: Change default credentials before deployment.
 * Documentation: Disable Swagger (/docs) in production builds.
 * Encryption: Use hashed passwords (bcrypt).

================================================================================

[ LICENSE ]

This project is proprietary software.
Unauthorized distribution or commercial use is prohibited.

================================================================================

[ MAINTAINER ]

CovenantGuard+
Risk & Compliance Software

Contact Information:
 * Name:  Kanishk Yadav
 * Email: kanishkyadav.7007@gmail.com
================================================================================

