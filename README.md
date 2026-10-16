# InsureFlow — AI-Powered Verified Embedded Insurance

InsureFlow is an embedded-insurance web application demonstration for PS-009: Embedded Insurance. It demonstrates the main story from the PPT: local PII masking, mock e-KYC, insurer licence validation, policy comparison, clause-grounded explanations, idempotent checkout, one-time demo policy issuance, and an audit trail.

## What's included

- `frontend/`: React + Vite user interface, Lucide icons and Framer Motion.
- `backend/`: FastAPI REST API, mock insurer registry, sample policy clauses, idempotency key handling, and audit endpoints.
- `backend/schema.sql`: MySQL 8.0 reference schema for a production-oriented implementation.
- `start-demo.bat`: starts the frontend and backend in separate terminal windows on Windows.
- `start-demo.sh`: starts the frontend and backend on macOS/Linux.

## Run on Windows

1. Install **Node.js LTS** and **Python 3.10+**.
2. Extract this ZIP file.
3. Double-click `start-demo.bat` (or run it from Command Prompt).
4. Open `http://localhost:5173` in your browser.
5. Optional API docs: `http://127.0.0.1:8000/docs`.

If Windows blocks the script, open a terminal in the extracted project folder and run:

```powershell
cd backend
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

## Run on macOS/Linux

```bash
chmod +x start-demo.sh
./start-demo.sh
```

Or start each service separately:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

## Demo walkthrough

1. **Overview:** Review the laptop invoice and identity step.
2. **Verify identity:** Use the demo button. It simulates e-KYC; it does not contact a real provider.
3. **Compare policies:** Select SafePlus or ShieldCare and ask “Does it cover water damage?” The answer comes from the sample clause text.
4. **Privacy Shield:** Try the masking demo with sample email/phone/ID-like values.
5. **Checkout:** Select a verified plan, tick consent, and continue. A simulated payment creates one demo certificate. The inactive QuickGuard insurer is blocked.
6. **Retry behavior:** The backend's `/api/checkout` endpoint requires an `Idempotency-Key`; repeating the same key returns the same policy instead of creating a duplicate.
7. **Policy vault / Audit trail:** View and download the sample certificate, or inspect session events.

## API endpoints

- `GET /health`
- `GET /api/insurers`
- `GET /api/plans`
- `POST /api/verify`
- `POST /api/explain`
- `POST /api/checkout` (requires `Idempotency-Key` header)
- `GET /api/policies`
- `GET /api/audit`

## Important prototype limitations

- This is a **demo prototype**, not a live insurance product. Insurer registry, e-KYC and payment are mocked; no actual IRDAI registry, e-KYC gateway, Razorpay/Stripe, or external LLM is connected.
- Policy explanations use bundled sample clauses (grounded demo logic), not an external RAG pipeline.
- Frontend demo checkout uses browser state for a smooth presentation. The FastAPI API separately demonstrates the backend idempotency flow.
- The backend currently stores demo records in memory; restarting the server clears them. `schema.sql` is a reference schema, not yet wired to MySQL.
- Regex-based PII masking is illustrative, not a guarantee of complete privacy protection. Do not enter real identity details.
- No real policy is issued and the generated certificate has no legal or insurance value.

## Stack from the PPT

React + Vite, Tailwind-inspired responsive styling, Lucide icons, Framer Motion, Python FastAPI, mock OAuth/e-KYC and insurer verification, idempotency middleware pattern, MySQL 8.0 reference schema, policy-clause grounded explanation demo, and simulated payment sandbox.
