"""InsureFlow demo API. Mock registry and payment only; not for production use."""
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import re, uuid

app = FastAPI(title="InsureFlow Demo API", version="1.0.0", description="Prototype APIs for verified embedded insurance")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

INSURERS = [
 {"id":"aster","name":"Aster General Insurance","licence":"IRDAI-MOCK-1042","active":True},
 {"id":"northstar","name":"Northstar Assurance","licence":"IRDAI-MOCK-2088","active":True},
 {"id":"quickguard","name":"QuickGuard Demo Insurance","licence":"IRDAI-MOCK-0000","active":False},
]
PLANS = [
 {"id":"safeplus","name":"SafePlus Device Protect","insurer_id":"aster","price":799,"coverage":50000,"duration":"1 year","includes":["Accidental damage","Liquid / water damage","Mechanical breakdown"],"excludes":["Intentional damage","Cosmetic scratches only"],"clauses":[{"ref":"Clause 4.2","topic":"water damage","text":"Accidental liquid ingress is covered after the applicable deductible, subject to inspection."},{"ref":"Clause 7.1","topic":"exclusions","text":"Intentional damage and cosmetic-only scratches are excluded."}]},
 {"id":"shieldcare","name":"ShieldCare Essentials","insurer_id":"northstar","price":499,"coverage":30000,"duration":"1 year","includes":["Accidental screen damage","Electrical failure"],"excludes":["Liquid / water damage","Theft without police report"],"clauses":[{"ref":"Clause 5.3","topic":"water damage","text":"Damage caused by liquid ingress is excluded from this plan."},{"ref":"Clause 3.1","topic":"screen damage","text":"Accidental screen damage is covered up to the insured limit."}]},
 {"id":"quickguard","name":"QuickGuard Premium","insurer_id":"quickguard","price":599,"coverage":40000,"duration":"1 year","includes":["Accidental damage"],"excludes":["Water damage"],"clauses":[{"ref":"Clause 5.0","topic":"water damage","text":"Water damage is excluded."}]},
]
issued_by_key = {}
audit = []
def log(event, status="OK"):
 audit.insert(0,{"id":len(audit)+1,"timestamp":datetime.now(timezone.utc).isoformat(),"event":event,"status":status})
def mask_pii(value: str) -> str:
 value = re.sub(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", "[EMAIL_MASKED]", value, flags=re.I)
 value = re.sub(r"\b\d{10}\b", "[PHONE_MASKED]", value)
 return re.sub(r"\b\d{12}\b", "[ID_MASKED]", value)
class VerifyRequest(BaseModel):
 email: str = ""
 phone: str = ""
 demo_consent: bool = False
class ExplainRequest(BaseModel):
 plan_id: str
 question: str = Field(min_length=1, max_length=500)
class CheckoutRequest(BaseModel):
 plan_id: str
 customer_token: str
 consent: bool
 payment_status: str = "confirmed"

@app.get("/")
def root(): return {"service":"InsureFlow Demo API","mode":"mock","docs":"/docs"}
@app.get("/health")
def health(): return {"status":"ok","mode":"mock-demo"}
@app.get("/api/insurers")
def insurers(): return [{**i,"status":"ACTIVE" if i["active"] else "INACTIVE","verified":i["active"]} for i in INSURERS]
@app.get("/api/plans")
def plans():
 result=[]
 for p in PLANS:
  insurer=next(i for i in INSURERS if i["id"]==p["insurer_id"])
  result.append({**p,"insurer":insurer["name"],"licence":insurer["licence"],"licence_active":insurer["active"],"checkout_allowed":insurer["active"]})
 return result
@app.post("/api/verify")
def verify(body: VerifyRequest):
 # Demo e-KYC: do not submit actual identity documents or sensitive identifiers.
 masked={"email":mask_pii(body.email),"phone":mask_pii(body.phone)}
 log("Demo e-KYC check; local/client data should be masked", "MASKED")
 return {"verified":True,"mode":"mock","message":"Demo identity status verified; no real e-KYC gateway was called.","masked_preview":masked,"customer_token":"cust_demo_"+uuid.uuid4().hex[:10]}
@app.post("/api/explain")
def explain(body: ExplainRequest):
 p=next((p for p in PLANS if p["id"]==body.plan_id),None)
 if not p: raise HTTPException(404,"Unknown plan")
 q=mask_pii(body.question).lower()
 match=next((c for c in p["clauses"] if c["topic"] in q or any(word in q for word in c["topic"].split())),None)
 if match: answer=match["text"]; ref=match["ref"]
 else: answer="The demo policy library has no matching clause for this question. Review the full policy wording before deciding."; ref="No matching sample clause"
 log("Grounded policy explanation generated from mock clauses", "MASKED")
 return {"answer":answer,"source":ref,"grounded":True,"mode":"mock-policy-library"}
@app.post("/api/checkout")
def checkout(body: CheckoutRequest, idempotency_key: Optional[str]=Header(default=None, alias="Idempotency-Key")):
 if not idempotency_key or len(idempotency_key)<8: raise HTTPException(400,"A unique Idempotency-Key header is required")
 if idempotency_key in issued_by_key:
  log("Duplicate checkout retry returned existing policy", "DEDUPED")
  return {**issued_by_key[idempotency_key],"idempotent_replay":True}
 p=next((p for p in PLANS if p["id"]==body.plan_id),None)
 if not p: raise HTTPException(404,"Unknown plan")
 insurer=next(i for i in INSURERS if i["id"]==p["insurer_id"])
 if not insurer["active"]: log("Checkout blocked: inactive insurer licence", "BLOCKED"); raise HTTPException(403,"Insurer licence is inactive; checkout blocked")
 if not body.consent: raise HTTPException(400,"Customer consent is required")
 if not body.customer_token.startswith("cust_demo_"): raise HTTPException(400,"Demo customer token required")
 if body.payment_status!="confirmed": raise HTTPException(402,"Policy cannot be issued before payment confirmation")
 policy={"certificate_id":"IF-"+uuid.uuid4().hex[:8].upper(),"plan_id":p["id"],"plan":p["name"],"insurer":insurer["name"],"premium":p["price"],"coverage":p["coverage"],"transaction_key":idempotency_key,"issued_at":datetime.now(timezone.utc).isoformat(),"demo_only":True,"idempotent_replay":False}
 issued_by_key[idempotency_key]=policy
 log("Simulated payment confirmed", "OK"); log("Demo policy issued exactly once", "OK")
 return policy
@app.get("/api/policies")
def policies(): return list(issued_by_key.values())
@app.get("/api/audit")
def get_audit(): return audit
