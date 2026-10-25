# RapForge

Локален AI рап генератор — фронтенд + Python backend за ACE-Step.

## Бърз старт

### 1. Инсталирай ACE-Step 1.5
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/ACE-Step/ACE-Step-1.5.git
cd ACE-Step-1.5
uv sync
uv run acestep-api   # стартира на порт 8001
```

### 2. Стартирай RapForge backend
```bash
cd rapforge
pip install -r requirements.txt
python server.py
```

### 3. Отвори фронтенда
Отвори `index.html` в браузър или служи със `python -m http.server`.

Бутонът праща към `http://localhost:8000/api/generate`.
