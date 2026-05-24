from pathlib import Path
from contextlib import asynccontextmanager

import sys
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, RedirectResponse

from app.api.routes import router
from app.api.auth_routes import router as auth_router
from app.db.storage import init_db


sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("🚀 NoteFlow AI запускается...")
    await init_db()
    logging.info("✅ PostgreSQL подключен")
    logging.info("✅ NoteFlow AI готов к работе")
    yield
    logging.info("🛑 Сервер остановлен")


app = FastAPI(
    title="NoteFlow AI",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
app.include_router(auth_router, prefix="/api")

frontend_path = Path("frontend")



@app.get("/")
async def serve_frontend():
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return JSONResponse({"status": "ok", "message": "Frontend not found"})



@app.get("/login", response_class=HTMLResponse)
async def login_page():
    login_file = frontend_path / "login.html"
    if login_file.exists():
        return HTMLResponse(login_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>login.html not found</h1>", status_code=404)



@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(token: str = ""):
    reset_file = frontend_path / "reset-password.html"
    if reset_file.exists():
        html = reset_file.read_text(encoding="utf-8")
       
        html = html.replace("__RESET_TOKEN__", token)
        return HTMLResponse(html)
    #
    return HTMLResponse(f"""
    <!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">
    <title>Сброс пароля</title>
    <style>body{{font-family:sans-serif;background:#010528;color:#E8F4FF;display:flex;align-items:center;justify-content:center;min-height:100vh}}
    .card{{background:rgba(0,32,96,.4);border:1px solid rgba(0,153,255,.2);border-radius:20px;padding:40px;max-width:380px;width:100%}}
    input{{width:100%;padding:10px 14px;border-radius:10px;background:rgba(0,32,96,.3);border:1px solid rgba(0,153,255,.2);color:#E8F4FF;font-size:14px;margin:8px 0 16px;outline:none}}
    button{{width:100%;padding:12px;border-radius:10px;background:linear-gradient(135deg,#0057A8,#003580);border:none;color:#fff;font-size:14px;font-weight:600;cursor:pointer}}
    .msg{{font-size:13px;margin-top:14px;padding:10px;border-radius:8px}}</style>
    </head><body><div class="card">
    <h2 style="margin:0 0 20px">🔑 Новый пароль</h2>
    <label style="font-size:12px;color:#7EB3D8">Новый пароль</label>
    <input type="password" id="pw" placeholder="Минимум 8 символов + цифра">
    <button onclick="doReset()">Сохранить пароль</button>
    <div class="msg" id="msg"></div>
    </div>
    <script>
    const token = "{token}";
    async function doReset() {{
        const pw = document.getElementById('pw').value;
        const msg = document.getElementById('msg');
        const res = await fetch('/api/auth/reset', {{
            method:'POST', headers:{{'Content-Type':'application/json'}},
            body: JSON.stringify({{token, new_password: pw}})
        }});
        const data = await res.json();
        msg.style.background = res.ok ? 'rgba(16,185,129,.15)' : 'rgba(239,68,68,.15)';
        msg.style.color = res.ok ? '#6EE7B7' : '#FCA5A5';
        msg.textContent = data.message || data.detail;
        if (res.ok) setTimeout(() => window.location.href = '/login', 2000);
    }}
    </script></body></html>
    """)