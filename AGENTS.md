# AGENTS.md — django-survey-local-dev

## Stack
- **Django 6.0**, Python ≥3.13, SQLite
- **Package manager**: `uv` (not pip, not poetry)
- **Templates**: Django templates + Bootstrap 5.3 + `crispy-bootstrap5`
- **No JS framework** (vanilla JS for cognitive tasks)

## Commands
```
uv run src/manage.py runserver          # dev server
uv run src/manage.py makemigrations      # after model changes
uv run src/manage.py migrate
uv run src/manage.py loaddata survey/fixtures/*.json
uv run src/manage.py createsuperuser
uv run python -m django check           # validate project
```

All commands must be run from the repo root (not from `src/`).

## Project layout
```
src/
├── manage.py
├── core/                               # Django project config (settings, urls, asgi, wsgi)
├── survey/                             # app: questionnaire & user data
│   ├── models.py, views.py, forms.py, admin.py
│   ├── fixtures/                       # JSON fixtures (questions, options, platforms, content types)
│   ├── question_data.json              # raw reference data (ASRS/MAAS/MPATS/TTAS questions), not a fixture
│   ├── templates/base.html
│   └── templates/survey/
├── tasks/                              # app: cognitive tasks
│   ├── models.py, views.py, admin.py, urls.py
│   ├── migrations/
│   │   ├── 0001_initial.py            # DigitSpanResult
│   │   ├── 0002_sartresult.py          # SARTResult
│   │   └── 0003_verbalfluency*.py     # VerbalFluency models
│   ├── fixtures/                       # verbal_fluency.json
│   ├── static/tasks/
│   │   ├── digitspan.js
│   │   └── sart.js
│   └── templates/tasks/
│       ├── digitspan.html
│       └── sart.html
└── db.sqlite3                          # tracked in git
```

## Survey flow (session-based, no auth)
`/` (landing) → `/begin-survey/` (creates UUID, stores in session) → `/user-info/` → `/habits/` (if `is_watching_SFV=True`) → `/questionnaire/` → redirects to `/tasks/digitspan/`.

UUID flows through `request.session["survey_user_id"]`. No user login required.

## Cognitive tasks (tasks app)

Tasks store results via `ForeignKey` to `survey.User`:

| Task | URL | Route name | Model | View |
|------|-----|-----------|-------|------|
| Forward digit span | `/tasks/digitspan/` | `digit_span` | `DigitSpanResult` | `digit_span_view` |
| Digit span result | `/tasks/digitspan/result/` | `digit_span_result` | — | `digit_span_result_view` (POST) |
| SART | `/tasks/sart/` | `sart` | `SARTResult` | `sart_view` |
| SART result | `/tasks/sart/result/` | `sart_result` | — | `sart_result_view` (POST) |

Result views are `@csrf_exempt` + `@require_POST`, accept JSON body.

**Forward digit span** (`digitspan.js`): shows digits one at a time (800ms each, 200ms gap), user types them back. Span starts at 2 and increments on each round. POST with `{span, sequence, answer}` to `/tasks/digitspan/result/`. No automatic transition — rounds continue indefinitely.

**SART** (`sart.js`): 30 trials, 300ms digit display, 700ms gap. No-go digit = 3 (don't click). Progress bar shown during test. POST with `{sequence, trials, commission_errors, omission_errors, mean_reaction_time}` to `/tasks/sart/result/`.

**Verbal fluency** (models exist, no UI yet): `VerbalFluencyCategory`, `VerbalFluencyTrial`, `VerbalFluencyResult` models + migration 0003 + fixture `tasks/fixtures/verbal_fluency.json`. Admin registered. No views, URLs, templates, or static files wired in yet.

## App conventions
- **All user-facing strings are Polish** (model verbose names, form labels, templates, questions in ASRS and MAAS; MPATS and TTAS are in English)
- **Each form** sets `self.title`, `self.description`, `self.back_url` — template renders these via `survey/survey_base.html`
- **Crispy Forms** with `bootstrap5` template pack everywhere
- **QuestionnaireAnswerForm** dynamically builds a `ChoiceField` + `RadioSelect` per `Question` — not a ModelForm
- **No type hints** anywhere in the codebase

## Models (survey app)
`User` (custom, UUID pk, NOT auth user) has fields: `age`, `gender`, `education`, `is_watching_SFV`, `is_on_mobile` (auto-detected via `django-user-agents` middleware), `added_at`.
`Habits` (OTO to User) → fields: `daily_SFV_time`, `daily_SFV_sessions`, M2Ms to `SFVPlatform`, `ContentType`.
`Answer` (FK to User + Question, `unique_together`) — stores selected answer text, not a FK.

`Question` has M2M to `AnswerOption` (5 options: Nigdy=0 through Bardzo czesto=4). `Answer` stores the selected text, not a FK to AnswerOption.

## Models (tasks app)
`DigitSpanResult` (FK→survey.User, span, sequence, user_answer, correct, created_at).
`SARTResult` (FK→survey.User, commission_errors, omission_errors, mean_reaction_time, trials_data [JSONField], sequence, created_at).
`VerbalFluencyCategory` (name), `VerbalFluencyTrial` (letter, FK→category, time_limit), `VerbalFluencyResult` (FK→survey.User, trials_data [JSONField], created_at).

## Admin (tasks app)
All five task models registered. Check `admin.py` for `list_display`, `list_filter`, `search_fields`.

## Testing & CI
- **No test framework configured** — `tests.py` in both apps are empty stubs
- **No linters/formatters configured** (no ruff, black, mypy, isort)
- **No CI/CD** (no `.github/`)
- **No Docker**

## Fixtures
Pre-loaded via JSON in `survey/fixtures/`. After a fresh DB:
```
uv run src/manage.py loaddata survey/fixtures/answer_options.json survey/fixtures/sfvplatform.json survey/fixtures/contenttype.json survey/fixtures/questions.json
```
FK constraints handled via natural keys. For verbal fluency: `tasks/fixtures/verbal_fluency.json`.

## State
- **0 git commits** — repo has never been committed
- Migrations applied: survey `0001_initial`, tasks `0001_initial` through `0003_verbalfluency`
- `django-stubs` is installed but no actual type hints are used
