import streamlit as st
import pandas as pd
import time
import datetime
# Import the underlying system logic (RA 2e, RA 6h)
import prismov2 as prismov

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="PRISMOV - Industrial Control",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling for a premium look
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .metric-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-top: 4px solid #4a90e2;
    }
    h1, h2, h3 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2800/2800015.png", width=100)
st.sidebar.title("PRISMOV Panel")
st.sidebar.markdown("---")
modo_analisis = st.sidebar.radio("Navigation", ["Real-Time Dashboard", "Historical Reports (RA 2g)", "Configuration / Endpoints"])
st.sidebar.markdown("---")
st.sidebar.info("Web demo designed to present the product to investors and plant technicians. Connects Edge data collection with Cloud visualization.")

# ==========================================
# VIEWS
# ==========================================
if modo_analisis == "Real-Time Dashboard":
    st.title("⚡ Plant Real-Time Dashboard")
    st.markdown("Live monitoring of consumption and predictive process analysis. *(RA: Criterion 6b and 6c)*")

    # Button to force scan
    if st.button("🔄 Execute Real-Time Scan"):
        with st.spinner("Collecting industrial system metrics..."):
            time.sleep(1) # Simulate network latency
            # Use native library to get a snapshot
            procesos = prismov.analizar_procesos()
            historial = prismov.load_history()
            
            # Extract quick metrics (Simulating Snapshot)
            try:
                cpu_total = sum(p['cpu'] for p in procesos)
                ram_total = sum(p['ram_mb'] for p in procesos)
            except:
                cpu_total, ram_total = 0, 0
                
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric("Total Plant CPU", f"{min(cpu_total, 100):.1f}%", "+2.1% (Trend)")
            col2.metric("General RAM Consumption", f"{ram_total:.1f} MB", "-50MB (Optimized)")
            col3.metric("Connected Nodes", "1 Active", "Local Edge")
            col4.metric("Alert Status (THD)", "Normal", "0 critical processes")
            
            st.markdown("---")
            st.subheader("📊 Top Processes (Resource Consumption)")
            
            # Process table
            df = pd.DataFrame(procesos[:15]) # Show top 15
            if not df.empty:
                df.columns = ["PID", "Process Name", "CPU (%)", "RAM (MB)"]
                
                # Bar chart for better visualization
                st.bar_chart(df.set_index("Process Name")["RAM (MB)"])
                
                # Interactive dataframe
                st.dataframe(df, use_container_width=True)

elif modo_analisis == "Historical Reports (RA 2g)":
    st.title("📄 Executive Reports (THD and Efficiency)")
    st.markdown("Audit history and saved states. Enables IT/OT integration.")
    
    historial = prismov.load_history()
    
    if len(historial) == 0:
        st.warning("No data in local history. Run desktop PRISMOV first.")
    else:
        st.success(f"Found **{len(historial)}** records in local database.")
        
        # Parse dates for historical chart
        fechas = []
        cpus = []
        rams = []
        for reg in historial:
            fechas.append(reg.get("timestamp", "Unknown"))
            cpus.append(reg.get("cpu_percent", 0))
            rams.append(reg.get("ram_percent", 0))
            
        df_hist = pd.DataFrame({"Date": fechas, "CPU (%)": cpus, "RAM (%)": rams})
        st.line_chart(df_hist.set_index("Date"))

else:
    st.title("⚙️ IT Configuration / Integrations")
    st.markdown("Endpoint Management, Telegram Bots and Security. *(RA Criterion 6g and Integrations)*")
    st.text_input("External API Webhook (ERP/CRM)", "https://api.mydomain.com/thd-ingest")
    st.text_input("Telegram Bot Token", type="password", value="********-*********")
    st.button("Save Configurations")
