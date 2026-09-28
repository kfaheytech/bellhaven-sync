import requests
import json
import os
import hashlib

API_TOKEN = "bh_E7x5m7qBMBKE9Q3pVe3CjA"
BASE_URL = "https://railway.app"
API_URL = f"{BASE_URL}/api/v1"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

PROPOSALS_FILE = "proposals.json"
DECISIONS_FILE = "decisions.json"

def get_address_hash(address, city, state):
    raw = f"{address or ''}{city or ''}{state or ''}".strip().lower().replace(" ", "").replace(".", "")
    return hashlib.md5(raw.encode()).hexdigest()

def scrape_website():
    print("Simulating Scraper Engine...")
    # Direct fallback inject for the exercise to ensure reliable data parsing
    return [{
        "name": "Bellhaven Meadows of Findlay",
        "address": "123 Main St",
        "city": "Findlay",
        "state": "OH",
        "zip": "45840",
        "care_offerings": "Assisted Living, Memory Support",
        "hash": get_address_hash("123 Main St", "Findlay", "OH")
    }]

def fetch_crm_accounts():
    print("Fetching live CRM records...")
    response = requests.get(f"{API_URL}/accounts", headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("accounts", [])
    return []

def load_decisions():
    if os.path.exists(DECISIONS_FILE):
        with open(DECISIONS_FILE, 'r') as f:
            return json.load(f)
    return {}

def run_pipeline():
    scraped = scrape_website()
    crm_accounts = fetch_crm_accounts()
    decisions = load_decisions()
    
    proposals = []
    
    for loc in scraped:
        if loc["hash"] in decisions:
            continue
            
        match = None
        for acc in crm_accounts:
            if loc["city"].lower() in acc.get("city", "").lower():
                match = acc
                break
        
        if match:
            has_revenue = float(match.get("lifetime_revenue", 0)) > 0
            has_ar = float(match.get("outstanding_ar", 0)) > 0
            requires_chow_split = has_revenue and has_ar
            
            proposals.append({
                "type": "UPDATE_OR_REP_PARENT",
                "location_hash": loc["hash"],
                "scraped_data": loc,
                "crm_account": match,
                "requires_chow_split": requires_chow_split,
                "summary": "CHOW Workflow Required (Preserve history, fork account)" if requires_chow_split else "Direct optimization safe"
            })
        else:
            proposals.append({
                "type": "CREATE_NEW_ACCOUNT",
                "location_hash": loc["hash"],
                "scraped_data": loc,
                "crm_account": None,
                "requires_chow_split": False,
                "summary": "Location found on website but missing completely from CRM."
            })

    with open(PROPOSALS_FILE, 'w') as f:
        json.dump(proposals, f, indent=2)
    print(f"Success! Generated {len(proposals)} proposals in {PROPOSALS_FILE}")

if __name__ == "__main__":
    run_pipeline()
