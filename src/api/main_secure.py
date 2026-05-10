import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, field_validator
from .auth import router as auth_router
from .security import get_current_user, require_admin
from security.rate_limiter import limiter, rate_limit_exceeded_handler
from security.encryption import encrypt_value, decrypt_value
import json
import os

app = FastAPI(title="Small Business Loan API")

# Rate limiter setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS — only allow your frontend, not everyone
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

DATA_FILE = "data/applications.json"


class LoanRequest(BaseModel):
    business_name: str
    annual_income: float
    credit_score: int
    requested_amount: float

    @field_validator("credit_score")
    @classmethod
    def credit_score_must_be_valid(cls, v):
        if v < 300 or v > 850:
            raise ValueError("Credit score must be between 300 and 850")
        return v

    @field_validator("annual_income", "requested_amount")
    @classmethod
    def must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Value must be greater than 0")
        return v

    @field_validator("business_name")
    @classmethod
    def name_must_be_clean(cls, v):
        if len(v) < 2 or len(v) > 100:
            raise ValueError("Business name must be between 2 and 100 characters")
        return v.strip()


@app.get("/")
def read_root():
    return {"status": "Active", "version": "2.0", "system": "Nova Industries AI"}


@app.post("/apply")
@limiter.limit("5/minute")
def apply_for_loan(
    request: Request,
    loan: LoanRequest,
    current_user: dict = Depends(get_current_user)
):
    is_approved = loan.credit_score > 650 and loan.annual_income > (loan.requested_amount * 0.2)
    risk_score = 0.15 if is_approved else 0.85

    result = {
        "business_name": loan.business_name,
        "annual_income": encrypt_value(str(loan.annual_income)),
        "credit_score": encrypt_value(str(loan.credit_score)),
        "requested_amount": encrypt_value(str(loan.requested_amount)),
        "decision": "Approved" if is_approved else "Rejected",
        "risk_score": risk_score,
        "submitted_by": current_user["email"]
    }

    save_to_json(result)
    return {
        "business_name": loan.business_name,
        "decision": result["decision"],
        "risk_score": risk_score,
        "submitted_by": current_user["email"]
    }


@app.get("/applications")
def get_all_applications(
    current_user: dict = Depends(require_admin)
):
    if not os.path.exists(DATA_FILE):
        return {"total_count": 0, "applications": []}
    with open(DATA_FILE, "r") as file:
        try:
            data = json.load(file)
            return {"total_count": len(data), "applications": data}
        except json.JSONDecodeError:
            return {"total_count": 0, "applications": []}


@app.get("/applications/{name}")
def get_application_by_name(
    name: str,
    current_user: dict = Depends(get_current_user)
):
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail="No applications database found")
    with open(DATA_FILE, "r") as file:
        data = json.load(file)
    match = next((item for item in data if item["business_name"].lower() == name.lower()), None)
    if match:
        return match
    raise HTTPException(status_code=404, detail="Business application not found")


@app.delete("/applications/{name}")
def delete_application(
    name: str,
    current_user: dict = Depends(require_admin)
):
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail="No data file found")
    with open(DATA_FILE, "r") as file:
        data = json.load(file)
    original_count = len(data)
    updated_data = [item for item in data if item["business_name"].lower() != name.lower()]
    if len(updated_data) == original_count:
        raise HTTPException(status_code=404, detail="Business not found to delete")
    with open(DATA_FILE, "w") as file:
        json.dump(updated_data, file, indent=4)
    return {"message": f"Successfully deleted application for {name}"}


def save_to_json(new_data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    data_list = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            try:
                data_list = json.load(file)
            except json.JSONDecodeError:
                data_list = []
    data_list.append(new_data)
    with open(DATA_FILE, "w") as file:
        json.dump(data_list, file, indent=4)


app.include_router(auth_router)