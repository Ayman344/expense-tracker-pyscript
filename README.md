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
2. **Summary dashboard** — a live balance with total income and total expenses, plus a
   **spending-by-category** bar chart that updates as data changes.
3. **Persistence, filtering & export** — transactions are saved to `localStorage` and
   survive reloads; the list can be **filtered by month and category**, and the current
   view can be **exported to CSV**.

## Tech stack
- **Python** (application logic) via **PyScript / Pyodide** (`2025.7.3`)
- Plain **HTML** and **CSS** — no framework, no build step
- **GitHub Pages** for hosting

## Run locally
PyScript loads its Python source over HTTP, so open the folder with a local server rather
than a `file://` URL:

```bash
python -m http.server 8000
# then open http://localhost:8000
```

## AI tools used
This project was developed with the help of AI coding tools:
- **Claude Code** (Anthropic), model **Claude Opus 4.8**

## Author
Ayman Sajjad Akash — https://github.com/Ayman344
