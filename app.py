import streamlit as st
import requests
import json
import time

st.set_page_config(page_title="API Tester", layout="wide", page_icon="🚀")

# --- Header ---
st.title("🚀 API Tester")
st.markdown("Test your APIs easily! Created by Abhishek")

# --- Input Section ---
col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    http_method = st.selectbox(
        "Method",
        ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
        key="method"
    )

with col2:
    url = st.text_input("Request URL", placeholder="https://api.example.com/v1/resource", key="url")

with col3:
    st.write("") # Spacer
    st.write("") # Spacer
    send_button = st.button("Send Request", type="primary", use_container_width=True)

# --- Request Details ---
st.write("### Request Details")
tab_params, tab_headers, tab_body = st.tabs(["Params", "Headers", "Body"])

with tab_params:
    st.caption("Query Parameters (Key-Value pairs)")
    # Initialize session state for params if not exists
    if "params" not in st.session_state:
        st.session_state.params = [{"key": "", "value": "", "active": True}]
        
    # We will implement a dynamic editor or just a simple JSON/Key-Value input
    # For simplicity v1, let's use a data editor if available or multiple text inputs.
    # Streamlit data_editor is perfect here.
    params_df = st.data_editor(
        [{"key": "", "value": "", "active": True}],
        num_rows="dynamic",
        column_config={
            "active": st.column_config.CheckboxColumn("Active", default=True),
            "key": st.column_config.TextColumn("Key"),
            "value": st.column_config.TextColumn("Value")
        },
        key="params_editor",
        use_container_width=True
    )

with tab_headers:
    st.caption("Request Headers")
    headers_df = st.data_editor(
        [{"key": "", "value": "", "active": True}],
        num_rows="dynamic",
        column_config={
            "active": st.column_config.CheckboxColumn("Active", default=True),
            "key": st.column_config.TextColumn("Key"),
            "value": st.column_config.TextColumn("Value")
        },
        key="headers_editor",
        use_container_width=True
    )

with tab_body:
    st.caption("Request Body")
    body_type = st.radio("Body Type", ["None", "JSON", "Form Data"], horizontal=True)
    
    request_body = None
    form_data = None
    
    if body_type == "JSON":
        request_body = st.text_area("JSON Body", height=200, placeholder='{"key": "value"}')
    elif body_type == "Form Data":
        st.write("Key-Value Pairs")
        form_data_df = st.data_editor(
            [{"key": "", "value": "", "active": True}],
            num_rows="dynamic",
            column_config={
                "active": st.column_config.CheckboxColumn("Active", default=True),
                "key": st.column_config.TextColumn("Key"),
                "value": st.column_config.TextColumn("Value")
            },
            key="form_body_editor",
            use_container_width=True
        )

# --- Logic ---
if send_button:
    if not url:
        st.error("Please enter a URL")
    else:
        # Prepare params
        params = {row["key"]: row["value"] for row in params_df if row["active"] and row["key"]}
        
        # Prepare headers
        headers = {row["key"]: row["value"] for row in headers_df if row["active"] and row["key"]}
        
        # Prepare body
        json_data = None
        data_payload = None
        
        if body_type == "JSON" and request_body:
            try:
                json_data = json.loads(request_body)
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON Body: {e}")
                st.stop()
        elif body_type == "Form Data":
            data_payload = {row["key"]: row["value"] for row in form_data_df if row["active"] and row["key"]}
        
        # Execute Request
        try:
            with st.spinner("Sending request..."):
                start_time = time.time()
                response = requests.request(
                    method=http_method,
                    url=url,
                    params=params,
                    headers=headers,
                    json=json_data,
                    data=data_payload
                )
                end_time = time.time()
                duration = (end_time - start_time) * 1000
                
            # --- Response Visualization ---
            st.divider()
            st.subheader("Response")
            
            # Metric
            status_color = "green" if 200 <= response.status_code < 300 else "red"
            st.markdown(f"**Status:** :{status_color}[{response.status_code} {response.reason}] | **Time:** {duration:.0f} ms | **Size:** {len(response.content)} bytes")

            # Tabs for Body and Headers
            res_tab_body, res_tab_headers, res_tab_raw = st.tabs(["Body", "Headers", "Raw"])
            
            with res_tab_body:
                try:
                    st.json(response.json())
                except ValueError:
                    st.code(response.text)

            with res_tab_headers:
                st.json(dict(response.headers))
                
            with res_tab_raw:
                st.text(response.text)
                
        except Exception as e:
            st.error(f"Error: {e}")
