---
type: plan
role: verification-packet
status: draft
project: armonia-dashboard
feature: workshop-roster-checkin
date: 2026-10-25
tags: [qa, verification-packet, test-data, blind-testing]
---

# Verification Packet: Group Workshop Roster Quick Check-in

> **Notice to Independent QA Reviewer:** This packet contains **all** instructions, test personas, and expected observable criteria needed to verify the feature. You must evaluate the running application *without* inspecting the pull request discussion, implementation source code, or the implementer's self-audit.

---

## 1. Frozen Environment & Runtime Configuration

Prior to executing test scenarios, verify that both services are running on the specified commits:

| Component | Target Directory | Verified Commit Hash | Start Command | Active Port |
| :--- | :--- | :--- | :--- | :--- |
| **Backend API** | `armonia/armonia-api` | `d9c86e27d926bab3287857ccc9b53ec4fbcec91b` | `DATABASE_URL=file:test_armonia.db uv run python -m uvicorn app.main:app --port 8000` | `http://localhost:8000` |
| **Frontend UI** | `armonia/armonia-dashboard` | PR Branch (`feat/anne/workshop-roster`) | `pnpm exec vp dev --port 5173` | `http://localhost:5173` |

---

## 2. Tested & Verified Test Database Seed Script with Preflight Assertions

Run this command inside `armonia-api` using `uv run python`. It creates a clean disposable SQLite database (`test_armonia.db`), initializes default services, seeds the exact test records required for today's date, and **formally asserts all four preflight conditions** before completing:

```bash
cd /home/kiskaadee/Projects/active/armonia/armonia-api && uv run python -c "
import os, asyncio
from datetime import datetime, UTC
from zoneinfo import ZoneInfo
from pathlib import Path

# Deterministic absolute path anchoring
abs_db_path = (Path.cwd() / 'test_armonia.db').resolve()
assert abs_db_path.name.startswith('test_') and abs_db_path.name != 'local.db', 'Safety failure: refusal to touch non-test database'
if abs_db_path.exists():
    abs_db_path.unlink()

os.environ['DATABASE_URL'] = f'file:{abs_db_path}'

from app.core.config import settings
settings.database_url = f'file:{abs_db_path}'
from app.db.init_db import init_schema_and_seed
from app.db.database import get_db
from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import create_session_token

async def seed_and_verify():
    # 1. Initialize schema and default services
    await init_schema_and_seed()
    
    async with get_db() as client:
        # Preflight 1: Assert service exists with expected capacity of 15
        res = await client.execute('SELECT id, name, price_mxn, max_capacity FROM services WHERE slug = \"circulo-cacao-presencial\" LIMIT 1;')
        assert res.rows, 'Preflight 1 Failed: circulo-cacao-presencial service not found!'
        cacao_id, cacao_name, price_mxn, max_capacity = res.rows[0]
        assert max_capacity == 15, f'Preflight 1 Failed: Expected capacity 15, got {max_capacity}'
        
        # Preflight 2: Calculate today's session instant at 18:00
        tz = ZoneInfo(settings.business_timezone)
        today = datetime.now(tz).date()
        today_str = today.isoformat()
        session_dt = datetime(today.year, today.month, today.day, 18, 0, 0, tzinfo=tz).astimezone(UTC).isoformat()
        now = datetime.now(UTC).isoformat()
        
        # Insert Elena Gómez (Prepaid SPEI: RESERVED + ACKNOWLEDGED)
        client_elena = 'c1111111-1111-1111-1111-111111111111'
        booking_elena = 'b1111111-1111-1111-1111-111111111111'
        await client.execute('INSERT OR REPLACE INTO clients (id, full_name, phone_whatsapp, email) VALUES (?, ?, ?, ?);',
                             [client_elena, 'Elena Gómez', '525511112222', 'elena@example.com'])
        await client.execute('''
            INSERT OR REPLACE INTO bookings (
                id, booking_code, service_id, client_id, scheduled_at, duration_minutes, buffer_minutes,
                booking_status, payment_arrangement, payment_status, amount_mxn, created_at
            ) VALUES (?, ?, ?, ?, ?, 120, 0, 'RESERVED', 'PREPAID_DEFAULT', 'ACKNOWLEDGED', ?, ?);
        ''', [booking_elena, 'ADS-1001', cacao_id, client_elena, session_dt, price_mxn, now])
        
        # Insert Carlos Méndez (Unpaid: RESERVED + AWAITING_ACKNOWLEDGMENT)
        client_carlos = 'c2222222-2222-2222-2222-222222222222'
        booking_carlos = 'b2222222-2222-2222-2222-222222222222'
        await client.execute('INSERT OR REPLACE INTO clients (id, full_name, phone_whatsapp, email) VALUES (?, ?, ?, ?);',
                             [client_carlos, 'Carlos Méndez', '525533334444', 'carlos@example.com'])
        await client.execute('''
            INSERT OR REPLACE INTO bookings (
                id, booking_code, service_id, client_id, scheduled_at, duration_minutes, buffer_minutes,
                booking_status, payment_arrangement, payment_status, amount_mxn, created_at
            ) VALUES (?, ?, ?, ?, ?, 120, 0, 'RESERVED', 'PREPAID_DEFAULT', 'AWAITING_ACKNOWLEDGMENT', ?, ?);
        ''', [booking_carlos, 'ADS-1002', cacao_id, client_carlos, session_dt, price_mxn, now])

    # Preflight 3: Endpoint level validation (assert endpoint returns exact expected session & attendees)
    tc = TestClient(app)
    headers = {'Authorization': f'Bearer {create_session_token(\"asistente@armoniadelser.mx\")}'}
    r = tc.get(f'/rosters?date_from={today_str}&date_to={today_str}', headers=headers)
    assert r.status_code == 200, f'Preflight 3 Failed: GET /rosters returned {r.status_code}'
    data = r.json()
    assert len(data) == 1, f'Preflight 3 Failed: Expected 1 session, got {len(data)}'
    sess = data[0]
    assert sess['occupied_count'] == 2 and sess['attended_count'] == 0, 'Preflight 3 Failed: Initial counts mismatch'
    codes = {att['booking_code'] for att in sess['attendees']}
    assert codes == {'ADS-1001', 'ADS-1002'}, f'Preflight 3 Failed: Missing expected codes {codes}'
    
    # Preflight 4: File existence & non-empty database target
    assert abs_db_path.exists() and abs_db_path.stat().st_size > 0, 'Preflight 4 Failed: Database file missing or empty'
    
    print('✅ Preflight assertions passed: 100% verified test database ready at', abs_db_path)

asyncio.run(seed_and_verify())
"
```

---

## 3. Pre-Configured Test Attendee Personas

| Attendee Persona | Initial Persisted State | Expected Initial UI Rendering | Expected Post-Action State |
| :--- | :--- | :--- | :--- |
| **Elena Gómez** (`ADS-1001`) | `booking_status: "RESERVED"`, `payment_status: "ACKNOWLEDGED"`, `attended: false` | Badge: `REGISTRADO`<br/>Badge: `PAGADO` (Green)<br/>Action: "Registrar Asistencia" | After check-in: Badge updates to `ASISTIÓ`. Counter increments to `1 presente`. |
| **Carlos Méndez** (`ADS-1002`) | `booking_status: "RESERVED"`, `payment_status: "AWAITING_ACKNOWLEDGMENT"`, `attended: false` | Badge: `REGISTRADO`<br/>Badge: `PENDIENTE` (Amber)<br/>Action: Check-in + "Cobro efectivo" | After cash check-in: Badge updates to `ASISTIÓ` AND `PAGADO`. Counter increments. |
| **Walk-in: Lucía Vega** | Not in database initially | Not present in list | After registration: Appears in list as `ASISTIÓ` and `PAGADO`. Occupancy becomes `3 / 15`. |

---

## 4. Test Execution Scenarios & Concrete Pass/Fail Criteria

### Scenario 1: Navigation, Tab Hash & Capacity Overview (`AC-1`)
1. Open `http://localhost:5173` in a desktop browser.
2. Click the "Talleres" navigation button in the top navigation bar.
3. **Pass Criteria:**
   - [ ] URL updates to `http://localhost:5173/#rosters`.
   - [ ] "Talleres" tab button reflects active state (`aria-selected="true"`).
   - [ ] Session card for "Círculo de Cacao (Presencial)" renders with time 18:00.
   - [ ] Capacity counter displays exactly: `Ocupación: 2 / 15 (0 presentes)`.

### Scenario 2: Attendee Roster Display & Status Badges (`AC-2`)
1. Inspect the attendee table/list for the active workshop.
2. **Pass Criteria:**
   - [ ] Elena Gómez is listed with booking code `ADS-1001`, status `REGISTRADO`, and payment pill `PAGADO`.
   - [ ] Carlos Méndez is listed with booking code `ADS-1002`, status `REGISTRADO`, and payment pill `PENDIENTE`.
   - [ ] Both rows display a clickable WhatsApp link (`wa.me/525511112222` and `wa.me/525533334444`).

### Scenario 3: Pre-paid Attendee Check-in & Persistence Verification (`AC-3`)
1. On Elena Gómez's row (`ADS-1001`), tap "Registrar Asistencia".
2. **Pass Criteria (UI & Persistence):**
   - [ ] Network inspector shows `POST /rosters/quick-checkin` returned HTTP 200 with payload `{"booking_id": "...", "paid_cash": false}`.
   - [ ] Elena's status badge updates from `REGISTRADO` to `ASISTIÓ`.
   - [ ] Capacity summary updates to `Ocupación: 2 / 15 (1 presentes)`.
   - [ ] An accessible toast announces: *"Asistencia registrada con éxito."*
   - [ ] **Persistence Proof:** Refresh the browser page (`F5`). Upon reload, Elena still renders as `ASISTIÓ` and capacity remains `1 presente`.

### Scenario 4: Cash Check-in & Payment Status Transition (`AC-4`)
1. On Carlos Méndez's row (`ADS-1002`), trigger check-in with the "Cobro en efectivo recibido" checkbox checked.
2. **Pass Criteria (UI & Persistence):**
   - [ ] Network inspector shows `POST /rosters/quick-checkin` returned HTTP 200 with `paid_cash: true`.
   - [ ] Carlos's status badge updates to `ASISTIÓ`.
   - [ ] Carlos's payment pill transitions from `PENDIENTE` to `PAGADO`.
   - [ ] Capacity summary updates to `Ocupación: 2 / 15 (2 presentes)`.
   - [ ] **Persistence Proof:** Refresh the browser page (`F5`). Carlos renders with both `ASISTIÓ` and `PAGADO`.

### Scenario 5: Walk-In Registration & Double-Submission Prevention (`AC-5`)
1. Click the "＋ Registrar Asistente Sin Cita" button.
2. In the modal:
   - Full Name: `Lucía Vega`
   - Phone: `525598765432`
   - Cash toggle: confirm it defaults to **checked (`true`)**.
3. **Double-Submission Test**: Rapidly click "Registrar y Marcar Asistencia" twice in succession.
4. **Pass Criteria:**
   - [ ] Submit button disables immediately while the request is in flight.
   - [ ] Exactly **one** walk-in record is created (network inspector shows only one successful registration; second click is ignored or blocked).
   - [ ] Modal closes upon HTTP 200.
   - [ ] Lucía Vega appears in the active attendee list with `ASISTIÓ` and `PAGADO`.
   - [ ] Capacity counter updates to exactly `Ocupación: 3 / 15 (3 presentes)` (NOT `4 / 15`).
   - [ ] **Persistence Proof:** Refresh the browser (`F5`). Exactly one Lucía Vega record remains persisted in the roster.

### Scenario 6: 409 Conflict Disambiguation & Reconciliation
1. **Case 6A (Already-Checked-In Idempotency)**: Trigger a duplicate check-in request via network replay or rapid re-tap for an already checked-in attendee (`ADS-1001`).
   - **Pass Criteria:**
     - [ ] Backend returns `HTTP 409 Conflict` (`"This attendee has already checked in."`).
     - [ ] UI catches the 409, reconciles state, displays informative feedback (*"El asistente ya contaba con asistencia registrada"*), and ensures row reflects `ASISTIÓ` without unhandled application crash.
2. **Case 6B (Capacity Reached Conflict)**: When submitting a walk-in to a session at max capacity:
   - **Pass Criteria:**
     - [ ] Backend returns `HTTP 409 Conflict` (`"El taller ha alcanzado su cupo máximo"`).
     - [ ] UI displays explicit capacity error alert; modal form data is preserved; row is **not** added to list.

### Scenario 7: Failed Roster Fetch & Actionable Retry (`AC-6`)
1. Temporarily stop the backend API process (`Ctrl+C` on uvicorn).
2. Switch dates or refresh the `#rosters` view.
3. **Pass Criteria:**
   - [ ] Error banner renders: *"No se pudieron cargar los talleres. Verifica tu conexión."*
   - [ ] A visible "Reintentar" button is displayed.
4. Restart the backend API process.
5. Click "Reintentar".
6. **Pass Criteria:**
   - [ ] Roster reloads successfully without needing a browser reload.

### Scenario 8: Mobile Ergonomics & Accessibility Tree (`AC-7`)
1. Switch browser DevTools to Mobile Emulation: **375 x 812 px** (iPhone SE/X).
2. **Pass Criteria:**
   - [ ] Zero horizontal scroll overflow on the table/cards.
   - [ ] All check-in buttons, toggles, and modal inputs have minimum touch bounding boxes of **44 x 44 px**.
3. Navigate the view using only the keyboard (`Tab` and `Shift+Tab`).
4. **Pass Criteria:**
   - [ ] Focus indicator is visibly highlighted on every active button and input.
   - [ ] Toast notification container possesses `role="status"` and `aria-live="polite"`.

---

## 5. Evidence Capture & Scorecard Deliverable

The QA Specialist must produce `qa-evidence-scorecard.md` containing:
1. Formal table checking every criterion (`AC-1` to `AC-7`, Scenarios 1 to 8) with verdict: `PASS`, `FAIL`, or `BLOCKED`.
2. Captured screenshots attached:
   - Desktop initial roster view.
   - Mobile 375px view showing touch targets.
   - Post-check-in state showing updated counter.
   - Walk-in modal open state.
3. Browser console log confirming zero uncaught JavaScript exceptions.
4. If any test fails, record: Exact visual element, HTTP status, and response JSON payload.

---

## 6. Reset & Cleanup Procedure

To restore the test environment between verification passes:
```bash
# 1. Stop backend API (Ctrl+C)
# 2. Delete test database file
rm -f /home/kiskaadee/Projects/active/armonia/armonia-api/test_armonia.db
# 3. Re-run the seed script from Section 2
# 4. Restart backend API
```
