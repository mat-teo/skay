# Skay Finance

Personal finance management application built with FastAPI and Vue.js.

## Features

- User authentication (JWT)
- Account management (create, edit, delete)
- Transaction tracking (income, expense, transfer)
- Category management
- Net worth chart with date filtering
- CSV export
- Apple-inspired UI design

## Tech Stack

**Backend:** FastAPI, SQLModel, JWT, SQLite/PostgreSQL

**Frontend:** Vue 3, Bootstrap 5, Chart.js, Vue Router

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

---

## API Endpoints

| Method | Endpoint | Description |
|----------|----------|-------------|
| POST | /api/auth/register | Create account |
| POST | /api/auth/login | Get JWT token |
| GET | /api/accounts | List accounts |
| POST | /api/accounts | Create account |
| PUT | /api/accounts/{id} | Update account |
| DELETE | /api/accounts/{id} | Delete account |
| GET | /api/transactions | List transactions |
| POST | /api/transactions | Create transaction |
| PUT | /api/transactions/{id} | Update transaction |
| DELETE | /api/transactions/{id} | Delete transaction |
| GET | /api/categories | List categories |
| POST | /api/categories | Create category |
| GET | /api/transactions/stats | Get financial stats |
| GET | /api/transactions/net-worth | Get net worth history |
| GET | /api/transactions/export | Export CSV |

---

## Environment Variables

### Backend (.env)

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./skay.db
```

### Frontend (.env.local)

```env
VITE_API_URL=http://localhost:8000/api
```

---

# Setup Guide

## Development Environment

### Backend Setup

#### 1. Clone Repository

```bash
git clone https://github.com/your-username/skay-finance.git
cd skay-finance/backend
```

#### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Create .env

```env
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=sqlite:///./skay.db
```

#### 5. Run Server

```bash
uvicorn main:app --reload
```

API available at:

```text
http://localhost:8000
```

### Frontend Setup

#### 1. Navigate to Frontend

```bash
cd ../frontend
```

#### 2. Install Dependencies

```bash
npm install
```

#### 3. Create .env.local

```env
VITE_API_URL=http://localhost:8000/api
```

#### 4. Run Development Server

```bash
npm run dev
```

Application available at:

```text
http://localhost:5173
```

---

## Production Build

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm run build
```

The `dist` folder contains static files ready to be served.

---

## Default Test Account

After starting the application for the first time, create a user:

### Request

```http
POST /api/auth/register
```

### Body

```json
{
  "email": "test@example.com",
  "password": "secret123",
  "base_currency": "EUR"
}
```

---

## Troubleshooting

### CORS Errors

Ensure `main.py` includes:

```python
allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]
```

### Database Errors

Delete:

```text
skay.db
```

and restart the backend.

### Invalid JWT Token

Verify Authorization header:

```http
Authorization: Bearer your-jwt-token-here
```

---

# Deployment Guide

## Option 1: Render

### Backend

1. Create account on Render
2. New → Web Service
3. Connect repository
4. Configure:

```text
Build Command:
pip install -r requirements.txt

Start Command:
uvicorn main:app --host 0.0.0.0 --port 10000
```

5. Add environment variables:

```env
SECRET_KEY=random-secret
DATABASE_URL=postgresql://...
```

### Frontend

1. New → Static Site
2. Connect repository
3. Configure:

```text
Publish Directory:
frontend/dist

Build Command:
cd frontend && npm install && npm run build
```

4. Environment Variables:

```env
VITE_API_URL=https://your-backend-url.onrender.com/api
```

---

## Option 2: Raspberry Pi

### Hardware

- Raspberry Pi 4 (4GB RAM or more)
- MicroSD 16GB+

### Installation

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx -y
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt install nodejs -y
```

### Clone & Build

```bash
git clone https://github.com/your-username/skay-finance.git

cd skay-finance/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd ../frontend
npm install
npm run build
```

### Nginx Configuration

Create:

```text
/etc/nginx/sites-available/skay
```

```nginx
server {
    listen 80;
    server_name your-domain.duckdns.org;

    location / {
        root /home/pi/skay-finance/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/skay /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Systemd Service

Create:

```text
/etc/systemd/system/skay.service
```

```ini
[Unit]
Description=Skay Finance Backend
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/skay-finance/backend
ExecStart=/home/pi/skay-finance/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Start Service:

```bash
sudo systemctl enable skay
sudo systemctl start skay
```

### DuckDNS

```bash
mkdir /etc/duckdns
nano /etc/duckdns/duck.sh
```

Content:

```bash
echo url="https://www.duckdns.org/update?domains=yourdomain&token=your-token&ip=" | curl -k -o /home/pi/duck.log -K -
```

Enable:

```bash
chmod +x /etc/duckdns/duck.sh
crontab -e
```

Add:

```cron
*/5 * * * * /etc/duckdns/duck.sh
```

---

## Option 3: DigitalOcean

1. Create Ubuntu 22.04 Droplet
2. SSH into server
3. Follow Raspberry Pi installation
4. Install SSL:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## Environment Variables Summary

| Variable | Purpose | Example |
|----------|----------|----------|
| SECRET_KEY | JWT signing key | random 32+ chars |
| DATABASE_URL | Database connection | postgresql://user:pass@localhost/db |
| VITE_API_URL | Frontend API endpoint | https://api.skay.com/api |

---

# Contributing

## Workflow

1. Fork repository
2. Create branch

```bash
git checkout -b feature/name
```

3. Make changes
4. Commit

```bash
git commit -m "feat: description"
```

5. Push

```bash
git push origin feature/name
```

6. Open Pull Request

---

## Commit Convention

| Prefix | Description |
|----------|-------------|
| feat | New feature |
| fix | Bug fix |
| docs | Documentation |
| style | Formatting |
| refactor | Refactoring |
| test | Tests |
| chore | Maintenance |

---

## Code Style

### Python Backend

- Follow PEP 8
- Use type hints
- Write docstrings

### Vue Frontend

- Composition API
- 2-space indentation
- Vue Style Guide

---

## Before Submitting a PR

- [ ] Code works locally
- [ ] No debug prints
- [ ] Tests pass
- [ ] Documentation updated

---

## License

MIT