import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import sys
import winreg

class ConfigTab:
    """Clase para gestionar la pestaña de Configuración."""
    
    def __init__(self, notebook, icons, db_manager, logger):
        """
        Inicializa la pestaña de Configuración.
        
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
        self.load_config()
    
    def setup_tab(self):
        """Configura los elementos de la pestaña."""
        # Crear la pestaña de Configuración
        self.config_frame = ttk.Frame(self.notebook)
        self.add_tab(self.notebook, self.config_frame, "Configuración", self.icons["config_icon"])
        
        # Frame principal contenedor de la sección de configuración
        self.config_process_frame = ttk.Frame(self.config_frame)
        self.config_process_frame.pack(padx=(5,5), fill=tk.X)
        
        # Configuración del grid en el contenedor principal para que todos los elementos se expandan
        self.config_process_frame.columnconfigure(0, weight=1)
        
        # Agrupando "Razón Social" y "Rut Empresa" dentro de un LabelFrame
        self.razon_rut_frame = ttk.LabelFrame(self.config_process_frame, text="Datos de Empresa", style="Custom.TLabelframe")
        self.razon_rut_frame.grid(row=0, column=0, sticky="nsew", pady=5, padx=5, columnspan=2)
        
        # Expande las columnas internas del LabelFrame 'Datos de Empresa'
        self.razon_rut_frame.columnconfigure(0, weight=1)
        self.razon_rut_frame.columnconfigure(1, weight=1)
        
        # Etiqueta y Entry para "Razón Social"
        ttk.Label(self.razon_rut_frame, text="Razón Social").grid(row=0, column=0, sticky="w", padx=(10,5), pady=(5,0))
        self.razon_social_entry = ttk.Entry(self.razon_rut_frame)
        self.razon_social_entry.grid(row=1, column=0, columnspan=4, padx=(10,5), sticky="ew")
        
        # Etiqueta y Entry para "Rut Empresa"
        ttk.Label(self.razon_rut_frame, text="Rut Empresa").grid(row=0, column=4, sticky="w", padx=(10,5), pady=(5,0))
        self.rut_entry = ttk.Entry(self.razon_rut_frame, validate="key", validatecommand=self.setup_rut_validation())
        self.rut_entry.grid(row=1, column=4, padx=10, sticky="ew")
        
        # Etiqueta y Entry para "Teléfono"
        ttk.Label(self.razon_rut_frame, text="Teléfono").grid(row=0, column=5, sticky="w", padx=(5,10), pady=(5,0))
        self.telefono_entry = ttk.Entry(self.razon_rut_frame, width=25)
        self.telefono_entry.grid(row=1, column=5, padx=(5,10), sticky="ew")
        
        # Dirección
        ttk.Label(self.razon_rut_frame, text="Dirección").grid(row=2, column=0, sticky="w", padx=(10,5), pady=(10,0))
        self.direc_entry = ttk.Entry(self.razon_rut_frame)
        self.direc_entry.grid(row=3, column=0, columnspan=3, padx=(10,10), sticky="ew")
        
        # Comuna
        ttk.Label(self.razon_rut_frame, text="Comuna").grid(row=2, column=3, sticky="w", padx=5, pady=(10,0))
        self.comuna_entry = ttk.Entry(self.razon_rut_frame)
        self.comuna_entry.grid(row=3, column=3, padx=(5, 5), sticky="ew")
        
        # Ciudad
        ttk.Label(self.razon_rut_frame, text="Ciudad").grid(row=2, column=4, sticky="w", padx=10, pady=(10,0))
        self.ciudad_entry = ttk.Entry(self.razon_rut_frame, width=35)
        self.ciudad_entry.grid(row=3, column=4, padx=10, sticky="ew")
        
        # Región
        ttk.Label(self.razon_rut_frame, text="Región").grid(row=2, column=5, sticky="w", padx=(5,0), pady=(10,0))
        self.region_entry = ttk.Entry(self.razon_rut_frame, width=15)
        self.region_entry.grid(row=3, column=5, padx=(5,10), sticky="ew")
        
        # Email
        ttk.Label(self.razon_rut_frame, text="Email").grid(row=4, column=0, sticky="w", padx=10, pady=(10,0))
        self.email_entry = ttk.Entry(self.razon_rut_frame, width=35)
        self.email_entry.grid(row=5, column=0, padx=(10,5), columnspan=4, sticky="ew")
        
        # Cód. Suc. SII
        ttk.Label(self.razon_rut_frame, text="Cód. Suc. SII").grid(row=4, column=4, sticky="w", padx=10, pady=(10,0))
        self.codsucursal_entry = ttk.Entry(self.razon_rut_frame, width=15)
        self.codsucursal_entry.grid(row=5, column=4, padx=10, sticky="ew")
        
        # Act. Económica
        ttk.Label(self.razon_rut_frame, text="Act. Económica").grid(row=4, column=5, sticky="w", padx=(5,0), pady=(10,0))
        self.act_entry = ttk.Entry(self.razon_rut_frame, width=20)
        self.act_entry.grid(row=5, column=5, padx=(5,10), sticky="ew")
        
        # Giro
        ttk.Label(self.razon_rut_frame, text="Giro (80 carac. max.)").grid(row=6, column=0, sticky="w", padx=(10,5), pady=(10,0))
        self.giro_var = tk.StringVar()
        self.giro_var.trace("w", self.limitar_giro)
        self.giro_entry = ttk.Entry(self.razon_rut_frame, textvariable=self.giro_var, width=85)
        self.giro_entry.grid(row=7, column=0, padx=(10,5), columnspan=4, sticky="ew")
        
        ttk.Label(self.razon_rut_frame, text="").grid(row=8, column=0, sticky="w", padx=(5,0), pady=(0,0))
        
        # Agrupando "Api Key" y "TPV" dentro de un LabelFrame
        self.api_tpv_frame = ttk.LabelFrame(self.config_process_frame, text="Configuración Técnica", style="Custom.TLabelframe")
        self.api_tpv_frame.grid(row=1, column=0, sticky="nsew", pady=5, padx=5, columnspan=2)
        
        # Expande las columnas internas del LabelFrame 'Configuración Técnica'
        self.api_tpv_frame.columnconfigure(0, weight=1)
        self.api_tpv_frame.columnconfigure(1, weight=1)
        self.api_tpv_frame.columnconfigure(2, weight=1)
        
        # Api Key
        ttk.Label(self.api_tpv_frame, text="Api Key").grid(row=0, column=0, sticky="w", padx=(10,5), pady=(5,0))
        self.api_key_entry = ttk.Entry(self.api_tpv_frame, show="*")
        self.api_key_entry.grid(row=1, column=0, columnspan=2, padx=(10,5), sticky="ew")
        
        # TPV
        ttk.Label(self.api_tpv_frame, text="TPV").grid(row=0, column=2, sticky="w", padx=(10,5), pady=(5,0))
        self.tpv_entry = ttk.Entry(self.api_tpv_frame)
        self.tpv_entry.grid(row=1, column=2, padx=(10,5), sticky="ew")
        
        # Checkbox para iniciar con Windows
        self.autostart_var = tk.BooleanVar()
        self.autostart_check = ttk.Checkbutton(self.api_tpv_frame, text="Iniciar con Windows", 
                                             variable=self.autostart_var, 
                                             command=self.toggle_autostart)
        self.autostart_check.grid(row=2, column=0, sticky="w", padx=(10,5), pady=(10,5))
        
        # Checkbox para iniciar procesamiento automáticamente
        self.autoprocess_var = tk.BooleanVar()
        self.autoprocess_check = ttk.Checkbutton(self.api_tpv_frame, text="Iniciar procesamiento automáticamente", 
                                               variable=self.autoprocess_var,
                                               command=self.toggle_autoprocess)
        self.autoprocess_check.grid(row=2, column=1, columnspan=2, sticky="w", padx=(10,5), pady=(10,5))
        
        # Verificar el estado de las configuraciones
        self.check_autostart_status()
        self.check_autoprocess_status()
        
        ttk.Label(self.api_tpv_frame, text="").grid(row=6, column=0, sticky="w", padx=(5,0), pady=(0,0))
        
        # Botones Editar y Guardar
        self.buttons_frame = ttk.Frame(self.config_frame)
        self.buttons_frame.pack(side=tk.BOTTOM, anchor='e', pady=10, padx=10)
        
        # Botón de Editar
        self.edit_button = ttk.Button(self.buttons_frame, text="Editar", image=self.icons["edit_icon"], 
                                      compound=tk.LEFT, command=self.habilitar_edicion)
        self.edit_button.pack(side=tk.LEFT, padx=5)
        
        # Botón de Guardar
        self.save_button = ttk.Button(self.buttons_frame, text="Guardar Config", image=self.icons["save_icon"], 
                                      compound=tk.LEFT, command=self.guardar_configuracion)
        self.save_button.pack(side=tk.LEFT, padx=5)
    
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
    
    def setup_rut_validation(self):
        """
        Configura la validación para el campo RUT.
        
        Returns:
            Tuple: Comando de validación para el Entry.
        """
        return (self.config_frame.register(self.validate_input), '%P')
    
    def validate_input(self, new_value):
        """
        Valida la entrada del campo RUT.
        
        Args:
            new_value: Nuevo valor del campo.
            
        Returns:
            bool: True si la entrada es válida, False en caso contrario.
        """
        # Si el campo está vacío, permitir borrar
        if new_value == '':
            return True

        # Limitar el número de caracteres a 12 (incluyendo puntos y guion)
        if len(new_value) > 12:
            return False
        
        # Eliminar puntos y guion para trabajar con el valor sin formato
        cleaned_value = new_value.replace('.', '').replace('-', '')
        
        # Verificar si el último carácter ingresado es "K"
        if 'K' in cleaned_value:
            k_index = cleaned_value.index('K')
            # Solo permitir "K" en la posición 8 o 9 (0-indexed, así que es cleaned_value[7] o cleaned_value[8])
            if k_index < 7:
                return False  # No permitir "K" en las posiciones 1 a 7
        
        # Permitir solo dígitos, K (en mayúscula), y manejar el formateo
        if cleaned_value.isdigit() or (len(cleaned_value) in [8, 9] and cleaned_value[-1].upper() == 'K'):
            formatted_rut = self.format_rut(cleaned_value)
            self.rut_entry.delete(0, tk.END)
            self.rut_entry.insert(0, formatted_rut)
            return True
        
        return False
    
    def format_rut(self, rut):
        """
        Formatea un RUT según el formato chileno.
        
        Args:
            rut: RUT sin formato.
            
        Returns:
            str: RUT formateado.
        """
        # Quitar puntos y guiones existentes
        rut = rut.replace('.', '').replace('-', '')
        
        # Asegurarse de que no exceda los 9 caracteres numéricos o numéricos más la K
        if len(rut) > 9:
            rut = rut[:9]
        
        # Solo aplicar formato si hay más de un carácter
        if len(rut) > 1:
            # Agregar guión antes del dígito verificador
            rut = rut[:-1] + '-' + rut[-1]
            # Agregar puntos en las posiciones correctas
            if len(rut) > 5:
                rut = rut[:-5] + '.' + rut[-5:]
            if len(rut) > 9:
                rut = rut[:-9] + '.' + rut[-9:]
        
        return rut
    
    def limitar_giro(self, *args):
        """Limita el número de caracteres en el campo Giro."""
        texto = self.giro_var.get()
        if len(texto) > 80:
            self.giro_var.set(texto[:80])
    
    def load_config(self):
        """Carga la configuración desde la base de datos."""
        try:
            config = self.db_manager.get_config()
            
            if config:
                # Cargar valores en los Entry y deshabilitarlos
                self.rut_entry.insert(0, config[0])
                self.razon_social_entry.insert(0, config[1])
                self.telefono_entry.insert(0, config[2])
                self.direc_entry.insert(0, config[3])
                self.comuna_entry.insert(0, config[4])
                self.email_entry.insert(0, config[5])
                self.codsucursal_entry.insert(0, config[6])
                self.giro_entry.insert(0, config[7])
                self.act_entry.insert(0, config[8])
                self.api_key_entry.insert(0, config[9])
                self.tpv_entry.insert(0, config[10])
                self.ciudad_entry.insert(0, config[11])
                self.region_entry.insert(0, config[12])

                # Deshabilitar los Entry
                self.disable_entries()
                
                self.logger.log_message("Configuraciones cargadas.", "INFO")
            else:
                self.logger.log_message_sindb("Tabla config vacía. Campos habilitados para ingresar información.", "INFO")

        except Exception as e:
            self.logger.log_message(f"Error al cargar configuración: {e}", "ERROR")
    
    def disable_entries(self):
        """Deshabilita todos los campos de entrada."""
        for entry in [self.rut_entry, self.razon_social_entry, self.telefono_entry, self.direc_entry, 
                     self.comuna_entry, self.email_entry, self.codsucursal_entry, self.giro_entry, 
                     self.act_entry, self.api_key_entry, self.tpv_entry, self.ciudad_entry, self.region_entry]:
            entry.config(state='disabled')
        # Deshabilitar también los checkbox
        self.autostart_check.config(state='disabled')
        self.autoprocess_check.config(state='disabled')
    
    def enable_entries(self):
        """Habilita todos los campos de entrada."""
        for entry in [self.rut_entry, self.razon_social_entry, self.telefono_entry, self.direc_entry, 
                     self.comuna_entry, self.email_entry, self.codsucursal_entry, self.giro_entry, 
                     self.act_entry, self.api_key_entry, self.tpv_entry, self.ciudad_entry, self.region_entry]:
            entry.config(state='normal')
        # Habilitar también los checkbox
        self.autostart_check.config(state='normal')
        self.autoprocess_check.config(state='normal')
    
    def habilitar_edicion(self):
        """Solicita contraseña y habilita la edición de los campos si es correcta."""
        # Solicitar la contraseña con un messagebox
        clave_ingresada = simpledialog.askstring("Autenticación requerida", "Ingrese la clave para habilitar la edición:", show='*')
        self.logger.log_message("Solicitando Clave de admin....")
        
        if clave_ingresada:
            # Verificar si la clave es correcta
            if self.db_manager.verify_admin_password(clave_ingresada):
                # Habilitar los Entry para permitir edición
                self.enable_entries()
                
                messagebox.showinfo("Acceso concedido", "Los campos ahora están habilitados para su edición.")
                self.logger.log_message("Acceso concedido, Habilitando edición de configuraciones...")
            else:
                messagebox.showerror("Acceso denegado", "Clave incorrecta. No se pudo habilitar la edición.")
                self.logger.log_message("Clave incorrecta. No se pudo habilitar la edición....")
                self.logger.log_message_sindb("--------------------------------------------------------------------------------------------------------------")
                
        else:
            messagebox.showwarning("Acción cancelada", "No se ingresó ninguna clave.")
    
    def guardar_configuracion(self):
        """Guarda la configuración en la base de datos."""
        try:
            # Obtener los valores de cada campo
            rut_empresa = self.rut_entry.get()
            razon_social = self.razon_social_entry.get()
            telefono = self.telefono_entry.get()
            direccion = self.direc_entry.get()
            comuna = self.comuna_entry.get()
            email = self.email_entry.get()
            codsuc_sii = self.codsucursal_entry.get()
            giro = self.giro_entry.get()
            act_economica = self.act_entry.get()
            apikey = self.api_key_entry.get()
            tpv = self.tpv_entry.get()
            ciudad = self.ciudad_entry.get()
            region = self.region_entry.get()
            
            # Crear una tupla con los datos
            config_data = (rut_empresa, razon_social, telefono, direccion, comuna, email, 
                          codsuc_sii, giro, act_economica, apikey, tpv, ciudad, region)
            
            # Guardar en la base de datos
            if self.db_manager.save_config(config_data):
                # Mostrar mensaje de confirmación
                messagebox.showinfo("Guardar Configuración", "Configuración guardada exitosamente.")
                
                # Deshabilitar todos los campos de entrada
                self.disable_entries()
                
                # Registrar los valores guardados en el log
                self.logger.log_message(f"Valores guardados en la tabla config:")
                self.logger.log_message(f"  RUT Empresa: {rut_empresa}, Razón Social: {razon_social}, Teléfono: {telefono}, Email: {email}")
                self.logger.log_message(f"  Dirección: {direccion}, Comuna: {comuna}, Ciudad: {ciudad}, Región: {region}, Cód. Suc. SII: {codsuc_sii}")
                self.logger.log_message(f"  Giro: {giro}, Act. Económica: {act_economica}, TPV: {tpv}")
                self.logger.log_message_sindb("--------------------------------------------------------------------------------------------------------------")
            else:
                messagebox.showerror("Error", "No se pudo guardar la configuración.")
                
        except Exception as e:
            self.logger.log_message(f"Error al guardar configuración: {e}", "ERROR")
            messagebox.showerror("Error", f"No se pudo guardar la configuración: {e}")
            
    def check_autostart_status(self):
        """Verifica si la aplicación está configurada para iniciar con Windows."""
        try:
            # Obtener el nombre de la aplicación (basado en el ejecutable o script principal)
            app_name = "Plain_Text_Demon"
            
            # Abrir la clave del registro para programas de inicio
            registry_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            
            try:
                # Intentar obtener el valor (si existe)
                winreg.QueryValueEx(registry_key, app_name)
                # Si no hay excepción, la clave existe
                self.autostart_var.set(True)
                self.logger.log_message("La aplicación está configurada para iniciar con Windows.", "INFO")
            except WindowsError:
                # La clave no existe
                self.autostart_var.set(False)
                
            # Cerrar la clave del registro
            winreg.CloseKey(registry_key)
            
        except Exception as e:
            self.logger.log_message(f"Error al verificar estado de inicio automático: {e}", "ERROR")
            self.autostart_var.set(False)
    
    def toggle_autostart(self):
        """Activa o desactiva el inicio automático con Windows."""
        try:
            # Obtener el estado actual del checkbox
            autostart_enabled = self.autostart_var.get()
            
            # Obtener el nombre de la aplicación y la ruta del ejecutable
            app_name = "Plain_Text_Demon"
            
            # Determinar la ruta del ejecutable
            if getattr(sys, 'frozen', False):
                # Si estamos en un entorno empaquetado, obtener la ruta del ejecutable
                app_path = sys.executable
            else:
                # Si estamos en un entorno de desarrollo, obtener la ruta del script
                app_path = os.path.abspath(sys.argv[0])
                # En desarrollo, usamos pythonw.exe para ejecutar el script
                app_path = f'"{sys.executable}" "{app_path}"'
            
            # Abrir la clave del registro para programas de inicio
            registry_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            
            if autostart_enabled:
                # Agregar la aplicación al inicio de Windows
                winreg.SetValueEx(registry_key, app_name, 0, winreg.REG_SZ, app_path)
                self.logger.log_message("La aplicación ha sido configurada para iniciar con Windows.", "INFO")
            else:
                # Intentar eliminar la aplicación del inicio de Windows
                try:
                    winreg.DeleteValue(registry_key, app_name)
                    self.logger.log_message("La aplicación ya no iniciará con Windows.", "INFO")
                except WindowsError:
                    # Si la clave no existe, no hay problema
                    pass
            
            # Cerrar la clave del registro
            winreg.CloseKey(registry_key)
            
        except Exception as e:
            error_msg = f"Error al configurar inicio automático: {e}"
            self.logger.log_message(error_msg, "ERROR")
            messagebox.showerror("Error", error_msg)
            
            # Restaurar el estado del checkbox a su valor anterior
            self.autostart_var.set(not self.autostart_var.get())
    
    def check_autoprocess_status(self):
        """Verifica si el procesamiento automático está habilitado."""
        try:
            # Intentar obtener la configuración de autoprocess desde la base de datos
            # Suponemos que existe una tabla "app_config" con una columna "autoprocess"
            autoprocess_enabled = self.db_manager.get_autoprocess_config()
            
            if autoprocess_enabled is not None:
                self.autoprocess_var.set(autoprocess_enabled)
                status = "habilitado" if autoprocess_enabled else "deshabilitado"
                self.logger.log_message(f"Inicio automático de procesamiento {status}.", "INFO")
            else:
                # Si no hay configuración, establecer por defecto como deshabilitado
                self.autoprocess_var.set(False)
                
        except Exception as e:
            self.logger.log_message(f"Error al verificar estado de inicio automático de procesamiento: {e}", "ERROR")
            self.autoprocess_var.set(False)
    
    def toggle_autoprocess(self):
        """Activa o desactiva el inicio automático del procesamiento."""
        try:
            # Obtener el estado actual del checkbox
            autoprocess_enabled = self.autoprocess_var.get()
            
            # Guardar la configuración en la base de datos
            if self.db_manager.save_autoprocess_config(autoprocess_enabled):
                status = "habilitado" if autoprocess_enabled else "deshabilitado"
                self.logger.log_message(f"Inicio automático de procesamiento {status}.", "INFO")
            else:
                # Si hubo un error al guardar, restaurar el estado del checkbox
                self.autoprocess_var.set(not autoprocess_enabled)
                self.logger.log_message("Error al guardar configuración de inicio automático de procesamiento.", "ERROR")
                
        except Exception as e:
            error_msg = f"Error al configurar inicio automático de procesamiento: {e}"
            self.logger.log_message(error_msg, "ERROR")
            
            # Restaurar el estado del checkbox a su valor anterior
            self.autoprocess_var.set(not self.autoprocess_var.get())