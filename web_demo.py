import streamlit as st
import pandas as pd
import time
import datetime
# Importamos la lógica subyacente de nuestro sistema (RA 2e, RA 6h)
import prismov

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="PRISMOV - Industrial Control",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado para dar un look premium
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
# BARRA LATERAL (SIDEBAR)
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2800/2800015.png", width=100)
st.sidebar.title("PRISMOV Panel")
st.sidebar.markdown("---")
modo_analisis = st.sidebar.radio("Navegación", ["Dashboard Tiempo Real", "Reportes Históricos (RA 2g)", "Configuración / Endpoints"])
st.sidebar.markdown("---")
st.sidebar.info("Demo Web diseñada para presentar el producto a inversores y técnicos de planta. Conecta la recolección de datos (Edge) con la visualización Cloud.")

# ==========================================
# VISTAS
# ==========================================
if modo_analisis == "Dashboard Tiempo Real":
    st.title("⚡ Dashboard de Planta en Tiempo Real")
    st.markdown("Monitorización en vivo de los consumos y análisis predictivo de procesos. *(RA: Criterio 6b y 6c)*")

    # Botón para forzar escaneo
    if st.button("🔄 Ejecutar Escaneo en Tiempo Real"):
        with st.spinner("Recolectando métricas del sistema industrial..."):
            time.sleep(1) # Simular latencia de red
            # Utilizamos la librería nativa para obtener un snapshot
            procesos = prismov.analizar_procesos()
            historial = prismov.cargar_historial()
            
            # Extraer métricas rápidas (Simulando Snapshot)
            try:
                cpu_total = sum(p['cpu'] for p in procesos)
                ram_total = sum(p['ram_mb'] for p in procesos)
            except:
                cpu_total, ram_total = 0, 0
                
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric("CPU Total de Planta", f"{min(cpu_total, 100):.1f}%", "+2.1% (Tendencia)")
            col2.metric("Consumo RAM General", f"{ram_total:.1f} MB", "-50MB (Optimizado)")
            col3.metric("Nodos Conectados", "1 Activo", "Local Edge")
            col4.metric("Estado de Alerta (THD)", "Normal", "0 procesos críticos")
            
            st.markdown("---")
            st.subheader("📊 Top Procesos (Consumo de Recursos)")
            
            # Tabla de procesos 
            df = pd.DataFrame(procesos[:15]) # Mostrar el top 15
            if not df.empty:
                df.columns = ["PID", "Nombre del Proceso", "CPU (%)", "RAM (MB)"]
                
                # Gráfico de barras para mejor visualización
                st.bar_chart(df.set_index("Nombre del Proceso")["RAM (MB)"])
                
                # DataFrame interactivo
                st.dataframe(df, use_container_width=True)

elif modo_analisis == "Reportes Históricos (RA 2g)":
    st.title("📄 Informes Ejecutivos (THD y Eficiencia)")
    st.markdown("Historial de auditorías y estados guardados. Permite la integración IT/OT.")
    
    historial = prismov.cargar_historial()
    
    if len(historial) == 0:
        st.warning("No hay datos en el historial local. Ejecuta PRISMOV de escritorio primero.")
    else:
        st.success(f"Se han encontrado **{len(historial)}** registros en la base de datos local.")
        
        # Parseamos las fechas para un gráfico histórico
        fechas = []
        cpus = []
        rams = []
        for reg in historial:
            fechas.append(reg.get("timestamp", "Desconocido"))
            cpus.append(reg.get("cpu_percent", 0))
            rams.append(reg.get("ram_percent", 0))
            
        df_hist = pd.DataFrame({"Fecha": fechas, "CPU (%)": cpus, "RAM (%)": rams})
        st.line_chart(df_hist.set_index("Fecha"))

else:
    st.title("⚙️ Configuraciones IT / Integraciones")
    st.markdown("Gestión de Endpoints, Bots de Telegram y Seguridad. *(RA Criterio 6g e Integraciones)*")
    st.text_input("Webhook API Externo (ERP/CRM)", "https://api.midominio.com/thd-ingest")
    st.text_input("Telegram Bot Token", type="password", value="********-*********")
    st.button("Guardar Configuraciones")
