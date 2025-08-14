import streamlit as st
import requests


st.set_page_config(page_title="Math Microservice GUI")
st.title("Math Microservice")


if "session" not in st.session_state:
    st.session_state["session"] = requests.Session()
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""


def login(username, password):
    login_url = "http://gateway:8000/auth/login"
    data = {"username": username, "password": password}
    response = st.session_state["session"].post(
        login_url, data=data, allow_redirects=False
    )
    if response.status_code == 302:
        st.session_state["authenticated"] = True
        st.session_state["username"] = username
        st.success("Login successful!")
        st.rerun()
    else:
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.error("Login failed. Check credentials.")


if not st.session_state["authenticated"]:
    st.subheader("Login to use math services")
    login_tab, register_tab = st.tabs(["Login", "Register"])
    with login_tab:
        username = st.text_input("Username", key="login_username")
        password = st.text_input(
            "Password", type="password", key="login_password"
        )
        if st.button("Login"):
            login(username, password)
    with register_tab:
        new_username = st.text_input("New Username", key="register_username")
        new_password = st.text_input(
            "New Password", type="password", key="register_password"
        )
        if st.button("Register"):
            register_url = "http://gateway:8000/auth/register"
            data = {"username": new_username, "password": new_password}
            response = st.session_state["session"].post(
                register_url, data=data, allow_redirects=False
            )
            if response.status_code == 302 and response.headers.get(
                "Location", ""
            ).endswith("/login"):
                st.success("Registration successful! You can now log in.")
            else:
                st.error(
                    "Registration failed. Username may already exist or fields are empty."
                )
    st.stop()


if st.session_state["authenticated"] and st.session_state["username"]:
    st.info(f"Logged in as: {st.session_state['username']}")
    if st.button("Log out / Erase username"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.success("You have been logged out and your username erased.")
        st.rerun()

operation = st.selectbox("Choose operation", ["pow", "factorial", "fibonacci"])

if operation == "pow":
    base = st.number_input("Base", value=2.0)
    exponent = st.number_input("Exponent", value=3.0)
elif operation in ["factorial", "fibonacci"]:
    n = st.number_input("n", min_value=0, step=1, value=5)

if st.button("Compute"):
    try:
        if operation == "pow":
            response = st.session_state["session"].get(
                "http://gateway:8000/math/pow",
                params={"base": base, "exp": exponent},
            )
        elif operation == "factorial":
            response = st.session_state["session"].get(
                "http://gateway:8000/math/factorial", params={"n": n}
            )
        elif operation == "fibonacci":
            response = st.session_state["session"].get(
                "http://gateway:8000/math/fibonacci", params={"n": n}
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
        response = st.session_state["session"].get(
            "http://gateway:8000/math/logs"
        )
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
