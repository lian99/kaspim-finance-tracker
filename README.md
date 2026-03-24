# 💸 Kaspim — Personal Finance Tracker

## 📌 Overview

Kaspim is a full-stack personal finance tracker designed to help users manage daily expenses, analyze spending habits, and gain insights through interactive visualizations.

The system includes a secure backend with JWT authentication, a REST API for financial data management, and a responsive frontend with real-time updates and charts.

---

## 🏗️ Architecture

* **Backend (FastAPI)**
  Handles authentication, business logic, and data persistence

* **Database (SQLite)**
  Stores users and financial records

* **Frontend (React + Chart.js)**
  Displays data, charts, and handles user interaction

* **Authentication (JWT)**
  Secures API endpoints and user sessions

**Flow:**
Client → REST API → Database

---

## ✨ Features

* ✅ Signup / Login with JWT authentication
* ✅ Secure protected API routes
* ✅ Add, update, and delete expenses
* ✅ Filter expenses by month and category
* ✅ 9 expense categories (food, transport, travel, etc.)
* ✅ Interactive charts:

  * Pie chart (category distribution)
  * Bar chart (monthly trend)
* ✅ Summary statistics (total, top category, avg/day)
* ✅ Persistent data storage using SQLite

---

## 🧠 Tech Stack

* **Backend:** Python, FastAPI
* **Frontend:** React, Chart.js (lightweight setup without build tools)
* **Database:** SQLite
* **Authentication:** JWT

---

## 🚀 How to Run

### Step 1 — Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2 — Start the application

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
python3 -m http.server 3000
```

Open:
👉 http://localhost:3000

Or run everything with:

```bash
chmod +x start.sh && ./start.sh
```

---

## 🔌 API Overview

### Auth (public)

| Method | Route          | Description           |
| ------ | -------------- | --------------------- |
| POST   | `/auth/signup` | Create account        |
| POST   | `/auth/login`  | Login → get JWT token |
| GET    | `/auth/me`     | Get current user      |

### Spendings (🔒 protected)

| Method | Route             | Description                       |
| ------ | ----------------- | --------------------------------- |
| GET    | `/spendings`      | List spendings (filter supported) |
| POST   | `/spendings`      | Add spending                      |
| PUT    | `/spendings/{id}` | Update spending                   |
| DELETE | `/spendings/{id}` | Delete spending                   |
| GET    | `/stats`          | Category totals + monthly trend   |

### Example API call

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -d "username=you@email.com&password=yourpass"

# Add spending
curl -X POST http://localhost:8000/spendings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description":"Coffee","amount":18,"category":"food","date":"2026-03-24"}'
```

---

## 💡 Key Engineering Decisions

* Used **JWT authentication** for secure and stateless session management
* Designed a **modular REST API** for scalability and maintainability
* Separated frontend and backend for flexibility and clean architecture
* Used **Chart.js** for lightweight, responsive data visualization
* Chose **SQLite** for simplicity and fast local development


## 🚀 Future Improvements

* Budget tracking with alerts
* Recurring expense detection
* Export reports (CSV)
* AI-based spending insights

---



