# Employee Agent — Requirements & Build Plan

Role-specialized LangGraph agent for **employee self-service**.  
Demo persona: **Neha Verma** (`neha.verma@novatech.example`).

The agent acts only on the **authenticated employee's own data**.  
Team approvals, org admin, and policy publishing belong to Manager / HR agents.

---

## Goals

- Let an employee complete HR self-service via chat (leave-first).
- Every agent action maps to a real service + Postgres tables.
- Enforce ownership in tools (employee_id from session, never from user text alone).

## Non-goals (v1 Employee Agent)

- Approve / reject leave for others
- View team attendance or other employees' balances
- Edit policies, assign tickets, change employment status
- Payroll, recruitment, performance

---

## Architecture (target)

```
User chat → FastAPI /chat → Employee LangGraph agent → Tools → Services → Postgres
```

**Agent state (minimum):** `messages`, `employee_id`, `organization_id`

**Graph style:** ReAct loop — LLM decides tools → execute tools → LLM final answer.

---

## Operations catalog

### Profile & directory

| Operation | Type | Tables / views |
|-----------|------|----------------|
| Get my profile | Read | `employees`, `v_employee_directory` |
| Who is my manager? | Read | `employees.manager_id` |
| Lookup colleague (public fields only) | Read | `v_employee_directory` |

### Leave (hero workflow)

| Operation | Type | Tables |
|-----------|------|--------|
| List leave types | Read | `leave_types` |
| Check my leave balance | Read | `leave_balances` |
| Apply for leave | Write | `leave_requests` (+ update `pending`) |
| List my leave requests | Read | `leave_requests` |
| Get leave request / approval trail | Read | `leave_requests`, `leave_approvals` |
| Cancel pending leave | Write | `leave_requests` → `cancelled` |

**Leave business rules**

- Only own requests
- `end_date >= start_date`
- Sufficient balance: `entitled - used - pending`
- Default `approver_id` = manager
- New requests start as `pending` (or `draft` if confirm-step is enabled)

### Attendance

| Operation | Type | Tables |
|-----------|------|--------|
| Attendance for a date / range | Read | `attendance_daily` |
| Holidays this year | Read | `holidays`, `holiday_calendars` |

### Helpdesk

| Operation | Type | Tables |
|-----------|------|--------|
| Create ticket | Write | `tickets` |
| List my tickets | Read | `tickets` |
| Comment on my ticket | Write | `ticket_comments` |

### Policies

| Operation | Type | Tables |
|-----------|------|--------|
| Ask / search policy questions | Read | `policies` (keyword first; RAG later) |

---

## Phased delivery

### Phase 1 — Services & REST (no agent yet)

Build the data layer the agent will call.

**Deliverables**

- SQLAlchemy models: employees, leave_types, leave_balances, leave_requests, leave_approvals
- Services:
  - `get_profile(employee_id)`
  - `get_leave_balances(employee_id, year)`
  - `list_leave_types(org_id)`
  - `apply_leave(...)`
  - `list_leave_requests(employee_id)`
  - `cancel_leave_request(employee_id, request_id)`
- REST endpoints (smoke / Swagger):
  - `GET /me`
  - `GET /leave/balances`
  - `GET /leave/types`
  - `POST /leave/requests`
  - `GET /leave/requests`
  - `POST /leave/requests/{id}/cancel`
- Simple identity for demos (header or fixed Neha employee id)

**Exit criteria:** All leave operations work via REST for Neha without the LLM.

---

### Phase 2 — Employee Agent MVP (leave chat)

**Tools (wrap Phase 1 services)**

| Tool | Purpose |
|------|---------|
| `get_my_profile` | Ground who is chatting |
| `get_leave_balances` | Remaining days by type |
| `list_leave_types` | Map “casual leave” → code |
| `apply_leave` | Create pending request |
| `list_my_leave_requests` | Status / history |
| `cancel_leave_request` | Cancel own pending only |

**Deliverables**

- LangChain tools + Employee system prompt
- LangGraph ReAct graph
- `POST /chat` (session = Neha for demos)
- Optional confirm step before `apply_leave`

**Demo success script**

1. “What’s my casual leave balance?”
2. “Apply CL for 10–11 Oct for personal work.”
3. “Show my leave requests.”
4. “Cancel the pending one for Oct.”

**Exit criteria:** That script completes end-to-end via chat; DB rows match.

---

### Phase 3 — Attendance + tickets

**New tools**

| Tool | Purpose |
|------|---------|
| `get_my_attendance` | Status for date / range |
| `list_holidays` | Upcoming holidays |
| `create_ticket` | Open HR/IT helpdesk ticket |
| `list_my_tickets` | Ticket status |
| `add_ticket_comment` | Follow-up on own ticket |

**Exit criteria:** Employee can ask attendance and raise a ticket in chat.

---

### Phase 4 — Policies + hardening

**Deliverables**

- `search_policies` (SQL/`ILIKE` or simple keyword)
- Later: RAG over `policies.content` with citations
- Audit log entries for write tools (`audit_logs`)
- Clear refusal when user asks for manager/HR-only actions
- Better auth (real user session → employee_id)

**Exit criteria:** Policy Q&A works; writes are audited; cross-employee access blocked.

---

## Suggested repo layout (when implementing)

```
app/
  agents/
    employee/
      graph.py          # LangGraph definition
      prompt.py         # System prompt
      tools.py          # Tool wrappers
  services/
    employees.py
    leave.py
    attendance.py
    tickets.py
    policies.py
  api/
    chat.py
    leave.py
    me.py
  models/
    ...
```

---

## MVP definition

**Employee Agent MVP = Phase 1 + Phase 2.**

Neha can check balance, apply leave, list status, and cancel pending leave entirely through chat.

---

## Open decisions (resolve before coding Phase 2)

1. Apply leave immediately vs draft + user confirm
2. Auth: fixed demo employee vs login
3. Chat API: single-turn only vs threaded conversation memory
```
