import streamlit as st
import json
import os
import requests

API_TOKEN = "bh_E7x5m7qBMBKE9Q3pVe3CjA"
API_URL = "https://railway.app"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

PROPOSALS_FILE = "proposals.json"
DECISIONS_FILE = "decisions.json"

st.set_page_config(layout="wide")
st.title("🛡️ Bellhaven CRM Verification Portal")

if not os.path.exists(PROPOSALS_FILE) or os.path.getsize(PROPOSALS_FILE) == 0:
    st.info("No active proposals found. Run Python pipeline first.")
    st.stop()

with open(PROPOSALS_FILE, 'r') as f:
    proposals = json.load(f)

if not proposals:
    st.success("🎉 All matches are clean!")
    st.stop()

item = proposals[0]

st.markdown(f"### Target Match Type: `{item['type']}`")
st.warning(f"**SOP Guidance:** {item['summary']}")

col1, col2 = st.columns(2)
with col1:
    st.subheader("🌐 Live Website Data")
    st.json(item['scraped_data'])
with col2:
    st.subheader("🗄️ CRM Profile Match")
    st.json(item['crm_account'] if item['crm_account'] else "No matching record.")

def log_decision(loc_hash, outcome):
    decisions = {}
    if os.path.exists(DECISIONS_FILE):
        with open(DECISIONS_FILE, 'r') as f:
            decisions = json.load(f)
    decisions[loc_hash] = outcome
    with open(DECISIONS_FILE, 'w') as f:
        json.dump(decisions, f, indent=2)

if st.button("✅ Approve Action & Write to CRM Sandbox"):
    loc_data = item['scraped_data']
    
    if item['type'] == "CREATE_NEW_ACCOUNT":
        requests.post(f"{API_URL}/accounts", json={**loc_data, "status": "Active"}, headers=HEADERS)
        st.success("Account provisioned!")
    elif item['type'] == "UPDATE_OR_REP_PARENT":
        crm_id = item['crm_account']['id']
        if item['requires_chow_split']:
            # Create a brand new fork for the new owner
            new_acc = requests.post(f"{API_URL}/accounts", json={"name": loc_data["name"], "status": "Active"}, headers=HEADERS).json()
            # Link legacy account to the new owner's id without mutating old billing balances
            requests.patch(f"{API_URL}/accounts/{crm_id}", json={"chow_current_account": new_acc.get("id"), "status": "Needs Review"}, headers=HEADERS)
            st.success("SOP Safeguard Applied! Created ownership fork record.")
        else:
            requests.patch(f"{API_URL}/accounts/{crm_id}", json={"name": loc_data["name"], "status": "Active"}, headers=HEADERS)
            st.success("Direct modification completed!")
            
    log_decision(item['location_hash'], "APPROVED")
    st.experimental_rerun()
