# PyExpense — Expense Tracker (PyScript)

A small but functional **expense / budget tracker** written in **Python** and running
entirely in the browser with **[PyScript](https://pyscript.net/)**. No backend and no
build step — it is hosted as static files on GitHub Pages, and all data stays in the
browser's `localStorage`.

**Live demo:** https://ayman344.github.io/expense-tracker-pyscript/

## Open-source reference project
This project was inspired by an existing open-source expense tracker and built as my own,
independent implementation.

- **Reference:** Expense Tracker (React) by Brad Traversy
- **GitHub URL:** https://github.com/bradtraversy/expense-tracker-react

The reference is a React app that tracks income and expenses and shows a running balance.
PyExpense targets comparable functionality and scope, but is written in Python (PyScript)
instead of React and adds categories, a spending chart, filtering, and CSV export. The
code here is my own — I used the reference only to define comparable scope, not to copy it.

## Major features
1. **Transaction management** — add, **edit**, and delete income and expense entries, each
   with a description, amount, type, category, and date.
2. **Dashboard** — balance, income, and expense cards, a **spending-by-category** chart,
   and the latest transactions, with its own period selector.
3. **Persistence, filtering & export** — transactions are saved to `localStorage` and
   survive reloads; the list can be **filtered by month and category**, and the current
   view can be **exported to CSV**.
4. **Recurring transactions** — create weekly or monthly rules (e.g. rent, salary). Due
   entries are added automatically — including any missed since the start date — and
   are marked with a "↻ recurring" badge. No duplicates on reload.
5. **Monthly budget goals with alerts** — set a monthly limit per expense category and track
   it with progress bars (green → amber at 80% → red when over). The dashboard shows an
   alert for categories near or over their limit, and a message pops up when a new expense
   crosses 80% or 100%.
6. **Modern interface** — sidebar navigation, **light / dark theme** (remembered between
   visits), and a responsive layout that works on phones.

## Design and feature references
- **UI design:** [shadcn/ui](https://github.com/shadcn-ui/ui) (MIT). shadcn/ui is built for
  React + Tailwind; PyExpense re-creates its *design concept* — the neutral "zinc" theme,
  CSS-variable design tokens, cards, buttons, badges, tables, and the sidebar/dashboard
  layout — in plain CSS, so the app stays buildless. No shadcn/ui code is copied.
- **Feature ideas:** [Actual Budget](https://github.com/actualbudget/actual) (MIT) — a
  local-first personal finance app. PyExpense follows the same local-first idea (your data
  stays in your browser) and takes inspiration from its budgets and schedules.

## Tech stack
- **Python** (application logic) via **PyScript / Pyodide** (`2025.7.3`)
- Plain **HTML** and **CSS** — no framework, no build step
- **GitHub Pages** for hosting

## Tests
Pure logic (recurrence dates, budget status) lives in `core.py`, which has no browser code, so it
can be tested with plain Python:

```bash
python -m unittest discover tests
```

## Run locally
PyScript loads its Python source over HTTP, so open the folder with a local server rather
than a `file://` URL:

```bash
python -m http.server 8000
# then open http://localhost:8000
```

## AI tools used
This project was developed with the help of AI coding tools:
- **Claude Code** (Anthropic) — model **Claude Opus 4.8** (initial version, Assignment 1)
- **Claude Code** (Anthropic) — model **Claude Opus 5.5** (Sprint 1: UI redesign, recurring transactions, budgets)

## Author
Ayman Sajjad Akash — https://github.com/Ayman344
