"""
PRISMOV - Enterprise System Monitor

A comprehensive system monitoring and analysis tool for real-time
performance tracking, process analysis, and automated reporting.

Author: Development Team
License: MIT
Version: 1.0.0
"""

import psutil
import time
import json
import os
import datetime
import requests
import random
import string
import webbrowser
import io
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics


# ============================================================
# FIXED PATHS FOR .EXE DEPLOYMENT
# ============================================================

DATA_DIR = os.path.join(os.getenv("LOCALAPPDATA"), "PRISMOV")
os.makedirs(DATA_DIR, exist_ok=True)

HISTORY_PATH = os.path.join(DATA_DIR, "history.json")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")

# ============================================================
# CARGA Y GUARDADO DE HISTORIAL
# ============================================================

def load_history():
    """
    Load system analysis history from persistent storage.
    
    Returns:
        list: Historical snapshots of system metrics, or empty list if file doesn't exist.
    
    Note:
        Gracefully handles missing or corrupted history files.
    """
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def save_history(history):
    """
    Persist system analysis history to disk.
    
    Args:
        history (list): List of system analysis snapshots to save.
    
    Raises:
        IOError: If file cannot be written to.
    """
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving history: {e}")

# ============================================================
# CARGA Y GUARDADO DE CONFIGURACIÓN
# ============================================================

def load_config():
    """
    Load application configuration from persistent storage.
    
    Returns:
        dict: Configuration dictionary with Telegram settings, scheduling, etc.
    
    Note:
        Returns default configuration if file doesn't exist or is corrupted.
    """
    default_config = {
        "chat_id": None,
        "scheduling": {},
        "supabase_enabled": False
    }

    try:
        if not os.path.exists(CONFIG_PATH):
            return default_config

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            content = f.read().strip()

            if not content:
                return default_config

            data = json.loads(content)

            # Ensure minimum required fields
            for key, value in default_config.items():
                if key not in data:
                    data[key] = value

            return data

    except Exception:
        return default_config

def save_config(config):
    """
    Persist application configuration to disk.
    
    Args:
        config (dict): Configuration dictionary to save.
    
    Raises:
        IOError: If file cannot be written.
    """
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving config: {e}")


def load_scheduling():
    """
    Load scheduling configuration for automated monitoring.
    
    Returns:
        dict: Dictionary containing scheduling parameters (active status, days, hours, interval).
    """
    config = load_config()
    prog = config.get("scheduling", {})

    # Default values if not present
    return {
        "active": prog.get("active", False),
        "days": prog.get("days", []),
        "start_time": prog.get("start_time", "00:00"),
        "end_time": prog.get("end_time", "23:59"),
        "interval_minutes": prog.get("interval_minutes", 60)
    }

def save_scheduling(new_schedule):
    """
    Persist scheduling configuration to disk.
    
    Args:
        new_schedule (dict): Schedule configuration to save.
    """
    config = load_config()
    config["scheduling"] = new_schedule
    save_config(config)

# ============================================================
# CÓDIGO DE VINCULACIÓN DE USUARIOS
# ============================================================

def generate_linking_code():
    """
    Generate a random 6-character code for user account linking.
    
    Returns:
        str: Alphanumeric linking code (uppercase letters + digits).
    """
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=6))
    return code

def load_linking_code():
    """
    Load the current user linking code, generating a new one if needed.
    
    Returns:
        str: Current linking code for user authentication.
    """
    config = load_config()
    code = config.get("linking_code")
    
    # Generate new code if none exists
    if not code:
        code = generate_linking_code()
        config["linking_code"] = code
        save_config(config)
    
    return code

def generate_new_linking_code():
    """
    Generate and save a new linking code.
    
    Returns:
        str: Newly generated linking code.
    """
    code = generate_linking_code()
    config = load_config()
    config["linking_code"] = code
    save_config(config)
    return code

def configurar_programacion_consola():
    print("\n=== CONFIGURAR PROGRAMACIÓN ===")

    dias_validos = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]

    print("Introduce los días separados por comas (ej: lunes,martes,viernes):")
    dias = input("Días: ").lower().replace(" ", "").split(",")
    dias = [d for d in dias if d in dias_validos]

    hora_inicio = input("Hora inicio (HH:MM): ")
    hora_fin = input("Hora fin (HH:MM): ")

    intervalo = int(input("Intervalo en minutos: "))

    nueva = {
        "activo": True,
        "dias": dias,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "intervalo_minutos": intervalo
    }

    save_scheduling(nueva)
    print("✔ Programación guardada correctamente.")

# ============================================================
# TELEGRAM
# ============================================================

TELEGRAM_TOKEN = "8488886057:AAH8PkpvspCgwGWNY4ImAKgJ7bf58fzpzjo"

def cargar_chat_id():
    return load_config().get("chat_id")

def guardar_chat_id(chat_id):
    config = load_config()
    config["chat_id"] = chat_id
    save_config(config)

def telegram_configurado():
    """Verifica si Telegram está configurado"""
    chat_id = load_config().get("chat_id")
    return chat_id is not None


def borrar_chat_id():
    """Elimina el chat_id almacenado (cierra sesión de Telegram)"""
    config = load_config()
    config["chat_id"] = None
    save_config(config)

def obtener_chat_id_y_validar_codigo():
    """
    Obtiene el chat_id pero verificando que el último mensaje contenga el código de vinculación correcto
    Retorna: (chat_id, código_valido) o (None, False)
    """
    codigo_esperado = load_linking_code()
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        r = requests.get(url).json()
        
        if "result" in r and len(r["result"]) > 0:
            ultimo_mensaje = r["result"][-1].get("message", {})
            texto_mensaje = ultimo_mensaje.get("text", "").upper()
            chat_id = ultimo_mensaje.get("chat", {}).get("id")
            
            # Verificar si el mensaje contiene el código
            if codigo_esperado in texto_mensaje:
                return chat_id, True
            else:
                return None, False
        
        return None, False
    except:
        return None, False

def obtener_chat_id():
    """Obtiene solo el chat_id del último mensaje"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        r = requests.get(url).json()
        if "result" in r and len(r["result"]) > 0:
            return r["result"][-1]["message"]["chat"]["id"]
        return None
    except:
        return None

def enviar_telegram(mensaje):
    """Envía mensaje a Telegram"""
    chat_id = load_config().get("chat_id")
    if not chat_id or not TELEGRAM_TOKEN:
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
        response = requests.post(url, data=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Error enviando mensaje a Telegram: {e}")
        return False

def enviar_reporte_telegram(snapshot):
    """Envía un resumen detallado del análisis al bot de Telegram"""
    if not telegram_configurado():
        return False
    
    try:
        a = snapshot["analisis_avanzado"]
        riesgo = a["score_detallado"]["riesgo_sistema"]
        
        # Emojis según riesgo
        emoji_riesgo = "🔴" if riesgo == "ALTO" else "🟠" if riesgo == "MEDIO" else "🟢"
        
        mensaje = f"""
🔍 *PRISMOV - Análisis Completo*
━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 {snapshot['timestamp']}

⚡ *Recursos del Sistema*
  • CPU: {snapshot['cpu_percent']:.1f}%
  • RAM: {snapshot['ram_percent']:.1f}%
  • Procesos Activos: {len(snapshot['procesos'])}

📈 *Tendencias*
  • CPU: {a['tendencias']['cpu']}
  • RAM: {a['tendencias']['ram']}
  • Promedio CPU: {a['huella_del_sistema']['cpu_promedio']:.1f}%
  • Promedio RAM: {a['huella_del_sistema']['ram_promedio']:.1f}%

{emoji_riesgo} *Evaluación de Riesgo: {riesgo}*

⚙️ *Procesos Críticos (Top 3)*
"""
        
        # Añadir procesos sospechosos
        if a["sospechosos_persistentes"]:
            for proc in a["sospechosos_persistentes"][:3]:
                mensaje += f"  • {proc['nombre']}: {proc['ram_mb']}MB, CPU {proc['cpu']}%\n"
        else:
            mensaje += "  ✓ Ninguno detectado\n"
        
        # Añadir recomendaciones
        mensaje += "\n💡 *Recomendaciones*\n"
        for rec in a["recomendaciones"][:3]:
            mensaje += f"  • {rec}\n"
        
        mensaje += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        return enviar_telegram(mensaje)
    except Exception as e:
        print(f"Error enviando reporte a Telegram: {e}")
        return False

# ============================================================
# ANÁLISIS DEL SISTEMA
# ============================================================

def analizar_procesos():
    procesos = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
        try:
            info = p.info
            procesos.append({
                "pid": info["pid"],
                "nombre": info["name"],
                "cpu": round(info["cpu_percent"], 2),
                "ram_mb": round(info["memory_info"].rss / (1024 * 1024), 2)
            })
        except:
            pass
    return sorted(procesos, key=lambda x: x["ram_mb"], reverse=True)

def analizar_tendencias(historial):
    """Analiza tendencias en el historial"""
    if len(historial) < 2:
        return "Datos insuficientes", "Datos insuficientes", []
    
    # Comparar últimos dos registros
    ultimo = historial[-1]
    anterior = historial[-2]
    
    cpu_actual = ultimo["cpu_percent"]
    cpu_anterior = anterior["cpu_percent"]
    ram_actual = ultimo["ram_percent"]
    ram_anterior = anterior["ram_percent"]
    
    # Determinar tendencia de CPU
    if cpu_actual > cpu_anterior + 10:
        tendencia_cpu = "↑ Creciente"
    elif cpu_actual < cpu_anterior - 10:
        tendencia_cpu = "↓ Decreciente"
    else:
        tendencia_cpu = "→ Estable"
    
    # Determinar tendencia de RAM
    if ram_actual > ram_anterior + 5:
        tendencia_ram = "↑ Creciente"
    elif ram_actual < ram_anterior - 5:
        tendencia_ram = "↓ Decreciente"
    else:
        tendencia_ram = "→ Estable"
    
    # Detectar procesos con consumo creciente
    procesos_crecientes = []
    procesos_actuales = {p["nombre"]: p for p in ultimo["procesos"]}
    procesos_anteriores = {p["nombre"]: p for p in anterior["procesos"]}
    
    for nombre, proc_actual in procesos_actuales.items():
        if nombre in procesos_anteriores:
            proc_anterior = procesos_anteriores[nombre]
            if proc_actual["ram_mb"] > proc_anterior["ram_mb"] + 50:  # Más de 50MB de aumento
                procesos_crecientes.append({
                    "nombre": nombre,
                    "ram_anterior": proc_anterior["ram_mb"],
                    "ram_actual": proc_actual["ram_mb"]
                })
    
    return tendencia_cpu, tendencia_ram, procesos_crecientes

def detectar_procesos_sospechosos(procesos):
    """Detecta procesos que consumen recursos anormales"""
    sospechosos = []
    
    # Obtener estadísticas
    if not procesos:
        return sospechosos
    
    # Procesos procesados
    procesos_con_recursos = [p for p in procesos if p["ram_mb"] > 0 or p["cpu"] > 0]
    
    if not procesos_con_recursos:
        return sospechosos
    
    ram_values = [p["ram_mb"] for p in procesos_con_recursos]
    ram_promedio = sum(ram_values) / len(ram_values)
    ram_desv = (sum((x - ram_promedio) ** 2 for x in ram_values) / len(ram_values)) ** 0.5
    
    cpu_values = [p["cpu"] for p in procesos_con_recursos if p["cpu"] > 0]
    cpu_promedio = sum(cpu_values) / len(cpu_values) if cpu_values else 0
    
    # Procesos que consumen >30% del RAM promedio o >5% CPU
    for proc in procesos_con_recursos:
        razon_ram = proc["ram_mb"] / ram_promedio if ram_promedio > 0 else 0
        
        if (proc["ram_mb"] > 500 and razon_ram > 2) or proc["cpu"] > 10:
            sospechosos.append({
                "nombre": proc["nombre"],
                "ram_mb": proc["ram_mb"],
                "cpu": proc["cpu"],
                "razon": f"Alto consumo de {'RAM' if proc['ram_mb'] > 500 else 'CPU'}"
            })
    
    return sorted(sospechosos, key=lambda x: x["ram_mb"], reverse=True)

def analisis_avanzado(snapshot, historial):
    """Análisis avanzado y preciso del sistema"""
    tendencia_cpu, tendencia_ram, procesos_crecientes = analizar_tendencias(historial)
    sospechosos = detectar_procesos_sospechosos(snapshot["procesos"])
    
    # Procesos frecuentes (top 5 por RAM)
    procesos_frecuentes = [p["nombre"] for p in snapshot["procesos"][:5]]
    
    # Calcular promedios históricos
    if len(historial) > 1:
        cpu_promedio = sum(s["cpu_percent"] for s in historial[-10:]) / min(10, len(historial))
        ram_promedio = sum(s["ram_percent"] for s in historial[-10:]) / min(10, len(historial))
    else:
        cpu_promedio = snapshot["cpu_percent"]
        ram_promedio = snapshot["ram_percent"]
    
    # Determinar riesgo
    riesgo = "BAJO"
    if len(sospechosos) > 3:
        riesgo = "ALTO"
    elif len(sospechosos) > 0:
        riesgo = "MEDIO"
    elif snapshot["cpu_percent"] > 80 or snapshot["ram_percent"] > 85:
        riesgo = "MEDIO"
    
    # Recomendaciones
    recomendaciones = []
    if snapshot["cpu_percent"] > 80:
        recomendaciones.append("CPU muy alta. Considera cerrar aplicaciones innecesarias.")
    if snapshot["ram_percent"] > 85:
        recomendaciones.append("RAM muy alta. Reinicia el sistema si es posible.")
    if len(sospechosos) > 0:
        recomendaciones.append(f"Detectados {len(sospechosos)} proceso(s) con alto consumo de recursos.")
    if not recomendaciones:
        recomendaciones.append("El sistema funciona correctamente.")
    
    return {
        "tendencias": {
            "cpu": tendencia_cpu,
            "ram": tendencia_ram,
            "procesos_crecientes": procesos_crecientes
        },
        "sospechosos_persistentes": sospechosos,
        "huella_del_sistema": {
            "cpu_promedio": round(cpu_promedio, 2),
            "ram_promedio": round(ram_promedio, 2),
            "procesos_frecuentes": procesos_frecuentes,
            "procesos_pesados_constantes": [p["nombre"] for p in snapshot["procesos"][:3]]
        },
        "procesos_nuevos": [p["nombre"] for p in snapshot["procesos"][:3]],
        "score_detallado": {
            "riesgo_sistema": riesgo
        },
        "recomendaciones": recomendaciones
    }

# ============================================================
# GENERAR REPORTES HTML
# ============================================================

REPORTES_DIR = os.path.join(DATA_DIR, "reportes")
os.makedirs(REPORTES_DIR, exist_ok=True)

def generar_reporte_html(snapshot):
    """Genera un reporte HTML detallado y atractivo"""
    a = snapshot["analisis_avanzado"]
    timestamp = snapshot["timestamp"]
    
    # Determinar color según riesgo
    riesgo = a["score_detallado"]["riesgo_sistema"]
    if riesgo == "BAJO":
        color_riesgo = "#4CAF50"  # Verde
        bg_riesgo = "#E8F5E9"
    elif riesgo == "MEDIO":
        color_riesgo = "#FF9800"  # Naranja
        bg_riesgo = "#FFF3E0"
    else:
        color_riesgo = "#F44336"  # Rojo
        bg_riesgo = "#FFEBEE"
    
    # Procesos sospechosos HTML
    procesos_html = ""
    if a["sospechosos_persistentes"]:
        for proc in a["sospechosos_persistentes"]:
            procesos_html += f"""
            <tr>
                <td>{proc['nombre']}</td>
                <td>{proc['ram_mb']:.2f} MB</td>
                <td>{proc['cpu']:.2f}%</td>
                <td>{proc['razon']}</td>
            </tr>
            """
    else:
        procesos_html = "<tr><td colspan='4' style='text-align:center; color:#999;'>✓ Ninguno detectado</td></tr>"
    
    # Procesos crecientes HTML
    procesos_crec_html = ""
    if a["tendencias"]["procesos_crecientes"]:
        for proc in a["tendencias"]["procesos_crecientes"]:
            procesos_crec_html += f"""
            <tr>
                <td>{proc['nombre']}</td>
                <td>{proc['ram_anterior']:.2f} MB</td>
                <td>{proc['ram_actual']:.2f} MB</td>
                <td>↑ +{proc['ram_actual'] - proc['ram_anterior']:.2f} MB</td>
            </tr>
            """
    else:
        procesos_crec_html = "<tr><td colspan='4' style='text-align:center; color:#999;'>✓ Ninguno detectado</td></tr>"
    
    # Procesos frecuentes
    procesos_freq_html = ""
    if a["huella_del_sistema"]["procesos_frecuentes"]:
        for proc in a["huella_del_sistema"]["procesos_frecuentes"]:
            procesos_freq_html += f"<li>{proc}</li>"
    
    # Recomendaciones
    recomendaciones_html = ""
    for rec in a["recomendaciones"]:
        recomendaciones_html += f"<li>{rec}</li>"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PRISMOV - Informe del Sistema</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                min-height: 100vh;
            }}
            .container {{
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                font-size: 32px;
                margin-bottom: 10px;
            }}
            .header p {{
                font-size: 14px;
                opacity: 0.9;
            }}
            .content {{
                padding: 30px;
            }}
            .section {{
                margin-bottom: 30px;
                border-bottom: 1px solid #eee;
                padding-bottom: 20px;
            }}
            .section:last-child {{
                border-bottom: none;
            }}
            .section h2 {{
                color: #667eea;
                font-size: 20px;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }}
            .stat-card {{
                background: #f5f5f5;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            }}
            .stat-card .label {{
                color: #666;
                font-size: 12px;
                text-transform: uppercase;
                margin-bottom: 8px;
            }}
            .stat-card .value {{
                font-size: 28px;
                font-weight: bold;
                color: #667eea;
            }}
            .stat-card .unit {{
                font-size: 14px;
                color: #999;
            }}
            .risk-box {{
                background: {bg_riesgo};
                border-left: 5px solid {color_riesgo};
                padding: 20px;
                border-radius: 5px;
                margin: 15px 0;
            }}
            .risk-box .risk-label {{
                font-size: 12px;
                color: #666;
                text-transform: uppercase;
                margin-bottom: 5px;
            }}
            .risk-box .risk-value {{
                font-size: 24px;
                font-weight: bold;
                color: {color_riesgo};
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }}
            table th {{
                background: #f5f5f5;
                padding: 12px;
                text-align: left;
                font-weight: 600;
                color: #333;
                border-bottom: 2px solid #ddd;
            }}
            table td {{
                padding: 12px;
                border-bottom: 1px solid #eee;
            }}
            table tr:hover {{
                background: #f9f9f9;
            }}
            .trend-good {{
                color: #4CAF50;
                font-weight: bold;
            }}
            .trend-warning {{
                color: #FF9800;
                font-weight: bold;
            }}
            .trend-danger {{
                color: #F44336;
                font-weight: bold;
            }}
            ul {{
                margin-left: 20px;
                margin-top: 10px;
            }}
            ul li {{
                margin-bottom: 8px;
                color: #333;
            }}
            .footer {{
                background: #f5f5f5;
                padding: 20px;
                text-align: center;
                color: #999;
                font-size: 12px;
                border-top: 1px solid #eee;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 PRISMOV</h1>
                <p>Informe de Análisis del Sistema</p>
                <p>{timestamp}</p>
            </div>
            
            <div class="content">
                <!-- RESUMEN RÁPIDO -->
                <div class="section">
                    <h2>⚡ Resumen Rápido</h2>
                    <div class="stats">
                        <div class="stat-card">
                            <div class="label">Uso de CPU</div>
                            <div class="value">{snapshot['cpu_percent']:.1f}<span class="unit">%</span></div>
                        </div>
                        <div class="stat-card">
                            <div class="label">Uso de RAM</div>
                            <div class="value">{snapshot['ram_percent']:.1f}<span class="unit">%</span></div>
                        </div>
                        <div class="stat-card">
                            <div class="label">Procesos Activos</div>
                            <div class="value">{len(snapshot['procesos'])}</div>
                        </div>
                        <div class="stat-card">
                            <div class="label">Riesgo del Sistema</div>
                            <div class="value" style="color: {color_riesgo};">{riesgo}</div>
                        </div>
                    </div>
                </div>

                <!-- EVALUACIÓN DE RIESGO -->
                <div class="section">
                    <h2>⚠️ Evaluación de Riesgo</h2>
                    <div class="risk-box">
                        <div class="risk-label">Nivel de Riesgo del Sistema</div>
                        <div class="risk-value">{riesgo}</div>
                    </div>
                </div>

                <!-- TENDENCIAS -->
                <div class="section">
                    <h2>📈 Tendencias</h2>
                    <table>
                        <tr>
                            <th>Recurso</th>
                            <th>Tendencia</th>
                            <th>Promedio (últimas 10 muestras)</th>
                        </tr>
                        <tr>
                            <td>CPU</td>
                            <td><span class="trend-good">{a['tendencias']['cpu']}</span></td>
                            <td>{a['huella_del_sistema']['cpu_promedio']:.2f}%</td>
                        </tr>
                        <tr>
                            <td>RAM</td>
                            <td><span class="trend-good">{a['tendencias']['ram']}</span></td>
                            <td>{a['huella_del_sistema']['ram_promedio']:.2f}%</td>
                        </tr>
                    </table>
                </div>

                <!-- PROCESOS SOSPECHOSOS -->
                <div class="section">
                    <h2>🕵️ Procesos con Alto Consumo</h2>
                    <table>
                        <tr>
                            <th>Nombre del Proceso</th>
                            <th>Memoria (MB)</th>
                            <th>CPU (%)</th>
                            <th>Razón</th>
                        </tr>
                        {procesos_html}
                    </table>
                </div>

                <!-- PROCESOS CON AUMENTO DE RECURSOS -->
                <div class="section">
                    <h2>📊 Procesos con Aumento de Recursos</h2>
                    <table>
                        <tr>
                            <th>Proceso</th>
                            <th>RAM Anterior (MB)</th>
                            <th>RAM Actual (MB)</th>
                            <th>Cambio</th>
                        </tr>
                        {procesos_crec_html}
                    </table>
                </div>

                <!-- PROCESOS PRINCIPALES -->
                <div class="section">
                    <h2>🔝 Procesos Principales</h2>
                    <ul>
                        {procesos_freq_html if procesos_freq_html else "<li>No hay procesos principales detectados</li>"}
                    </ul>
                </div>

                <!-- RECOMENDACIONES -->
                <div class="section">
                    <h2>💡 Recomendaciones</h2>
                    <ul>
                        {recomendaciones_html}
                    </ul>
                </div>
            </div>

            <div class="footer">
                <p>PRISMOV © 2026 - Sistema de Monitorización Avanzado del Sistema</p>
                <p>Reporte generado automáticamente</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def guardar_reporte(snapshot):
    """Guarda el reporte en HTML"""
    html = generar_reporte_html(snapshot)
    
    # Nombre del archivo con timestamp
    timestamp = snapshot["timestamp"].replace(":", "-").replace(" ", "_")
    filename = f"reporte_{timestamp}.html"
    filepath = os.path.join(REPORTES_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    
    return filepath



def generar_vista_previa_html(contenido_log, nombre_archivo):
    html_template = f"""
    <html>
    <head>
        <title>Log: {nombre_archivo}</title>
        <style>
            body {{ background-color: #1e1e1e; color: #d4d4d4; font-family: 'Consolas', monospace; padding: 20px; }}
            .container {{ border-left: 3px solid #007acc; padding-left: 15px; white-space: pre-wrap; }}
            h2 {{ color: #569cd6; border-bottom: 1px solid #333; padding-bottom: 10px; }}
        </style>
    </head>
    <body>
        <h2>Vista de Log: {nombre_archivo}</h2>
        <div class="container">{contenido_log}</div>
    </body>
    </html>
    """
    # Guardar temporalmente y abrir
    with open("temp_log.html", "w", encoding="utf-8") as f:
        f.write(html_template)
    
    webbrowser.open('file://' + os.path.realpath("temp_log.html"))

def abrir_reporte(filepath):
    """Abre el reporte en el navegador por defecto"""
    try:
        webbrowser.open(f"file:///{filepath.replace(chr(92), '/')}")
        return True
    except:
        return False

# ============================================================
# EJECUTAR ANÁLISIS
# ============================================================

def ejecutar_analisis(historial):
    """Ejecuta un análisis completo y genera reporte"""
    print("🔥 DEBUG → entrando en ejecutar_analisis")
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    procesos = analizar_procesos()

    # Snapshot base REAL
    snapshot_base = {
        "cpu_percent": cpu,
        "ram_percent": ram,
        "procesos": procesos
    }

    # Análisis avanzado con datos reales
    analisis = analisis_avanzado(snapshot_base, historial)

    snapshot = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_percent": cpu,
        "ram_percent": ram,
        "procesos": procesos,
        "analisis_avanzado": analisis
    }

    historial.append(snapshot)
    save_history(historial)

    # Guardar reporte HTML
    filepath_reporte = guardar_reporte(snapshot)

    # Enviar a Telegram si está configurado
    if telegram_configurado():
        enviar_reporte_telegram(snapshot)

    return filepath_reporte



# ============================================================
# MODO AUTOMÁTICO
# ============================================================

def iniciar_modo_automatico(historial):
    """Inicia el modo automático de análisis según programación"""
    while True:
        try:
            prog = load_scheduling()

            if prog["active"]:
                ahora = datetime.datetime.now()
                dia = ahora.strftime("%A").lower()

                if dia in prog["days"]:
                    h_inicio = datetime.datetime.strptime(prog["start_time"], "%H:%M").time()
                    h_fin = datetime.datetime.strptime(prog["end_time"], "%H:%M").time()

                    if h_inicio <= ahora.time() <= h_fin:
                        print(f"🔄 Ejecutando análisis automático a las {ahora.strftime('%H:%M')}")
                        ejecutar_analisis(historial)

            intervalo = prog.get("interval_minutes", 60)
            time.sleep(intervalo * 60)
        except Exception as e:
            print(f"Error en modo automático: {e}")
            time.sleep(60)  # Esperar 1 minuto antes de reintentar


# ============================================================
# MAIN PARA EJECUCIÓN DESDE CONSOLA
# (La GUI no usa este menú, pero sigue siendo útil)
# ============================================================

def main():
    print("=== PRISMOV - Sistema de Monitorización ===")

    # Cargar historial
    historial = load_history()

    # =============================
    # CONFIGURAR TELEGRAM SI NO EXISTE
    # =============================
    config = load_config()

    if config.get("chat_id") is None:
        print("\n⚠ Telegram no está configurado.")
        print("1) Abre tu bot en Telegram")
        print("2) Escríbele cualquier mensaje (por ejemplo: hola)")

        input("Cuando lo hayas hecho, pulsa ENTER...")

        chat_id = obtener_chat_id()
        if chat_id:
            guardar_chat_id(chat_id)
            print(f"✔ Telegram configurado correctamente. chat_id = {chat_id}")
        else:
            print("❌ No se pudo obtener el chat_id. Telegram seguirá desactivado.")

    # =============================
    # MENÚ PRINCIPAL (LOGIN NO OBLIGATORIO)
    # =============================
    while True:
        print("\n--- MENÚ ---")
        print("1) Ejecutar análisis ahora")
        print("2) Iniciar modo automático")
        print("3) Configurar programación")
        print("4) Salir")

        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            try:
                ejecutar_analisis(historial)
                print("✔ Análisis completado.")
            except Exception as e:
                print("❌ Error al ejecutar análisis:", e)

        elif opcion == "2":
            print("Modo automático iniciado. Pulsa CTRL+C para detenerlo.")
            iniciar_modo_automatico(historial)

        elif opcion == "3":
            configurar_programacion_consola()

        elif opcion == "4":
            print("Saliendo...")
            break

        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()