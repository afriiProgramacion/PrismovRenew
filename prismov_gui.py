import sys
import threading
import os
import glob
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QTextEdit, QLabel, QMessageBox, QDialog, QCheckBox,
    QHBoxLayout, QTimeEdit, QSpinBox, QGridLayout, QProgressBar, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QTime, QTimer
from PyQt5.QtWidgets import QWidget, QMessageBox, QInputDialog
import pyqtgraph as pg

import prismov


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
        self.setWindowTitle("Configurar programación - RA: Criterio 5b) Ciclo de vida del dato")
        self.setGeometry(300, 300, 400, 300)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Selecciona los días:"))
        dias_layout = QGridLayout()

        self.dias_check = {}
        dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]

        for i, d in enumerate(dias):
            chk = QCheckBox(d.capitalize())
            self.dias_check[d] = chk
            dias_layout.addWidget(chk, i // 2, i % 2)

        layout.addLayout(dias_layout)

        layout.addWidget(QLabel("Hora de inicio:"))
        self.hora_inicio = QTimeEdit()
        self.hora_inicio.setDisplayFormat("HH:mm")
        layout.addWidget(self.hora_inicio)

        layout.addWidget(QLabel("Hora de fin:"))
        self.hora_fin = QTimeEdit()
        self.hora_fin.setDisplayFormat("HH:mm")
        layout.addWidget(self.hora_fin)

        layout.addWidget(QLabel("Intervalo (minutos):"))
        self.intervalo = QSpinBox()
        self.intervalo.setRange(1, 1440)
        layout.addWidget(self.intervalo)

        btn_guardar = QPushButton("Guardar programación")
        btn_guardar.clicked.connect(self.guardar)
        layout.addWidget(btn_guardar)

        self.setLayout(layout)
        self.cargar_programacion()

    def cargar_programacion(self):
        prog = prismov.cargar_programacion()

        for d in prog["dias"]:
            if d in self.dias_check:
                self.dias_check[d].setChecked(True)

        self.hora_inicio.setTime(QTime.fromString(prog["hora_inicio"], "HH:mm"))
        self.hora_fin.setTime(QTime.fromString(prog["hora_fin"], "HH:mm"))
        self.intervalo.setValue(prog["intervalo_minutos"])

    def guardar(self):
        dias = [d for d, chk in self.dias_check.items() if chk.isChecked()]

        nueva_prog = {
            "activo": True,
            "dias": dias,
            "hora_inicio": self.hora_inicio.time().toString("HH:mm"),
            "hora_fin": self.hora_fin.time().toString("HH:mm"),
            "intervalo_minutos": self.intervalo.value()
        }

        prismov.guardar_programacion(nueva_prog)
        QMessageBox.information(self, "Guardado", "Programación guardada correctamente.")
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

        self.setWindowTitle("PRISMOV - Control Panel y Monitoreo THD")
        self.setGeometry(100, 100, 1200, 800)  # Ventana más grande por defecto
        # Permitir pantalla completa / maximizado por defecto
        self.showMaximized()

        self.dark_mode = False

        # Layout Principal Horizontal (Sidebar + Contenido)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =========================================================
        # 1. SIDEBAR (Lateral Izquierdo)
        # =========================================================
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(20)
        sidebar_layout.setContentsMargins(20, 40, 20, 20)

        logo_label = QLabel("⚡ PRISMOV\nIndustrial")
        logo_label.setObjectName("titleLabel")
        logo_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo_label)

        self.chk_dark = QCheckBox("🌙 Modo oscuro")
        self.chk_dark.stateChanged.connect(self.toggle_dark_mode)
        sidebar_layout.addWidget(self.chk_dark)

        # Botón explicación RA
        self.btn_explicar = QPushButton("📚 Explicación de RA")
        self.btn_explicar.clicked.connect(self.mostrar_explicacion_ra)
        sidebar_layout.addWidget(self.btn_explicar)
        
        sidebar_layout.addWidget(QLabel("RA: 5i) Seguridad y regulación"))
        self.btn_telegram = QPushButton("⚙️ Configurar Telegram")
        self.btn_telegram.clicked.connect(self.configurar_telegram)
        sidebar_layout.addWidget(self.btn_telegram)

        self.btn_logout = QPushButton("🚪 Cerrar sesión Telegram")
        self.btn_logout.clicked.connect(self.logout_telegram)
        self.btn_logout.setObjectName("btnLogout")
        sidebar_layout.addWidget(self.btn_logout)

        sidebar_layout.addWidget(QLabel("RA: 5b) Ciclo de vida"))
        self.btn_prog = QPushButton("⏱ Configurar Cron")
        self.btn_prog.clicked.connect(self.abrir_programacion)
        sidebar_layout.addWidget(self.btn_prog)
        
        sidebar_layout.addWidget(QLabel("RA: 5f) Almacenaje en nube"))
        self.btn_auto = QPushButton("🚀 Iniciar Modo Auto")
        self.btn_auto.clicked.connect(self.iniciar_modo_automatico)
        sidebar_layout.addWidget(self.btn_auto)

        sidebar_layout.addStretch()
        sidebar.setLayout(sidebar_layout)
        sidebar.setFixedWidth(280)
        main_layout.addWidget(sidebar)

        # =========================================================
        # 2. CONTENT AREA (Panel Central Dashboard)
        # =========================================================
        content_area = QFrame()
        content_area.setObjectName("contentArea")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)

        header_label = QLabel("Dashboard de Consumo y Diagnóstico THD")
        header_label.setObjectName("headerLabel")
        content_layout.addWidget(header_label)

        # ==================== DATA HISTORY FOR GRAPH ====================
        self.time_data = list(range(-60, 1))  # Last 60 seconds
        self.cpu_data = [0] * 61
        self.ram_data = [0] * 61

        # ==================== TOP METRICS & GAUGE ====================
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(30)

        # Tarjeta CPU
        cpu_card = QFrame()
        cpu_card.setObjectName("card")
        cpu_layout = QVBoxLayout()
        self.cpu_label = QLabel("⚡ CPU en Tiempo Real (%)")
        self.cpu_label.setObjectName("cardTitle")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setValue(0)
        self.cpu_bar.setTextVisible(True)
        cpu_layout.addWidget(self.cpu_label)
        cpu_layout.addWidget(self.cpu_bar)
        
        self.salud_label = QLabel("Estado: Evaluando...")
        self.salud_label.setStyleSheet("font-size: 14px; color: #718096; font-weight: bold; margin-top: 10px;")
        cpu_layout.addWidget(self.salud_label)
        cpu_card.setLayout(cpu_layout)
        metrics_layout.addWidget(cpu_card)

        # Tarjeta RAM
        ram_card = QFrame()
        ram_card.setObjectName("card")
        ram_layout = QVBoxLayout()
        self.ram_label = QLabel("🧠 RAM en Tiempo Real (%)")
        self.ram_label.setObjectName("cardTitle")
        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)
        self.ram_bar.setValue(0)
        self.ram_bar.setTextVisible(True)
        ram_layout.addWidget(self.ram_label)
        ram_layout.addWidget(self.ram_bar)
        
        self.trend_label = QLabel("Tendencia: Estable")
        self.trend_label.setStyleSheet("font-size: 14px; color: #718096; font-weight: bold; margin-top: 10px;")
        ram_layout.addWidget(self.trend_label)
        ram_card.setLayout(ram_layout)
        metrics_layout.addWidget(ram_card)

        content_layout.addLayout(metrics_layout)

        # ==================== MAIN GRAPHIC ====================
        graph_card = QFrame()
        graph_card.setObjectName("card")
        graph_layout = QVBoxLayout()
        graph_title = QLabel("📈 Tendencia Histórica de Consumo (Último Minuto)")
        graph_title.setObjectName("cardTitle")
        graph_layout.addWidget(graph_title)

        pg.setConfigOptions(antialias=True)
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground("transparent")
        self.graph_widget.showGrid(x=True, y=True, alpha=0.3)
        self.graph_widget.setYRange(0, 100)
        self.graph_widget.setMouseEnabled(x=False, y=False)
        self.graph_widget.hideAxis('bottom')
        
        self.cpu_line = self.graph_widget.plot(self.time_data, self.cpu_data, pen=pg.mkPen(color='#3182CE', width=3), name="CPU")
        self.ram_line = self.graph_widget.plot(self.time_data, self.ram_data, pen=pg.mkPen(color='#D69E2E', width=3), name="RAM")
        
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
        proc_title = QLabel("⚙️ Top Procesos Críticos")
        proc_title.setObjectName("cardTitle")
        proc_layout.addWidget(proc_title)
        
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Proceso", "CPU %", "RAM (MB)"])
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
        acc_title = QLabel("📲 Acciones y Conectividad")
        acc_title.setObjectName("cardTitle")
        acc_layout.addWidget(acc_title)

        acciones_hlayout = QHBoxLayout()
        self.btn_analizar = QPushButton("📊 Forzar Auditoría (RA 2e)")
        self.btn_analizar.clicked.connect(self.ejecutar_analisis)
        acciones_hlayout.addWidget(self.btn_analizar)

        self.btn_abrir_reporte = QPushButton("📄 Abrir Reporte (RA 2g)")
        self.btn_abrir_reporte.clicked.connect(self.abrir_reporte)
        acciones_hlayout.addWidget(self.btn_abrir_reporte)
        acc_layout.addLayout(acciones_hlayout)

        self.info_telegram = QLabel("📱 TELEGRAM (Pendiente vincular)")
        self.info_telegram.setObjectName("infoTelegram")
        acc_layout.addWidget(self.info_telegram)

        codigo = prismov.cargar_codigo_vinculacion()
        self.codigo_label = QLabel(f"📝 Código: {codigo}")
        self.codigo_label.setObjectName("instr")
        acc_layout.addWidget(self.codigo_label)

        self.btn_nuevo_codigo = QPushButton("🔄 Re-Generar Código")
        self.btn_nuevo_codigo.clicked.connect(self.generar_nuevo_codigo)
        acc_layout.addWidget(self.btn_nuevo_codigo)

        acc_card.setLayout(acc_layout)
        bottom_layout.addWidget(acc_card)

        content_layout.addLayout(bottom_layout)

        content_area.setLayout(content_layout)
        main_layout.addWidget(content_area)

        self.setLayout(main_layout)

        self.historial = prismov.cargar_historial()
        self.auto_thread = None
        self.auto_activo = False

        # Timer para gráficos en tiempo real
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_graficos)
        self.timer.start(2000)  # Cada 2 segundos

        self.update_telegram_status()
        self.apply_theme()
        self.historial = prismov.cargar_historial()

    def actualizar_graficos(self):
        try:
            import psutil
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            
            # --- Update Progress Bars and Health Labels ---
            self.cpu_bar.setValue(int(cpu))
            self.ram_bar.setValue(int(ram))
            
            if cpu > 85:
                self.cpu_bar.setStyleSheet("QProgressBar::chunk { background-color: #E53E3E; border-radius: 6px; }")
                self.salud_label.setText("⚠ Riesgo Crítico")
                self.salud_label.setStyleSheet("font-size: 16px; color: #E53E3E; font-weight: 800; margin-top: 10px;")
            elif cpu > 60:
                self.cpu_bar.setStyleSheet("QProgressBar::chunk { background-color: #D69E2E; border-radius: 6px; }")
                self.salud_label.setText("⚠ Carga Elevada")
                self.salud_label.setStyleSheet("font-size: 16px; color: #D69E2E; font-weight: 800; margin-top: 10px;")
            else:
                self.cpu_bar.setStyleSheet("") # Vuelve al de apply_theme
                self.salud_label.setText("✅ Sistema Óptimo")
                self.salud_label.setStyleSheet("font-size: 16px; color: #38A169; font-weight: 800; margin-top: 10px;")
                
            if ram > 85:
                self.ram_bar.setStyleSheet("QProgressBar::chunk { background-color: #E53E3E; border-radius: 6px; }")
                self.trend_label.setText("Tendencia: Peligro de Memoria")
            elif ram > 60:
                self.ram_bar.setStyleSheet("QProgressBar::chunk { background-color: #D69E2E; border-radius: 6px; }")
                self.trend_label.setText("Tendencia: Atención Requerida")
            else:
                self.ram_bar.setStyleSheet("")
                self.trend_label.setText("Tendencia: Reservas Disponibles")

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
    # ESTILO PROFESIONAL APPLE / iOS (Minimalista y Limpio)
    # ============================================================

    def apply_theme(self):
        # Colores inspirados en Human Interface Guidelines de Apple
        if self.dark_mode:
            bg_main = "#000000"  # Fondo principal negro puro
            bg_card = "#1C1C1E"  # Tarjetas gris muy oscuro espacial
            text_color = "#F2F2F7"
            text_secondary = "#EBEBF5" # 60% opacidad blanco
            border_color = "#38383A"
            
            btn_bg = "#0A84FF"  # Azul iOS oscuro
            btn_hover = "#0062CC"
            
            btn_danger = "#FF453A" # Rojo iOS oscuro
            btn_danger_hover = "#D70015"
            
            progress_bg = "#38383A"
        else:
            bg_main = "#F2F2F7"  # Gris perla muy claro (fondo por defecto iOS)
            bg_card = "#FFFFFF"  # Blancos puros para las tarjetas
            text_color = "#000000"
            text_secondary = "#8E8E93" # Gris secundario
            border_color = "#E5E5EA"
            
            btn_bg = "#007AFF"   # Azul iOS claro
            btn_hover = "#0056B3"
            
            btn_danger = "#FF3B30" # Rojo iOS claro
            btn_danger_hover = "#C5000B"
            
            progress_bg = "#E5E5EA"

        # Font stack nativo de Apple (San Francisco)
        font_family = "system-ui, -apple-system, 'SF Pro Display', 'San Francisco', 'Helvetica Neue', Arial, sans-serif"

        stylesheet = f"""
            QWidget {{
                background-color: {bg_main};
                color: {text_color};
                font-family: {font_family};
                font-size: 14px;
            }}

            #sidebar {{
                background-color: {bg_card};
                border-right: 1px solid {border_color};
            }}
            
            #contentArea {{
                background-color: transparent;
            }}
            
            #titleLabel {{
                font-size: 26px;
                font-weight: 800;
                color: {btn_bg};
                margin-bottom: 20px;
                letter-spacing: -0.5px;
            }}
            
            #headerLabel {{
                font-size: 30px;
                font-weight: 700;
                color: {text_color};
                letter-spacing: -0.5px;
            }}

            #card {{
                background-color: {bg_card};
                border: 1px solid {border_color};
                border-radius: 16px;
                padding: 16px;
            }}

            #cardTitle {{
                font-size: 17px;
                font-weight: 600;
                color: {text_color};
                margin-bottom: 10px;
                letter-spacing: -0.3px;
            }}

            /* Progress Bar Styling - Minimalista */
            QProgressBar {{
                border: none;
                border-radius: 10px;
                background-color: {progress_bg};
                text-align: center;
                height: 20px;
                font-weight: 600;
                font-size: 12px;
                color: #FFFFFF;
            }}
            QProgressBar::chunk {{
                background-color: {btn_bg};
                border-radius: 10px;
            }}

            /* Tarjetas y zonas de texto */
            QTextEdit, QLabel#infoTelegram, QLabel#instr {{
                background: {bg_card};
                border: 1px solid {border_color};
                border-radius: 12px;
                padding: 12px;
                selection-background-color: {btn_bg};
                color: {text_color};
            }}

            /* Scrollbars */
            QScrollBar:vertical {{
                border: none;
                background: {bg_main};
                width: 8px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: #C6C6C8;
                min-height: 30px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #AEAEB2;
            }}

            QLabel#raLabel {{
                font-style: italic;
                font-size: 13px;
                color: {text_secondary};
            }}

            /* Botones estilo iOS */
            QPushButton {{
                background: {btn_bg};
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                padding: 10px 18px;
                font-weight: 600;
                font-size: 15px;
                letter-spacing: -0.2px;
            }}

            QPushButton:hover {{
                background: {btn_hover};
            }}

            QPushButton:pressed {{
                background-color: {btn_bg};
                padding-top: 11px;
                padding-bottom: 9px;
                opacity: 0.8;
            }}

            /* Botón de Logout (Destructive Action) */
            QPushButton#btnLogout {{
                background: {btn_danger};
                color: white;
            }}

            QPushButton#btnLogout:hover {{
                background: {btn_danger_hover};
            }}
            
            /* Checkbox estilo switch simplificado */
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
                border-radius: 11px;
                border: 1px solid {border_color};
                background: {progress_bg};
            }}
            QCheckBox::indicator:checked {{
                background-color: {btn_bg};
                border: none;
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0yMC4yODUgNWwteC0uMDE1IDEuNDE1LS4wMTUgOSAwIDEzLjc4NS04LjIxNUw1LDI4NSAxMy4yMTUgNS4yODUgMTRsLTEuNDE1LS4wMTUgNC4yODUiLz48L3N2Zz4=);
            }}
            
            /* Tablas Dashboard Minimalista */
            QTableWidget {{
                background-color: {bg_card};
                border: none;
                border-radius: 12px;
                gridline-color: transparent;
                selection-background-color: rgba(0, 122, 255, 0.15);
                color: {text_color};
            }}
            QHeaderView::section {{
                background-color: {bg_card};
                border: none;
                border-bottom: 1px solid {border_color};
                padding: 8px 4px;
                font-weight: 600;
                font-size: 13px;
                color: {text_secondary};
                text-align: left;
            }}
            QTableWidget::item {{
                padding-left: 5px;
                border-bottom: 1px solid {border_color};
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

        try:
            filepath_reporte = prismov.ejecutar_analisis(self.historial)

            self.ultima_ruta_reporte = filepath_reporte

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
        nuevo_codigo = prismov.generar_nuevo_codigo()
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

            prog = prismov.cargar_programacion()
            intervalo = prog.get("intervalo_minutos", 60)
            prismov.time.sleep(intervalo * 60)

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
    ventana = PrismovGUI()
    ventana.show()
    sys.exit(app.exec_())
