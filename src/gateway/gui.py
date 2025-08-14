import streamlit as st
import requests

st.set_page_config(page_title="Math Microservice GUI")
st.title("Math Microservice")

# ---- Session bootstrap ----
if "session" not in st.session_state:
    st.session_state["session"] = requests.Session()
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

GATEWAY = "http://gateway:8000"

def _apply_auth_headers(token: str, username: str | None = None):
    """
    Attach Authorization and X-Username headers for all subsequent requests.
    """
    sess = st.session_state["session"]
    # Keep any existing headers and just update these two
    sess.headers.update({
        "Authorization": f"Bearer {token}"
    })
    # Optional: helpful during transition / quick tests
    if username:
        sess.headers.update({"X-Username": username})

def login(username: str, password: str):
    """
    Try JWT JSON login first (preferred). Fallback to legacy 302 flow.
    """
    login_url = f"{GATEWAY}/auth/login"

    # Preferred: JSON API
    try:
        resp = st.session_state["session"].post(
            login_url,
            json={"username": username, "password": password},
            allow_redirects=False,  # if server still redirects, we'll catch below
            timeout=10,
        )
    except Exception as e:
        st.session_state["authenticated"] = False
        st.error(f"Login request failed: {e}")
        return

    # Case 1: JWT JSON response
    if resp.headers.get("content-type", "").startswith("application/json"):
        if resp.status_code in (200, 201):
            data = resp.json()
            token = data.get("access_token")
            uname = data.get("username") or username
            if not token:
                st.session_state["authenticated"] = False
                st.error("Login failed: missing token in response.")
                return
            st.session_state["access_token"] = token
            st.session_state["username"] = uname
            _apply_auth_headers(token, uname)
            st.session_state["authenticated"] = True
            st.success(f"Login successful as {uname}!")
            st.rerun()
        else:
            # JSON error from server
            try:
                err = resp.json()
            except Exception:
                err = {"error": resp.text}
            st.session_state["authenticated"] = False
            st.error(f"Login failed ({resp.status_code}): {err}")
        return

    # Case 2: Legacy redirect (302) flow
    if resp.status_code == 302:
        # In legacy flow, there is no JWT; downstream will log 'anonymous' unless gateway adds X-Username.
        # We can set X-Username anyway to keep your logs correct:
        st.session_state["access_token"] = None
        st.session_state["username"] = username
        st.session_state["session"].headers.update({"X-Username": username})
        st.session_state["authenticated"] = True
        st.success(f"Login successful (legacy) as {username}!")
        st.rerun()
        return

    # Anything else:
    st.session_state["authenticated"] = False
    st.error(f"Login failed: HTTP {resp.status_code} - {resp.text}")

def register(username: str, password: str):
    register_url = f"{GATEWAY}/auth/register"
    try:
        # Prefer JSON register (returns token in the JWT implementation)
        resp = st.session_state["session"].post(
            register_url,
            json={"username": username, "password": password},
            allow_redirects=False,
            timeout=10,
        )
    except Exception as e:
        st.error(f"Registration failed: {e}")
        return

    if resp.headers.get("content-type", "").startswith("application/json"):
        if resp.status_code in (200, 201):
            data = resp.json()
            st.success("Registration successful.")
            # If the API returns a token, auto-login:
            token = data.get("access_token")
            uname = data.get("username") or username
            if token:
                st.session_state["access_token"] = token
                st.session_state["username"] = uname
                _apply_auth_headers(token, uname)
                st.session_state["authenticated"] = True
                st.info("You have been logged in automatically.")
                st.rerun()
            else:
                st.info("Please log in with your new credentials.")
        elif resp.status_code == 409:
            st.error("Registration failed: username already exists.")
        else:
            st.error(f"Registration failed ({resp.status_code}): {resp.text}")
        return

    # Legacy redirect register flow (no JSON)
    if resp.status_code == 302 and resp.headers.get("Location", "").endswith("/login"):
        st.success("Registration successful! You can now log in.")
    else:
        st.error("Registration failed. Username may already exist or fields are empty.")

def logout():
    # Local logout only (stateless JWT)
    st.session_state["authenticated"] = False
    st.session_state["access_token"] = None
    st.session_state["username"] = None
    # Clear headers
    sess = st.session_state["session"]
    for h in ["Authorization", "X-Username"]:
        if h in sess.headers:
            del sess.headers[h]
    st.success("Logged out.")
    st.rerun()

# ---- UI ----
if not st.session_state["authenticated"]:
    st.subheader("Login to use math services")
    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if not username or not password:
                st.error("Please provide both username and password.")
            else:
                login(username, password)

    with register_tab:
        new_username = st.text_input("New Username", key="register_username")
        new_password = st.text_input("New Password", type="password", key="register_password")
        if st.button("Register"):
            if not new_username or not new_password:
                st.error("Please fill both fields.")
            else:
                register(new_username, new_password)

    st.stop()

# Authenticated area
col1, col2 = st.columns([3, 1])
with col1:
    st.write(f"Signed in as **{st.session_state['username'] or 'unknown'}**")
with col2:
    if st.button("Logout", type="secondary"):
        logout()

operation = st.selectbox("Choose operation", ["pow", "factorial", "fibonacci"])

if operation == "pow":
    base = st.number_input("Base", value=2.0)
    exponent = st.number_input("Exponent", value=3.0)
elif operation in ["factorial", "fibonacci"]:
    n = st.number_input("n", min_value=0, step=1, value=5)

if st.button("Compute"):
    try:
        if operation == "pow":
            resp = st.session_state["session"].get(
                f"{GATEWAY}/math/pow", params={"base": base, "exp": exponent}, timeout=15
            )
        elif operation == "factorial":
            resp = st.session_state["session"].get(
                f"{GATEWAY}/math/factorial", params={"n": n}, timeout=15
            )
        else:
            resp = st.session_state["session"].get(
                f"{GATEWAY}/math/fibonacci", params={"n": n}, timeout=15
            )

        if resp.status_code == 200:
            data = resp.json()
            st.success(f"Result: {data.get('result')}")
            st.json(data)
        else:
            st.error(f"Error: {resp.status_code} - {resp.text}")
    except Exception as e:
        st.error(f"Exception: {str(e)}")

st.markdown("---")
if st.checkbox("Recent logs from database"):
    try:
        resp = st.session_state["session"].get(f"{GATEWAY}/math/logs", timeout=15)
        if resp.status_code == 200:
            logs = resp.json()
            if logs:
                st.subheader("Recent Requests")
                st.table(logs)
            else:
                st.info("No logs found.")
        else:
            st.error(f"Failed to fetch logs: {resp.status_code} - {resp.text}")
    except Exception as e:
        st.error(f"Exception: {str(e)}")
