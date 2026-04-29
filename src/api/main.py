import json
import os
from fastapi import FastAPI, HTTPException  # Fixed import (FastAPI uses its own HTTPException)
from pydantic import BaseModel

app = FastAPI(title="Small Business Loan API")

# Path updated to align with your project structure
DATA_FILE = "data/applications.json"


class LoanRequest(BaseModel):
    business_name: str
    annual_income: float
    credit_score: int
    requested_amount: float


@app.get("/")
def read_root():
    return {"status": "Active", "version": "1.1", "system": "Nova Industries AI"}


@app.post("/apply")
def apply_for_loan(request: LoanRequest):
    # Decision logic based on business criteria
    is_approved = request.credit_score > 650 and request.annual_income > (request.requested_amount * 0.2)
    risk_score = 0.15 if is_approved else 0.85

    result = {
        "business_name": request.business_name,
        "annual_income": request.annual_income,
        "credit_score": request.credit_score,
        "requested_amount": request.requested_amount,
        "decision": "Approved" if is_approved else "Rejected",
        "risk_score": risk_score
    }

    save_to_json(result)
    return result


@app.get("/applications")
def get_all_applications():
    if not os.path.exists(DATA_FILE):
        return {"total_count": 0, "applications": []}
    with open(DATA_FILE, "r") as file:
        try:
            data = json.load(file)
            return {"total_count": len(data), "applications": data}
        except json.JSONDecodeError:
            return {"total_count": 0, "applications": []}


@app.get("/applications/{name}")
def get_application_by_name(name: str):
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail="No applications database found")

    with open(DATA_FILE, "r") as file:
        data = json.load(file)

    match = next((item for item in data if item["business_name"].lower() == name.lower()), None)

    if match:
        return match
    raise HTTPException(status_code=404, detail="Business application not found")


@app.delete("/applications/{name}")
def delete_application(name: str):
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
    # Ensure data directory exists
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