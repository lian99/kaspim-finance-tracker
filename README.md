# 💸 Kaspim — Personal Finance Tracker

A full-stack personal finance tracker with login, expense tracking, categories, and charts.

## Stack
- **Backend**: Python + FastAPI + SQLite
- **Auth**: JWT (protected routes)
- **Frontend**: React + Chart.js (single HTML file, no build step)

## Run it (2 steps)

### Step 1 — Install Python dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2 — Start everything
```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
python3 -m http.server 3000
```

Then open **http://localhost:3000**

Or just run:
```bash
chmod +x start.sh && ./start.sh
```

## API Endpoints

### Auth (public)
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/auth/signup` | Create account |
| POST | `/auth/login` | Login → get JWT token |
| GET | `/auth/me` | Get current user |

### Spendings (🔒 protected — requires Bearer token)
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/spendings` | List spendings (filter by `?month=YYYY-MM&category=food`) |
| POST | `/spendings` | Add spending |
| PUT | `/spendings/{id}` | Update spending |
| DELETE | `/spendings/{id}` | Delete spending |
| GET | `/stats` | Category totals + monthly trend |

### Example API call
```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -d "username=you@email.com&password=yourpass"

# Add spending (with token)
curl -X POST http://localhost:8000/spendings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description":"Coffee","amount":18,"category":"food","date":"2026-03-24"}'
```

## Features
- ✅ Signup / Login with JWT auth
- ✅ Protected API routes
- ✅ Add / delete spendings
- ✅ 9 categories (food, transport, travel, etc.)
- ✅ Pie chart — spending by category
- ✅ Bar chart — monthly trend (last 6 months)
- ✅ Filter by month and category
- ✅ Stat cards (total, top category, avg/day)
- ✅ Data persists in SQLite

## What I'd add next
- [ ] Edit spending inline
- [ ] Budget limits per category with alerts
- [ ] CSV export
- [ ] Recurring expense detection
- [ ] AI-powered monthly insight

---
Built for Wix KickstartX '26 application.
"# kaspim-finance-tracker" 
"# kaspim-finance-tracker" 
"# kaspim-finance-tracker" 
