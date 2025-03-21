# -*- coding: utf-8 -*-
"""
Configuraciones generales de la aplicación.
"""

import os
import sys

def get_base_path():
    """
    Obtiene la ruta base adecuada dependiendo de si la aplicación está empaquetada
    como un ejecutable o se ejecuta en modo desarrollo.
    """
    # Si estamos ejecutando como .exe (PyInstaller)
    if getattr(sys, 'frozen', False):
        # Usar el directorio del ejecutable
        app_path = os.path.dirname(sys.executable)
    else:
        # En modo desarrollo usar el directorio del proyecto
        app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return app_path

# Obtener la ruta absoluta del directorio base del proyecto
BASE_DIR = get_base_path()

# Rutas de directorios
IMG_DIR = os.path.join(BASE_DIR, "img")

# Configuración de la base de datos con ruta absoluta
DB_CONFIG = {
    "path": os.path.join(BASE_DIR, "config.db")
}

# Configuración de la ventana principal
WINDOW_CONFIG = {
    "geometry": "1000x520",
    "title": "Plain_Text_Bowa",
    "resizable": (False, False),
    "icon": os.path.join(IMG_DIR, "logo.ico")  # Ruta absoluta al icono
}