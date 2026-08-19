# htDash Setup Guide — Installation & Environment

Complete guide to setting up htDash (main application) and the Training Simulator.

---

## Prerequisites

- **Python:** 3.13 or higher
- **Node.js:** 18+ (for Puppeteer PDF generation)
- **Git:** For version control
- **Operating System:** Windows, macOS, or Linux

---

## Quick Start (Recommended)

### Option 1: Using UV (Fast, Recommended)

**Why UV?** Faster dependency resolution, deterministic installs, integrated virtual environment management.

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
# or on Windows:
powershell -ExecutionPolicy BypassUser -Command "irm https://astral.sh/uv/install.ps1 | iex"

# Clone the repository
git clone https://github.com/your-org/htDash.git
cd htDash

# Sync dependencies (creates .venv automatically)
uv sync

# Activate virtual environment
source .venv/bin/activate
# or on Windows:
.venv\Scripts\activate

# Install Node.js dependencies (for Puppeteer)
npm install

# Run the main Flask app
python main.py

# OR run the training simulator
python -m training_simulator
```

---

### Option 2: Using pip (Traditional)

```bash
# Clone the repository
git clone https://github.com/your-org/htDash.git
cd htDash

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate
# or on Windows:
venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for Puppeteer)
npm install

# Run the main Flask app
python main.py

# OR run the training simulator
python -m training_simulator
```

---

## What Gets Installed

### Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| **Flask** | ≥3.1.3 | Web framework (main app) |
| **bcrypt** | ≥5.0.0 | Secure password hashing |
| **boto3** | ≥1.43.46 | AWS S3 file storage |
| **pandas** | ≥3.0.3 | Data analysis & manipulation |
| **pytz** | ≥2026.2 | Timezone support (IST) |
| **reportlab** | ≥5.0.0 | PDF generation |
| **qrcode** | ≥8.2 | QR code generation |
| **Pillow** | ≥10.0.0 | Image processing |

### Node.js Packages

| Package | Version | Purpose |
|---------|---------|---------|
| **Puppeteer** | Latest | Headless browser for server-side PDF rendering |

---

## Directory Structure After Setup

```
htDash/
├── .venv/                           # Virtual environment (auto-created)
├── node_modules/                    # Node.js packages (auto-created)
├── data/                            # Patient data & credentials
│   ├── ranipet/patients/
│   ├── manipal/patients/
│   ├── ludhiana/patients/
│   └── credentials.json (gitignored)
├── training_simulator/              # Training simulator package
│   ├── ui/
│   ├── curriculum/
│   ├── __main__.py
│   └── ...
├── templates/                       # Flask HTML templates
├── static/                          # CSS, JS, assets
├── routes/                          # Flask blueprints
├── utils/                           # Shared utilities
├── scripts/                         # Helper scripts
├── main.py                          # Flask app entry point
├── config.py                        # Configuration
├── requirements.txt                 # Python dependencies (NEW)
├── SETUP_GUIDE.md                   # This file (NEW)
└── pyproject.toml                   # Project metadata
```

---

## Running the Application

### Main Flask App (Production)

```bash
python main.py
```

Accessible at: `http://localhost:5000`

**Test credentials:**
- Therapist (Ranipet): `RP-HS-1002` / `password`
- Admin (Ranipet): `RP-HS-ADMIN` / `password`
- Supervisor: `LAB-HS-DATA` / `password`

### Training Simulator (Desktop GUI)

```bash
python -m training_simulator
```

Launches a Tkinter window where trainers can:
- Set up fake cohorts (1-10 patients)
- Advance through 187-day protocol
- Verify trainee filings in real-time
- Generate pass/fail reports

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"

**Solution:** Activate virtual environment and reinstall dependencies.

```bash
source venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### "Puppeteer not found" (when saving PDFs)

**Solution:** Install Node.js dependencies.

```bash
npm install
```

Ensure Node.js ≥18 is installed:
```bash
node --version
npm --version
```

### "No such file or directory: data/ranipet/patients/..."

**Solution:** Initialize test data.

```bash
python scripts/reset_test_patient.py 23/03 24/03 22/03 21/03
```

### Port 5000 already in use

**Solution:** Change the port in `config.py` or use a different port:

```bash
FLASK_ENV=development FLASK_APP=main.py python -m flask run --port 5001
```

### Virtual environment won't activate

**Windows (PowerShell):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

---

## Environment Variables (Optional)

Create a `.env` file in the root directory:

```bash
# Flask
FLASK_ENV=development
FLASK_DEBUG=True

# AWS S3 (if using cloud storage)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=your_bucket_name

# Database (if future migration from JSON)
DATABASE_URL=postgresql://user:password@localhost/htdash

# Timezone
TZ=Asia/Kolkata
```

Then load in `config.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Development Setup

### Optional Dev Dependencies

For code quality and testing:

```bash
# Install dev tools
pip install black flake8 mypy pytest pytest-cov

# Format code
black .

# Lint
flake8 .

# Type check
mypy routes/

# Run tests
pytest tests/
```

---

## Docker Setup (Optional)

For production deployment:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Node.js for Puppeteer
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install puppeteer

# Copy application
COPY . .

# Run
CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t htdash .
docker run -p 5000:5000 htdash
```

---

## Updating Dependencies

To update to latest versions (breaking changes possible):

```bash
# With UV
uv sync --upgrade

# With pip
pip install --upgrade -r requirements.txt
```

---

## Next Steps

1. **Complete Setup:** Follow "Quick Start" above
2. **Initialize Test Data:** `python scripts/reset_test_patient.py ...`
3. **Start Main App:** `python main.py`
4. **Try Training Simulator:** `python -m training_simulator`
5. **Read CLAUDE.md:** Project documentation and architecture

---

## Support

- **Issues:** Check `TROUBLESHOOTING.md` in repo
- **Architecture:** See `CLAUDE.md`
- **Training:** See `training_simulator/COVERAGE_MATRIX.md`
- **API Docs:** See `docs/pages.md`

---

**Version:** August 2026  
**Last Updated:** 2026-08-07  
**Python:** 3.13+  
**Node.js:** 18+
