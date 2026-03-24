import warnings
warnings.filterwarnings("ignore")

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import sqlite3

SECRET_KEY = "kaspim-secret-change-in-prod-2024"
ALGORITHM  = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24
DB_PATH = "kaspim.db"

CATEGORIES = ["food", "transport", "shopping", "subscriptions",
              "entertainment", "health", "education", "travel", "other"]

app = FastAPI(title="Kaspim API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_ctx = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            email    TEXT UNIQUE NOT NULL,
            name     TEXT NOT NULL,
            password TEXT NOT NULL,
            created  TEXT DEFAULT (datetime('now'))
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS spendings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            description TEXT NOT NULL,
            amount      REAL NOT NULL,
            category    TEXT NOT NULL,
            date        TEXT NOT NULL,
            created     TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class SpendingCreate(BaseModel):
    description: str
    amount: float
    category: str
    date: str

class SpendingUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    date: Optional[str] = None

def hash_password(pw):
    return pwd_ctx.hash(pw)

def verify_password(plain, hashed):
    return pwd_ctx.verify(plain, hashed)

def create_token(user_id, email):
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": str(user_id), "email": email, "exp": expire},
        SECRET_KEY, algorithm=ALGORITHM
    )

def get_current_user(token: str = Depends(oauth2_scheme), db: sqlite3.Connection = Depends(get_db)):
    exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except Exception:
        raise exc
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        raise exc
    return dict(user)

@app.post("/auth/signup", status_code=201)
def signup(body: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    if db.execute("SELECT id FROM users WHERE email = ?", (body.email,)).fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")
    cur = db.execute("INSERT INTO users (email, name, password) VALUES (?, ?, ?)",
                     (body.email, body.name, hash_password(body.password)))
    db.commit()
    return {"access_token": create_token(cur.lastrowid, body.email), "token_type": "bearer", "name": body.name}

@app.post("/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: sqlite3.Connection = Depends(get_db)):
    user = db.execute("SELECT * FROM users WHERE email = ?", (form.username,)).fetchone()
    if not user or not verify_password(form.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_token(user["id"], user["email"]), "token_type": "bearer", "name": user["name"]}

@app.get("/auth/me")
def me(current_user=Depends(get_current_user)):
    return {"id": current_user["id"], "name": current_user["name"], "email": current_user["email"]}

@app.get("/spendings")
def list_spendings(month: Optional[str] = None, category: Optional[str] = None,
                   current_user=Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    q = "SELECT * FROM spendings WHERE user_id = ?"
    p = [current_user["id"]]
    if month:    q += " AND date LIKE ?";    p.append("{}%".format(month))
    if category: q += " AND category = ?";  p.append(category)
    q += " ORDER BY date DESC, created DESC"
    return [dict(r) for r in db.execute(q, p).fetchall()]

@app.post("/spendings", status_code=201)
def add_spending(body: SpendingCreate, current_user=Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    if body.category not in CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    cur = db.execute("INSERT INTO spendings (user_id, description, amount, category, date) VALUES (?, ?, ?, ?, ?)",
                     (current_user["id"], body.description, body.amount, body.category, body.date))
    db.commit()
    return dict(db.execute("SELECT * FROM spendings WHERE id = ?", (cur.lastrowid,)).fetchone())

@app.put("/spendings/{spending_id}")
def update_spending(spending_id: int, body: SpendingUpdate, current_user=Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    row = db.execute("SELECT * FROM spendings WHERE id = ? AND user_id = ?", (spending_id, current_user["id"])).fetchone()
    if not row: raise HTTPException(status_code=404, detail="Spending not found")
    u = dict(row)
    if body.description is not None: u["description"] = body.description
    if body.amount is not None:      u["amount"]      = body.amount
    if body.category is not None:    u["category"]    = body.category
    if body.date is not None:        u["date"]        = body.date
    db.execute("UPDATE spendings SET description=?, amount=?, category=?, date=? WHERE id=?",
               (u["description"], u["amount"], u["category"], u["date"], spending_id))
    db.commit()
    return dict(db.execute("SELECT * FROM spendings WHERE id = ?", (spending_id,)).fetchone())

@app.delete("/spendings/{spending_id}", status_code=204)
def delete_spending(spending_id: int, current_user=Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    if not db.execute("SELECT id FROM spendings WHERE id = ? AND user_id = ?", (spending_id, current_user["id"])).fetchone():
        raise HTTPException(status_code=404, detail="Spending not found")
    db.execute("DELETE FROM spendings WHERE id = ?", (spending_id,))
    db.commit()

@app.get("/stats")
def stats(month: Optional[str] = None, current_user=Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    uid = current_user["id"]
    p = [uid]
    q = "SELECT category, SUM(amount) as total FROM spendings WHERE user_id = ?"
    if month: q += " AND date LIKE ?"; p.append("{}%".format(month))
    q += " GROUP BY category ORDER BY total DESC"
    by_cat = db.execute(q, p).fetchall()

    monthly = db.execute("""
        SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
        FROM spendings WHERE user_id = ?
        GROUP BY month ORDER BY month DESC LIMIT 6
    """, (uid,)).fetchall()

    tp = [uid]
    tq = "SELECT COALESCE(SUM(amount),0) as t FROM spendings WHERE user_id = ?"
    if month: tq += " AND date LIKE ?"; tp.append("{}%".format(month))
    total = db.execute(tq, tp).fetchone()["t"]

    return {"total": total, "by_category": [dict(r) for r in by_cat], "monthly": [dict(r) for r in reversed(list(monthly))]}
