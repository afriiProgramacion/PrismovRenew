# 📚 PRISMOV V2 - Project Wiki

## Table of Contents
1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Features](#features)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Architecture](#architecture)
7. [API Reference](#api-reference)
8. [Configuration](#configuration)
9. [Development](#development)
10. [Troubleshooting](#troubleshooting)

---

## Overview

**PRISMOV** is a professional enterprise-grade system monitoring and analysis application designed for industrial control environments. It focuses on real-time performance tracking, process analysis, automated reporting, and integration with business systems.

### Key Objectives
- **Real-time Monitoring**: Track CPU, RAM, and process metrics in real-time
- **Data Lifecycle Management**: Automated data collection, storage, and archival (RA Criterion 5b)
- **Business Intelligence**: Convert technical metrics (THD - Total Harmonic Distortion) to business insights (RA Criterion 2e)
- **Automated Reporting**: Generate comprehensive HTML/PDF reports automatically (RA Criterion 2g)
- **Secure Communications**: Telegram bot integration for real-time alerts (RA Criterion 5i)
- **IT/OT Integration**: Bridge gap between IT systems and operational technology

---

## Project Structure

```
PRISMOV2/
├── prismov2.py              # Core system monitoring library
├── prismov_gui.py           # PyQt5 desktop GUI application
├── web_demo.py              # Streamlit web dashboard demo
├── config.json              # Application configuration file
├── perfil_base.json         # Base profile/user settings
├── historial.json           # Historical data storage
├── preguntas.md             # FAQ and documentation
├── README.md                # Project introduction
├── CONTRIBUTING.md          # Contribution guidelines
├── WIKI.md                  # This wiki documentation
├── LICENSE                  # MIT License
├── prismov_gui.spec         # PyInstaller spec for .exe generation
└── .git/                    # Version control
```

---

## Features

### 1. Real-Time Dashboard
- **Live Metrics**: CPU and RAM usage updated every 2 seconds
- **Visual Feedback**: Color-coded health status (Green/Yellow/Red)
- **Historical Trends**: Last 60-second consumption graph
- **Top Processes Table**: Displays the 5 most resource-intensive processes

### 2. Automated Analysis
- **Batch Processing**: Analyze all running processes
- **Comprehensive Metrics**: CPU%, RAM, PID, Process Name
- **History Tracking**: Store snapshots for trend analysis
- **Export Capabilities**: Generate PDF/HTML reports

### 3. Telegram Integration
- **Secure Bot Linking**: QR code or linking code generation
- **Remote Notifications**: Send alerts to Telegram
- **Report Distribution**: Automated report delivery to mobile devices
- **Command-Based Control**: Execute analyses remotely

### 4. Scheduling & Automation
- **Cron-like Scheduling**: Configure daily/weekly automated scans
- **Custom Intervals**: Set monitoring frequency (1-1440 minutes)
- **Time Windows**: Define start/end times for automation
- **Background Execution**: Run tasks without UI interaction

### 5. Professional UI
- **Modern Design**: Apple/macOS-inspired glassmorphism
- **Dark Mode Support**: Toggle between light and dark themes
- **Responsive Layout**: Sidebar navigation with tabbed content
- **Professional Typography**: Minimalist and clean interface

### 6. Data Management
- **Persistent Storage**: Local JSON-based storage in AppData
- **Configuration Management**: Save/load application settings
- **History Archival**: Long-term trend analysis
- **Data Export**: Export historical data for external analysis

---

## Installation

### System Requirements
- **Python**: 3.10 or higher
- **OS**: Windows 10/11 (primary), Linux/macOS (with adjustments)
- **RAM**: Minimum 2GB available
- **Disk Space**: 100MB for application and data

### Method 1: From Source

1. **Clone Repository**
   ```bash
   git clone https://github.com/your-username/PRISMOV.git
   cd PRISMOV2
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Linux/macOS
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Application**
   ```bash
   python prismov_gui.py
   ```

### Method 2: Pre-built Executable
- Download `prismov_gui.exe` from [Releases](https://github.com/your-username/PRISMOV/releases)
- Run the executable directly (no Python installation required)
- Data stored in `%LOCALAPPDATA%\PRISMOV\`

### Method 3: Web Demo (Streamlit)
```bash
streamlit run web_demo.py
```
Accessible at `http://localhost:8501`

---

## Usage

### Desktop Application (PyQt5)

#### Main Dashboard
1. **Launch** the application
2. **Monitor** real-time CPU and RAM metrics
3. **View** top processes consuming resources
4. **Access** historical data and trends

#### Execute Analysis
- Click **📊 Audit** button to scan all processes
- Results displayed in tabular format
- Metrics exported to JSON history file

#### Generate Reports
- Click **📄 Report** to create PDF/HTML report
- Report includes:
  - System metrics snapshot
  - Top processes analysis
  - Historical trends
  - Recommendations

#### Configure Telegram Bot
1. Click **⚙️ Telegram** in sidebar
2. Click **🔄 Re-Generate Code** to get linking code
3. Send code to `@PrisMovBot` on Telegram
4. Confirm linking in the application
5. Receive alerts and reports via Telegram

#### Schedule Automated Scans
1. Click **🕐 Configure Cron** in sidebar
2. Select days (Monday-Sunday)
3. Set start/end times
4. Configure scan interval
5. Click **Save Schedule**
6. Scans run automatically in background

#### Enable Automatic Mode
- Click **🚀 Automatic Mode** to activate background monitoring
- Application continues monitoring even when minimized
- Alerts sent automatically when thresholds exceeded

#### Toggle Theme
- Click **🌙 Dark Mode** checkbox to switch themes
- Preference persists across sessions

### Web Dashboard (Streamlit)

#### Real-Time Dashboard Tab
- View current CPU and RAM usage
- Click **🔄 Execute Real-Time Scan** to collect fresh metrics
- See top processes consuming resources
- View historical consumption trends

#### Historical Reports Tab
- View audit history from local database
- Line chart showing CPU/RAM trends over time
- Export data for analysis

#### Configuration Tab
- Set external API webhooks
- Configure Telegram bot token
- Manage integration endpoints

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────┐
│        User Interface Layer                 │
│  ┌──────────────┐  ┌──────────────────┐   │
│  │ PyQt5 GUI    │  │ Streamlit Web    │   │
│  │ (Desktop)    │  │ (Browser)        │   │
│  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────┐
│        Business Logic Layer                 │
│  ┌───────────────────────────────────────┐  │
│  │  prismov2.py - Core Engine            │  │
│  │  • Process Analysis                   │  │
│  │  • Metrics Calculation                │  │
│  │  • Report Generation                  │  │
│  │  • History Management                 │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────┐
│        Data & Storage Layer                 │
│  ┌──────────────┐  ┌──────────────────┐   │
│  │  psutil      │  │ Local JSON Store │   │
│  │  (System)    │  │ (Persistent)     │   │
│  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────┐
│        Integration Layer                    │
│  ┌──────────────┐  ┌──────────────────┐   │
│  │ Telegram Bot │  │ External APIs    │   │
│  │ Integration  │  │ (Webhooks)       │   │
│  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────┘
```

### Data Flow

1. **Collection**: `psutil` library reads system metrics
2. **Processing**: prismov2 calculates aggregates and trends
3. **Storage**: Results saved to local JSON database
4. **Visualization**: UI displays current state and history
5. **Distribution**: Reports sent via Telegram/API

### Key Libraries

| Library | Purpose | Version |
|---------|---------|---------|
| psutil | System monitoring | Latest |
| PyQt5 | Desktop GUI | 5.15+ |
| Streamlit | Web dashboard | Latest |
| ReportLab | PDF generation | Latest |
| Requests | HTTP API calls | Latest |

---

## API Reference

### Core Functions (prismov2.py)

#### System Monitoring
```python
def analizar_procesos() -> list
    """
    Analyze all running processes and return their metrics.
    Returns: List of dicts with {name, cpu, ram_mb}
    """

def get_system_snapshot() -> dict
    """
    Get current system metrics snapshot.
    Returns: {cpu_percent, ram_percent, timestamp}
    """
```

#### History Management
```python
def load_history() -> list
    """Load historical snapshots from disk."""

def save_history(history: list) -> None
    """Persist history snapshots to disk."""
```

#### Configuration
```python
def load_config() -> dict
    """Load application configuration."""

def save_config(config: dict) -> None
    """Save application configuration."""

def load_scheduling() -> dict
    """Load scheduling configuration."""

def save_scheduling(schedule: dict) -> None
    """Save scheduling configuration."""
```

#### Report Generation
```python
def generate_report(format: str = 'html') -> str
    """
    Generate analysis report.
    Parameters:
        format: 'html' or 'pdf'
    Returns: File path to generated report
    """
```

#### Telegram Integration
```python
def load_linking_code() -> str
    """Get or generate new Telegram linking code."""

def send_telegram_alert(message: str, code: str) -> bool
    """Send alert message via Telegram bot."""

def send_telegram_report(file_path: str, code: str) -> bool
    """Send report file via Telegram bot."""
```

---

## Configuration

### config.json Structure
```json
{
  "chat_id": "123456789",
  "telegram_token": "bot_token_here",
  "scheduling": {
    "activo": true,
    "dias": ["monday", "friday"],
    "hora_inicio": "08:00",
    "hora_fin": "18:00",
    "intervalo_minutos": 60
  },
  "supabase_enabled": false,
  "api_webhook": "https://api.domain.com/ingest"
}
```

### perfil_base.json Structure
```json
{
  "usuario": "Administrator",
  "empresa": "Company Name",
  "departamento": "Operations",
  "localizacion": "Plant A",
  "contacto": "admin@company.com"
}
```

### Environment Variables
```bash
PRISMOV_DATA_DIR    # Override default data directory
TELEGRAM_BOT_TOKEN  # Telegram bot API token
SUPABASE_URL        # Supabase backend URL
```

---

## Development

### Setting Up Development Environment

1. **Clone and Install**
   ```bash
   git clone https://github.com/your-username/PRISMOV.git
   cd PRISMOV2
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development tools
   ```

2. **Code Style**
   - Follow PEP 8 guidelines
   - Use 4-space indentation
   - Maximum line length: 100 characters
   - Add docstrings to all functions

3. **Testing**
   ```bash
   pytest tests/
   pytest --cov=prismov2  # With coverage
   ```

4. **Building Executable**
   ```bash
   pyinstaller prismov_gui.spec
   # Output: dist/prismov_gui.exe
   ```

### Project Structure for Development

```
PRISMOV2/
├── src/
│   ├── prismov2.py
│   ├── prismov_gui.py
│   └── web_demo.py
├── tests/
│   ├── test_core.py
│   ├── test_reporting.py
│   └── test_integration.py
├── docs/
│   ├── api.md
│   └── user_guide.md
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

### Contribution Workflow

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/new-feature`
3. **Commit** changes: `git commit -am 'Add new feature'`
4. **Push** to branch: `git push origin feature/new-feature`
5. **Create** Pull Request on GitHub

---

## Troubleshooting

### Common Issues

#### Issue: "Permission denied" when accessing processes
**Solution**: Run PRISMOV as Administrator
- Right-click application → Run as Administrator
- Or set startup shortcut to run in elevated mode

#### Issue: Telegram bot not sending messages
**Solution**: Verify bot configuration
1. Check Telegram token in `config.json`
2. Verify bot is active and connected
3. Check chat_id is correct
4. Re-generate linking code and send to bot

#### Issue: Historical data not saving
**Solution**: Check file permissions
1. Verify `%LOCALAPPDATA%\PRISMOV\` folder exists and is writable
2. Check disk space availability
3. Review application logs

#### Issue: High CPU usage on startup
**Solution**: This is normal during initial process scan
- First scan takes 10-20 seconds
- Subsequent scans are cached
- UI updates every 2 seconds (configurable)

#### Issue: Cannot generate PDF reports
**Solution**: Install missing font library
```bash
pip install reportlab
python -m reportlab.pdfbase.ttfonts.py
```

### Performance Optimization

#### Reduce CPU Usage
- Increase timer interval in GUI: `self.timer.start(5000)` (5 seconds)
- Disable real-time graphs during high load
- Use automatic mode instead of constant monitoring

#### Reduce Memory Usage
- Limit historical data retention
- Clear old history files manually
- Archive history to external storage

#### Improve Response Time
- Reduce number of processes displayed
- Use faster storage (SSD vs HDD)
- Disable real-time PDF generation

---

## FAQ

**Q: Can PRISMOV monitor remote machines?**
A: Current version monitors local machine only. Remote monitoring requires agent installation on target machines (planned for v3.0).

**Q: Is PRISMOV open-source?**
A: Yes, released under MIT License. Contributions welcome!

**Q: Can I customize the dashboard?**
A: Yes, modify `prismov_gui.py` or `web_demo.py` to customize appearance.

**Q: What is Total Harmonic Distortion (THD)?**
A: THD measures electrical signal quality. PRISMOV maps THD to system performance metrics for business analysis.

**Q: Does PRISMOV work on macOS/Linux?**
A: Partially. Core `prismov2.py` is cross-platform but GUI requires adjustments for non-Windows OS.

---

## Support & Contact

- **Issues**: Report bugs on [GitHub Issues](https://github.com/your-username/PRISMOV/issues)
- **Discussions**: Join [GitHub Discussions](https://github.com/your-username/PRISMOV/discussions)
- **Email**: support@prismov.dev
- **Documentation**: Full docs at [PRISMOV Wiki](https://github.com/your-username/PRISMOV/wiki)

---

## License

PRISMOV V2 is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 PRISMOV Development Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

**Version**: 2.0.0 | **Last Updated**: 2024 | **Status**: Active Development
