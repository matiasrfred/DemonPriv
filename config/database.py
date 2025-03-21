# -*- coding: utf-8 -*-
"""
Módulo para manejar las operaciones de base de datos.
"""

import os
import re
import sqlite3
import tkinter as tk
from tkinter import messagebox
from config.settings import DB_CONFIG

class DatabaseManager:
    """Clase para gestionar las operaciones de la base de datos."""
    
    def __init__(self, db_path=None, log_function=None):
        """
        Inicializa el gestor de base de datos.
        
        Args:
            db_path: Ruta al archivo de base de datos. Si es None, usa la ruta de DB_CONFIG.
            log_function: Función para registrar mensajes de log.
        """
        # Usar la ruta de la configuración si no se proporciona una específica
        self.db_path = db_path if db_path is not None else DB_CONFIG["path"]
        self.log_function = log_function
        
    def _log_message(self, message, tipo="INFO"):
        """Registra un mensaje utilizando la función de log proporcionada."""
        if self.log_function:
            self.log_function(message, tipo)
    
    def connect(self):
        """Establece una conexión a la base de datos."""
        try:
            # Asegurar que el directorio de la base de datos exista
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
                
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            self._log_message(f"Error al conectar con la base de datos: {e}", "ERROR")
            raise
    
    def execute_query(self, query, params=None):
        """
        Ejecuta una consulta SQL.
        
        Args:
            query: Consulta SQL a ejecutar.
            params: Parámetros para la consulta (opcional).
            
        Returns:
            Resultado de la consulta si es SELECT, None en caso contrario.
        """
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
                return result
            
            conn.commit()
            return None
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            self._log_message(f"Error en la consulta SQL: {e}", "ERROR")
            raise
        finally:
            if conn:
                conn.close()

    def create_tables(self):
        """Crea las tablas necesarias en la base de datos si no existen."""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Definir las consultas SQL para crear las tablas
            tablas_sql = [
                """
                CREATE TABLE IF NOT EXISTS "admin" (
                    "password" TEXT(50) NOT NULL
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS "config" (
                    "rut_empresa" TEXT(12) NOT NULL,
                    "razon_social" TEXT(200) NOT NULL,
                    "telefono" INTEGER,
                    "direccion" TEXT(200) NOT NULL,
                    "comuna" TEXT(25) NOT NULL,
                    "email" TEXT(100),
                    "codsuc_sii" INTEGER NOT NULL,
                    "giro" TEXT(80) NOT NULL,
                    "act_economica" INTEGER NOT NULL,
                    "apikey" TEXT NOT NULL,
                    "tpv" TEXT NOT NULL,
                    "ciudad" TEXT(30) NOT NULL,
                    "region" TEXT(35) NOT NULL
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS "directorios" (
                    "ruta_procesar" TEXT NOT NULL,
                    "ruta_procesado" TEXT NOT NULL,
                    "intervalo_exec" INTEGER NOT NULL
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS "impresion" (
                    "hab_printer" INTEGER,
                    "printer" TEXT,
                    "num_copias" INTEGER,
                    "habdesc_local" INTEGER,
                    "ruta_descargas" TEXT
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS "log_procesos" (
                    "fecha"	TEXT NOT NULL,
                    "hora"	TEXT,
                    "tipo"	TEXT,
                    "asunto"	TEXT
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS "app_config" (
                    "autoprocess" INTEGER DEFAULT 0,
                    "autostart_windows" INTEGER DEFAULT 0
                );
                """
            ]

            # Crear tablas si no existen
            for tabla_sql in tablas_sql:
                cursor.execute(tabla_sql)
            
            # Verificar si ya existe un registro en admin y agregarlo si no
            cursor.execute("SELECT COUNT(*) FROM admin")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO admin (password) VALUES ('admin00')")
            
            # Verificar si ya existe un registro en app_config y agregarlo si no
            cursor.execute("SELECT COUNT(*) FROM app_config")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO app_config (autoprocess, autostart_windows) VALUES (0, 0)")
            
            conn.commit()
            self._log_message("Tablas creadas o verificadas correctamente.", "INFO")
            
        except sqlite3.Error as e:
            self._log_message(f"Error al crear tablas: {e}", "ERROR")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def save_log(self, fecha, hora, tipo, asunto):
        """
        Guarda un registro de log en la base de datos.
        
        Args:
            fecha: Fecha del log.
            hora: Hora del log.
            tipo: Tipo de log (INFO, ERROR, etc.).
            asunto: Mensaje del log.
        """
        try:
            self.execute_query(
                "INSERT INTO log_procesos (fecha, hora, tipo, asunto) VALUES (?, ?, ?, ?)",
                (fecha, hora, tipo, asunto)
            )
        except sqlite3.Error as e:
            # No usar self._log_message para evitar recursión infinita
            print(f"Error al guardar log en la base de datos: {e}")
    
    def get_config(self):
        """
        Obtiene la configuración guardada en la base de datos.
        
        Returns:
            Registro de configuración o None si no existe.
        """
        try:
            result = self.execute_query("SELECT * FROM config LIMIT 1")
            return result[0] if result else None
        except sqlite3.Error as e:
            self._log_message(f"Error al obtener configuración: {e}", "ERROR")
            return None
    
    def save_config(self, config_data):
        """
        Guarda o actualiza la configuración en la base de datos.
        
        Args:
            config_data: Tupla con los datos de configuración.
            
        Returns:
            True si se guardó correctamente, False en caso contrario.
        """
        try:
            # Verificar si existe un registro en la tabla config
            result = self.execute_query("SELECT COUNT(*) FROM config")
            tiene_registro = result[0][0] > 0

            if tiene_registro:
                # Actualizar el registro existente
                self.execute_query(
                    '''
                    UPDATE config SET
                        rut_empresa = ?, razon_social = ?, telefono = ?, direccion = ?, 
                        comuna = ?, email = ?, codsuc_sii = ?, giro = ?, act_economica = ?, 
                        apikey = ?, tpv = ?, ciudad = ?, region = ?
                    ''', 
                    config_data
                )
                self._log_message("Configuración actualizada exitosamente.", "INFO")
            else:
                # Insertar un nuevo registro
                self.execute_query(
                    '''
                    INSERT INTO config (
                        rut_empresa, razon_social, telefono, direccion, comuna, email,
                        codsuc_sii, giro, act_economica, apikey, tpv, ciudad, region
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', 
                    config_data
                )
                self._log_message("Configuración guardada exitosamente.", "INFO")
            
            return True
        except Exception as e:
            self._log_message(f"Error al guardar configuración: {e}", "ERROR")
            return False
    
    def get_directories(self):
        """
        Obtiene la configuración de directorios guardada.
        
        Returns:
            Configuración de directorios o None si no existe.
        """
        try:
            result = self.execute_query("SELECT * FROM directorios LIMIT 1")
            return result[0] if result else None
        except sqlite3.Error as e:
            self._log_message(f"Error al obtener directorios: {e}", "ERROR")
            return None
    
    def save_directories(self, directories_data):
        """
        Guarda o actualiza la configuración de directorios.
        
        Args:
            directories_data: Tupla con los datos de directorios.
            
        Returns:
            True si se guardó correctamente, False en caso contrario.
        """
        try:
            # Verificar si existe un registro en la tabla directorios
            result = self.execute_query("SELECT COUNT(*) FROM directorios")
            tiene_registro = result[0][0] > 0

            if tiene_registro:
                # Actualizar el registro existente
                self.execute_query(
                    '''
                    UPDATE directorios SET
                        ruta_procesar = ?, ruta_procesado = ?, intervalo_exec = ?
                    ''', 
                    directories_data
                )
                self._log_message("Directorios actualizados exitosamente.", "INFO")
            else:
                # Insertar un nuevo registro
                self.execute_query(
                    '''
                    INSERT INTO directorios (ruta_procesar, ruta_procesado, intervalo_exec)
                    VALUES (?, ?, ?)
                    ''', 
                    directories_data
                )
                self._log_message("Directorios guardados exitosamente.", "INFO")
            
            return True
        except Exception as e:
            self._log_message(f"Error al guardar directorios: {e}", "ERROR")
            return False
    
    def get_print_config(self):
        """
        Obtiene la configuración de impresión guardada.
        
        Returns:
            Configuración de impresión o None si no existe.
        """
        try:
            result = self.execute_query("SELECT * FROM impresion LIMIT 1")
            return result[0] if result else None
        except sqlite3.Error as e:
            self._log_message(f"Error al obtener configuración de impresión: {e}", "ERROR")
            return None
    
    def save_print_config(self, print_data):
        """
        Guarda o actualiza la configuración de impresión.
        
        Args:
            print_data: Tupla con los datos de impresión.
            
        Returns:
            True si se guardó correctamente, False en caso contrario.
        """
        try:
            # Verificar si existe un registro en la tabla impresion
            result = self.execute_query("SELECT COUNT(*) FROM impresion")
            tiene_registro = result[0][0] > 0

            if tiene_registro:
                # Actualizar el registro existente
                self.execute_query(
                    '''
                    UPDATE impresion SET
                        hab_printer = ?, printer = ?, num_copias = ?, habdesc_local = ?, ruta_descargas = ?
                    ''', 
                    print_data
                )
                self._log_message("Configuración de impresión actualizada exitosamente.", "INFO")
            else:
                # Insertar un nuevo registro
                self.execute_query(
                    '''
                    INSERT INTO impresion (hab_printer, printer, num_copias, habdesc_local, ruta_descargas)
                    VALUES (?, ?, ?, ?, ?)
                    ''', 
                    print_data
                )
                self._log_message("Configuración de impresión guardada exitosamente.", "INFO")
            
            return True
        except Exception as e:
            self._log_message(f"Error al guardar configuración de impresión: {e}", "ERROR")
            return False
    
    def verify_admin_password(self, password):
        """
        Verifica si la contraseña de administrador es correcta.
        
        Args:
            password: Contraseña a verificar.
            
        Returns:
            True si la contraseña es correcta, False en caso contrario.
        """
        try:
            result = self.execute_query("SELECT password FROM admin LIMIT 1")
            if result and result[0][0] == password:
                return True
            return False
        except sqlite3.Error as e:
            self._log_message(f"Error al verificar contraseña: {e}", "ERROR")
            return False
        
    def load_config_data(self):
        """
        Carga los campos específicos de la tabla config que se necesitan
        para la función process_and_post_txt.
        
        Returns:
            dict: Diccionario con los campos de configuración necesarios
        """
        config_fields = {
            'rut_empresa': '',
            'razon_social': '',
            'giro': '',
            'act_economica': '',
            'direccion': '',
            'comuna': '',
            'telefono': '',
            'codsuc_sii': '',
            'email': '',
            'apikey': '',
            'tpv': ''
        }
        
        try:
            # Obtener el registro de configuración
            config = self.get_config()
            
            if config:
                # Mapear los campos según el orden en la tabla
                config_fields['rut_empresa'] = re.sub(r'\.', '', config[0])
                config_fields['razon_social'] = config[1]
                config_fields['telefono'] = config[2]
                config_fields['direccion'] = config[3]
                config_fields['comuna'] = config[4]
                config_fields['email'] = config[5]
                config_fields['codsuc_sii'] = config[6]
                config_fields['giro'] = config[7]
                config_fields['act_economica'] = config[8]
                config_fields['apikey'] = config[9]
                config_fields['tpv'] = config[10]
        except Exception as e:
            if self.log_function:
                self.log_function(f"Error al cargar configuración: {e}", "ERROR")
            else:
                print(f"Error al cargar configuración: {e}")
        
        return config_fields
    
    def get_autoprocess_config(self):
        """
        Obtiene la configuración de inicio automático del procesamiento.
        
        Returns:
            bool: True si está habilitado, False en caso contrario. None si ocurre un error.
        """
        try:
            result = self.execute_query("SELECT autoprocess FROM app_config LIMIT 1")
            if result and len(result) > 0:
                # Convertir el valor de INTEGER a booleano (0 = False, 1 = True)
                return bool(result[0][0])
            else:
                # Si no hay registros, insertar uno con valor predeterminado False
                self.execute_query("INSERT INTO app_config (autoprocess, autostart_windows) VALUES (0, 0)")
                return False
        except sqlite3.Error as e:
            self._log_message(f"Error al obtener configuración de autoprocess: {e}", "ERROR")
            return None

    def save_autoprocess_config(self, enabled):
        """
        Guarda la configuración de inicio automático del procesamiento.
        
        Args:
            enabled: True para habilitar, False para deshabilitar.
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario.
        """
        try:
            # Convertir el booleano a INTEGER (0 o 1)
            autoprocess_value = 1 if enabled else 0
            
            # Verificar si existe un registro en la tabla app_config
            result = self.execute_query("SELECT COUNT(*) FROM app_config")
            tiene_registro = result[0][0] > 0

            if tiene_registro:
                # Actualizar el registro existente
                self.execute_query(
                    "UPDATE app_config SET autoprocess = ?", 
                    (autoprocess_value,)
                )
                self._log_message(f"Configuración de inicio automático de procesamiento {'habilitada' if enabled else 'deshabilitada'}.", "INFO")
            else:
                # Insertar un nuevo registro
                self.execute_query(
                    "INSERT INTO app_config (autoprocess, autostart_windows) VALUES (?, 0)",
                    (autoprocess_value,)
                )
                self._log_message(f"Configuración de inicio automático de procesamiento {'habilitada' if enabled else 'deshabilitada'}.", "INFO")
            
            return True
        except Exception as e:
            self._log_message(f"Error al guardar configuración de inicio automático: {e}", "ERROR")
            return False