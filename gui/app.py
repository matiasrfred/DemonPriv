# -*- coding: utf-8 -*-
"""
Módulo principal de la interfaz gráfica.
"""

import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from ttkthemes import ThemedTk
from datetime import datetime
import webbrowser
from config.settings import IMG_DIR, WINDOW_CONFIG
from config.database import DatabaseManager
from utils.logger import Logger
from utils.file_processor import FileProcessor
from gui.styles import setup_styles
from gui.tabs.config_tab import ConfigTab
from gui.tabs.directory_tab import DirectoryTab
from gui.tabs.print_tab import PrintTab
from gui.tabs.log_tab import LogTab

class Application:
    """Clase principal de la aplicación."""
    
    def __init__(self, root):
        """
        Inicializa la aplicación.
        
        Args:
            root: Ventana principal de la aplicación.
        """
        self.root = root
        self.is_running = False
        self.setup_window()
        self.load_icons()
        self.setup_frames()
        self.setup_notebook()
        self.setup_side_panel()
        
        # Cargar las pestañas
        self.log_tab = LogTab(self.notebook, self.icons)
        self.setup_logger()
        
        # Inicializar el procesador de archivos
        self.file_processor = FileProcessor(logger=self.logger)
        
        # Inicializar el gestor de base de datos
        self.db_manager = DatabaseManager(log_function=self.logger.log_message)
        
        # Crear las tablas en la base de datos
        self.db_manager.create_tables()
        
        # Cargar las pestañas que necesitan la base de datos y el logger
        self.config_tab = ConfigTab(self.notebook, self.icons, self.db_manager, self.logger)
        self.directory_tab = DirectoryTab(self.notebook, self.icons, self.db_manager, self.logger)
        self.print_tab = PrintTab(self.notebook, self.icons, self.db_manager, self.logger)
        
        # Iniciar la actualización del tiempo
        self.update_time()
        
        # Verificar si debe iniciar el procesamiento automáticamente
        self.check_autoprocess()
    
    def setup_window(self):
        """Configura la ventana principal."""
        self.root.geometry(WINDOW_CONFIG["geometry"])
        self.root.title(WINDOW_CONFIG["title"])
        self.root.resizable(*WINDOW_CONFIG["resizable"])
        self.root.iconbitmap(WINDOW_CONFIG["icon"])
    
    def load_icons(self):
        """Carga los íconos utilizados en la aplicación."""
        self.icons = {}
        
        # Cargar imágenes de iconos para las pestañas
        self.icons["config_icon"] = ImageTk.PhotoImage(Image.open(os.path.join(IMG_DIR, "config_icon.png")).resize((20, 20)))
        self.icons["folder_icon"] = ImageTk.PhotoImage(Image.open(os.path.join(IMG_DIR, "folder_icon.png")).resize((20, 20)))
        self.icons["printer_icon"] = ImageTk.PhotoImage(Image.open(os.path.join(IMG_DIR, "printer_icon.png")).resize((20, 20)))
        self.icons["log_process_icon"] = ImageTk.PhotoImage(Image.open(os.path.join(IMG_DIR, "log_process_icon.png")).resize((20, 20)))
        self.icons["log_error_icon"] = ImageTk.PhotoImage(Image.open(os.path.join(IMG_DIR, "log_error_icon.png")).resize((20, 20)))
        self.icons["help_icon"] = ImageTk.PhotoImage(Image.open(os.path.join(IMG_DIR, "help_icon.png")).resize((20, 20)))
        self.icons["fopen_icon"] = ImageTk.PhotoImage(Image.open(os.path.join(IMG_DIR, "folder_open.png")).resize((20, 20)))
        self.icons["clock_icon"] = ImageTk.PhotoImage(Image.open(os.path.join(IMG_DIR, "clock_icon.png")).resize((20, 20)))
        
        # Cargar imágenes de iconos para los botones
        self.icons["start_icon"] = ImageTk.PhotoImage(Image.open(os.path.join(IMG_DIR, "start_icon.png")).resize((20, 20)))
        self.icons["stop_icon"] = ImageTk.PhotoImage(Image.open(os.path.join(IMG_DIR, "stop_icon.png")).resize((20, 20)))
        self.icons["save_icon"] = ImageTk.PhotoImage(Image.open(os.path.join(IMG_DIR, "save_icon.png")).resize((20, 20)))
        self.icons["check_icon"] = ImageTk.PhotoImage(Image.open(os.path.join(IMG_DIR, "check_icon.png")).resize((20, 20)))
        self.icons["exit_icon"] = ImageTk.PhotoImage(Image.open(os.path.join(IMG_DIR, "exit_icon.png")).resize((20, 20)))
        self.icons["edit_icon"] = ImageTk.PhotoImage(Image.open(os.path.join(IMG_DIR, "edit_icon.png")).resize((14, 14)))
        self.icons["num_copias_img"] = ImageTk.PhotoImage(Image.open(os.path.join(IMG_DIR, "num_copias.png")).resize((32, 32)))
        
        # Imagen de logo
        self.icons["icon_image"] = ImageTk.PhotoImage(Image.open(os.path.join(IMG_DIR, "app_icon.png")))
        self.root.iconphoto(False, self.icons["icon_image"])
    
    def setup_frames(self):
        """Configura los frames principales de la aplicación."""
        # Crear un marco principal para el contenido
        self.main_frame = ttk.Frame(self.root, padding=5)
        self.main_frame.place(relx=0, rely=0, relwidth=0.85, relheight=1.0)  # Ocupa el 85% del ancho y 100% de la altura
        
        # Crear un frame para el panel lateral (botones) que ocupará el 15% del ancho
        self.side_panel = ttk.Frame(self.root, padding=10)
        self.side_panel.place(relx=0.85, rely=0, relwidth=0.15, relheight=1.0)
    
    def setup_notebook(self):
        """Configura el notebook (sistema de pestañas)."""
        self.notebook = ttk.Notebook(self.main_frame, takefocus=False)
        self.notebook.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
        
        # Configurar estilo para las pestañas
        self.style = setup_styles(self.root)
    
    def setup_logger(self):
        """Configura el sistema de logs."""
        self.logger = Logger(self.log_tab.log_textbox)
    
    def open_website(self):
        """Abre una página web en el navegador predeterminado."""
        try:
            url = "https://admin.qpos.io"  # Cambia esta URL por la que necesites
            
            # Registrar la acción en el log
            self.logger.log_message(f"Abriendo página web: {url}")
            
            # Abrir la página web
            webbrowser.open(url)
            
        except Exception as e:
            error_msg = f"Error al abrir el navegador: {str(e)}"
            self.logger.log_message(error_msg, "ERROR")
    
    def setup_side_panel(self):
        """Configura el panel lateral con botones y fecha/hora."""
        # Crear un Frame para el botón con borde de color
        self.button_frame = tk.Frame(self.side_panel, relief="solid", padx=5)
        self.button_frame.pack(side=tk.BOTTOM, anchor='se', fill=tk.X)
        self.button_frame.config(highlightbackground="red", highlightcolor="red", highlightthickness=2)
        
        # Crear los botones en el panel lateral
        self.exit_button = self.create_button(self.side_panel, "Salir", self.icons["exit_icon"], command=self.root.quit)
        self.check_button = self.create_button(self.side_panel, "Revisar", self.icons["check_icon"], command=self.open_website)

        
        # Crear el botón de inicio/detener dentro del Frame con borde
        self.start_button = self.create_button(self.button_frame, "Iniciar", self.icons["start_icon"], 
                                               command=self.toggle_process)
        
        # Crear los Labels para la fecha y hora
        self.date_text_label = ttk.Label(self.side_panel, text="Fecha de hoy:", font=("Arial", 10, "bold"))
        self.date_label = ttk.Label(self.side_panel, text="", font=("Arial", 8))
        self.time_text_label = ttk.Label(self.side_panel, text="Hora Actual:", font=("Arial", 10, "bold"))
        self.time_label = ttk.Label(self.side_panel, text="", font=("Arial", 8))
        
        # Empaquetar los Labels desde abajo hacia arriba
        self.time_label.pack(side=tk.BOTTOM, pady=(0, 10))
        self.time_text_label.pack(side=tk.BOTTOM, pady=(0, 5))
        self.date_label.pack(side=tk.BOTTOM, pady=(0, 10))
        self.date_text_label.pack(side=tk.BOTTOM, pady=(0, 5))
    
    def create_button(self, parent, text, image, command=None):
        """
        Crea un botón con imagen y texto.
        
        Args:
            parent: Widget padre.
            text: Texto del botón.
            image: Imagen para el botón.
            command: Función a ejecutar al hacer clic.
            
        Returns:
            ttk.Button: Botón creado.
        """
        button = ttk.Button(parent, text=text, image=image, compound=tk.LEFT, takefocus=False, command=command)
        button.pack(side=tk.BOTTOM, anchor='se', pady=5, fill=tk.X)
        return button
    
    def update_time(self):
        """Actualiza la fecha y hora en el panel lateral."""
        now = datetime.now()
        self.date_label.config(text=now.strftime("%d/%m/%Y"))
        self.time_label.config(text=now.strftime("%H:%M:%S"))
        self.root.after(1000, self.update_time)  # Actualizar cada 1 segundo
    
    def check_autoprocess(self):
        """Verifica si debe iniciar el procesamiento automáticamente."""
        try:
            # Verificar si el procesamiento automático está habilitado
            autoprocess_enabled = self.db_manager.get_autoprocess_config()
            
            if autoprocess_enabled:
                self.logger.log_message("Iniciando procesamiento automáticamente...", "INFO")
                # Programar el inicio del proceso para que se ejecute después de cargar completamente la aplicación
                self.root.after(1000, self.iniciar_proceso_automatico)
                
        except Exception as e:
            self.logger.log_message(f"Error al verificar inicio automático: {e}", "ERROR")
    
    def iniciar_proceso_automatico(self):
        """Inicia el procesamiento de archivos automáticamente."""
        try:
            # Verificar el estado de los campos clave
            campos = [
                (self.config_tab.razon_social_entry, "Configuración"),
                (self.directory_tab.process_dir_entry, "Directorios"),
                (self.print_tab.num_copias_spinbox, "Impresión")
            ]
            
            for campo, nombre_pestana in campos:
                if not self.verificar_estado_campo(campo, nombre_pestana, mostrar_error=False):
                    self.logger.log_message(f"No se pudo iniciar automáticamente: Pestaña {nombre_pestana} no está correctamente configurada.", "ERROR")
                    return
            
            # Obtener valores de las rutas y el intervalo
            ruta_procesar = self.directory_tab.process_dir_entry.get()
            ruta_procesado = self.directory_tab.processed_dir_entry.get()
            intervalo = int(self.directory_tab.spinbox.get())
            
            # Validar que las rutas no estén vacías
            if not ruta_procesar or not ruta_procesado:
                self.logger.log_message("Rutas no configuradas. No se puede iniciar automáticamente.", "ERROR")
                return
            
            # Actualizar el botón y el borde
            self.start_button.config(text="Detener", image=self.icons["stop_icon"])
            self.button_frame.config(highlightbackground="green", highlightcolor="green")
            self.is_running = True
            
            # Iniciar el procesamiento de archivos
            self.file_processor.start()
            self.file_processor.process_files(ruta_procesar, ruta_procesado, intervalo, self.root)
            
            self.logger.log_message("Proceso iniciado automáticamente.", "INFO")
            self.logger.log_message_sindb("--------------------------------------------------------------------------------------------------------------", "INFO")
            
        except Exception as e:
            self.logger.log_message(f"Error al iniciar proceso automático: {e}", "ERROR")
    
    def verificar_estado_campo(self, campo, nombre_pestana, mostrar_error=True):
        """
        Verifica si el campo está en estado 'disabled'.
        
        Args:
            campo: Widget a verificar.
            nombre_pestana: Nombre de la pestaña a la que pertenece el campo.
            mostrar_error: Si se debe mostrar un messagebox de error.
            
        Returns:
            bool: True si el campo está en estado 'disabled', False en caso contrario.
        """
        estado = str(campo.cget("state"))
        
        if estado != "disabled":
            self.logger.log_message_sindb("--------------------------------------------------------------------------------------------------------------", "INFO")
            self.logger.log_message(f"Error: Pestaña {nombre_pestana} tiene cambios sin guardar.", "ERROR")
            
            if mostrar_error:
                tk.messagebox.showerror("Error", f"Pestaña {nombre_pestana} tiene cambios sin guardar")
                
            return False
        return True
    
    def toggle_process(self):
        """Inicia o detiene el procesamiento de archivos."""
        try:
            self.logger.log_message("Intentando iniciar proceso...", "INFO")
            
            # Verificar el estado de los campos clave
            campos = [
                (self.config_tab.razon_social_entry, "Configuración"),
                (self.directory_tab.process_dir_entry, "Directorios"),
                (self.print_tab.num_copias_spinbox, "Impresión")
            ]
            
            for campo, nombre_pestana in campos:
                if not self.verificar_estado_campo(campo, nombre_pestana):
                    return
            
            # Toggle el estado de ejecución
            if self.is_running:
                self.logger.log_message("Deteniendo proceso...", "INFO")
                self.start_button.config(text="Iniciar", image=self.icons["start_icon"])
                self.button_frame.config(highlightbackground="red", highlightcolor="red")
                self.is_running = False
                self.file_processor.stop()
                self.logger.log_message("Proceso detenido correctamente.", "INFO")
                self.logger.log_message_sindb("--------------------------------------------------------------------------------------------------------------", "INFO")
            else:
                # Obtener valores de las rutas y el intervalo
                ruta_procesar = self.directory_tab.process_dir_entry.get()
                ruta_procesado = self.directory_tab.processed_dir_entry.get()
                intervalo = int(self.directory_tab.spinbox.get())
                
                # Validar que las rutas no estén vacías
                if not ruta_procesar or not ruta_procesado:
                    self.logger.log_message("Rutas no configuradas. Por favor, complete las rutas.", "ERROR")
                    tk.messagebox.showerror("Error", "Las rutas de procesar y procesado deben estar configuradas.")
                    return
                
                self.logger.log_message("Iniciando proceso...", "INFO")
                self.start_button.config(text="Detener", image=self.icons["stop_icon"])
                self.button_frame.config(highlightbackground="green", highlightcolor="green")
                self.is_running = True
                self.file_processor.start()
                
                # Iniciar el procesamiento de archivos
                self.file_processor.process_files(ruta_procesar, ruta_procesado, intervalo, self.root)
                self.logger.log_message("Proceso iniciado correctamente.", "INFO")
                self.logger.log_message_sindb("--------------------------------------------------------------------------------------------------------------", "INFO")
                
        except Exception as e:
            self.logger.log_message(f"Error al intentar iniciar o detener el proceso: {e}", "ERROR")
            tk.messagebox.showerror("Error", f"Ocurrió un error durante el proceso: {e}")

def create_app():
    """
    Crea la aplicación principal.
    
    Returns:
        ThemedTk: Instancia de la ventana principal.
    """
    # Crear la ventana principal usando ThemedTk con el tema Scid (Lima)
    root = ThemedTk(theme="scidgreen")
    
    # Inicializar la aplicación
    app = Application(root)
    
    return root