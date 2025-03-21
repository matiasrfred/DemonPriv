# -*- coding: utf-8 -*-
"""
Módulo para la pestaña de Impresión.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from utils.printer import obtener_impresoras

class PrintTab:
    """Clase para gestionar la pestaña de Impresión."""
    
    def __init__(self, notebook, icons, db_manager, logger):
        """
        Inicializa la pestaña de Impresión.
        
        Args:
            notebook: Notebook donde se añadirá la pestaña.
            icons: Diccionario con los iconos de la aplicación.
            db_manager: Gestor de base de datos.
            logger: Objeto para registrar eventos.
        """
        self.notebook = notebook
        self.icons = icons
        self.db_manager = db_manager
        self.logger = logger
        self.setup_tab()
        self.load_print_config()
    
    def setup_tab(self):
        """Configura los elementos de la pestaña."""
        # Crear la pestaña de Impresión
        self.printer_frame = ttk.Frame(self.notebook)
        self.add_tab(self.notebook, self.printer_frame, " Impresión ", self.icons["printer_icon"])
        
        # Configuración del grid en el contenedor principal para que todos los elementos se expandan
        self.printer_frame.columnconfigure(0, weight=1)
        
        # LabelFrame para "Configuración Impresión"
        self.print_config_labelframe = ttk.LabelFrame(self.printer_frame, text="Configuración Impresión", style="Custom.TLabelframe")
        self.print_config_labelframe.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        
        # Frame contenedor para el título y checkbox de impresión
        self.printer_title_frame = ttk.Frame(self.print_config_labelframe)
        self.printer_title_frame.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Checkbox para habilitar o deshabilitar la impresión
        self.enable_printing_var = tk.BooleanVar(value=False)
        self.enable_printing_checkbox = ttk.Checkbutton(
            self.printer_title_frame, text="Habilitar impresión", variable=self.enable_printing_var
        )
        self.enable_printing_checkbox.grid(row=0, column=0, padx=5, sticky="w")
        
        # Frame contenedor para el Combobox y el botón "Modificar"
        self.printer_selection_frame = ttk.Frame(self.print_config_labelframe)
        self.printer_selection_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.printer_selection_frame.columnconfigure(0, weight=1)
        
        # Combobox para enlistar impresoras disponibles
        self.printer_combobox = ttk.Combobox(self.printer_selection_frame, state="readonly", width=35)
        self.printer_combobox.grid(row=1, column=0, padx=5, sticky="w")
        
        # Botón "Modificar" para habilitar el Combobox
        self.modify_button = ttk.Button(
            self.printer_selection_frame, text="Modificar", 
            command=lambda: self.printer_combobox.config(state="readonly")
        )
        self.modify_button.grid(row=1, column=1, padx=(10,80))
        
        # Obtener impresoras del sistema y agregarlas al Combobox
        impresoras_disponibles = obtener_impresoras()
        self.printer_combobox['values'] = impresoras_disponibles
        
        # Etiqueta de imagen para "N° de Copias"
        self.num_copias_image_label = ttk.Label(self.print_config_labelframe, image=self.icons["num_copias_img"])
        self.num_copias_image_label.grid(row=0, column=2, sticky="w", padx=(25, 0), pady=(5, 0))
        
        # Frame contenedor para "N° de Copias" label y spinbox
        self.copias_frame = ttk.Frame(self.print_config_labelframe)
        self.copias_frame.grid(row=1, column=2, sticky="w", padx=5, pady=5)
        
        # Etiqueta para "N° de Copias"
        self.num_copias_text_label = ttk.Label(self.copias_frame, text="N° de Copias:")
        self.num_copias_text_label.grid(row=1, column=2, sticky="w")
        
        # Spinbox para seleccionar el número de copias
        self.num_copias_spinbox = ttk.Spinbox(self.copias_frame, from_=1, to=10, width=5)
        self.num_copias_spinbox.grid(row=1, column=3, padx=5)
        
        # LabelFrame para la sección de descarga
        self.download_config_labelframe = ttk.LabelFrame(self.printer_frame, text="Configuración de Descarga", style="Custom.TLabelframe")
        self.download_config_labelframe.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Checkbox para habilitar o deshabilitar la descarga local
        self.enable_local_download_var = tk.BooleanVar(value=False)
        self.enable_local_download_checkbox = ttk.Checkbutton(
            self.download_config_labelframe, text="Habilitar descarga local", 
            variable=self.enable_local_download_var
        )
        self.enable_local_download_checkbox.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        # Label y Entry para la ruta de descarga
        ttk.Label(self.download_config_labelframe, text="Ruta a carpeta de descarga:").grid(row=1, column=0, sticky="w", padx=10)
        
        # Frame contenedor para el Entry y los botones de la ruta
        self.path_frame = ttk.Frame(self.download_config_labelframe)
        self.path_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.path_frame.columnconfigure(0, weight=1)
        
        # Entry para la ruta de descarga local
        self.local_download_entry = ttk.Entry(self.path_frame, width=65)
        self.local_download_entry.grid(row=0, column=0, sticky="ew", padx=5)
        
        # Botón para modificar la ruta
        self.modify_path_button = ttk.Button(
            self.path_frame, text="Modificar", image=self.icons["fopen_icon"], 
            compound=tk.LEFT, command=self.seleccionar_ruta_descarga
        )
        self.modify_path_button.grid(row=0, column=1, padx=5)
        
        # Botón para abrir la ruta seleccionada
        self.open_path_button = ttk.Button(
            self.path_frame, text="", image=self.icons["fopen_icon"], 
            compound=tk.LEFT, command=self.abrir_carpeta_descarga
        )
        self.open_path_button.grid(row=0, column=2, padx=5)
        
        # Crear el Frame para los botones "Editar" y "Guardar Impresión" en la parte inferior derecha
        self.buttons_frame = ttk.Frame(self.printer_frame)
        self.buttons_frame.grid(row=2, column=0, sticky="se", pady=10, padx=10)
        
        # Botón "Editar" para habilitar la edición de los campos de impresión
        self.editar_button = ttk.Button(
            self.buttons_frame, text="Editar", image=self.icons["edit_icon"], 
            compound=tk.LEFT, command=self.habilitar_edicion_impresion
        )
        self.editar_button.pack(side=tk.LEFT, padx=5)
        
        # Botón "Guardar Impresión" para guardar la configuración de impresión
        self.guardar_button = ttk.Button(
            self.buttons_frame, text="Guardar Impresión", image=self.icons["save_icon"], 
            compound=tk.LEFT, command=self.guardar_y_deshabilitar_impresora
        )
        self.guardar_button.pack(side=tk.LEFT, padx=5)
        
        # Configurar el layout de printer_frame para que empuje el `buttons_frame` hacia abajo
        self.printer_frame.rowconfigure(1, weight=0)  # Ajustar el layout de printer_frame para expandir el espacio
        self.printer_frame.rowconfigure(2, weight=2)  # Ajustar el layout de printer_frame para expandir el espacio
        self.printer_frame.columnconfigure(0, weight=1)
    
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
    
    def seleccionar_ruta_descarga(self):
        """Selecciona la ruta de descarga para archivos procesados."""
        ruta_seleccionada = filedialog.askdirectory(title="Seleccione una carpeta para descargas")
        if ruta_seleccionada:
            self.local_download_entry.delete(0, tk.END)
            self.local_download_entry.insert(0, ruta_seleccionada)
    
    def abrir_carpeta_descarga(self):
        """Abre la carpeta de descarga en el explorador de archivos."""
        import os
        import subprocess
        import sys
        
        ruta = self.local_download_entry.get()
        
        try:
            if os.path.isdir(ruta):
                if os.name == 'nt':
                    os.startfile(ruta)
                elif os.name == 'posix':
                    subprocess.Popen(['open', ruta] if sys.platform == 'darwin' else ['xdg-open', ruta])
            else:
                raise ValueError("La ruta especificada no es válida.")
        except Exception as e:
            self.logger.log_message(f"Error al abrir carpeta: {e}", "ERROR")
            messagebox.showerror("Error", f"No se pudo abrir la carpeta: {e}")
    
    def habilitar_edicion_impresion(self):
        """Habilita la edición de los campos de impresión."""
        self.logger.log_message("Comenzando edición de configuraciones de impresión...")
        
        # Habilitar los campos de la pestaña de impresión
        self.printer_combobox.config(state="readonly")
        self.enable_printing_checkbox.config(state="normal")
        self.enable_local_download_checkbox.config(state="normal")
        self.local_download_entry.config(state="normal")
        self.num_copias_spinbox.config(state="normal")
        self.modify_button.config(state="normal")
        self.modify_path_button.config(state="normal")
    
    def guardar_y_deshabilitar_impresora(self):
        """Guarda la configuración de impresión y deshabilita los controles."""
        impresora_seleccionada = self.printer_combobox.get()
        hab_impresion = self.enable_printing_var.get()  # Obtener estado del checkbox de impresión
        hab_download = self.enable_local_download_var.get()  # Obtener estado del checkbox de descarga
        dir_download = self.local_download_entry.get()  # Obtener la ruta de descarga del Entry
        num_copias = self.num_copias_spinbox.get()  # Obtener el número de copias del Spinbox
        
        # Convertir los valores de los checkboxes a 0 o 1
        hab_impresion_val = 1 if hab_impresion else 0
        hab_descarga_val = 1 if hab_download else 0
        
        # Crear una tupla con los datos
        print_data = (hab_impresion_val, impresora_seleccionada, num_copias, hab_descarga_val, dir_download)
        
        # Guardar en la base de datos
        if self.db_manager.save_print_config(print_data):
            # Mostrar mensaje de confirmación
            messagebox.showinfo("Guardar Impresión", "Configuración de impresión guardada exitosamente.")
            
            # Deshabilitar los controles
            self.printer_combobox.config(state="disabled")
            self.enable_printing_checkbox.config(state="disabled")
            self.enable_local_download_checkbox.config(state="disabled")
            self.local_download_entry.config(state="disabled")
            self.num_copias_spinbox.config(state="disabled")
            self.modify_button.config(state="disabled")
            self.modify_path_button.config(state="disabled")
            
            # Registrar los valores guardados en el log_textbox
            self.logger.log_message(f"Configuración de impresión guardada:")
            self.logger.log_message(f"  Impresora habilitada: {hab_impresion_val}")
            self.logger.log_message(f"  Impresora seleccionada: {impresora_seleccionada}")
            self.logger.log_message(f"  Número de copias: {num_copias}")
            self.logger.log_message(f"  Descarga local habilitada: {hab_descarga_val}")
            self.logger.log_message(f"  Ruta de descarga: {dir_download}")
            self.logger.log_message_sindb("--------------------------------------------------------------------------------------------------------------")
        else:
            messagebox.showerror("Error", "No se pudo guardar la configuración de impresión.")
    
    def load_print_config(self):
        """Carga la configuración de impresión desde la base de datos."""
        try:
            print_config = self.db_manager.get_print_config()
            
            if print_config:
                hab_printer, printer, num_copias, habdesc_local, ruta_descargas = print_config
                self.logger.log_message("Cargando configuración de impresión...", "INFO")
                
                # Cargar los valores en los campos de la pestaña Impresión
                self.enable_printing_var.set(bool(hab_printer))
                self.printer_combobox.set(printer)
                self.num_copias_spinbox.set(num_copias)
                self.enable_local_download_var.set(bool(habdesc_local))
                self.local_download_entry.delete(0, tk.END)
                self.local_download_entry.insert(0, ruta_descargas)
                
                # Deshabilitar todos los campos de impresión si hay configuración
                self.printer_combobox.config(state="disabled")
                self.enable_printing_checkbox.config(state="disabled")
                self.enable_local_download_checkbox.config(state="disabled")
                self.local_download_entry.config(state="disabled")
                self.num_copias_spinbox.config(state="disabled")
                self.modify_button.config(state="disabled")
                self.modify_path_button.config(state="disabled")
                
                self.logger.log_message("Configuración de impresión cargada.", "INFO")
            else:
                self.logger.log_message_sindb("Tabla impresion vacía. Campos habilitados para ingresar información.", "INFO")
                
                # Habilitar los campos si no existe configuración en impresión
                self.enable_printing_var.set(False)
                self.printer_combobox.config(state="readonly")
                self.num_copias_spinbox.set(1)
                self.enable_local_download_var.set(False)
                self.local_download_entry.config(state="normal")
                self.modify_button.config(state="normal")
                self.modify_path_button.config(state="normal")
                
        except Exception as e:
            self.logger.log_message(f"Error al cargar configuración de impresión: {e}", "ERROR")