# Contributing to PRISMOV

First off, thank you for considering contributing to PRISMOV! It's people like you that make PRISMOV an incredible tool for industrial digital transformation.

## How Can I Contribute?

### Reporting Bugs
This section guides you through submitting a bug report for PRISMOV.
* **Use a clear and descriptive title** for the issue.
* **Describe the exact steps** which reproduce the problem.
* Include screenshots and any relevant traceback errors from your terminal or `pyqt` GUI.

### Suggesting Enhancements
* Determine if your enhancement solves a business (management) or plant (production) problem.
* Provide an actionable, well-documented issue. Provide visual mockups if applicable.

### Setting Up a Development Environment
1. Ensure `python 3.10+` is installed.
2. We highly recommend using a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate # Unix/Mac
   .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```
3. Run tests before pushing changes.

## Future Extensions & Roadmap (Criterio 6e)
We are actively looking for contributors for:
1. **Migration from PyQt5 to Web App (Streamlit / Next.js)** for easier cloud deployment.
2. **Machine Learning Integration**: predictive maintenance based on historical THD data.
3. **Advanced Integrations**: ERP/MES system plugins and REST APIs to interconnect digitized operations with non-digital factory modules.
4. **Enhanced Authorization**: Expanding the Telegram Bot into a full Cloud Dashboard with Role-Based Access Control (RBAC).

## Code Style & Documentation
* Use **PEP 8** standard for Python code.
* Ensure all new implementations are documented using standard **Docstrings** (e.g., Sphinx or Google style).
* Ensure that the code reflects the alignment of production and business needs (RA 2e, 6b).

## Required Skills (Criterio 6k)
If you wish to maintain and expand the core software:
- **Core Developers**: Advanced Python, Object-Oriented Programming (PyQt5), and File-System manipulation.
- **Data Engineers**: Expertise in data aggregation, JSON processing, and real-time data pipelines.
- **Security Experts**: Knowledge of OAuth, Token management (Telegram APIs).

### Mentorship & Training
We aim to train new contributors effectively. We regularly annotate our `good-first-issue` tags and offer code reviews focusing not only on technical correctness but also on operational logic alignment.