import streamlit as st
import requests

st.set_page_config(page_title="Math Microservice GUI")

st.title("Math Microservice")

operation = st.selectbox("Choose operation", ["pow", "factorial", "fibonacci"])

if operation == "pow":
    base = st.number_input("Base", value=2.0)
    exponent = st.number_input("Exponent", value=3.0)
elif operation in ["factorial", "fibonacci"]:
    n = st.number_input("n", min_value=0, step=1, value=5)

if st.button("Compute"):
    try:
        if operation == "pow":
            response = requests.get(
                "http://localhost:5000/math/pow",
                params={"base": base, "exp": exponent}
            )
        elif operation == "factorial":
            response = requests.get(
                "http://localhost:5000/math/factorial",
                params={"n": n}
            )
        elif operation == "fibonacci":
            response = requests.get(
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
        response = requests.get("http://localhost:5000/math/logs")
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
