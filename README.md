# PRISMOV - Industrial System Monitoring (THD)

## Motivation
PRISMOV is a professional desktop application designed to monitor industrial systems, specifically focusing on Total Harmonic Distortion (THD) and its implications for both business and plant operations. By bridging the gap between raw data collection and actionable business intelligence, PRISMOV enables organizations to optimize performance, reduce downtime, and seamlessly integrate digital solutions into their operational lifecycle.

## Features
- **Automated Data Lifecycle**: Schedule systematic data collection routines (RA 5b).
- **Cloud & Automation**: Background cron-jobs for continuous reporting.
- **Secure Communications**: Telegram bot integration for real-time secure alerts (RA 5i).
- **Business Intelligence**: Instant THD analysis mapping technical metrics to business impact (RA 2e).
- **Comprehensive Reporting**: Generates interactive HTML reports automatically (RA 2g).

## Installation & Deployment
1. Clone the repository.
2. Ensure you have Python 3.10+ installed.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python prismov_gui.py
   ```

## Usage Examples
1. **Interactive Analysis**: Click "Ejecutar análisis ahora" to instantly generate a local report of your machine statuses.
2. **Telegram Alerts**: Click "Generar nuevo código", send it to `@PrisMovBot` on Telegram, and receive reports directly to your mobile device.
3. **Scheduled Monitoring**: Navigate to "Configurar programación" and set PRISMOV to run every 60 minutes on weekdays.

## Demo
*(Since this is a desktop GUI built with PyQt5, a web demo via Streamlit is not directly applicable. However, the core logic in `prismov.py` can be easily decoupled and hosted via FastAPI + Streamlit in future releases.)*

## Documentation
Check our [Wiki](https://github.com/your-username/PRISMOV/wiki) for full technical documentation, or generate local HTML docs using `pdoc`:
```bash
pdoc --html --output-dir docs prismov_gui.py prismov.py
```
