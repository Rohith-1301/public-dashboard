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
    st.title("📊 Analytics Dashboard")
    st.markdown("---")
    
    # Dashboard with Print/Download functionality
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
            .dashboard-container {{
                width: 100%;
                background: #f8f9fa;
                border-radius: 12px;
                padding: 15px;
            }}
            
            .btn-container {{
                text-align: center;
                margin-bottom: 20px;
            }}
            
            .download-btn {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 40px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                transition: all 0.3s ease;
            }}
            
            .download-btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            }}
            
            .download-btn:disabled {{
                opacity: 0.7;
                cursor: wait;
            }}
            
            .iframe-box {{
                width: 100%;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                background: white;
            }}
            
            .iframe-box iframe {{
                width: 100%;
                height: 600px;
                border: none;
            }}
            
            .status {{
                text-align: center;
                margin-top: 15px;
                padding: 10px;
                border-radius: 8px;
                display: none;
            }}
            
            .status.show {{
                display: block;
            }}
            
            .status.success {{
                background: #d4edda;
                color: #155724;
            }}
            
            .status.info {{
                background: #e7f3ff;
                color: #0c5460;
            }}
            
            .instructions {{
                background: #fff3cd;
                border: 1px solid #ffc107;
                border-radius: 8px;
                padding: 15px;
                margin-top: 15px;
                display: none;
            }}
            
            .instructions.show {{
                display: block;
            }}
            
            .instructions h4 {{
                margin: 0 0 10px 0;
                color: #856404;
            }}
            
            .instructions ol {{
                margin: 0;
                padding-left: 20px;
                color: #856404;
            }}
            
            .instructions li {{
                margin-bottom: 5px;
            }}
            
            .key {{
                background: #333;
                color: white;
                padding: 2px 8px;
                border-radius: 4px;
                font-family: monospace;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="dashboard-container">
            <div class="btn-container">
                <button class="download-btn" id="downloadBtn" onclick="downloadDashboard()">
                    📸 Download Dashboard as Image
                </button>
            </div>
            
            <div class="iframe-box" id="dashboardFrame">
                <iframe src="{POWERBI_URL}" allowFullScreen="true"></iframe>
            </div>
            
            <div class="status" id="statusMsg"></div>
            
            <div class="instructions" id="instructions">
                <h4>📥 To Save Dashboard as Image:</h4>
                <ol>
                    <li>Press <span class="key">Ctrl</span> + <span class="key">Shift</span> + <span class="key">S</span> (Windows) or <span class="key">Cmd</span> + <span class="key">Shift</span> + <span class="key">4</span> (Mac)</li>
                    <li>Select the dashboard area you want to capture</li>
                    <li>The image will be saved to your computer</li>
                </ol>
                <p style="margin-top:10px; color:#856404;"><strong>Or:</strong> Right-click on the dashboard → Select "Take Screenshot" (in Firefox) or use Snipping Tool</p>
            </div>
        </div>
        
        <script>
            function downloadDashboard() {{
                var btn = document.getElementById('downloadBtn');
                var status = document.getElementById('statusMsg');
                var instructions = document.getElementById('instructions');
                
                btn.disabled = true;
                btn.innerHTML = '⏳ Preparing...';
                
                // Show instructions
                instructions.className = 'instructions show';
                
                // Try to capture using html2canvas
                html2canvas(document.getElementById('dashboardFrame'), {{
                    useCORS: true,
                    allowTaint: true,
                    logging: false,
                    scale: 2
                }}).then(function(canvas) {{
                    // Check if canvas has content
                    var ctx = canvas.getContext('2d');
                    var imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    var hasContent = false;
                    
                    for (var i = 0; i < imageData.data.length; i += 4) {{
                        if (imageData.data[i] !== 255 || imageData.data[i+1] !== 255 || imageData.data[i+2] !== 255) {{
                            hasContent = true;
                            break;
                        }}
                    }}
                    
                    if (hasContent) {{
                        // Download the image
                        var link = document.createElement('a');
                        link.download = 'dashboard_' + new Date().toISOString().slice(0,10) + '.png';
                        link.href = canvas.toDataURL('image/png');
                        link.click();
                        
                        status.innerHTML = '✅ Dashboard downloaded successfully!';
                        status.className = 'status show success';
                        instructions.className = 'instructions';
                    }} else {{
                        // Show manual instructions
                        status.innerHTML = '📋 Please use the keyboard shortcut below to capture the dashboard';
                        status.className = 'status show info';
                    }}
                    
                    btn.disabled = false;
                    btn.innerHTML = '📸 Download Dashboard as Image';
                    
                }}).catch(function(error) {{
                    // Show manual instructions on error
                    status.innerHTML = '📋 Please use the keyboard shortcut below to capture the dashboard';
                    status.className = 'status show info';
                    
                    btn.disabled = false;
                    btn.innerHTML = '📸 Download Dashboard as Image';
                }});
                
                // Auto-hide status after 10 seconds
                setTimeout(function() {{
                    status.className = 'status';
                }}, 10000);
            }}
        </script>
    </body>
    </html>
    '''
    
    components.html(html, height=780, scrolling=False)


# ============ VIEW DATA PAGE ============
def show_view_data():
    st.title("📋 View Data")
    st.markdown("---")
    
    df = load_data()
    
    if df.empty:
        st.warning("No data available")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cats = ["All"] + list(df["Category"].unique()) if "Category" in df.columns else ["All"]
        cat = st.selectbox("Category", cats)
    
    with col2:
        regs = ["All"] + list(df["Region"].unique()) if "Region" in df.columns else ["All"]
        reg = st.selectbox("Region", regs)
    
    with col3:
        search = st.text_input("Search")
    
    # Filter data
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
    
    # Stats
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
    st.title("📥 Download Data")
    st.markdown("---")
    
    df = load_data()
    
    if df.empty:
        st.warning("No data available")
        return
    
    st.dataframe(df.head(10), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Excel")
        buf = BytesIO()
        df.to_excel(buf, index=False)
        buf.seek(0)
        st.download_button("Download Excel", buf, "data.xlsx", use_container_width=True)
    
    with col2:
        st.subheader("📄 CSV")
        st.download_button("Download CSV", df.to_csv(index=False), "data.csv", use_container_width=True)


# ============ ADMIN: UPLOAD ============
def show_upload():
    st.title("📤 Upload Data")
    st.markdown("---")
    
    file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])
    
    if file:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        st.success(f"Loaded {len(df)} records")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        if st.button("Confirm Upload", type="primary"):
            save_data(df)
            st.success("Data uploaded!")
            st.balloons()


# ============ ADMIN: MANAGE ============
def show_manage():
    st.title("📊 Manage Data")
    st.markdown("---")
    
    df = load_data()
    
    if df.empty:
        st.warning("No data")
        if st.button("Create Sample Data"):
            save_data(load_data())
            st.rerun()
        return
    
    c1, c2 = st.columns(2)
    c1.metric("Records", len(df))
    c2.metric("Columns", len(df.columns))
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["View", "Edit"])
    
    with tab1:
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    with tab2:
        edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
        if st.button("Save Changes", type="primary"):
            save_data(edited)
            st.success("Saved!")
            st.rerun()


# ============ ADMIN: USERS ============
def show_users():
    st.title("👥 Users")
    st.markdown("---")
    
    data = load_users()
    users = data.get("users", [])
    
    if not users:
        st.warning("No users")
        return
    
    rows = [{"Username": u["username"], "Role": u["role"].upper(), "Created": u.get("created", "N/A")} for u in users]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.metric("Total Users", len(users))


# ============ MAIN ============
def main():
    if not st.session_state.logged_in:
        show_login()
        return
    
    # Sidebar
    with st.sidebar:
        st.title("📋 Menu")
        st.markdown("---")
        st.write(f"👤 **{st.session_state.user}**")
        st.write(f"🔑 **{st.session_state.role.upper()}**")
        st.markdown("---")
        
        if st.session_state.role == "admin":
            pages = ["Upload Data", "Manage Data", "View Data", "Download Data", "View Users"]
        else:
            pages = ["Dashboard", "View Data", "Download Data"]
        
        page = st.radio("Navigate", pages)
        
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.role = None
            st.rerun()
    
    # Pages
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


if __name__ == "__main__":
    main()