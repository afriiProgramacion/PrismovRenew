import sys
import threading
import os
import glob
import time
import psutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QTextEdit, QLabel, QMessageBox, QDialog, QCheckBox,
    QHBoxLayout, QTimeEdit, QSpinBox, QGridLayout, QProgressBar, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
)
from PyQt5.QtCore import Qt, QTime, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QIcon, QFont, QColor, QLinearGradient
from PyQt5.QtWidgets import QWidget, QMessageBox, QInputDialog
import pyqtgraph as pg

import prismov2 as prismov

# ============================================================
# SCHEDULE CONFIGURATION WINDOW
# ============================================================

class VentanaProgramacion(QDialog):
    """
    Dialog Window for configuring automated task schedules.
    Matches Criterion RA: 5b) Data Lifecycle.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Scheduling - RA: Criterion 5b) Data Lifecycle")
        self.setGeometry(300, 300, 400, 300)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Select days:"))
        dias_layout = QGridLayout()

        self.dias_check = {}
        dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for i, d in enumerate(dias):
            chk = QCheckBox(d.capitalize())
            self.dias_check[d.lower()] = chk
            dias_layout.addWidget(chk, i // 2, i % 2)

        layout.addLayout(dias_layout)

        layout.addWidget(QLabel("Start time:"))
        self.hora_inicio = QTimeEdit()
        self.hora_inicio.setDisplayFormat("HH:mm")
        layout.addWidget(self.hora_inicio)

        layout.addWidget(QLabel("End time:"))
        self.hora_fin = QTimeEdit()
        self.hora_fin.setDisplayFormat("HH:mm")
        layout.addWidget(self.hora_fin)

        layout.addWidget(QLabel("Interval (minutes):"))
        self.intervalo = QSpinBox()
        self.intervalo.setRange(1, 1440)
        layout.addWidget(self.intervalo)

        btn_guardar = QPushButton("Save Schedule")
        btn_guardar.clicked.connect(self.guardar)
        layout.addWidget(btn_guardar)

        self.setLayout(layout)
        self.cargar_programacion()

    def cargar_programacion(self):
        prog = prismov.load_scheduling()

        # Use .get() to provide default values and avoid KeyErrors
        for d in prog.get("dias", []):
            if d in self.dias_check:
                self.dias_check[d].setChecked(True)

        self.hora_inicio.setTime(QTime.fromString(prog.get("hora_inicio", "00:00"), "HH:mm"))
        self.hora_fin.setTime(QTime.fromString(prog.get("hora_fin", "23:59"), "HH:mm"))
        self.intervalo.setValue(prog.get("intervalo_minutos", 60))

    def guardar(self):
        dias = [d for d, chk in self.dias_check.items() if chk.isChecked()]

        nueva_prog = {
            "activo": True,
            "dias": dias,
            "hora_inicio": self.hora_inicio.time().toString("HH:mm"),
            "hora_fin": self.hora_fin.time().toString("HH:mm"),
            "intervalo_minutos": self.intervalo.value()
        }

        prismov.save_scheduling(nueva_prog)
        QMessageBox.information(self, "Saved", "Schedule saved successfully.")
        self.close()


# ============================================================
# MAIN GUI
# ============================================================

class PrismovGUI(QWidget):
    """
    Main GUI Class for the PRISMOV Industrial Monitoring System.
    
    This class handles the initialization of the dashboard, manages
    user interactions (Telegram binding, scheduled tasks, immediate analysis),
    and updates the UI state.
    
    Attributes:
        dark_mode (bool): Flag indicating if the dark theme is active.
        historial (list): The historical data loaded from the system.
        auto_thread (threading.Thread): Background thread for automated analysis.
        auto_activo (bool): Flag indicating if the automated mode is running.
    """
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon("icon.ico"))
        self.setWindowTitle("PRISMOV - Control Panel and THD Monitoring")
        self.setGeometry(100, 100, 1200, 800)  # Larger default window
        # Allow fullscreen / maximized by default
        self.showMaximized()

        self.dark_mode = False

        # Main Horizontal Layout (Sidebar + Content)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =========================================================
        # 1. SIDEBAR (Left Side)
        # =========================================================
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(24)
        sidebar_layout.setContentsMargins(20, 40, 20, 40)

        logo_label = QLabel("⚡ PRISMOV")
        logo_label.setObjectName("titleLabel")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFont(QFont("Arial", 22, QFont.Bold))
        sidebar_layout.addWidget(logo_label)
        
        subtitle_label = QLabel("Industrial Monitoring")
        subtitle_label.setObjectName("instr")
        subtitle_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(subtitle_label)

        self.chk_dark = QCheckBox("🌙 Dark Mode")
        self.chk_dark.stateChanged.connect(self.toggle_dark_mode)
        self.chk_dark.setFont(QFont("Arial", 11, QFont.Medium))
        sidebar_layout.addWidget(self.chk_dark)

        # Separador visual
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.1);")
        sidebar_layout.addWidget(separator)

        # Botón explicación RA
        self.btn_explicar = QPushButton("📚 RA Explanation")
        self.btn_explicar.clicked.connect(self.mostrar_explicacion_ra)
        self.btn_explicar.setFont(QFont("Arial", 12, QFont.Medium))
        sidebar_layout.addWidget(self.btn_explicar)
        
        sidebar_layout.addWidget(QLabel("🔐 Security"))
        self.btn_telegram = QPushButton("⚙️ Telegram")
        self.btn_telegram.clicked.connect(self.configurar_telegram)
        self.btn_telegram.setFont(QFont("Arial", 12, QFont.Medium))
        sidebar_layout.addWidget(self.btn_telegram)

        self.btn_logout = QPushButton("🚪 Logout")
        self.btn_logout.clicked.connect(self.logout_telegram)
        self.btn_logout.setObjectName("btnLogout")
        self.btn_logout.setFont(QFont("Arial", 12, QFont.Medium))
        sidebar_layout.addWidget(self.btn_logout)

        sidebar_layout.addWidget(QLabel("⏱ automation"))
        self.btn_prog = QPushButton("🕐 Configure Cron")
        self.btn_prog.clicked.connect(self.abrir_programacion)
        self.btn_prog.setFont(QFont("Arial", 12, QFont.Medium))
        sidebar_layout.addWidget(self.btn_prog)
        
        sidebar_layout.addWidget(QLabel("☁️ Cloud"))
        self.btn_auto = QPushButton("🚀 Automatic")
        self.btn_auto.clicked.connect(self.iniciar_modo_automatico)
        self.btn_auto.setFont(QFont("Arial", 12, QFont.Medium))
        sidebar_layout.addWidget(self.btn_auto)

        sidebar_layout.addStretch()
        
        # Footer en sidebar
        footer_label = QLabel("PRISMOV v2.0")
        footer_label.setObjectName("instr")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setFont(QFont("Arial", 9, QFont.Light))
        sidebar_layout.addWidget(footer_label)
        
        sidebar.setLayout(sidebar_layout)
        sidebar.setFixedWidth(300)
        main_layout.addWidget(sidebar)

        # =========================================================
        # 2. CONTENT AREA (Panel Central Dashboard)
        # =========================================================
        content_area = QFrame()
        content_area.setObjectName("contentArea")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(50, 50, 50, 50)
        content_layout.setSpacing(32)

        header_label = QLabel("🎯 Dashboard of Real Time Monitoring")
        header_label.setObjectName("headerLabel")
        header_label.setFont(QFont("Arial", 32, QFont.Bold))
        content_layout.addWidget(header_label)

        # ==================== DATA HISTORY FOR GRAPH ====================
        self.time_data = list(range(-60, 1))  # Last 60 seconds
        self.cpu_data = [0] * 61
        self.ram_data = [0] * 61

        # ==================== TOP METRICS & GAUGE ====================
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(30)

        # CPU Card
        cpu_card = QFrame()
        cpu_card.setObjectName("card")
        cpu_layout = QVBoxLayout()
        self.cpu_label = QLabel("⚡ CPU Real-Time")
        self.cpu_label.setObjectName("cardTitle")
        self.cpu_label.setFont(QFont("Arial", 15, QFont.Bold))
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setValue(0)
        self.cpu_bar.setTextVisible(True)
        self.cpu_bar.setMinimumHeight(28)
        cpu_layout.addWidget(self.cpu_label)
        cpu_layout.addWidget(self.cpu_bar)
        
        self.salud_label = QLabel("🟢 Optimal System")
        self.salud_label.setStyleSheet("font-size: 12px; color: #34c759; font-weight: 700; margin-top: 12px;")
        cpu_layout.addWidget(self.salud_label)
        cpu_card.setLayout(cpu_layout)
        metrics_layout.addWidget(cpu_card)

        # RAM Card
        ram_card = QFrame()
        ram_card.setObjectName("card")
        ram_layout = QVBoxLayout()
        self.ram_label = QLabel("🧠 RAM Real-Time")
        self.ram_label.setObjectName("cardTitle")
        self.ram_label.setFont(QFont("Arial", 15, QFont.Bold))
        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)
        self.ram_bar.setValue(0)
        self.ram_bar.setTextVisible(True)
        self.ram_bar.setMinimumHeight(28)
        ram_layout.addWidget(self.ram_label)
        ram_layout.addWidget(self.ram_bar)
        
        self.trend_label = QLabel("🟢 Resources Available")
        self.trend_label.setStyleSheet("font-size: 12px; color: #34c759; font-weight: 700; margin-top: 12px;")
        ram_layout.addWidget(self.trend_label)
        ram_card.setLayout(ram_layout)
        metrics_layout.addWidget(ram_card)

        content_layout.addLayout(metrics_layout)

        # ==================== MAIN GRAPHIC ====================
        graph_card = QFrame()
        graph_card.setObjectName("card")
        graph_layout = QVBoxLayout()
        graph_title = QLabel("📈 Historical Consumption Trends (Last Minute)")
        graph_title.setObjectName("cardTitle")
        graph_layout.addWidget(graph_title)

        pg.setConfigOptions(antialias=True)
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground("transparent")
        self.graph_widget.showGrid(x=True, y=True, alpha=0.1)
        self.graph_widget.setYRange(0, 100)
        self.graph_widget.setMouseEnabled(x=False, y=False)
        self.graph_widget.hideAxis('bottom')
        self.graph_widget.setLabel('left', 'Uso (%)', color='#b0b0b5', **{'font-size': '11pt'})
        
        # Gradientes para las líneas
        self.cpu_line = self.graph_widget.plot(
            self.time_data, self.cpu_data, 
            pen=pg.mkPen(color='#0a84ff', width=3),
            name="CPU",
            fillLevel=0,
            fillBrush=pg.mkBrush(10, 132, 255, 60)
        )
        self.ram_line = self.graph_widget.plot(
            self.time_data, self.ram_data, 
            pen=pg.mkPen(color='#30b0c0', width=3),
            name="RAM",
            fillLevel=0,
            fillBrush=pg.mkBrush(48, 176, 192, 60)
        )
        
        graph_layout.addWidget(self.graph_widget)
        graph_card.setLayout(graph_layout)
        content_layout.addWidget(graph_card)

        # ==================== PROCESSES AND TELEGRAM ====================
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(30)
        
        # Top Processes Table
        proc_card = QFrame()
        proc_card.setObjectName("card")
        proc_layout = QVBoxLayout()
        proc_title = QLabel("⚙️ Top Critical Processes")
        proc_title.setObjectName("cardTitle")
        proc_layout.addWidget(proc_title)
        
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Process", "CPU %", "RAM (MB)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setFixedHeight(180)
        proc_layout.addWidget(self.table)
        proc_card.setLayout(proc_layout)
        bottom_layout.addWidget(proc_card)

        # Actions & Telegram Card
        acc_card = QFrame()
        acc_card.setObjectName("card")
        acc_layout = QVBoxLayout()
        acc_title = QLabel("📲 Actions and Connectivity")
        acc_title.setObjectName("cardTitle")
        acc_layout.addWidget(acc_title)

        acciones_hlayout = QHBoxLayout()
        self.btn_analizar = QPushButton("📊 Audit")
        self.btn_analizar.clicked.connect(self.ejecutar_analisis)
        self.btn_analizar.setFont(QFont("Arial", 12, QFont.Medium))
        self.btn_analizar.setMinimumHeight(40)
        acciones_hlayout.addWidget(self.btn_analizar)

        self.btn_abrir_reporte = QPushButton("📄 Report")
        self.btn_abrir_reporte.clicked.connect(self.abrir_reporte)
        self.btn_abrir_reporte.setFont(QFont("Arial", 12, QFont.Medium))
        self.btn_abrir_reporte.setMinimumHeight(40)
        acciones_hlayout.addWidget(self.btn_abrir_reporte)

        self.btn_enviar_bot = QPushButton("📨 Send Bot")
        self.btn_enviar_bot.clicked.connect(self.enviar_analisis_bot)
        self.btn_enviar_bot.setFont(QFont("Arial", 12, QFont.Medium))
        self.btn_enviar_bot.setMinimumHeight(40)
        acciones_hlayout.addWidget(self.btn_enviar_bot)
        acc_layout.addLayout(acciones_hlayout)

        # Telegram Info
        self.info_telegram = QLabel("📱 TELEGRAM (Not linked)")
        self.info_telegram.setObjectName("instr")
        self.info_telegram.setFont(QFont("Arial", 11, QFont.Medium))
        acc_layout.addWidget(self.info_telegram)

        codigo = prismov.load_linking_code()
        self.codigo_label = QLabel(f"🔐 Code: {codigo}")
        self.codigo_label.setObjectName("instr")
        self.codigo_label.setFont(QFont("Arial", 10, QFont.Medium))
        acc_layout.addWidget(self.codigo_label)

        self.btn_nuevo_codigo = QPushButton("🔄 Re-Generate Code")
        self.btn_nuevo_codigo.clicked.connect(self.generar_nuevo_codigo)
        self.btn_nuevo_codigo.setFont(QFont("Arial", 11, QFont.Medium))
        acc_layout.addWidget(self.btn_nuevo_codigo)

        acc_card.setLayout(acc_layout)
        bottom_layout.addWidget(acc_card)

        content_layout.addLayout(bottom_layout)

        content_area.setLayout(content_layout)
        main_layout.addWidget(content_area)

        self.setLayout(main_layout)

        self.historial = prismov.load_history()
        self.auto_thread = None
        self.auto_activo = False

        # Timer for real-time graphics
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_graficos)
        self.timer.start(2000)  # Every 2 seconds

        self.update_telegram_status()
        self.apply_theme()
        self.historial = prismov.load_history()

    def actualizar_graficos(self):
        """Update real-time graphics and metrics with smooth animations"""
        try:
            import psutil
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            
            # --- Update Progress Bars with smooth animation ---
            self.cpu_bar.setValue(int(cpu))
            self.ram_bar.setValue(int(ram))
            
            # --- Determine health status and styling ---
            if cpu > 85:
                self.cpu_bar.setStyleSheet("""
                    QProgressBar {
                        border: none; border-radius: 10px;
                        background-color: #3a3a3f; text-align: center;
                        height: 24px; font-weight: 600; font-size: 11px;
                        color: #ffffff; padding: 2px;
                    }
                    QProgressBar::chunk {
                        background: linear-gradient(90deg, #ff453a, #ff6b5a);
                        border-radius: 8px; margin: 2px;
                    }
                """)
                self.salud_label.setText("🔴 CRITICAL RISK")
                self.salud_label.setStyleSheet("font-size: 14px; color: #ff453a; font-weight: 800; margin-top: 10px;")
            elif cpu > 60:
                self.cpu_bar.setStyleSheet("""
                    QProgressBar {
                        border: none; border-radius: 10px;
                        background-color: #3a3a3f; text-align: center;
                        height: 24px; font-weight: 600; font-size: 11px;
                        color: #ffffff; padding: 2px;
                    }
                    QProgressBar::chunk {
                        background: linear-gradient(90deg, #ff9500, #ffb84d);
                        border-radius: 8px; margin: 2px;
                    }
                """)
                self.salud_label.setText("🟠 HIGH LOAD")
                self.salud_label.setStyleSheet("font-size: 14px; color: #ff9500; font-weight: 800; margin-top: 10px;")
            else:
                self.cpu_bar.setStyleSheet("""
                    QProgressBar {
                        border: none; border-radius: 10px;
                        background-color: #3a3a3f; text-align: center;
                        height: 24px; font-weight: 600; font-size: 11px;
                        color: #ffffff; padding: 2px;
                    }
                    QProgressBar::chunk {
                        background: linear-gradient(90deg, #0a84ff, #30b0c0);
                        border-radius: 8px; margin: 2px;
                    }
                """)
                self.salud_label.setText("🟢 OPTIMAL SYSTEM")
                self.salud_label.setStyleSheet("font-size: 14px; color: #34c759; font-weight: 800; margin-top: 10px;")
                
            if ram > 85:
                self.ram_bar.setStyleSheet("""
                    QProgressBar {
                        border: none; border-radius: 10px;
                        background-color: #3a3a3f; text-align: center;
                        height: 24px; font-weight: 600; font-size: 11px;
                        color: #ffffff; padding: 2px;
                    }
                    QProgressBar::chunk {
                        background: linear-gradient(90deg, #ff453a, #ff6b5a);
                        border-radius: 8px; margin: 2px;
                    }
                """)
                self.trend_label.setText("🔴 MEMORY DANGER")
            elif ram > 60:
                self.ram_bar.setStyleSheet("""
                    QProgressBar {
                        border: none; border-radius: 10px;
                        background-color: #3a3a3f; text-align: center;
                        height: 24px; font-weight: 600; font-size: 11px;
                        color: #ffffff; padding: 2px;
                    }
                    QProgressBar::chunk {
                        background: linear-gradient(90deg, #ff9500, #ffb84d);
                        border-radius: 8px; margin: 2px;
                    }
                """)
                self.trend_label.setText("🟠 ATTENTION REQUIRED")
            else:
                self.ram_bar.setStyleSheet("""
                    QProgressBar {
                        border: none; border-radius: 10px;
                        background-color: #3a3a3f; text-align: center;
                        height: 24px; font-weight: 600; font-size: 11px;
                        color: #ffffff; padding: 2px;
                    }
                    QProgressBar::chunk {
                        background: linear-gradient(90deg, #34c759, #5ce55e);
                        border-radius: 8px; margin: 2px;
                    }
                """)
                self.trend_label.setText("🟢 RESOURCES AVAILABLE")

            # --- Update Historical Line Charts ---
            self.cpu_data = self.cpu_data[1:] + [cpu]
            self.ram_data = self.ram_data[1:] + [ram]
            
            self.cpu_line.setData(self.time_data, self.cpu_data)
            self.ram_line.setData(self.time_data, self.ram_data)

            # --- Update Top Processes Table ---
            procesos = []
            for p in psutil.process_iter():
                try:
                    procesos.append({
                        "name": p.name(),
                        "cpu": round(p.cpu_percent(interval=None) or 0.0, 1),
                        "ram": round(p.memory_info().rss / (1024*1024), 1)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                    
            # Sort by RAM
            procesos = sorted(procesos, key=lambda x: x["ram"], reverse=True)[:5]
            
            self.table.setRowCount(len(procesos))
            for row, val in enumerate(procesos):
                self.table.setItem(row, 0, QTableWidgetItem(str(val["name"])))
                self.table.setItem(row, 1, QTableWidgetItem(f"{val['cpu']}%"))
                self.table.setItem(row, 2, QTableWidgetItem(f"{val['ram']} MB"))
                
        except Exception as e:
            pass
 

    # ============================================================
    # PROFESSIONAL APPLE / iOS STYLING (Minimalist and Clean)
    # ============================================================

    def apply_theme(self):
        """Apply modern macOS theme with glassmorphism and neumorphism"""
        if self.dark_mode:
            # Paleta Oscura Premium (macOS Big Sur inspired)
            bg_main = "#0f0f0f"  # Fondo ultra oscuro
            bg_secondary = "#1a1a1a"  # Fondo secundario
            bg_card = "#242428"  # Tarjetas con tono gris
            bg_card_hover = "#2a2a2f"  # Hover effect
            
            text_primary = "#ffffff"  # Texto blanco puro
            text_secondary = "#b0b0b5"  # Texto secundario
            text_tertiary = "#7a7a7f"  # Texto terciario
            
            border_color = "#3a3a3f"  # Bordes finos
            border_light = "#4a4a4f"  # Bordes para hover
            
            accent_primary = "#0a84ff"  # Azul iOS
            accent_secondary = "#30b0c0"  # Cyan moderno
            accent_success = "#34c759"  # Verde iOS
            accent_warning = "#ff9500"  # Naranja
            accent_danger = "#ff453a"  # Rojo iOS
            
            gradient_start = "#1a1a2e"
            gradient_end = "#16213e"
            
        else:
            # Paleta Clara Premium (macOS Big Sur inspired)
            bg_main = "#f5f7fa"  # Gris perla muy claro
            bg_secondary = "#ffffff"  # Blanco puro
            bg_card = "#ffffff"  # Tarjetas blancas
            bg_card_hover = "#f9fafb"  # Hover effect ligero
            
            text_primary = "#000000"  # Texto negro puro
            text_secondary = "#6e7681"  # Texto secundario
            text_tertiary = "#8b949e"  # Texto terciario
            
            border_color = "#e5e7eb"  # Bordes finos
            border_light = "#d1d5db"  # Bordes para hover
            
            accent_primary = "#0066ff"  # Azul vibrante
            accent_secondary = "#00bcd4"  # Cyan moderno
            accent_success = "#10b981"  # Verde moderno
            accent_warning = "#f59e0b"  # Naranja
            accent_danger = "#ef4444"  # Rojo moderno
            
            gradient_start = "#f0f4f8"
            gradient_end = "#e8ecf1"

        # Font stack moderno
        font_family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif"

        stylesheet = f"""
            /* ============ GENERAL STYLING ============ */
            QWidget {{
                background-color: {bg_main};
                color: {text_primary};
                font-family: '{font_family}';
                font-size: 13px;
                outline: none;
            }}
            
            QWidget:focus {{
                outline: none;
            }}

            /* ============ SIDEBAR STYLING ============ */
            #sidebar {{
                background-color: {bg_card};
                border-right: 1px solid {border_color};
                padding: 0px;
            }}
            
            #sidebar QLabel {{
                color: {text_primary};
                font-weight: 600;
            }}

            /* ============ CONTENT AREA ============ */
            #contentArea {{
                background-color: {bg_main};
            }}
            
            #headerLabel {{
                font-size: 32px;
                font-weight: 800;
                color: {text_primary};
                letter-spacing: -0.8px;
                margin: 0px;
                padding: 0px;
            }}
            
            #titleLabel {{
                font-size: 28px;
                font-weight: 900;
                background: linear-gradient(135deg, {accent_primary}, {accent_secondary});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                letter-spacing: -0.5px;
                margin-bottom: 20px;
            }}

            /* ============ CARDS & FRAMES ============ */
            #card {{
                background-color: {bg_card};
                border: 1px solid {border_color};
                border-radius: 18px;
                padding: 22px;
                margin: 0px;
            }}
            
            #card:hover {{
                background-color: {bg_card_hover};
                border-color: {border_light};
            }}

            #cardTitle {{
                font-size: 16px;
                font-weight: 700;
                color: {text_primary};
                margin-bottom: 16px;
                letter-spacing: -0.3px;
            }}

            /* ============ PROGRESS BARS ============ */
            QProgressBar {{
                border: none;
                border-radius: 10px;
                background-color: {bg_secondary};
                text-align: center;
                height: 24px;
                font-weight: 600;
                font-size: 11px;
                color: {text_primary};
                padding: 2px;
            }}
            
            QProgressBar::chunk {{
                background: linear-gradient(90deg, {accent_primary}, {accent_secondary});
                border-radius: 8px;
                margin: 2px;
            }}

            /* ============ BUTTONS ============ */
            QPushButton {{
                background-color: {accent_primary};
                color: {text_primary};
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 14px;
                letter-spacing: -0.2px;
                transition: all 0.2s ease;
            }}
            
            QPushButton:hover {{
                background-color: {accent_secondary};
                transform: translateY(-2px);
                box-shadow: 0 8px 16px rgba(10, 132, 255, 0.2);
            }}
            
            QPushButton:pressed {{
                background-color: {accent_primary};
                padding-top: 11px;
                padding-bottom: 9px;
            }}
            
            QPushButton#btnLogout {{
                background-color: {accent_danger};
            }}
            
            QPushButton#btnLogout:hover {{
                background-color: {accent_warning};
            }}

            /* ============ LABELS ============ */
            QLabel {{
                color: {text_primary};
                background-color: transparent;
            }}
            
            QLabel#instr {{
                font-size: 12px;
                color: {text_secondary};
                font-weight: 500;
            }}

            /* ============ TEXT EDITING ============ */
            QTextEdit {{
                background-color: {bg_secondary};
                color: {text_primary};
                border: 1px solid {border_color};
                border-radius: 10px;
                padding: 12px;
                font-size: 13px;
                selection-background-color: {accent_primary};
            }}

            /* ============ CHECKBOXES ============ */
            QCheckBox {{
                color: {text_primary};
                font-weight: 500;
                spacing: 8px;
            }}
            
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 6px;
                border: 2px solid {border_color};
                background-color: {bg_secondary};
                margin-right: 6px;
            }}
            
            QCheckBox::indicator:hover {{
                border-color: {accent_primary};
                background-color: {bg_card_hover};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {accent_primary};
                border: 2px solid {accent_primary};
            }}

            /* ============ TABLES ============ */
            QTableWidget {{
                background-color: {bg_card};
                alternate-background-color: {bg_card_hover};
                border: 1px solid {border_color};
                border-radius: 12px;
                gridline-color: transparent;
                color: {text_primary};
                selection-background-color: rgba(10, 132, 255, 0.1);
            }}
            
            QTableWidget::item {{
                padding: 12px 8px;
                border: none;
                background-color: transparent;
            }}
            
            QTableWidget::item:selected {{
                background-color: {bg_card_hover};
            }}
            
            QHeaderView::section {{
                background-color: {bg_card};
                color: {text_secondary};
                padding: 10px 8px;
                border: none;
                border-bottom: 1px solid {border_color};
                font-weight: 600;
                font-size: 12px;
                text-align: left;
            }}

            /* ============ SCROLLBARS ============ */
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 10px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {border_light};
                min-height: 30px;
                border-radius: 5px;
                margin: 2px 2px 2px 2px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {accent_primary};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}

            /* ============ TIME EDIT & SPINBOX ============ */
            QTimeEdit, QSpinBox {{
                background-color: {bg_secondary};
                color: {text_primary};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 500;
            }}
            
            QTimeEdit:focus, QSpinBox:focus {{
                border: 2px solid {accent_primary};
                background-color: {bg_card_hover};
            }}

            /* ============ DIALOGS ============ */
            QDialog {{
                background-color: {bg_main};
            }}
        """

        self.setStyleSheet(stylesheet)

    def toggle_dark_mode(self):
        self.dark_mode = self.chk_dark.isChecked()
        self.apply_theme()

    # ============================================================
    # EXPLICACIÓN RA (VENTANA COMPLETA)
    # ============================================================

    def mostrar_explicacion_ra(self):
        texto = (
            "📘 **EXPLICACIÓN DE CUMPLIMIENTO DE RA**\n\n"
            "🔹 **RA 5b – Ciclo de vida del dato**\n"
            "La programación permite definir cuándo se generan datos, cómo se almacenan y cuándo se procesan.\n\n"
            "🔹 **RA 5f – Almacenaje en la nube**\n"
            "El modo automático simula almacenamiento periódico de datos y reportes.\n\n"
            "🔹 **RA 5i – Seguridad y regulación**\n"
            "La vinculación con Telegram usa códigos únicos y permite cerrar sesión para proteger datos.\n\n"
            "🔹 **RA 2e – Implicación THD en negocio y planta**\n"
            "El análisis evalúa el rendimiento y genera conclusiones útiles para ambos entornos.\n\n"
            "🔹 **RA 2g – Informe THD**\n"
            "Los reportes HTML relacionan tecnologías con sus áreas de aplicación.\n"
        )

        dialog = QDialog(self)
        dialog.setWindowTitle("Explicación de RA")
        v = QVBoxLayout(dialog)

        label = QTextEdit()
        label.setReadOnly(True)
        label.setText(texto)
        v.addWidget(label)

        btn = QPushButton("Cerrar")
        btn.clicked.connect(dialog.accept)
        v.addWidget(btn)

        dialog.exec_()

    # ============================================================
    # LÓGICA (SIN CAMBIOS)
    # ============================================================
    def ejecutar_analisis(self):
        """Ejecuta análisis y genera reporte"""
        try:
            filepath_reporte = prismov.ejecutar_analisis(self.historial)
            self.ultima_ruta_reporte = filepath_reporte
            self.historial = prismov.load_history()
            
            # Guardar el último snapshot para enviar al bot
            if self.historial:
                self.ultimo_snapshot = self.historial[-1]

            print("✔ Análisis ejecutado correctamente.\n")

            if QMessageBox.question(
                self,
                "✔ Análisis Completado",
                "¿Deseas abrir el reporte?",
                QMessageBox.Yes | QMessageBox.No
            ) == QMessageBox.Yes:

                prismov.abrir_reporte(filepath_reporte)

        except Exception as e:
            self.mostrar_error(e)

    def abrir_reporte(self):
        try:
            if hasattr(self, 'ultima_ruta_reporte'):
                prismov.abrir_reporte(self.ultima_ruta_reporte)
                return

            reportes = glob.glob(os.path.join(prismov.REPORTES_DIR, "*.html"))
            if reportes:
                reporte_reciente = max(reportes, key=os.path.getctime)
                prismov.abrir_reporte(reporte_reciente)
                self.ultima_ruta_reporte = reporte_reciente
            else:
                QMessageBox.warning(self, "Error", "No hay reportes generados.")

        except Exception as e:
            self.mostrar_error(e)

    def enviar_analisis_bot(self):
        """Envia el ultimo analisis al bot de Telegram"""
        if not hasattr(self, 'ultimo_snapshot'):
            QMessageBox.warning(self, "Sin Analisis", "Ejecuta un analisis primero.")
            return
        
        if not prismov.telegram_configurado():
            QMessageBox.warning(self, "Telegram No Configurado", 
                               "Configura Telegram primero en la seccion de Seguridad.")
            return
        
        try:
            success = prismov.enviar_reporte_telegram(self.ultimo_snapshot)
            if success:
                QMessageBox.information(self, "✔ Exito", 
                                       "Analisis enviado al bot de Telegram exitosamente!")
            else:
                QMessageBox.warning(self, "Error", 
                                   "No se pudo enviar el analisis. Verifica la configuracion de Telegram.")
        except Exception as e:
            self.mostrar_error(e)

    def configurar_telegram(self):
        chat_id, codigo_valido = prismov.obtener_chat_id_y_validar_codigo()
        print("RA: 5i) Seguridad de datos\n")

        if codigo_valido and chat_id:
            prismov.guardar_chat_id(chat_id)
            QMessageBox.information(self, "✔ Telegram Configurado",
                                    f"Chat ID: {chat_id}")
            self.update_telegram_status()
        else:
            QMessageBox.warning(self, "❌ Error",
                                "Código incorrecto o no detectado.")
            print("❌ Código incorrecto.\n")

    def generar_nuevo_codigo(self):
        nuevo_codigo = prismov.generate_new_linking_code()
        QMessageBox.information(self, "✔ Nuevo código generado",
                                f"Tu nuevo código es:\n\n{nuevo_codigo}")
        self.codigo_label.setText(f"📝 TU CÓDIGO DE VINCULACIÓN:\n{nuevo_codigo}")

    def refresh_telegram_section(self):
        if prismov.telegram_configurado():
            self.info_telegram.hide()
            self.codigo_label.hide()
            self.btn_nuevo_codigo.hide()
            self.btn_logout.show()
        else:
            self.info_telegram.show()
            self.codigo_label.show()
            self.btn_nuevo_codigo.show()
            self.btn_logout.hide()

    def update_telegram_status(self):
        if prismov.telegram_configurado():
            self.btn_telegram.setText("✔ Telegram Configurado")
        else:
            self.btn_telegram.setText("⚙️ Configurar Telegram")

        self.refresh_telegram_section()

    def logout_telegram(self):
        prismov.borrar_chat_id()
        QMessageBox.information(self, "✔ Sesión cerrada", "Telegram desconectado.")
        self.update_telegram_status()

    def iniciar_modo_automatico(self):
        if self.auto_activo:
            QMessageBox.information(self, "Modo automático", "Ya está en ejecución.")
            return

        self.auto_activo = True
        print("⏳ Modo automático iniciado...\n")

        self.auto_thread = threading.Thread(target=self.loop_automatico, daemon=True)
        self.auto_thread.start()

    def loop_automatico(self):
        while self.auto_activo:
            try:
                filepath_reporte = prismov.ejecutar_analisis(self.historial)
                self.ultima_ruta_reporte = filepath_reporte
                print("✔ Análisis automático ejecutado.\n")
            except Exception as e:
                print(f"❌ Error: {str(e)}\n")

            prog = prismov.load_scheduling()
            intervalo = prog.get("interval_minutes", 60)
            time.sleep(intervalo * 60)

    def abrir_programacion(self):
        ventana = VentanaProgramacion(self)
        ventana.exec_()

    def mostrar_error(self, error):
        QMessageBox.critical(self, "Error", str(error))
        print(f"❌ Error: {str(error)}\n")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    ventana = PrismovGUI()
    ventana.show()
    sys.exit(app.exec_())