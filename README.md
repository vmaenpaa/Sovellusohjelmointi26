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
3. Run 
```bash
docker compose exec api alembic upgrade head

# Seed system units and activity types
docker compose exec api python -m app.db.init_db
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

#After that run also
alembic upgrade head
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

## .env variables

**SQLADMIN**

SQLAdmin is available at `http://localhost:8000/admin`. Configure its separate login (NOT JWT!) in the root `.env` file:

```env
SQLADMIN_SECRET_KEY=replace-with-a-long-random-secret
SQLADMIN_USERNAME=admin
SQLADMIN_PASSWORD=change-this-password
```
**CORS**

Remember to add your frontend to `.env`:

```env
CORS origin=
```

**JWT/SECRET**

Make sure to also add JWT token and expire time to `.env`: 

```env
JWT_SECRET=
ACCESS_TOKEN_EXPIRE_MINUTES=
```

<br>

## URLS

**API URLs:**
| URL          | Explanation    |
| -------------|---------       |
| /docs        | documents      |
| /health      | health check   |
| /auth/register | Register a user and return the public user plus a bearer access token |
| /admin | SQLAdmin page. After running ```alembic upgrade head``` you should see all the seeded unit/activity catalog ([As shown here](/docs/sprints/tickets/sprint-02-tickets.md)).|


**Frontend URLs:**
| URL          | Explanation    |
| -------------|---------       |
| /            | Landing page to test if api /health works      |

## Creating first user

1. Head over to ```/register```
2. Fill in username, email and password.
3. After creating user you are redirected to ```/login``` and you can use your information to login.


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

## Note to self

1. /register navigates to /login, does not auto-login.

## Links

[Docs README.md](docs/sprints/README.md).