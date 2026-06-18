# Agent Instructions

Permanent rules for future work in this repository:

- Work only inside this repository unless the user explicitly asks otherwise.
- Do not add fake market data to production code.
- Demo data is allowed only in `src/russian_markets_lab/demo/`.
- Demo mode must stay off by default and must be visibly marked when enabled.
- Dashboard language defaults to English; Russian must remain available.
- Position the project as a research platform, not an order-sending or signal-selling app.
- Do not add broker integrations, credential handling, or real order placement.
- Keep the dashboard thin: UI orchestration in `app.py`, rendering in `views.py`, reusable UI in `components.py`, charts in `charts.py`, loading in `data_loader.py`.
- Prefer small, focused changes that preserve the current pipeline and analytics architecture.
- Final responses should be concise and include changed files, commands run, results, and unresolved issues.
