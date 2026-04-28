# Questions and Answers - Phase 2: Utility and Application Analysis (PRISMOV)

## Criterion 6a) Strategic Objectives
**What specific strategic objectives does your software address for the company?**
PRISMOV addresses the main strategic objective of maximizing operational efficiency (OEE) and reducing unplanned downtime. This is achieved through continuous monitoring of harmonics (THD) and critical parameters in industrial equipment.
**How does the software align with the general digitalization strategy?**
It aligns by digitalizing the data lifecycle (RA 5b) that was previously collected manually with multimeters, and sending automatic reports via messaging bots (RA 5i, Telegram) instantly, democratizing plant information (OT) to business decision-making levels (IT).

## Criterion 6b) Business Areas and Communications
**Which company areas (production, business, communications) benefit most from your software?**
1. *Production*: By receiving preventive alerts and automatic reports, maintenance technicians act before a failure occurs.
2. *Business/Management*: By having executive reports (RA 2g) that translate THD failures into financial impact.
3. *Communications*: Integrates operators through secure conversational bots, accelerating decision-making.
**What operational impact do you expect in daily operations?**
A reduction of bottlenecks through much lower Mean Time To Repair (MTTR) and savings in hours of manual log analysis on paper.

## Criterion 6c) Areas Susceptible to Digitalization
**Which company areas are most susceptible to being digitalized with your software?**
The Preventive/Predictive Maintenance Area and the Electrical Quality Control Department. These areas depend on constant readings that are easily automatable through PRISMOV's "Automatic Mode".
**How will digitalization improve operations in those areas?**
It will allow operators to schedule daily and weekly analyses ("Configure Scheduling"), transitioning from a "reactive" model (fix what breaks) to one completely digitalized and analytical ("preventive").

## Criterion 6d) Fit of Digitalized Areas (DA)
**How do digitalized areas interact with non-digitalized ones?**
Digitalized areas (Maintenance with PRISMOV) generate a "THD Report" that is exported (for example, in PDF or paper if necessary) to non-digitalized areas (for example, line operators or pure accounting without ERP).
**What solutions or improvements would you propose to integrate these areas?**
I would propose a documented REST API in PRISMOV so that other systems (ERP/CRM) can consume THD data generated internally, forcing horizontal digitalization of the entire value chain.

## Criterion 6e) Present and Future Needs
**What current company needs does your software resolve?**
It solves the lack of real-time visibility of machinery status (continuous THD monitoring and immediate reporting on Telegram) and eliminates human error in data transcription (automated data lifecycle).
**Future Proposals (Roadmap)**:
1. Migration to a Multi-user Web App.
2. Data ingestion from multiple industrial plants (IoT / Edge computing).
3. Artificial Intelligence capabilities for predictive analysis.

## Criterion 6f) Relationship with Technologies
**What enabling technologies have you employed and how do they impact company areas?**
- **Cloud Computing / APIs and Bots (Application Level)**: Use of Telegram and cron-jobs in the cloud or on-premise servers (RA 5f). It impacts by streamlining communications and reports.
- **Graphical Interfaces and Dynamic Reports**: PyQt5 interfaces with dark mode for ergonomic human visualization in plants.
**What specific benefits does the implementation of these technologies provide?**
Interactivity, reduction of friction in software adoption thanks to a modern and professional GUI, and availability of asynchronous information via Telegram.

## Criterion 6g) Security Gaps
**What possible security gaps could arise when implementing your software?**
1. Exposure of API tokens and database URLs in visible source code.
2. Data interception in transit if reports are not encrypted.
3. Unauthorized access by local operators to program configurations.
**What specific measures would you propose to mitigate them?**
Already implemented: Explicit Supabase disconnection and management of unique one-time linking codes (Tokenization) for Telegram (RA 5i).
To implement: Encryption at rest (AES) of the `historial.json` file and use of `.env` environment variables instead of saving credentials in the code base.

## Criterion 6h) Data Management and Analysis
**How is data managed in your software and what methodologies do you use?**
Raw data (sensors) is collected, formatted, grouped and stored temporarily, managing its complete lifecycle (RA 5b). Then, internal algorithms (in `prismov.py`) extract indices and business comparisons.
**What do you do to guarantee data quality and consistency?**
By using standardized formats (`.json`) and validations prior to analysis execution or scheduling hours (like `QTimeEdit` or `QSpinBox` that enforce minute intervals), injection of impure data by the end user is avoided.
