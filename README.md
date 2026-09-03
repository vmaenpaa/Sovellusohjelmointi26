My exercise progress tracker app.

## Installing and running app

Before installing, make sure you have following installed: 

###

- Node.js
- Docker
- Git
- Python 

**With docker**
1. Copy .env.example to .env
2. Run 
```bash
docker compose up --build
```
<br>

**Or without docker**

1. Create python venv and install requirements
```bash
# Go to backend folder
cd backend

#install python virtual environment
python3 -m venv .venv
```

2. Activate venv

Windows:
```bash
.\.venv\Scripts\Activate.ps1
```

Linux/Mac:
```bash
source .venv/bin/activate
```

3. Install requirements
```bash
pip install -r requirements.txt
```

<br>

**Starting app locally**

1. Run command:

API:
```bash
#Go to backend folder
cd backend

#Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Web:
```bash
#Go to frontend folder
cd frontend

#Install dependencies
npm install

#Run backend
npm run dev
```

<br>

**Ports**:
- **Postgres**: 5432 
- **API**: 8000
- **Frontend**: 5173

<br>

## URLS

**API URLs:**
| URL          | Explanation    |
| -------------|---------       |
| /docs        | documents      |
| /health      |                |


**Frontend URLs:**
| URL          | Explanation    |
| -------------|---------       |
| /            | Landing page to test if api /health works      |



## Troubleshooting

**Port in use**

If port 5432, 8000, or 5173 is already in use, stop the application using it or change the corresponding port in the configuration before restarting Docker Compose.

**Postgres not ready**

Check the database status and logs:

```bash
docker compose ps
docker compose logs db
```

**Forgotten .env**

Make sure you have copied .env.example to .env in root folder and in /frontend.

## Links

[Docs README.md](docs/sprints/README.md).