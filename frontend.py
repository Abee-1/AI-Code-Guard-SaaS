import streamlit as st
import requests
from database import authenticate_user, init_db

# Initialize internal client records auto-heal
init_db()

st.set_page_config(page_title="AI Code Guard Enterprise Portal", layout="wide")

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["company_name"] = ""

# Sidebar Branding Panel
with st.sidebar:
    st.title("🏢 Enterprise Hub")
    if st.session_state["authenticated"]:
        st.success(f"Connected: {st.session_state['company_name']}")
        st.info("Plan Tier: Premium Enterprise")
        if st.button("Logout Account"):
            st.session_state["authenticated"] = False
            st.rerun()
    else:
        st.warning("Awaiting Session Authentication")

# Authentication Interface Gateway
if not st.session_state["authenticated"]:
    st.header("🔑 AI Code Guard System Login")
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Corporate ID Username")
        password = st.text_input("System Access Password", type="password")
        if st.button("Authenticate Session"):
            user = authenticate_user(username, password)
            if user:
                st.session_state["authenticated"] = True
                st.session_state["company_name"] = user[0]
                st.rerun()
            else:
                st.error("Invalid Enterprise Credentials.")
else:
    # Authenticated Penetration Dashboard
    st.title("🎯 Enterprise Security & Performance Scanner")
    st.write(f"Welcome back, operations center for **{st.session_state['company_name']}**.")
    st.markdown("---")
    
    col_input, col_report = st.columns([2, 3])
    
    with col_input:
        st.subheader("🌐 Target Asset Registry")
        target_url = st.text_input("Paste Target Platform URL Here:", placeholder="e.g., https://target-company.com")
        
        st.markdown("""
        > **Automated Scope Boundaries:** > Clicking below executes passive web infrastructure reconnaissance, dependency mapping, architectural review, and AI threat modeling.
        """)
        
        if st.button("🚀 Execute Live System Audit"):
            if not target_url:
                st.error("Please insert a valid URL asset target first.")
            else:
                with st.spinner("Analyzing web assets, mapping threat models, and generating business fixes..."):
                    try:
                        # Direct connection string over the open Render Web API channel
                        payload = {"target_url": target_url}
                        api_endpoint = "https://ai-code-guard-api.onrender.com/scan"
                        
                        response = requests.post(api_endpoint, json=payload, timeout=90)
                        
                        if response.status_code == 200:
                            st.session_state["latest_report"] = response.json().get("report", "Error processing analytical results.")
                        else:
                            st.session_state["latest_report"] = f"🛑 **API Server Connectivity Lag (Status Code {response.status_code})**\nYour background API engine is waking up from sleep. Please wait 10 seconds and click the button again!"
                    except Exception as e:
                        st.session_state["latest_report"] = f"🛑 **Network Gateway Timeout:** Unable to reach the backend core service over the internet. Ensure your backend service is running live on Render."

    with col_report:
        st.subheader("📊 Live Security Audit & Business Assessment")
        if "latest_report" in st.session_state:
            st.markdown(st.session_state["latest_report"])
        else:
            st.info("Ready. Please supply a target URL interface configuration on the left workspace panel.")