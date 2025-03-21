# -*- coding: utf-8 -*-
"""
Módulo para la pestaña de Directorios.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess

class DirectoryTab:
    """Clase para gestionar la pestaña de Directorios."""
    
    def __init__(self, notebook, icons, db_manager, logger):
        """
        Inicializa la pestaña de Directorios.
        
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
        self.load_directories()
    
    def setup_tab(self):
        """Configura los elementos de la pestaña."""
        # Crear la pestaña de Directorios
        self.directory_frame = ttk.Frame(self.notebook)
        self.add_tab(self.notebook, self.directory_frame, "Directorios", self.icons["folder_icon"])
        
        # Frame principal para el contenido
        self.config_routes_frame = ttk.Frame(self.directory_frame)
        self.config_routes_frame.pack(padx=(5,5), fill=tk.BOTH, expand=True)
        
        # Configuración del grid en el contenedor principal
        self.config_routes_frame.columnconfigure(0, weight=1)
        self.config_routes_frame.rowconfigure(0, weight=0)
        self.config_routes_frame.rowconfigure(1, weight=0)
        self.config_routes_frame.rowconfigure(2, weight=5)
        
        # Crear un LabelFrame para agrupar las entradas y botones relacionados con rutas
        self.routes_labelframe = ttk.LabelFrame(self.config_routes_frame, text="Configuración de Rutas", style="Custom.TLabelframe")
        self.routes_labelframe.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(5,0), padx=5)
        
        # Frame contenedor para la primera entrada y botones
        self.process_frame = ttk.Frame(self.routes_labelframe)
        self.process_frame.grid(row=0, column=0, pady=5, padx=5, sticky="ew")
        
        # Etiqueta y widgets para "Ruta de directorio a procesar"
        ttk.Label(self.process_frame, text="Ruta de directorio a procesar:").grid(row=0, column=0, padx=5, sticky="w")
        
        self.process_dir_entry = ttk.Entry(self.process_frame, width=50)
        self.process_dir_entry.grid(row=1, column=0, pady=5, padx=5, sticky="w")
        
        # Crear el botón "Modificar" para la entrada de "Ruta de directorio a procesar"
        self.modificar_procesar_button = ttk.Button(
            self.process_frame, text="Modificar", image=self.icons["fopen_icon"], compound=tk.LEFT,
            command=lambda: self.seleccionar_ruta(self.process_dir_entry)
        )
        self.modificar_procesar_button.grid(row=1, column=1, padx=5)
        
        # Botón para "Abrir" después
        self.open_process_button = ttk.Button(
            self.process_frame, text="", image=self.icons["fopen_icon"],
            command=lambda: self.abrir_carpeta(self.process_dir_entry)
        )
        self.open_process_button.grid(row=1, column=2, padx=5)
        self.open_process_button.config(state=tk.DISABLED)  # Deshabilitado inicialmente
        
        # Frame para la segunda entrada y botones dentro del LabelFrame
        self.processed_frame = ttk.Frame(self.routes_labelframe)
        self.processed_frame.grid(row=1, column=0, pady=(5,0), padx=5, sticky="ew")
        
        # Etiqueta y widgets para "Ruta de directorio procesado"
        ttk.Label(self.processed_frame, text="Ruta de directorio procesado:").grid(row=0, column=0, padx=5, sticky="w")
        
        self.processed_dir_entry = ttk.Entry(self.processed_frame, width=50)
        self.processed_dir_entry.grid(row=1, column=0, pady=5, padx=5, sticky="w")
        
        # Crear el botón "Modificar" para la entrada de "Ruta de directorio procesado"
        self.modificar_procesado_button = ttk.Button(
            self.processed_frame, text="Modificar", image=self.icons["fopen_icon"], compound=tk.LEFT,
            command=lambda: self.seleccionar_ruta(self.processed_dir_entry)
        )
        self.modificar_procesado_button.grid(row=1, column=1, padx=5)
        
        # Botón para "Abrir" después
        self.open_processed_button = ttk.Button(
            self.processed_frame, text="", image=self.icons["fopen_icon"],
            command=lambda: self.abrir_carpeta(self.processed_dir_entry)
        )
        self.open_processed_button.grid(row=1, column=2, padx=5)
        self.open_processed_button.config(state=tk.DISABLED)  # Deshabilitado inicialmente
        
        ttk.Label(self.processed_frame, text="").grid(row=2, column=0, sticky="w", padx=(5,0), pady=(0,0))
        
        # Crear un LabelFrame para los elementos de "Revisar Cada"
        self.icon_labelframe = ttk.LabelFrame(self.config_routes_frame, text="Intervalo de Revisión", style="Custom.TLabelframe")
        self.icon_labelframe.grid(row=1, column=0, columnspan=2, pady=(10,5), padx=5, sticky="ew")
        
        # Frame contenedor para los elementos de intervalo de revisión
        self.icon_frame = ttk.Frame(self.icon_labelframe)
        self.icon_frame.grid(row=0, column=0, pady=(10,5), padx=5, sticky="ew")
        
        # Icono y etiquetas para la configuración de intervalo
        ttk.Label(self.icon_frame, image=self.icons["clock_icon"]).grid(row=0, column=0, padx=5)
        ttk.Label(self.icon_frame, text="Revisar Cada:").grid(row=0, column=1, padx=5)
        
        # Spinbox para elegir el intervalo en segundos
        self.spinbox = ttk.Spinbox(self.icon_frame, from_=1, to=60, width=5)
        self.spinbox.grid(row=0, column=2, padx=5)
        
        ttk.Label(self.icon_frame, text="Segundos").grid(row=0, column=3, padx=5)
        ttk.Label(self.icon_frame, text="").grid(row=1, column=0, sticky="w", padx=(5,0), pady=(0,0))
        
        # Crear un Frame para los botones en la última fila de config_routes_frame
        self.buttons_directory_frame = ttk.Frame(self.config_routes_frame)
        self.buttons_directory_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="se")
        
        # Botón "Editar"
        self.editar_button = ttk.Button(
            self.buttons_directory_frame, text="Editar", image=self.icons["edit_icon"], 
            compound=tk.LEFT, command=self.editar_directorios
        )
        self.editar_button.grid(row=0, column=0, padx=5)
        
        # Botón "Guardar Directorios"
        self.guardar_button = ttk.Button(
            self.buttons_directory_frame, text="Guardar Directorios", image=self.icons["save_icon"], 
            compound=tk.LEFT, command=self.guardar_directorios
        )
        self.guardar_button.grid(row=0, column=1, padx=5)
        
        # Asociar eventos de validación
        self.process_dir_entry.bind("<KeyRelease>", lambda e: self.verificar_rutas())
        self.processed_dir_entry.bind("<KeyRelease>", lambda e: self.verificar_rutas())
    
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
    
    def seleccionar_ruta(self, entry_widget):
        """
        Abre el diálogo para seleccionar una carpeta y actualiza el Entry.
        
        Args:
            entry_widget: Widget Entry a actualizar con la ruta seleccionada.
        """
        # Abrir el cuadro de diálogo para seleccionar una carpeta
        entry_widget.config(state='normal')
        ruta_seleccionada = filedialog.askdirectory(title="Seleccione una carpeta")
        
        # Si el usuario selecciona una carpeta, actualizar el Entry correspondiente
        if ruta_seleccionada:
            entry_widget.config(state='normal')  # Asegurar que el Entry esté habilitado temporalmente
            entry_widget.delete(0, tk.END)       # Limpiar el contenido del Entry
            entry_widget.insert(0, ruta_seleccionada)  # Insertar la ruta seleccionada
        
        # Verificar el estado de los botones
        self.verificar_rutas()
    
    def abrir_carpeta(self, entry_widget):
        """
        Abre la carpeta especificada en el explorador de archivos.
        
        Args:
            entry_widget: Widget Entry que contiene la ruta a abrir.
        """
        ruta = entry_widget.get()
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
    
    def verificar_rutas(self, *args):
        """
        Verifica si las rutas están configuradas y habilita/deshabilita los botones correspondientes.
        """
        # Verificar si el Entry de "Ruta de directorio a procesar" está vacío
        if self.process_dir_entry.get():
            self.open_process_button.config(state=tk.NORMAL)
        else:
            self.open_process_button.config(state=tk.DISABLED)

        # Verificar si el Entry de "Ruta de directorio procesado" está vacío
        if self.processed_dir_entry.get():
            self.open_processed_button.config(state=tk.NORMAL)
        else:
            self.open_processed_button.config(state=tk.DISABLED)
    
    def editar_directorios(self):
        """Habilita la edición de los campos de directorios."""
        self.logger.log_message("Habilitando edición de directorios...")
        
        # Habilitar los campos y los botones de modificar
        for entry in [self.process_dir_entry, self.processed_dir_entry]:
            entry.config(state='normal')
        self.spinbox.config(state='normal')
        self.modificar_procesar_button.config(state=tk.NORMAL)
        self.modificar_procesado_button.config(state=tk.NORMAL)
    
    def guardar_directorios(self):
        """Guarda la configuración de directorios en la base de datos."""
        try:
            # Obtener los valores de los Entry y Spinbox
            ruta_procesar = self.process_dir_entry.get()
            ruta_procesado = self.processed_dir_entry.get()
            intervalo_exec = int(self.spinbox.get())
            
            # Crear una tupla con los datos
            directories_data = (ruta_procesar, ruta_procesado, intervalo_exec)
            
            # Guardar en la base de datos
            if self.db_manager.save_directories(directories_data):
                # Mostrar mensaje de confirmación
                messagebox.showinfo("Guardar Directorios", "Directorios guardados exitosamente.")
                
                # Deshabilitar los campos y actualizar el estado de los botones después de guardar
                for entry in [self.process_dir_entry, self.processed_dir_entry]:
                    entry.config(state='disabled')
                self.spinbox.config(state='disabled')
                
                self.modificar_procesar_button.config(state=tk.DISABLED)
                self.modificar_procesado_button.config(state=tk.DISABLED)
                self.open_process_button.config(state=tk.NORMAL)
                self.open_processed_button.config(state=tk.NORMAL)
                
                # Agregar los valores guardados al log_textbox
                self.logger.log_message(f"Valores guardados en la tabla directorios:")
                self.logger.log_message(f"  Ruta de directorio a procesar: {ruta_procesar}")
                self.logger.log_message(f"  Ruta de directorio procesado: {ruta_procesado}")
                self.logger.log_message(f"  Intervalo de revisión: {intervalo_exec} segundos")
                self.logger.log_message_sindb("--------------------------------------------------------------------------------------------------------------")
            else:
                messagebox.showerror("Error", "No se pudo guardar la configuración de directorios.")
            
        except Exception as e:
            self.logger.log_message(f"Error al guardar directorios: {e}", "ERROR")
            messagebox.showerror("Error", f"No se pudo guardar el directorio: {e}")
    
    def load_directories(self):
        """Carga la configuración de directorios desde la base de datos."""
        try:
            directories = self.db_manager.get_directories()
            
            if directories:
                # Cargar valores en los Entry y Spinbox y deshabilitarlos
                self.process_dir_entry.insert(0, directories[0])
                self.processed_dir_entry.insert(0, directories[1])
                self.spinbox.set(directories[2])
                
                for entry in [self.process_dir_entry, self.processed_dir_entry]:
                    entry.config(state='disabled')
                self.spinbox.config(state='disabled')
                
                # Estado de los botones si existe un registro
                self.open_process_button.config(state=tk.NORMAL)
                self.open_processed_button.config(state=tk.NORMAL)
                self.modificar_procesar_button.config(state=tk.DISABLED)
                self.modificar_procesado_button.config(state=tk.DISABLED)
                
                self.logger.log_message("Configuraciones de directorios cargadas.", "INFO")
            else:
                self.logger.log_message_sindb("Tabla directorios vacía. Campos habilitados para ingresar información.", "INFO")
                
                # Habilitar los Entry y Spinbox para ingresar datos nuevos
                for entry in [self.process_dir_entry, self.processed_dir_entry]:
                    entry.config(state='normal')
                self.spinbox.config(state='normal')
                
                # Estado de los botones si no existe un registro
                self.open_process_button.config(state=tk.DISABLED)
                self.open_processed_button.config(state=tk.DISABLED)
                self.modificar_procesar_button.config(state=tk.NORMAL)
                self.modificar_procesado_button.config(state=tk.NORMAL)
                
        except Exception as e:
            self.logger.log_message(f"Error al cargar directorios: {e}", "ERROR")