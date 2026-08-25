# Exercise Progress Tracker — Your Sprint Guide

New to the course? Start at [course-overview.md](../course-overview.md).

Welcome. This is your roadmap for building the **Exercise Progress Tracker**—a gym you open in stages: first the building, then memberships, then the training floor, then a scoreboard, then a house coach. Members log **sessions**, see their own progress, and get AI-assisted feedback from _their_ history.

Work through the sprints in order. Each sprint’s **ticket backlog** tells you **what to build**, **why it matters**, and **which tickets to pick up** week by week.

## What you are building

| Layer    | Your tools                                                 |
| -------- | ---------------------------------------------------------- |
| Frontend | React, TypeScript, Vite                                    |
| Backend  | Python FastAPI                                             |
| Database | PostgreSQL                                                 |
| AI       | Ollama on your machine (later you can plug in a cloud API) |
| Ops      | Docker Compose and `.env` config                           |

```text
Your browser (React/TS)  --REST/JWT-->  FastAPI
                                            |
                              +-------------+-------------+
                              |             |             |
                         PostgreSQL    Analytics     AI provider
                                                     (Ollama → cloud later)
```

The ticket files under **`tickets/`** are your week-by-week work. Keep the current sprint’s backlog open while you implement.

## Your calendar (core = Sprints 1–5 → 14 weeks; Sprint 6 optional → +3 weeks)

Focus on **Sprints 1–5**. That is enough for a complete product demo (shell → auth → sessions/clone/plans/calendar → analytics → AI insights). **Sprint 6 is optional**—do it if you have time after Sprint 5 for testing, security docs, and deployment polish.

| Sprint       | Weeks | Tickets                                                              | You will focus on                              |
| ------------ | ----- | -------------------------------------------------------------------- | ---------------------------------------------- |
| 1            | 1–2   | [sprint-01-tickets.md](tickets/sprint-01-tickets.md)                 | Project foundation & scaffolding               |
| 2            | 3–5   | [sprint-02-tickets.md](tickets/sprint-02-tickets.md)                 | Auth, exercise catalog, SQLAdmin               |
| 3            | 6–8   | [sprint-03-tickets.md](tickets/sprint-03-tickets.md)                 | Sessions, clone, plans (`plan_id`), calendar & ownership |
| 4            | 9–11  | [sprint-04-tickets.md](tickets/sprint-04-tickets.md)                 | Analytics & progress charts                    |
| 5            | 12–14 | [sprint-05-tickets.md](tickets/sprint-05-tickets.md)                 | AI insights with Ollama                        |
| 6 (optional) | 15–17 | [sprint-06-tickets.md](tickets/sprint-06-tickets.md)                 | Testing, security & deployment (if time)       |

```text
Core:     Sprint 1 → Sprint 2 → Sprint 3 → Sprint 4 → Sprint 5
Optional:                                              └→ Sprint 6 (if time)
```

## How to use tickets

Detailed ticket backlogs live in **`docs/sprints/tickets/`** (one file per sprint).

| Sprint | Tickets file                                                                   |
| ------ | ------------------------------------------------------------------------------ |
| 1      | [tickets/sprint-01-tickets.md](tickets/sprint-01-tickets.md)                   |
| 2      | [tickets/sprint-02-tickets.md](tickets/sprint-02-tickets.md)                   |
| 3      | [tickets/sprint-03-tickets.md](tickets/sprint-03-tickets.md)                   |
| 4      | [tickets/sprint-04-tickets.md](tickets/sprint-04-tickets.md)                   |
| 5      | [tickets/sprint-05-tickets.md](tickets/sprint-05-tickets.md)                   |
| 6      | [tickets/sprint-06-tickets.md](tickets/sprint-06-tickets.md) (optional sprint) |

Copy tickets into GitHub Issues, GitLab, Azure Boards, or your course board if that helps your team.

| Field      | Meaning for you                                                                                                                                           |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ID         | `S{sprint}-{number}` — e.g. `S1-03`, `S5-07`                                                                                                              |
| Stretch ID | `S{sprint}-S{n}` — optional extras, e.g. `S1-S1`                                                                                                          |
| Type       | `feature`, `chore`, `docs`, or `test`                                                                                                                     |
| Week       | Week inside that sprint (Sprint 1 has weeks 1–2; Sprints 2–5 have weeks 1–3; Sprint 6 optional)                                                           |
| Priority   | **Must** (needed to finish that sprint), **Should** (do unless blocked), **Stretch** (nice to have). Sprint 6 Must items apply only if you take Sprint 6. |
| Estimate   | S / M / L — rough size only                                                                                                                               |

Each ticket expands on **New here** (concept + **Docs & tutorials**), **Your task**, **Instructions**, **Stay in scope**, **hints**, **acceptance criteria**, **suggested paths**, and **Commit**. Prefer one commit per ticket (or a tightly related pair). Put the ID in the commit message and PR title, e.g. `S3-10: enforce session ownership`.

At the end of each sprint, copy that sprint’s **report template** from [templates/](templates/README.md) to `docs/reports/sprint-0N.md` and fill it. That is how you document the development process for graders.

## Target folder layout

```text
exercise-tracker/
  README.md
  docker-compose.yml
  .env.example
  frontend/
  backend/
    app/
      main.py            # composition root
      admin.py           # SQLAdmin (presentation exception)
      api/               # routers — HTTP only
      schemas/           # Pydantic DTOs
      services/          # business logic / use cases
      repositories/      # SQLAlchemy persistence
      models/            # ORM entities
      db/                # engine, session, Base, init hook
      core/              # settings, later security
  docs/
    sprints/          ← you are here
      tickets/        ← expanded ticket backlogs (one file per sprint)
      templates/      ← sprint report templates (copy, do not fill here)
    reports/          ← your filled reports under docs/reports/ (e.g. sprint-01.md)
    security.md       ← optional: write in Sprint 6
    deployment.md     ← optional: write in Sprint 6
```

**Backend layering:** call inward only — `api` → `services` → `repositories` → `models`/`db`. Routers should not contain business rules or raw queries; services should not import FastAPI.

## Working together

- Use a branch per week or ticket, e.g. `sprint-01/compose-api`.
- After each ticket, create a **new commit** with the ticket ID in the message (see **Commit** on the ticket).
- Open a PR at the end of the week with a short note: what to run and what to click.
- Never commit real secrets. Keep `.env` gitignored and update `.env.example` when you add variables.
- When the sprint is done, fill [that sprint’s report template](templates/README.md) and commit it under `docs/reports/`.

## Starting the app (from Sprint 1 onward)

```bash
cp .env.example .env
docker compose up --build
```

You will usually have `db` (PostgreSQL), `api` (FastAPI), `web` (frontend), and later an optional `ollama` profile (Sprint 5).

## Auth (from Sprint 2)

You will store the JWT in `localStorage` and send `Authorization: Bearer <token>`. That is easy to debug while you learn. If you take optional Sprint 6, document the XSS trade-off in `docs/security.md`.

## When is a sprint “done”?

Check all of these before you move on:

1. **You can demo it** — a classmate can follow your “Done when” steps without secret knowledge.
2. **It starts** — backend and frontend run the way your README describes.
3. **Tickets** — every **Must** ticket is done, or you have written down why it was deferred.
4. **Docs** — you updated the root `README.md` if startup steps changed.
5. **Sprint report** — you copied that sprint’s template from [templates/](templates/README.md) to `docs/reports/` and filled it.
6. **Ready for next** — prerequisites for the next _required_ sprint’s tickets are met (after Sprint 5 you are done with the core course; Sprint 6 is optional).

## Skills you will practice

| Sprint       | Weeks | Skills                                                   |
| ------------ | ----- | -------------------------------------------------------- |
| 1            | 1–2   | Tooling, Docker, monorepo, layered API/UI shells         |
| 2            | 3–5   | DB design, unit catalog, SQLAdmin, auth, security basics |
| 3            | 6–8   | Sessions, clone, plans (`plan_id`), calendar, authorization |
| 4            | 9–11  | Python analytics, charts, unit tests                     |
| 5            | 12–14 | Local AI, abstractions, AI UX                            |
| 6 (optional) | 15–17 | Testing, security review, deployment docs                |

## Start here

Open **[Sprint 1 tickets](tickets/sprint-01-tickets.md)** and pick up the Week 1 work.
