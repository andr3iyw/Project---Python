import streamlit as st
import requests


st.set_page_config(page_title="Math Microservice GUI")
st.title("Math Microservice")

# Session object to persist login
if 'session' not in st.session_state:
    st.session_state['session'] = requests.Session()
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

def login(username, password):
    login_url = "http://localhost:5000/auth/login"
    data = {"username": username, "password": password}
    response = st.session_state['session'].post(login_url, data=data)
    if response.url.endswith("/math/") or response.status_code == 200:
        st.session_state['authenticated'] = True
        st.success("Login successful!")
        st.rerun()
    else:
        st.session_state['authenticated'] = False
        st.error("Login failed. Check credentials.")


if not st.session_state['authenticated']:
    st.subheader("Login to use math services")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        login(username, password)
    st.stop()

operation = st.selectbox("Choose operation", ["pow", "factorial", "fibonacci"])

if operation == "pow":
    base = st.number_input("Base", value=2.0)
    exponent = st.number_input("Exponent", value=3.0)
elif operation in ["factorial", "fibonacci"]:
    n = st.number_input("n", min_value=0, step=1, value=5)

if st.button("Compute"):
    try:
        if operation == "pow":
            response = st.session_state['session'].get(
                "http://localhost:5000/math/pow",
                params={"base": base, "exp": exponent}
            )
        elif operation == "factorial":
            response = st.session_state['session'].get(
                "http://localhost:5000/math/factorial",
                params={"n": n}
            )
        elif operation == "fibonacci":
            response = st.session_state['session'].get(
                "http://localhost:5000/math/fibonacci",
                params={"n": n}
            )

        if response.status_code == 200:
            data = response.json()
            st.success(f"Result: {data['result']}")
            st.json(data)
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Exception: {str(e)}")

st.markdown("---")
if st.checkbox("Recent logs from database"):
    try:
        response = st.session_state['session'].get("http://localhost:5000/math/logs")
        if response.status_code == 200:
            logs = response.json()
            if logs:
                st.subheader("Recent Requests")
                st.table(logs)
            else:
                st.info("No logs found.")
        else:
            st.error(f"Failed to fetch logs: {response.status_code}")
    except Exception as e:
        st.error(f"Exception: {str(e)}")
