import streamlit as st
import pandas as pd
import json
from pathlib import Path
import bcrypt
from datetime import datetime
from io import BytesIO
import streamlit.components.v1 as components

# Page Config
st.set_page_config(
    page_title="Global Data Management",
    page_icon="📊",
    layout="wide"
)

# ==================== HIDE STREAMLIT UI ELEMENTS ====================
hide_streamlit_style = """
<style>
    /* Hide the entire Streamlit header */
    header[data-testid="stHeader"] {
        display: none !important;
        height: 0 !important;
    }
    
    /* Hide the decorator (GitHub icon) */
    .stDeployButton {
        display: none !important;
    }
    
    /* Hide the main menu button (hamburger menu) */
    #MainMenu {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* Hide the footer */
    footer {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* Hide "Made with Streamlit" footer text */
    footer:after {
        content: none !important;
        display: none !important;
    }
    
    /* Hide the toolbar (Fork on GitHub button) */
    .stToolbar {
        display: none !important;
    }
    
    /* Hide any GitHub related links */
    a[href*='github.com/streamlit'] {
        display: none !important;
    }
    
    /* Hide View app source */
    ._profilePreview_g8x02_53 {
        display: none !important;
    }
    
    /* Hide the floating action button */
    .stActionButton {
        display: none !important;
    }
    
    /* Hide deploy button */
    button[title="Deploy this app"] {
        display: none !important;
    }
    
    /* Hide any element with Fork text */
    div[title*="Fork"] {
        display: none !important;
    }
    
    /* Hide header decoration */
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    /* Hide the entire top toolbar */
    [data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* Remove extra padding from top after hiding header */
    .main > div:first-child {
        padding-top: 1rem !important;
    }
    
    /* Hide viewer badge */
    ._viewerBadge_1bx8f_121 {
        display: none !important;
    }
    
    /* Hide any cloud/deploy related buttons */
    button[kind="header"] {
        display: none !important;
    }
    
    /* Additional selectors for GitHub elements */
    .css-1rs6os {
        display: none !important;
    }
    
    div[class*="viewerBadge"] {
        display: none !important;
    }
    
    /* Hide manage app button */
    button[title*="Manage"] {
        display: none !important;
    }
    
    /* Clean up the top spacing */
    .block-container {
        padding-top: 2rem !important;
    }
</style>
"""

# Apply the CSS globally
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Power BI URL
POWERBI_URL = "https://app.powerbi.com/view?r=eyJrIjoiZTFlNTRlNWYtYTQ2OS00NjAwLWE1MGUtNDczZjMzYmI3Y2IzIiwidCI6ImUxNGU3M2ViLTUyNTEtNDM4OC04ZDY3LThmOWYyZTJkNWE0NiIsImMiOjEwfQ%3D%3D&pageName=f4e6760f1492a2bc4b61"

# File Paths
USERS_FILE = Path("users/users.json")
DATA_FILE = Path("data/global_data.xlsx")


# ============ USER FUNCTIONS ============
def load_users():
    if USERS_FILE.exists():
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {"users": []}


def save_users(data):
    Path("users").mkdir(exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def hash_pw(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_pw(stored, provided):
    try:
        return bcrypt.checkpw(provided.encode(), stored.encode())
    except:
        return False


def login(username, password):
    data = load_users()
    for u in data.get("users", []):
        if u["username"] == username and check_pw(u["password"], password):
            return u["role"]
    return None


def signup(username, password):
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(password) < 4:
        return False, "Password must be at least 4 characters"
    
    data = load_users()
    for u in data.get("users", []):
        if u["username"].lower() == username.lower():
            return False, "Username already exists"
    
    data["users"].append({
        "username": username,
        "password": hash_pw(password),
        "role": "user",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_users(data)
    return True, "Account created"


# ============ DATA FUNCTIONS ============
def load_data():
    if DATA_FILE.exists():
        return pd.read_excel(DATA_FILE)
    df = pd.DataFrame({
        "ID": [1, 2, 3, 4, 5],
        "Product": ["Laptop", "Mouse", "Keyboard", "Monitor", "Headphones"],
        "Category": ["Electronics", "Accessories", "Accessories", "Electronics", "Accessories"],
        "Price": [999.99, 25.50, 49.99, 299.99, 79.99],
        "Stock": [50, 200, 150, 75, 120],
        "Region": ["North", "South", "East", "West", "North"]
    })
    save_data(df)
    return df


def save_data(df):
    Path("data").mkdir(exist_ok=True)
    df.to_excel(DATA_FILE, index=False)


# ============ SESSION ============
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None


# ============ LOGIN PAGE ============
def show_login():
    # Re-apply CSS on login page to ensure it's hidden
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🔐 Global Data Management")
        
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
        
        with tab1:
            st.subheader("Welcome Back!")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)
                
                if submitted:
                    if username and password:
                        role = login(username, password)
                        if role:
                            st.session_state.logged_in = True
                            st.session_state.user = username
                            st.session_state.role = role
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    else:
                        st.warning("Please enter username and password")
        
        with tab2:
            st.subheader("Create Account")
            with st.form("signup_form"):
                new_user = st.text_input("Choose Username")
                new_pass = st.text_input("Choose Password", type="password")
                confirm = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Create Account", use_container_width=True)
                
                if submitted:
                    if not new_user or not new_pass or not confirm:
                        st.warning("Please fill all fields")
                    elif new_pass != confirm:
                        st.error("Passwords do not match")
                    else:
                        ok, msg = signup(new_user, new_pass)
                        if ok:
                            st.success(msg + "! Please login.")
                        else:
                            st.error(msg)


# ============ DASHBOARD PAGE ============
def show_dashboard():
    # Re-apply CSS to ensure consistency
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    st.title("📊 Analytics Dashboard")
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("💡 Click download button to save dashboard")
    
    with col2:
        download_html = f"""
        <a href="{POWERBI_URL}" target="_blank" 
           style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                  color: white; padding: 10px 20px; text-decoration: none; border-radius: 8px; 
                  font-weight: bold; text-align: center;">
           📥 Download Dashboard
        </a>
        """
        st.markdown(download_html, unsafe_allow_html=True)
    
    dashboard_embed = f"""
    <iframe 
        src="{POWERBI_URL}"
        width="100%"
        height="600"
        style="border: none; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
    </iframe>
    """
    
    components.html(dashboard_embed, height=620)


# ============ VIEW DATA PAGE ============
def show_view_data():
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    st.title("📋 View Data")
    st.markdown("---")
    
    df = load_data()
    
    if df.empty:
        st.warning("No data available")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cats = ["All"] + list(df["Category"].unique()) if "Category" in df.columns else ["All"]
        cat = st.selectbox("Category", cats)
    
    with col2:
        regs = ["All"] + list(df["Region"].unique()) if "Region" in df.columns else ["All"]
        reg = st.selectbox("Region", regs)
    
    with col3:
        search = st.text_input("Search")
    
    filtered = df.copy()
    if cat != "All":
        filtered = filtered[filtered["Category"] == cat]
    if reg != "All":
        filtered = filtered[filtered["Region"] == reg]
    if search:
        mask = filtered.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
        filtered = filtered[mask]
    
    st.markdown("---")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Records", len(filtered))
    c2.metric("Columns", len(df.columns))
    if "Price" in filtered.columns:
        c3.metric("Avg Price", f"${filtered['Price'].mean():.2f}")
    if "Stock" in filtered.columns:
        c4.metric("Total Stock", int(filtered['Stock'].sum()))


# ============ DOWNLOAD PAGE ============
def show_download():
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    st.title("📥 Download Data")
    st.markdown("---")
    
    df = load_data()
    
    if df.empty:
        st.warning("No data available")
        return
    
    st.dataframe(df.head(10), use_container_width=True, hide_index=True)
    st.caption(f"Showing 10 of {len(df)} records")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Excel")
        buf = BytesIO()
        df.to_excel(buf, index=False)
        buf.seek(0)
        st.download_button(
            "⬇️ Download Excel",
            buf,
            "data.xlsx",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        st.subheader("📄 CSV")
        st.download_button(
            "⬇️ Download CSV",
            df.to_csv(index=False),
            "data.csv",
            use_container_width=True,
            type="primary"
        )


# ============ ADMIN: UPLOAD ============
def show_upload():
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    st.title("📤 Upload Data")
    st.markdown("---")
    
    st.info("Upload a CSV or Excel file to replace existing data")
    
    file = st.file_uploader("Choose file", type=["csv", "xlsx", "xls"])
    
    if file:
        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            st.success(f"✅ Loaded {len(df)} records")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm Upload", type="primary", use_container_width=True):
                    save_data(df)
                    st.success("Data uploaded successfully!")
                    st.balloons()
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")


# ============ ADMIN: MANAGE ============
def show_manage():
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    st.title("📊 Manage Data")
    st.markdown("---")
    
    df = load_data()
    
    if df.empty:
        st.warning("No data available")
        if st.button("Create Sample Data", type="primary"):
            save_data(load_data())
            st.rerun()
        return
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Records", len(df))
    c2.metric("Columns", len(df.columns))
    if "Price" in df.columns:
        c3.metric("Avg Price", f"${df['Price'].mean():.2f}")
    if "Stock" in df.columns:
        c4.metric("Total Stock", int(df['Stock'].sum()))
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["👁️ View", "✏️ Edit"])
    
    with tab1:
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    with tab2:
        edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Changes", type="primary", use_container_width=True):
                save_data(edited)
                st.success("Changes saved!")
                st.rerun()
        with col2:
            if st.button("🔄 Reset", use_container_width=True):
                st.rerun()


# ============ ADMIN: USERS ============
def show_users():
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    st.title("👥 Registered Users")
    st.markdown("---")
    
    data = load_users()
    users = data.get("users", [])
    
    if not users:
        st.warning("No users found")
        return
    
    rows = []
    for u in users:
        rows.append({
            "Username": u["username"],
            "Role": u["role"].upper(),
            "Created": u.get("created", "N/A")
        })
    
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.metric("Total Users", len(users))


# ============ MAIN ============
def main():
    # Apply CSS globally at the start
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        show_login()
        return
    
    # Sidebar
    with st.sidebar:
        st.title("📋 Menu")
        st.markdown("---")
        st.markdown(f"👤 **{st.session_state.user}**")
        st.markdown(f"🔑 **{st.session_state.role.upper()}**")
        st.markdown("---")
        
        if st.session_state.role == "admin":
            pages = ["Upload Data", "Manage Data", "View Data", "Download Data", "View Users"]
        else:
            pages = ["Dashboard", "View Data", "Download Data"]
        
        page = st.radio("Navigate", pages)
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.role = None
            st.rerun()
        
        st.markdown("---")
        st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Page routing
    if page == "Dashboard":
        show_dashboard()
    elif page == "View Data":
        show_view_data()
    elif page == "Download Data":
        show_download()
    elif page == "Upload Data":
        show_upload()
    elif page == "Manage Data":
        show_manage()
    elif page == "View Users":
        show_users()
    
    # Custom footer
    st.markdown("---")
    st.caption(f"© 2024 Global Data Management | Logged in as {st.session_state.user}")


if __name__ == "__main__":
    main()