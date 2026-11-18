# NetScope – Website Performance Monitoring System

NetScope is a web-based website performance monitoring and diagnostic system that collects website loading performance metrics through a Chrome extension and displays the results on a Django dashboard.

## Features

- Monitor website performance.
- Capture DNS lookup time.
- Capture TCP connection time.
- Capture TLS handshake time.
- Measure Time to First Byte (TTFB).
- Measure page load time.
- Automatically analyze performance metrics.
- Detect performance warnings using threshold-based diagnostics.
- View website performance history through charts.
- View detailed performance information for individual visits.

## Technologies Used

### Frontend

- HTML
- CSS
- JavaScript
- Bootstrap 5
- Chart.js

### Backend

- Python
- Django
- Django REST Framework
- SQLite

### Browser Extension

- Chrome Extension Manifest V3
- Chrome Scripting API
- Navigation Timing API

## Project Structure

```text
NetScope/
│
├── backend/
│   ├── config/
│   ├── core/
│   ├── templates/
│   ├── static/
│   ├── manage.py
│   └── requirements.txt
│
├── extension/
│   ├── manifest.json
│   ├── popup.html
│   └── popup.js
│
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd NetScope
```

### 2. Create a virtual environment

```bash
cd backend
python -m venv .venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure Django Secret Key

Set an environment variable in PowerShell:

```powershell
$env:DJANGO_SECRET_KEY="your-own-secret-key"
```

### 6. Apply migrations

```bash
python manage.py migrate
```

### 7. Start the Django server

```bash
python manage.py runserver
```

Open:

http://127.0.0.1:8000/

## Chrome Extension Setup

1. Open Google Chrome.
2. Navigate to `chrome://extensions/`.
3. Enable Developer mode.
4. Click Load unpacked.
5. Select the `extension` folder from the NetScope project.
6. Open a normal website using HTTP or HTTPS.
7. Click the NetScope extension.
8. Click Capture Performance.

The collected performance data will be sent to the Django backend.

## How It Works

1. The Chrome extension captures browser performance timing information.
2. The extension sends the collected metrics to the Django REST API.
3. Django stores the website visits and performance metrics in SQLite.
4. The diagnostic engine analyzes the metrics using predefined thresholds.
5. The dashboard displays performance statistics, charts and diagnostic results.

## Important Notes

- NetScope currently captures performance data when a user manually clicks Capture Performance.
- Diagnostic results are based on predefined thresholds.
- Browser timing measurements may vary depending on caching, network conditions and browser behavior.
- This project is intended for educational and demonstration purposes.

## Author

Developed as a computer science project.
