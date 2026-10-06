# Sprint 1 Review — PyExpense

**Sprint:** Sprint 1 (Oct 5 – Oct 8, 2026) · **Milestone:** [Sprint 1](https://github.com/Ayman344/expense-tracker-pyscript/milestone/1) · **Board:** [Expense Tracker — Development](https://github.com/users/Ayman344/projects/2)

## Sprint Goal
> Make PyExpense easier to use and more proactive: a clean shadcn/ui-style interface with a light/dark theme, recurring income/expenses that add themselves, and monthly category budgets that warn before overspending.

**Result: goal met.** All three Sprint 1 issues are closed (milestone 100%), merged into `main`, and live at https://ayman344.github.io/expense-tracker-pyscript/.

## Sprint Backlog and outcome
| Issue (from Assignment 1 backlog) | Feature branch | Pull request | Status |
|---|---|---|---|
| #3 Add dark / light theme toggle | `feature/7-ui-redesign` | [#8](https://github.com/Ayman344/expense-tracker-pyscript/pull/8) | Done |
| #4 Add recurring transactions | `feature/4-recurring-transactions` | [#9](https://github.com/Ayman344/expense-tracker-pyscript/pull/9) | Done |
| #5 Add monthly budget goals with alerts | `feature/5-budget-goals` | [#10](https://github.com/Ayman344/expense-tracker-pyscript/pull/10) | Done |

Every commit references its issue number (e.g. `(#4)`), and every PR body references its issue with `Closes #N`.

## What was implemented
### #3 — Light/dark theme toggle (with the UI redesign, #7)
- A theme toggle in the sidebar switches between light and dark mode. The choice is saved in `localStorage` and applied before the first paint, so the page never flashes the wrong theme.
- During Sprint Planning this item grew into a wider UI redesign, tracked as #7 and delivered in the same PR. The design follows the **shadcn/ui** concept (MIT): its neutral "zinc" design tokens, cards, buttons, badges, table, and sidebar/dashboard layout, re-created in plain CSS because shadcn/ui needs React + Node. The redesign adds sidebar navigation (Dashboard / Transactions), KPI cards, a recent-transactions card, a responsive mobile menu, and HTML escaping of user text.

### #4 — Recurring transactions
- New **Recurring** view: create weekly or monthly rules (e.g. rent, salary) with a start date; the rules table shows the next due date.
- Due entries are created automatically on load — including missed dates since the start — and marked with a "↻ recurring" badge. A `last_generated` date per rule prevents duplicates after reload. Deleting a rule keeps entries already created.
- Feature idea from **Actual Budget**'s "Schedules" (MIT).

### #5 — Monthly budget goals with alerts
- New **Budgets** view: a monthly limit per expense category, with spent, remaining, and a progress bar — green (<80%), amber (80–100%), red (over). A month selector shows past months.
- The Dashboard shows an alert for categories near or over their limit, and a toast message appears when a new expense crosses 80% or 100%.
- Feature idea from **Actual Budget**'s category budgets.

### Quality
- Date and budget logic lives in `core.py` (pure Python, no browser code) with **18 unit tests** (`python -m unittest discover tests`) — month-end clamping, leap years, catch-up, no duplicates, and exact 80% / 100% thresholds.
- Each feature was checked in the browser against its acceptance criteria before the PR, and again on the live site after merge.

## How AI coding tools were used
**Claude Code** (Anthropic, model **Claude Opus 5.5**) was used throughout the sprint, with me directing and reviewing:
- **Research and design:** compared open-source references (Actual Budget, TailAdmin, Mosaic, shadcn/ui) and studied the shadcn/ui dashboard block before coding.
- **Planning:** turned the Sprint Goal into acceptance criteria and a Definition of Done for each issue.
- **Implementation:** wrote the HTML/CSS/Python for each feature, and wrote the `core.py` logic together with its unit tests first.
- **Testing:** ran the unit tests and drove the app in a browser (adding transactions, rules, and budgets; checking reloads and the mobile layout).
- **Workflow:** ran the Git/GitHub steps — feature branches, issue-referencing commits, pull requests, merges, milestone, and board updates through the `gh` CLI.

## Sprint Retrospective
**One thing that went well:** The feature-branch → pull request → merge loop, with a clear Definition of Done, kept `main` always working. Each merge produced a usable increment on the live site, and putting the tricky logic in a tested `core.py` made the features reliable (e.g. Jan 31 → Feb 28 → Mar 31 for monthly rules).

**One challenge:** shadcn/ui, the chosen design reference, is a React + Tailwind library, and this project has no Node build step (it runs Python in the browser with PyScript). The design had to be re-created by hand in plain CSS — matching shadcn's design tokens and component styles without using its code — which took more work than installing a library.

**Process note (transparency):** Sprint Planning first included a new issue (#7, UI redesign). Because the assignment requires Sprint 1 issues from the Assignment 1 backlog, the sprint was corrected to use #3 (theme toggle), which #7 had grown out of; #7 is closed outside the milestone. #3 had been marked *In Progress* since Assignment 1, so on the board it moved In Progress → Done in this sprint rather than starting from To Do. Lesson: check sprint scope against the requirements before starting work.

## Next sprint candidates (backlog refinement)
- #6 Write a user guide in the documentation
- Self-host the PyScript/Pyodide files so the app does not depend on pyscript.net (also enables offline use)
- Multi-device sync (idea from Actual Budget)
