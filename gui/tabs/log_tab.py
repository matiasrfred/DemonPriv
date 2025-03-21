# -*- coding: utf-8 -*-
"""
Módulo para la pestaña de Log Procesos.
"""

from datetime import datetime
import os
import sys
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
import openpyxl
from tkcalendar import DateEntry
from config.settings import DB_CONFIG

class LogTab:
    """Clase para gestionar la pestaña de Log Procesos."""
    
    def __init__(self, notebook, icons):
        """
        Inicializa la pestaña de Log Procesos.
        
        Args:
            notebook: Notebook donde se añadirá la pestaña.
            icons: Diccionario con los iconos de la aplicación.
        """
        self.notebook = notebook
        self.icons = icons
        self.setup_tab()
    
    def setup_tab(self):
        """Configura los elementos de la pestaña."""
        # Crear la pestaña de Log Procesos
        self.log_process_frame = ttk.Frame(self.notebook)
        self.add_tab(self.notebook, self.log_process_frame, "Log Procesos", self.icons["log_process_icon"])
        
        # Configuración del grid en el contenedor principal para que los elementos se expandan
        self.log_process_frame.columnconfigure(0, weight=1)
        self.log_process_frame.rowconfigure(1, weight=1)  # La segunda fila se expande para el Textbox
        
        # LabelFrame para "Revisión Logs" en la parte superior
        self.log_revision_labelframe = ttk.LabelFrame(self.log_process_frame, text="Revisión Logs", style="Custom.TLabelframe")
        self.log_revision_labelframe.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # DatePicker debajo del Label
        self.date_picker = DateEntry(self.log_revision_labelframe, width=15, background='darkblue', 
                                    foreground='white', borderwidth=2)
        self.date_picker.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        # Botón para Confirmar
        self.confirm_button = ttk.Button(self.log_revision_labelframe, text="Confirmar", command=self.filter_logs)
        self.confirm_button.grid(row=1, column=1, padx=5, pady=10, sticky="w")
        
        # LabelFrame para el "Log Procesos" que contendrá el Textbox, en la parte inferior
        self.log_text_labelframe = ttk.LabelFrame(self.log_process_frame, text="Log Procesos", style="Custom.TLabelframe")
        self.log_text_labelframe.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Crear un Scrollbar y asociarlo con el Textbox
        self.scrollbar = ttk.Scrollbar(self.log_text_labelframe, orient="vertical")
        self.scrollbar.grid(row=0, column=1, sticky="ns")  # Colocarlo a la derecha del Textbox
        
        # Textbox grande dentro del LabelFrame "Log Procesos"
        self.log_textbox = tk.Text(self.log_text_labelframe, wrap=tk.WORD, yscrollcommand=self.scrollbar.set)
        self.log_textbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Reducir el interlineado
        self.log_textbox.config(font=("Helvetica", 8), spacing1=0, spacing2=0, spacing3=0)
        
        # Configurar el Scrollbar para desplazarse con el Textbox
        self.scrollbar.config(command=self.log_textbox.yview)
        
        # Configurar el Textbox para ser solo lectura y ocultar el parpadeo del cursor
        self.log_textbox.config(insertontime=0, state=tk.DISABLED)
        
        # Expansión del Textbox dentro del LabelFrame "Log Procesos"
        self.log_text_labelframe.rowconfigure(0, weight=1)
        self.log_text_labelframe.columnconfigure(0, weight=1)
    
    def add_tab(self, notebook, frame, text, image):
        """
        Añade una pestaña al notebook con un icono.
        
        Args:
            notebook: Notebook donde se añadirá la pestaña.
            frame: Frame que contendrá el contenido de la pestaña.
            text: Texto que se mostrará en la pestaña.
            image: Icono que se mostrará en la pestaña.
        """
        text_with_spaces = f" {text} "
        notebook.add(frame, text=text_with_spaces, image=image, compound=tk.LEFT)
    
    def update_log_textbox(self, message, tipo="INFO"):
        """
        Actualiza el textbox de logs con un nuevo mensaje usando el formato estándar.
        
        Args:
            message: Mensaje que se añadirá al textbox.
            tipo: Tipo de mensaje (INFO, ERROR, etc.).
        """
        # Habilitar el textbox para escritura
        self.log_textbox.config(state=tk.NORMAL)
        
        # Añadir fecha y hora al mensaje con el formato estándar
        current_date = datetime.now().strftime("%d/%m/%Y")
        current_time = datetime.now().strftime("%H:%M:%S")
        log_message = f"{current_date} {current_time} - [{tipo}] {message}\n"
        
        # Insertar el mensaje al final
        self.log_textbox.insert(tk.END, log_message)
        
        # Desplazar hacia abajo para mostrar el mensaje más reciente
        self.log_textbox.see(tk.END)
        
        # Deshabilitar el textbox de nuevo
        self.log_textbox.config(state=tk.DISABLED)

    def filter_logs(self):
        """
        Filtra los logs según la fecha seleccionada, consulta la base de datos
        y muestra los resultados en Excel.
        """
        try:
            # Obtener la fecha seleccionada (formato dd/mm/yyyy)
            selected_date = self.date_picker.get_date().strftime("%d/%m/%Y")
            self.update_log_textbox(f"Fecha seleccionada: {selected_date}")
            
            # Usar la ruta configurada en settings.py para la base de datos
            db_path = DB_CONFIG["path"]
            
            self.update_log_textbox(f"Buscando base de datos en: {db_path}")
            
            # Verificar si existe la base de datos
            if not os.path.exists(db_path):
                self.update_log_textbox("Error: No se encontró la base de datos config.db", "ERROR")
                messagebox.showerror("Error", "No se encontró la base de datos config.db")
                return
            
            # Conectar a la base de datos
            self.update_log_textbox("Conectando a la base de datos...")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Ejecutar la consulta
            self.update_log_textbox(f"Consultando registros para la fecha: {selected_date}")
            cursor.execute("SELECT * FROM log_procesos WHERE fecha = ?", (selected_date,))
            results = cursor.fetchall()
            
            # Obtener los nombres de las columnas
            column_names = [description[0] for description in cursor.description]
            
            # Cerrar la conexión
            conn.close()
            
            # Verificar si hay resultados
            if not results:
                self.update_log_textbox("No se encontraron registros para esta fecha.")
                messagebox.showinfo("Información", "No se encontraron registros para esta fecha.")
                return
            
            # Crear un DataFrame con los resultados
            df = pd.DataFrame(results, columns=column_names)
            self.update_log_textbox(f"Se encontraron {len(df)} registros.")
            
            # Crear el nombre del archivo Excel con la fecha actual
            current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_filename = f"log_procesos_{current_datetime}.xlsx"
            excel_path = os.path.join(os.path.expanduser("~"), "Downloads", excel_filename)
            
            # Exportar a Excel
            self.update_log_textbox(f"Exportando resultados a Excel: {excel_filename}")
            df.to_excel(excel_path, index=False)
            
            # Mostrar mensaje de éxito
            self.update_log_textbox(f"Exportación completada. Archivo guardado en: {excel_path}")
            messagebox.showinfo("Exportación Exitosa", f"Los datos se han exportado correctamente a:\n{excel_path}")
            
            # Abrir automáticamente el archivo Excel (opcional)
            try:
                os.startfile(excel_path)
            except Exception as e:
                self.update_log_textbox(f"No se pudo abrir el archivo Excel automáticamente: {str(e)}", "ERROR")
        
        except sqlite3.Error as e:
            error_msg = f"Error en la base de datos: {str(e)}"
            self.update_log_textbox(error_msg, "ERROR")
            messagebox.showerror("Error de Base de Datos", error_msg)
        
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            self.update_log_textbox(error_msg, "ERROR")
            messagebox.showerror("Error", error_msg)