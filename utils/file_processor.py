# -*- coding: utf-8 -*-
"""
Módulo para procesar archivos - Versión optimizada.
"""

import datetime
import os
import shutil
from utils.api import process_and_post_txt
from config.database import DatabaseManager
from utils.logger import Logger

class FileProcessor:
    """Clase para gestionar el procesamiento de archivos."""
    
    def __init__(self, logger=None, api_key=None):
        """
        Inicializa el procesador de archivos.
        
        Args:
            logger: Objeto Logger para registrar eventos.
            api_key: Clave API para enviar datos procesados.
        """
        self.logger = logger
        self.api_key = api_key
        self.is_running = False
        # Cargar configuración al inicio para evitar consultas repetitivas
        self.config_data = None
        self.db_manager = None
        if logger:
            # Inicializar DatabaseManager una sola vez
            self.db_manager = DatabaseManager(log_function=self.logger.log_message if self.logger else None)
    
    def set_api_key(self, api_key):
        """Establece la clave API."""
        self.api_key = api_key
    
    def start(self):
        """
        Inicia el procesamiento de archivos y carga la configuración de la BD.
        """
        # Cargar la configuración una sola vez al iniciar
        if self.db_manager:
            try:
                self.config_data = self.db_manager.load_config_data()
                if self.logger:
                    self.logger.log_message("Configuración cargada exitosamente al iniciar el procesador")
            except Exception as e:
                if self.logger:
                    self.logger.log_message(f"Error al cargar configuración inicial: {e}", "ERROR")
        
        self.is_running = True
    
    def stop(self):
        """Detiene el procesamiento de archivos."""
        self.is_running = False
    
    def process_files(self, ruta_procesar, ruta_procesado, intervalo, root):
        """
        Procesa los archivos de la carpeta especificada.
        
        Args:
            ruta_procesar: Ruta donde se buscarán los archivos a procesar.
            ruta_procesado: Ruta donde se moverán los archivos procesados.
            intervalo: Tiempo en segundos entre cada verificación.
            root: Ventana principal de Tkinter para programar la siguiente ejecución.
        """
        try:
            # Verificar si el directorio de procesar existe
            if not os.path.exists(ruta_procesar):
                if self.logger:
                    self.logger.log_message(f"Directorio {ruta_procesar} no encontrado.", "ERROR")
                return

            # Obtener lista de archivos en la ruta de procesar
            archivos = os.listdir(ruta_procesar)
            if not archivos:
                if self.logger:
                    self.logger.log_message("Directorio vacío.", "INFO")
                    self.logger.log_message_sindb("--------------------------------------------------------------------------------------------------------------", "INFO")
            else:
                # Ordenar por fecha de modificación y tomar el archivo más antiguo
                archivos.sort(key=lambda x: os.path.getmtime(os.path.join(ruta_procesar, x)))
                archivo_mas_antiguo = archivos[0]
                ruta_archivo = os.path.join(ruta_procesar, archivo_mas_antiguo)
                destino_procesado = os.path.join(ruta_procesado, archivo_mas_antiguo)

                if self.logger:
                    self.logger.log_message(f"Archivo encontrado: {archivo_mas_antiguo}")
                    self.logger.log_message(f"Procesando archivo: {archivo_mas_antiguo}")

                # Variable para controlar si el archivo debe ser movido
                mover_archivo = True
                
                # Verificar extensión del archivo para procesamiento específico
                if archivo_mas_antiguo.lower().endswith('.txt'):
                    if self.logger:
                        self.logger.log_message(f"Archivo TXT detectado, preparando para enviar a API: {archivo_mas_antiguo}")
                    
                    try:
                        # Usar la configuración ya cargada en el inicio
                        if not self.config_data:
                            # Solo si no se cargó previamente o necesita actualizarse
                            if not self.db_manager:
                                self.db_manager = DatabaseManager(log_function=self.logger.log_message if self.logger else None)
                            self.config_data = self.db_manager.load_config_data()
                            if self.logger:
                                self.logger.log_message("Cargando configuración por primera vez")
                        
                        if self.logger:
                            self.logger.log_message(f"Enviando a API: {archivo_mas_antiguo}")
                        
                        # Procesar y enviar a API usando la config ya cargada
                        result = process_and_post_txt(ruta_archivo, self.config_data, self.logger)
                        
                        if self.logger:
                            self.logger.log_message(f"Resultado de API: {result}")
                        
                        # Solo mover el archivo si la respuesta contiene StatusCode 200 y StatusDesc OK
                        if (result and 
                            result.get('StatusCode') == "200" and 
                            result.get('StatusDesc') == "OK"):
                            if self.logger:
                                self.logger.log_message(f"Archivo enviado a API exitosamente: {archivo_mas_antiguo}")
                        else:
                            # No mover el archivo a procesados, sino a error/mes_año
                            mover_archivo = False
                            # Obtener la fecha actual para la carpeta mes_año
                            fecha_actual = datetime.datetime.now()
                            nombre_carpeta_mes = f"{fecha_actual.strftime('%m_%Y')}"  # formato: mes_año (01_2025)
                            
                            # Crear la estructura de carpetas para errores: error/mes_año
                            ruta_error_base = os.path.join(ruta_procesado, "error")
                            os.makedirs(ruta_error_base, exist_ok=True)
                            
                            ruta_error_mes = os.path.join(ruta_error_base, nombre_carpeta_mes)
                            os.makedirs(ruta_error_mes, exist_ok=True)
                            
                            # Definir la ruta de destino en la carpeta de error del mes correspondiente
                            destino_error = os.path.join(ruta_error_mes, archivo_mas_antiguo)
                            
                            try:
                                shutil.move(ruta_archivo, destino_error)
                                if self.logger:
                                    self.logger.log_message(f"Error al enviar a API. StatusCode: {result.get('StatusCode', 'No disponible')}, StatusDesc: {result.get('StatusDesc', 'No disponible')}. Archivo movido a carpeta de error: {destino_error}", "ERROR")
                            except Exception as move_error:
                                if self.logger:
                                    self.logger.log_message(f"No se pudo mover el archivo a la carpeta de error: {move_error}", "ERROR")
                    except Exception as api_error:
                        mover_archivo = False
                        if self.logger:
                            self.logger.log_message(f"Error al procesar con API: {api_error}", "ERROR")
                        
                        # Obtener la fecha actual para la carpeta mes_año
                        fecha_actual = datetime.datetime.now()
                        nombre_carpeta_mes = f"{fecha_actual.strftime('%m_%Y')}"  # formato: mes_año (01_2025)
                        
                        # Crear la estructura de carpetas para errores: error/mes_año
                        ruta_error_base = os.path.join(ruta_procesado, "error")
                        os.makedirs(ruta_error_base, exist_ok=True)
                        
                        ruta_error_mes = os.path.join(ruta_error_base, nombre_carpeta_mes)
                        os.makedirs(ruta_error_mes, exist_ok=True)
                        
                        # Definir la ruta de destino en la carpeta de error del mes correspondiente
                        destino_error = os.path.join(ruta_error_mes, archivo_mas_antiguo)
                        
                        try:
                            shutil.move(ruta_archivo, destino_error)
                            if self.logger:
                                self.logger.log_message(f"Error al procesar con API. Archivo movido a carpeta de error: {destino_error}", "ERROR")
                        except Exception as move_error:
                            if self.logger:
                                self.logger.log_message(f"No se pudo mover el archivo a la carpeta de error: {move_error}", "ERROR")
                
                # Mover el archivo al directorio procesado solo si se obtuvo éxito
                if mover_archivo:
                    try:
                        shutil.move(ruta_archivo, destino_procesado)
                        if self.logger:
                            self.logger.log_message(f"Archivo procesado y movido a carpeta procesados: {archivo_mas_antiguo}", "INFO")
                            self.logger.log_message_sindb("--------------------------------------------------------------------------------------------------------------", "INFO")
                    except Exception as e:
                        # Manejar errores al mover el archivo exitoso
                        if self.logger:
                            self.logger.log_message(f"Error al mover archivo procesado: {e}", "ERROR")
                        
                        # Obtener la fecha actual para la carpeta mes_año
                        fecha_actual = datetime.datetime.now()
                        nombre_carpeta_mes = f"{fecha_actual.strftime('%m_%Y')}"  # formato: mes_año (01_2025)
                        
                        # Crear la estructura de carpetas para errores: error/mes_año
                        ruta_error_base = os.path.join(ruta_procesado, "error")
                        os.makedirs(ruta_error_base, exist_ok=True)
                        
                        ruta_error_mes = os.path.join(ruta_error_base, nombre_carpeta_mes)
                        os.makedirs(ruta_error_mes, exist_ok=True)
                        
                        # Definir la ruta de destino en la carpeta de error del mes correspondiente
                        destino_error = os.path.join(ruta_error_mes, archivo_mas_antiguo)
                        
                        try:
                            shutil.move(ruta_archivo, destino_error)
                            if self.logger:
                                self.logger.log_message(f"Error al mover archivo. Movido a carpeta de error: {destino_error}. Error: {e}", "ERROR")
                        except Exception as move_error:
                            if self.logger:
                                self.logger.log_message(f"No se pudo mover el archivo a la carpeta de error: {move_error}", "ERROR")
                        finally:
                            if self.logger:
                                self.logger.log_message_sindb("--------------------------------------------------------------------------------------------------------------", "INFO")

            # Programar la siguiente ejecución si el proceso sigue activo
            if self.is_running:
                root.after(intervalo * 1000, lambda: self.process_files(ruta_procesar, ruta_procesado, intervalo, root))
                
        except Exception as e:
            if self.logger:
                self.logger.log_message(f"Error general en el proceso: {e}", "ERROR")