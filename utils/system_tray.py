# -*- coding: utf-8 -*-
"""
Módulo para implementar la funcionalidad de system tray.
"""

import os
import threading
import pystray
from PIL import Image, ImageTk
from config.settings import IMG_DIR

class SystemTray:
    """Clase para gestionar la funcionalidad del system tray."""
    
    def __init__(self, root, logger=None):
        """
        Inicializa el gestor del system tray.
        
        Args:
            root: Ventana principal de la aplicación.
            logger: Objeto para registrar eventos (opcional).
        """
        self.root = root
        self.logger = logger
        self.icon = None
        self.icon_image_path = os.path.join(IMG_DIR, "app_icon.png")
        self.is_minimized = False
        
        # Configurar el evento de cierre de la ventana
        self.original_protocol = root.protocol("WM_DELETE_WINDOW")
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Configurar el evento de minimización
        root.bind("<Unmap>", self.on_minimize)
        
        # Iniciar el icono del system tray en un hilo separado
        self.setup_tray_icon()
    
    def setup_tray_icon(self):
        """Configura el icono del system tray."""
        try:
            # Cargar la imagen para el icono
            icon_image = Image.open(self.icon_image_path)
            
            # Crear el menú del system tray
            menu = pystray.Menu(
                pystray.MenuItem('Mostrar', self.show_window)
            )
            
            # Crear el icono
            self.icon = pystray.Icon("plain_text_demon", icon_image, "Plain Text Bowa", menu)
            
            # Iniciar el icono en un hilo separado
            threading.Thread(target=self.icon.run, daemon=True).start()
            
            if self.logger:
                self.logger.log_message("System tray inicializado correctamente.", "INFO")
                
        except Exception as e:
            if self.logger:
                self.logger.log_message(f"Error al inicializar system tray: {e}", "ERROR")
            else:
                print(f"Error al inicializar system tray: {e}")
    
    def on_minimize(self, event=None):
        """
        Maneja el evento de minimización de la ventana.
        
        Args:
            event: Evento de minimización (opcional).
        """
        # Comprobar si realmente es un evento de minimización
        # La propiedad state será 'iconic' cuando la ventana esté minimizada
        if event and self.root.state() == 'iconic':
            self.minimize_to_tray()
    
    def minimize_to_tray(self):
        """Minimiza la aplicación al system tray."""
        if not self.is_minimized:
            self.root.withdraw()  # Ocultar la ventana principal
            self.is_minimized = True
            
            if self.logger:
                self.logger.log_message("Aplicación minimizada al system tray.", "INFO")
    
    def show_window(self, icon=None, item=None):
        """
        Muestra la ventana principal desde el system tray.
        
        Args:
            icon: Icono del system tray (opcional).
            item: Elemento del menú seleccionado (opcional).
        """
        self.root.deiconify()  # Mostrar la ventana principal
        self.root.state('normal')  # Restaurar el estado normal
        self.root.focus_force()  # Dar foco a la ventana
        self.is_minimized = False
        
        if self.logger:
            self.logger.log_message("Aplicación restaurada desde el system tray.", "INFO")
    
    def on_close(self):
        """Maneja el evento de cierre de la ventana."""
        try:
            # Detener el icono del system tray si existe
            if self.icon:
                self.icon.stop()
                
            # Llamar al protocolo de cierre original
            if callable(self.original_protocol):
                self.original_protocol()
            else:
                self.root.destroy()
                
            if self.logger:
                self.logger.log_message("Aplicación cerrada correctamente.", "INFO")
                
        except Exception as e:
            if self.logger:
                self.logger.log_message(f"Error al cerrar la aplicación: {e}", "ERROR")
            else:
                print(f"Error al cerrar la aplicación: {e}")
            
            # Asegurarse de que la aplicación se cierre en caso de error
            self.root.destroy()
    
    def stop(self):
        """Detiene el icono del system tray."""
        if self.icon:
            self.icon.stop()