"""
PyExpense — a local-first expense/budget tracker written in Python, running in
the browser with PyScript. All logic (state, totals, chart, persistence, CSV
export, navigation, theme) is Python.

UI design concept: shadcn/ui (re-created in plain CSS, see styles.css).

Features:
  F1  Transaction management ..... add, edit, and delete income/expense entries.
  F2  Dashboard .................. balance/income/expense cards, spending chart,
                                    recent transactions.
  F3  Persistence & tools ........ localStorage saving, month/category filters,
                                    and CSV export.
  F4  Recurring transactions ...... weekly/monthly rules that add entries
                                    automatically when due (issue #4).
  UI  Sidebar navigation, light/dark theme toggle, responsive layout.
"""

import json
from datetime import date
from html import escape
from urllib.parse import quote

from pyscript import document, window, when

import core

STORAGE_KEY = "pyexpense.transactions"
THEME_KEY = "pyexpense.theme"
RECURRING_KEY = "pyexpense.recurring"

VIEW_TITLES = {
    "dashboard": "Dashboard",
    "transactions": "Transactions",
    "recurring": "Recurring",
}

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


# Recurring rules (issue #4) ----------------------------------------------------
rules = []                 # list of rule dicts
next_rule_id = 1


def load_rules():
    global rules, next_rule_id
    raw = window.localStorage.getItem(RECURRING_KEY)
    if raw:
        try:
            rules = json.loads(raw)
        except Exception:
            rules = []
    if rules:
        next_rule_id = max(r["id"] for r in rules) + 1


def save_rules():
    window.localStorage.setItem(RECURRING_KEY, json.dumps(rules))


def generate_due():
    """Create transactions for every rule occurrence that is due (up to today)
    and not yet generated. Returns how many transactions were added."""
    global next_id
    today = date.today()
    added = 0
    for rule in rules:
        due = core.due_occurrences(rule, today)
        for day in due:
            transactions.append({
                "id": next_id,
                "desc": rule["desc"],
                "amount": rule["amount"],
                "type": rule["type"],
                "category": rule["category"],
                "date": day,
                "rule_id": rule["id"],
            })
            next_id += 1
            added += 1
        if due:
            rule["last_generated"] = due[-1]
    if added:
        save_transactions()
        save_rules()
    return added


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def q(selector):
    return document.querySelector(selector)


def money(value):
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.2f}"


def signed(t):
    return t["amount"] if t["type"] == "income" else -t["amount"]


def plural(n, word, many=None):
    return f"{n} {word}" if n == 1 else f"{n} {many or word + 's'}"


def newest_first(rows):
    return sorted(rows, key=lambda t: (t["date"], t["id"]), reverse=True)


def all_months():
    return sorted({t["date"][:7] for t in transactions}, reverse=True)


def in_month(rows, month):
    if month == "all":
        return list(rows)
    return [t for t in rows if t["date"].startswith(month)]


def filtered_transactions():
    """Rows for the Transactions table (month + category filters)."""
    month = q("#filter-month").value
    category = q("#filter-category").value
    rows = in_month(transactions, month)
    if category != "all":
        rows = [t for t in rows if t["category"] == category]
    return newest_first(rows)


def dashboard_transactions():
    """Rows for the Dashboard (its own period select)."""
    return newest_first(in_month(transactions, q("#dash-month").value))


def fill_month_select(selector, all_label):
    select = q(selector)
    keep = select.value
    months = all_months()
    options = [f'<option value="all">{all_label}</option>']
    options += [f'<option value="{m}">{m}</option>' for m in months]
    select.innerHTML = "".join(options)
    select.value = keep if keep in ["all"] + months else "all"


# ----------------------------------------------------------------------------
# Rendering — Dashboard
# ----------------------------------------------------------------------------
def render_stats(rows):
    incomes = [t for t in rows if t["type"] == "income"]
    expenses = [t for t in rows if t["type"] == "expense"]
    income = sum(t["amount"] for t in incomes)
    expense = sum(t["amount"] for t in expenses)
    q("#stat-balance").innerText = money(income - expense)
    q("#stat-income").innerText = money(income)
    q("#stat-expense").innerText = money(expense)
    q("#kpi-income-count").innerText = plural(len(incomes), "entry", "entries")
    q("#kpi-expense-count").innerText = plural(len(expenses), "entry", "entries")
    month = q("#dash-month").value
    q("#kpi-scope").innerText = "All time" if month == "all" else month


def render_chart(rows):
    totals = {}
    for t in rows:
        if t["type"] == "expense":
            totals[t["category"]] = totals.get(t["category"], 0) + t["amount"]

    chart = q("#chart")
    if not totals:
        chart.innerHTML = '<p class="empty">No expenses in this period.</p>'
        return

    top = max(totals.values())
    parts = []
    for cat, amt in sorted(totals.items(), key=lambda kv: kv[1], reverse=True):
        pct = (amt / top) * 100
        parts.append(
            '<div class="bar-row">'
            f'<span class="bar-label">{escape(cat)}</span>'
            f'<span class="bar-track"><span class="bar-fill" style="width:{pct:.1f}%"></span></span>'
            f'<span class="bar-value">{money(amt)}</span>'
            '</div>'
        )
    chart.innerHTML = "".join(parts)


def render_recent(rows):
    lst = q("#recent-list")
    recent = rows[:5]
    if not recent:
        lst.innerHTML = '<li><span class="empty">No transactions yet. Use “Quick add”.</span></li>'
        return
    items = []
    for t in recent:
        cls = "amt-income" if t["type"] == "income" else "amt-expense"
        items.append(
            '<li>'
            '<div class="r-main">'
            f'<span class="r-desc">{escape(t["desc"])}</span>'
            f'<span class="r-sub">{escape(t["category"])} · {t["date"]}</span>'
            '</div>'
            f'<span class="{cls}">{money(signed(t))}</span>'
            '</li>'
        )
    lst.innerHTML = "".join(items)


def render_dashboard():
    rows = dashboard_transactions()
    render_stats(rows)
    render_chart(rows)
    render_recent(rows)


# ----------------------------------------------------------------------------
# Rendering — Transactions table
# ----------------------------------------------------------------------------
def render_table():
    rows = filtered_transactions()
    q("#tx-count").innerText = plural(len(rows), "transaction")
    body = q("#tx-list")
    if not rows:
        body.innerHTML = '<tr class="empty-row"><td colspan="5">No transactions match this filter.</td></tr>'
        return

    items = []
    for t in rows:
        cls = "amt-income" if t["type"] == "income" else "amt-expense"
        badge = "badge-income" if t["type"] == "income" else "badge"
        items.append(
            '<tr>'
            f'<td>{t["date"]}</td>'
            f'<td>{escape(t["desc"])}{recurring_badge(t)}</td>'
            f'<td><span class="badge {badge}">{escape(t["category"])}</span></td>'
            f'<td class="num {cls}">{money(signed(t))}</td>'
            '<td><div class="row-actions">'
            f'<button type="button" class="btn btn-ghost icon-btn" data-action="edit" data-id="{t["id"]}" title="Edit">&#9998;</button>'
            f'<button type="button" class="btn btn-ghost icon-btn danger" data-action="delete" data-id="{t["id"]}" title="Delete">&#10005;</button>'
            '</div></td>'
            '</tr>'
        )
    body.innerHTML = "".join(items)


def recurring_badge(t):
    if t.get("rule_id"):
        return '<span class="badge badge-outline badge-recurring" title="Added by a recurring rule">&#8635; recurring</span>'
    return ""


# ----------------------------------------------------------------------------
# Rendering — Recurring rules (issue #4)
# ----------------------------------------------------------------------------
def render_rules():
    q("#rule-count").innerText = plural(len(rules), "rule")
    body = q("#rule-list")
    if not rules:
        body.innerHTML = '<tr class="empty-row"><td colspan="5">No recurring rules yet.</td></tr>'
        return
    today = date.today()
    items = []
    for r in sorted(rules, key=lambda r: core.next_due(r, today) or ""):
        cls = "amt-income" if r["type"] == "income" else "amt-expense"
        amount = r["amount"] if r["type"] == "income" else -r["amount"]
        items.append(
            '<tr>'
            f'<td>{escape(r["desc"])}<div class="r-sub">{escape(r["category"])}</div></td>'
            f'<td><span class="badge badge-outline">{r["frequency"].capitalize()}</span></td>'
            f'<td>{core.next_due(r, today) or "—"}</td>'
            f'<td class="num {cls}">{money(amount)}</td>'
            '<td><div class="row-actions">'
            f'<button type="button" class="btn btn-ghost icon-btn danger" data-rule-delete="{r["id"]}" title="Delete rule">&#10005;</button>'
            '</div></td>'
            '</tr>'
        )
    body.innerHTML = "".join(items)


def render_all():
    fill_month_select("#dash-month", "All time")
    fill_month_select("#filter-month", "All months")
    render_dashboard()
    render_table()
    render_rules()


# ----------------------------------------------------------------------------
# Navigation (sidebar)
# ----------------------------------------------------------------------------
def show_view(name):
    if name not in VIEW_TITLES:
        name = "dashboard"
    for section in document.querySelectorAll("[data-view]"):
        section.hidden = section.dataset.view != name
    for item in document.querySelectorAll(".nav-item"):
        if item.dataset.nav == name:
            item.classList.add("active")
        else:
            item.classList.remove("active")
    q("#page-title").innerText = VIEW_TITLES[name]
    close_menu()


@when("click", "[data-nav]")
def on_nav(event):
    event.preventDefault()
    target = event.target.closest("[data-nav]")
    if target:
        show_view(target.dataset.nav)


@when("click", "#quick-add")
def on_quick_add(event):
    reset_form()
    show_view("transactions")
    q("#desc").focus()


# Mobile menu --------------------------------------------------------------
def close_menu():
    q("#sidebar").classList.remove("open")
    q("#backdrop").classList.remove("open")


@when("click", "#menu-btn")
def on_menu(event):
    q("#sidebar").classList.toggle("open")
    q("#backdrop").classList.toggle("open")


@when("click", "#backdrop")
def on_backdrop(event):
    close_menu()


# ----------------------------------------------------------------------------
# Theme toggle (light / dark)
# ----------------------------------------------------------------------------
def current_theme():
    return document.documentElement.getAttribute("data-theme") or "light"


def apply_theme(theme):
    document.documentElement.setAttribute("data-theme", theme)
    q("#theme-label").innerText = "Light mode" if theme == "dark" else "Dark mode"


@when("click", "#theme-toggle")
def on_theme_toggle(event):
    theme = "light" if current_theme() == "dark" else "dark"
    apply_theme(theme)
    window.localStorage.setItem(THEME_KEY, theme)


# ----------------------------------------------------------------------------
# Form: add / edit  (F1)
# ----------------------------------------------------------------------------
def reset_form():
    q("#edit-id").value = ""
    q("#tx-form").reset()
    q("#date").value = date.today().isoformat()
    q("#form-title").innerText = "Add transaction"
    q("#submit-btn").innerText = "Add transaction"
    q("#cancel-btn").hidden = True


@when("submit", "#tx-form")
def on_submit(event):
    global next_id
    event.preventDefault()
    desc = q("#desc").value.strip()
    try:
        amount = round(float(q("#amount").value), 2)
    except (TypeError, ValueError):
        amount = 0.0
    if not desc or amount <= 0:
        window.alert("Please enter a description and a positive amount.")
        return

    entry = {
        "desc": desc,
        "amount": amount,
        "type": q("#type").value,
        "category": q("#category").value,
        "date": q("#date").value or date.today().isoformat(),
    }

    edit_id = q("#edit-id").value
    if edit_id:
        for t in transactions:
            if t["id"] == int(edit_id):
                t.update(entry)
                break
    else:
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
def on_table_click(event):
    global transactions
    btn = event.target.closest("button[data-action]")
    if not btn:
        return
    tid = int(btn.dataset.id)

    if btn.dataset.action == "delete":
        transactions = [t for t in transactions if t["id"] != tid]
        save_transactions()
        render_all()
    elif btn.dataset.action == "edit":
        tx = next((t for t in transactions if t["id"] == tid), None)
        if not tx:
            return
        q("#edit-id").value = str(tx["id"])
        q("#desc").value = tx["desc"]
        q("#amount").value = str(tx["amount"])
        q("#type").value = tx["type"]
        q("#category").value = tx["category"]
        q("#date").value = tx["date"]
        q("#form-title").innerText = "Edit transaction"
        q("#submit-btn").innerText = "Save changes"
        q("#cancel-btn").hidden = False
        q("#desc").focus()


# ----------------------------------------------------------------------------
# Filters, dashboard period, CSV export  (F3)
# ----------------------------------------------------------------------------
@when("change", ".filter")
def on_filter_change(event):
    render_table()


@when("change", "#dash-month")
def on_dash_month(event):
    render_dashboard()


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
# Recurring rules: add / delete  (issue #4)
# ----------------------------------------------------------------------------
@when("submit", "#rule-form")
def on_rule_submit(event):
    global next_rule_id
    event.preventDefault()
    desc = q("#rule-desc").value.strip()
    try:
        amount = round(float(q("#rule-amount").value), 2)
    except (TypeError, ValueError):
        amount = 0.0
    if not desc or amount <= 0:
        window.alert("Please enter a description and a positive amount.")
        return

    rules.append({
        "id": next_rule_id,
        "desc": desc,
        "amount": amount,
        "type": q("#rule-type").value,
        "category": q("#rule-category").value,
        "frequency": q("#rule-frequency").value,
        "start_date": q("#rule-start").value or date.today().isoformat(),
        "last_generated": None,
    })
    next_rule_id += 1
    save_rules()
    added = generate_due()

    q("#rule-form").reset()
    q("#rule-start").value = date.today().isoformat()
    q("#rule-note").innerText = (
        f"Rule added. {plural(added, 'past entry', 'past entries')} created."
        if added else "Rule added. The first entry will be created on its start date."
    )
    render_all()


@when("click", "#rule-list")
def on_rule_list_click(event):
    global rules
    btn = event.target.closest("button[data-rule-delete]")
    if not btn:
        return
    rid = int(btn.dataset.ruleDelete)
    rules = [r for r in rules if r["id"] != rid]
    save_rules()                      # past transactions are kept
    q("#rule-note").innerText = "Rule deleted. Entries already created are kept."
    render_all()


# ----------------------------------------------------------------------------
# Boot
# ----------------------------------------------------------------------------
load_transactions()
load_rules()
generate_due()
q("#rule-start").value = date.today().isoformat()
apply_theme(current_theme())
q("#date").value = date.today().isoformat()
render_all()
show_view("dashboard")
q("#loading").hidden = True
q("#app").hidden = False
