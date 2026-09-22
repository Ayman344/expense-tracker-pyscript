"""
PyExpense — an expense/budget tracker written in Python, running in the browser
with PyScript. All logic (state, totals, chart, persistence, CSV export) is Python.

Major features:
  F1  Transaction management ..... add, edit, and delete income/expense entries.
  F2  Summary dashboard .......... live balance/income/expense totals + a
                                    per-category spending chart.
  F3  Persistence & tools ........ localStorage saving, month/category filters,
                                    and CSV export.
"""

import json
from datetime import date
from urllib.parse import quote

from pyscript import document, window, when

STORAGE_KEY = "pyexpense.transactions"

# ----------------------------------------------------------------------------
# State + persistence
# ----------------------------------------------------------------------------
transactions = []          # list of dicts
next_id = 1


def load_transactions():
    """Read saved transactions from the browser's localStorage."""
    global transactions, next_id
    raw = window.localStorage.getItem(STORAGE_KEY)
    if raw:
        try:
            transactions = json.loads(raw)
        except Exception:
            transactions = []
    if transactions:
        next_id = max(t["id"] for t in transactions) + 1


def save_transactions():
    """Persist transactions to localStorage as JSON."""
    window.localStorage.setItem(STORAGE_KEY, json.dumps(transactions))


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def money(value):
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.2f}"


def signed(t):
    return t["amount"] if t["type"] == "income" else -t["amount"]


def current_filters():
    month = document.querySelector("#filter-month").value
    category = document.querySelector("#filter-category").value
    return month, category


def filtered_transactions():
    month, category = current_filters()
    result = []
    for t in transactions:
        if month != "all" and not t["date"].startswith(month):
            continue
        if category != "all" and t["category"] != category:
            continue
        result.append(t)
    # newest date first
    return sorted(result, key=lambda t: t["date"], reverse=True)


# ----------------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------------
def render_stats(rows):
    income = sum(t["amount"] for t in rows if t["type"] == "income")
    expense = sum(t["amount"] for t in rows if t["type"] == "expense")
    document.querySelector("#stat-balance").innerText = money(income - expense)
    document.querySelector("#stat-income").innerText = money(income)
    document.querySelector("#stat-expense").innerText = money(expense)


def render_chart(rows):
    totals = {}
    for t in rows:
        if t["type"] == "expense":
            totals[t["category"]] = totals.get(t["category"], 0) + t["amount"]

    chart = document.querySelector("#chart")
    if not totals:
        chart.innerHTML = '<p class="empty">No expenses to chart.</p>'
        return

    top = max(totals.values())
    parts = []
    for cat, amt in sorted(totals.items(), key=lambda kv: kv[1], reverse=True):
        pct = (amt / top) * 100
        parts.append(
            f'<div class="bar-row">'
            f'<span class="bar-label">{cat}</span>'
            f'<span class="bar-track"><span class="bar-fill" style="width:{pct:.1f}%"></span></span>'
            f'<span class="bar-value">{money(amt)}</span>'
            f'</div>'
        )
    chart.innerHTML = "".join(parts)


def render_list(rows):
    lst = document.querySelector("#tx-list")
    if not rows:
        lst.innerHTML = '<li class="empty-row">No transactions match this filter.</li>'
        return

    items = []
    for t in rows:
        cls = "income" if t["type"] == "income" else "expense"
        amt = money(signed(t))
        items.append(
            f'<li class="tx {cls}">'
            f'<div class="tx-main">'
            f'<span class="tx-desc">{t["desc"]}</span>'
            f'<span class="tx-sub">{t["category"]} &middot; {t["date"]}</span>'
            f'</div>'
            f'<span class="tx-amt">{amt}</span>'
            f'<span class="tx-actions">'
            f'<button type="button" class="icon-btn" data-action="edit" data-id="{t["id"]}" title="Edit">&#9998;</button>'
            f'<button type="button" class="icon-btn danger" data-action="delete" data-id="{t["id"]}" title="Delete">&#10005;</button>'
            f'</span>'
            f'</li>'
        )
    lst.innerHTML = "".join(items)


def populate_month_filter():
    months = sorted({t["date"][:7] for t in transactions}, reverse=True)
    select = document.querySelector("#filter-month")
    keep = select.value
    options = ['<option value="all">All months</option>']
    for m in months:
        options.append(f'<option value="{m}">{m}</option>')
    select.innerHTML = "".join(options)
    # restore previous selection if still available
    values = ["all"] + months
    select.value = keep if keep in values else "all"


def render_all():
    populate_month_filter()
    rows = filtered_transactions()
    render_stats(rows)
    render_chart(rows)
    render_list(rows)


# ----------------------------------------------------------------------------
# Form: add / edit  (F1)
# ----------------------------------------------------------------------------
def reset_form():
    document.querySelector("#edit-id").value = ""
    document.querySelector("#tx-form").reset()
    document.querySelector("#date").value = date.today().isoformat()
    document.querySelector("#form-title").innerText = "Add transaction"
    document.querySelector("#submit-btn").innerText = "Add"
    document.querySelector("#cancel-btn").hidden = True


@when("submit", "#tx-form")
def on_submit(event):
    event.preventDefault()
    desc = document.querySelector("#desc").value.strip()
    amount_raw = document.querySelector("#amount").value
    try:
        amount = round(float(amount_raw), 2)
    except (TypeError, ValueError):
        amount = 0.0
    if not desc or amount <= 0:
        window.alert("Please enter a description and a positive amount.")
        return

    entry = {
        "desc": desc,
        "amount": amount,
        "type": document.querySelector("#type").value,
        "category": document.querySelector("#category").value,
        "date": document.querySelector("#date").value or date.today().isoformat(),
    }

    edit_id = document.querySelector("#edit-id").value
    if edit_id:
        for t in transactions:
            if t["id"] == int(edit_id):
                t.update(entry)
                break
    else:
        global next_id
        entry["id"] = next_id
        next_id += 1
        transactions.append(entry)

    save_transactions()
    reset_form()
    render_all()


@when("click", "#cancel-btn")
def on_cancel(event):
    reset_form()


@when("click", "#tx-list")
def on_list_click(event):
    btn = event.target.closest("button[data-action]")
    if not btn:
        return
    action = btn.dataset.action
    tid = int(btn.dataset.id)

    if action == "delete":
        global transactions
        transactions = [t for t in transactions if t["id"] != tid]
        save_transactions()
        render_all()
    elif action == "edit":
        tx = next((t for t in transactions if t["id"] == tid), None)
        if not tx:
            return
        document.querySelector("#edit-id").value = str(tx["id"])
        document.querySelector("#desc").value = tx["desc"]
        document.querySelector("#amount").value = str(tx["amount"])
        document.querySelector("#type").value = tx["type"]
        document.querySelector("#category").value = tx["category"]
        document.querySelector("#date").value = tx["date"]
        document.querySelector("#form-title").innerText = "Edit transaction"
        document.querySelector("#submit-btn").innerText = "Update"
        document.querySelector("#cancel-btn").hidden = False
        window.scrollTo(0, 0)


# ----------------------------------------------------------------------------
# Filters + CSV export  (F3)
# ----------------------------------------------------------------------------
@when("change", ".filter")
def on_filter_change(event):
    rows = filtered_transactions()
    render_stats(rows)
    render_chart(rows)
    render_list(rows)


@when("click", "#export-btn")
def on_export(event):
    rows = filtered_transactions()
    if not rows:
        window.alert("Nothing to export for the current filter.")
        return
    lines = ["Date,Description,Category,Type,Amount"]
    for t in rows:
        desc = t["desc"].replace('"', '""')
        lines.append(f'{t["date"]},"{desc}",{t["category"]},{t["type"]},{signed(t):.2f}')
    csv = "\n".join(lines)

    link = document.createElement("a")
    link.href = "data:text/csv;charset=utf-8," + quote(csv)
    link.download = "transactions.csv"
    document.body.appendChild(link)
    link.click()
    link.remove()


# ----------------------------------------------------------------------------
# Boot
# ----------------------------------------------------------------------------
load_transactions()
document.querySelector("#date").value = date.today().isoformat()
render_all()
document.querySelector("#loading").style.display = "none"
document.querySelector("#app").removeAttribute("hidden")
