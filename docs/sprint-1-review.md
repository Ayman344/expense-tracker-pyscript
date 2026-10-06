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
This sprint was **human-led and AI-assisted**. I set the direction, made the decisions, and reviewed every step; **Claude Code** (Anthropic, model **Claude Opus 5.5**) did most of the hands-on work under that direction.

### Planning — led by me
- **Started the sprint:** gave Claude Code the assignment and the course slides (Agile and Plan-driven Software Development) and asked it to explain *what, why, and how* for every step, so I could learn the process while doing it.
- **Set the working rules** in a project instructions file (`CLAUDE.md`): plain step-by-step replies, a progress map in every reply, ask instead of assuming, and confirm before any public action.
- **Chose the sprint content:** proposed a new UI-improvement item based on an open-source GitHub design, picked #4 (recurring transactions) and #5 (budget goals), and decided to fold the theme toggle (#3) into the UI work.
- **Chose the references:** compared three open-source dashboards with live demos (Actual Budget, TailAdmin, Mosaic) and picked Actual Budget. During plan review I **revised** this: shadcn/ui for the UI design and Actual Budget for feature ideas only, and had the UI part re-planned.
- **Reviewed and approved the written sprint plan** — Sprint Goal, acceptance criteria per issue, Definition of Done, work order (#7 → #4 → #5), and verification steps — only after my revisions were in.
- **Planning documents produced:**
  - `Sprint-1-Plan.md` — the approved sprint plan with its revision history (v1 → v2 after my review → v3 scope correction).
  - `CLAUDE.md` — requirements checklist, locked decisions, Definition of Done, progress checklist, and future backlog.
  - On GitHub — the Sprint Goal in the milestone, acceptance criteria in issue #7, and test notes in each pull request.

### Review and course correction — me
- Reviewed each increment on the live site before the next issue started.
- **Audited the sprint against the assignment checklist** mid-sprint and found that Sprint 1 contained an issue (#7) that was not from the Assignment 1 backlog. I chose the fix — move #3 into the milestone and keep #7 outside it — and approved renaming PR #8 so its title references #3.
- Questioned how other people can use the app without installing PyScript; the answer exposed two risks (dependency on pyscript.net, data locked to one browser), which I added to the future backlog.

### Hands-on work — Claude Code, under my direction
- **Research:** found candidate open-source references with live demos and studied the shadcn/ui dashboard layout.
- **Implementation:** wrote the HTML, CSS, and Python for each feature, writing the core logic in `core.py` and its unit tests first.
- **Testing:** ran the 18 unit tests and drove the app in a browser (transactions, rules, budgets, reloads, mobile layout).
- **Git/GitHub workflow:** created the feature branches, issue-referencing commits, pull requests, merges, milestone, and board updates with the `gh` CLI.

## Sprint Retrospective
**One thing that went well:** The feature-branch → pull request → merge loop, with a clear Definition of Done, kept `main` always working. Each merge produced a usable increment on the live site, and putting the tricky logic in a tested `core.py` made the features reliable (e.g. Jan 31 → Feb 28 → Mar 31 for monthly rules).

**One challenge:** shadcn/ui, the chosen design reference, is a React + Tailwind library, and this project has no Node build step (it runs Python in the browser with PyScript). The design had to be re-created by hand in plain CSS — matching shadcn's design tokens and component styles without using its code — which took more work than installing a library.

**Process note (transparency):** Sprint Planning first included a new issue (#7, UI redesign). Because the assignment requires Sprint 1 issues from the Assignment 1 backlog, the sprint was corrected to use #3 (theme toggle), which #7 had grown out of; #7 is closed outside the milestone. #3 had been marked *In Progress* since Assignment 1, so on the board it moved In Progress → Done in this sprint rather than starting from To Do. Lesson: check sprint scope against the requirements before starting work.

## Next sprint candidates (backlog refinement)
- #6 Write a user guide in the documentation
- Self-host the PyScript/Pyodide files so the app does not depend on pyscript.net (also enables offline use)
- Multi-device sync (idea from Actual Budget)
