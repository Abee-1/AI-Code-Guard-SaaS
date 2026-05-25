import streamlit as st
import requests
import streamlit as st
import requests
# 1. Update this import line to include init_db
from database import authenticate_user, init_db

# 2. Add this line right below it to auto-create your tables on the cloud server
init_db()

st.set_page_config(page_title="AI Code Guard Portal", layout="wide")
# ... (Leave absolutely everything else below this exactly the same!)
from database import authenticate_user

st.set_page_config(page_title="AI Code Guard Portal", layout="wide")

# Initialize login states in session memory
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.company_name = ""
    st.session_state.api_key = ""
    st.session_state.plan_tier = ""

# --- SCENARIO A: LOGIN FORM PORTAL ---
if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🛡️ AI Code Guard Enterprise Portal</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Sign in to access your secure static analysis scanning core.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("🔑 Client Authentication Login")
            input_username = st.text_input("Username")
            input_password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Authenticate Session", use_container_width=True)
            
            if submit_login:
                user_info = authenticate_user(input_username, input_password)
                if user_info:
                    st.session_state.authenticated = True
                    st.session_state.company_name = user_info[0]
                    st.session_state.api_key = user_info[1]
                    st.session_state.plan_tier = user_info[2]
                    st.rerun()
                else:
                    st.error("❌ Invalid Username or Password.")

# --- SCENARIO B: PREMIUM LOGGED-IN PORTAL INTERFACE ---
else:
    st.sidebar.markdown(f"### 🏢 {st.session_state.company_name}")
    if st.session_state.plan_tier == 'Premium':
        st.sidebar.markdown("👑 **Subscription:** <span style='color:#FFD700;'>Premium Enterprise</span>", unsafe_allow_html=True)
    else:
        st.sidebar.markdown("🌱 **Subscription:** <span style='color:#00FFA3;'>Free Tier</span>", unsafe_allow_html=True)
        
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout Account", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    st.title("🛡️ AI Code Guard Application Portal")
    st.markdown(f"Welcome back, team **{st.session_state.company_name}**.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💻 Source Code Input Workspace")
        test_code_input = st.text_area("Paste Code Here:", height=320, value="import os\n\ndef ping_website(user_input_ip):\n    command = 'ping -n 1 ' + user_input_ip\n    os.system(command)")
        trigger_scan = st.button("🚀 Run Cloud Security Scan", use_container_width=True)
        
    with col2:
        st.subheader("📊 Live Security Audit Assessment")
        if trigger_scan:
            with st.spinner("Analyzing code structures..."):
                headers = {"X-API-Key": st.session_state.api_key}
                payload = {"code": test_code_input}
                try:
                    response = requests.post("https://ai-code-guard-api.onrender.com/scan", json=payload, headers=headers)
                    if response.status_code == 200:
                        data = response.json().get("analysis", {})
                        if data.get("vulnerability_found"):
                            st.error(f"⚠️ Flaw Detected: {data.get('vulnerability_type')}")
                            st.metric(label="Threat Severity Level", value=data.get('severity'))
                            st.markdown("#### 📝 Threat Explanation")
                            st.write(data.get("explanation"))
                            st.markdown("#### 🛠️ Actionable Remediation Steps")
                            st.info(data.get("remediation"))
                            st.markdown("#### 🔒 Secure Code Patch")
                            st.code(data.get("secure_code_patch"), language="python")
                        else:
                            st.success("🎉 Code Check Complete! Matches all secure engineering patterns.")
                    else:
                        st.error(f"Error: API returned status code {response.status_code}")
                except Exception as e:
                    st.error(f"Could not connect to API server. Details: {e}")
        else:
            st.info("Ready. Paste a script framework and execute the scanner pipeline.")
