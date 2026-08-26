My exercise progress tracker app layout.

## Create python venv and install requirements

1. Go to backend folder
```bash
cd backend
```

2. install python virtual environment
```bash
python -m venv .venv
```

or

```bash
python3 -m venv .venv
```

3. Activate venv
# Windows:
```bash
.\.venv\Scripts\Activate.ps1
```

# Linux/Mac
```bash
source .venv/bin/activate
```

4. Install requirements
```bash
pip install -r requirements.txt
```

## Starting app locally

1. Run command:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```


