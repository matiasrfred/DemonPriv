#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Punto de entrada principal para la aplicación.
"""

import os
import sys
import tempfile
import ctypes
import tkinter as tk
from tkinter import messagebox
from gui.app import create_app

# Nombre del archivo de bloqueo (con ruta completa)
TEMP_DIR = tempfile.gettempdir()  # Normalmente C:\Users\[Usuario]\AppData\Local\Temp
LOCK_FILE = os.path.join(TEMP_DIR, "plain_text_demon.lock")

def check_single_instance():
    """Verifica si la aplicación ya está en ejecución usando un archivo de bloqueo."""
    try:
        # Si el archivo ya existe, verificamos si el proceso aún está activo
        if os.path.exists(LOCK_FILE):
            with open(LOCK_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            # Verificamos si el proceso con el PID guardado sigue en ejecución (solo Windows)
            kernel32 = ctypes.windll.kernel32
            SYNCHRONIZE = 0x00100000
            process = kernel32.OpenProcess(SYNCHRONIZE, 0, pid)
            
            if process != 0:  # Si el proceso existe
                kernel32.CloseHandle(process)
                print(f"Aplicación ya en ejecución con PID {pid}")
                return False  # Ya está en ejecución
            
            # Si llegamos aquí, el proceso no existe, entonces podemos sobrescribir el archivo
            print(f"Se encontró un archivo de bloqueo, pero el proceso {pid} ya no existe")
        
        # Crear el archivo de bloqueo con el PID actual
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
        
        print(f"Archivo de bloqueo creado en: {LOCK_FILE}")
        
        # Registrar una función para eliminar el archivo de bloqueo al salir
        import atexit
        atexit.register(lambda: os.remove(LOCK_FILE) if os.path.exists(LOCK_FILE) else None)
        
        return True  # Instancia única, podemos continuar
    except Exception as e:
        print(f"Error al verificar instancia única: {e}")
        # En caso de error, permitimos que la aplicación se ejecute
        return True

def main():
    """Función principal que inicia la aplicación."""
    # Verificar si la aplicación ya está en ejecución
    if not check_single_instance():
        # Mostrar un mensaje y salir si la aplicación ya está en ejecución
        root = tk.Tk()
        root.withdraw()  # Ocultar la ventana principal
        messagebox.showwarning(
            "Aplicación ya en ejecución",
            "La aplicación ya está en ejecución. Solo se permite una instancia."
        )
        root.destroy()
        sys.exit(0)
    
    # Si no hay otra instancia en ejecución, iniciar la aplicación
    app = create_app()
    app.mainloop()

if __name__ == "__main__":
    main()