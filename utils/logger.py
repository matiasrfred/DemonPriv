# -*- coding: utf-8 -*-
"""
Módulo para funciones de registro (logging).
"""

import os
import sqlite3
import tkinter as tk
from datetime import datetime
from config.settings import DB_CONFIG

class Logger:
    """Clase para gestionar los logs de la aplicación."""

    def __init__(self, log_textbox):
        """
        Inicializa el logger.

        Args:
            log_textbox: Widget de texto donde se mostrarán los logs.
        """
        self.log_textbox = log_textbox
        
        # Asegurar que el directorio donde se almacenará la base de datos exista
        db_dir = os.path.dirname(DB_CONFIG["path"])
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def log_message(self, message, tipo="INFO"):
        """
        Registra un mensaje en el textbox y en la base de datos SQLite.

        Args:
            message: Mensaje a registrar.
            tipo: Tipo de mensaje (INFO, ERROR, etc.).
        """
        # Obtener fecha y hora actual
        current_date = datetime.now().strftime("%d/%m/%Y")
        current_time = datetime.now().strftime("%H:%M:%S")
        full_message = f"{current_date} {current_time} - [{tipo}] {message}\n"

        # Insertar el log en el log_textbox
        self._insert_into_textbox(full_message)

        # Guardar el log en la base de datos SQLite
        try:
            self._save_to_db(current_date, current_time, tipo, message)
        except Exception as e:
            error_msg = f"Error al guardar log en la base de datos: {str(e)}"
            print(error_msg)  # Imprimir en consola para depuración
            self._insert_into_textbox(f"{datetime.now().strftime('%d/%m/%Y')} {datetime.now().strftime('%H:%M:%S')} - [ERROR] {error_msg}\n")

    def log_message_sindb(self, message, tipo="INFO"):
        """
        Registra un mensaje solo en el textbox (sin guardarlo en la base de datos).

        Args:
            message: Mensaje a registrar.
            tipo: Tipo de mensaje (INFO, ERROR, etc.).
        """
        # Obtener fecha y hora actual
        current_date = datetime.now().strftime("%d/%m/%Y")
        current_time = datetime.now().strftime("%H:%M:%S")
        full_message = f"{current_date} {current_time} - [{tipo}] {message}\n"

        # Insertar el log en el log_textbox
        self._insert_into_textbox(full_message)

    def _insert_into_textbox(self, full_message):
        """Muestra el mensaje en el widget de logs."""
        try:
            self.log_textbox.config(state=tk.NORMAL)
            self.log_textbox.insert(tk.END, full_message)
            self.log_textbox.config(state=tk.DISABLED)
            self.log_textbox.see(tk.END)
        except Exception as e:
            print(f"Error al insertar en textbox: {str(e)}")

    def _save_to_db(self, date, time, tipo, message):
        """Guarda el mensaje en la base de datos SQLite."""
        try:
            # Asegurar que la tabla log_procesos existe antes de intentar insertar
            with sqlite3.connect(DB_CONFIG["path"]) as conn:
                cursor = conn.cursor()
                
                # Verificar si la tabla log_procesos existe
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='log_procesos'")
                if not cursor.fetchone():
                    # Si no existe, crearla
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS "log_procesos" (
                            "fecha" TEXT NOT NULL,
                            "hora" TEXT,
                            "tipo" TEXT,
                            "asunto" TEXT
                        )
                    """)
                    conn.commit()
                
                # Insertar el log
                cursor.execute("INSERT INTO log_procesos(fecha, hora, tipo, asunto) VALUES (?, ?, ?, ?)",
                               (date, time, tipo, message))
                conn.commit()
        except sqlite3.Error as e:
            # En caso de error, lanzar la excepción para manejarla en el método llamador
            raise Exception(f"Error SQLite al guardar log: {str(e)}")