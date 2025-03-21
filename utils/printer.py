# -*- coding: utf-8 -*-
"""
Módulo para funciones relacionadas con impresoras y manejo de PDFs.
"""

import os
import subprocess
import sys
import time
import win32print
import requests
import tempfile
from config.database import DatabaseManager

# Caché para la configuración de impresión
_print_config_cache = None
_db_manager_instance = None

def obtener_impresoras():
    """
    Obtiene la lista de impresoras disponibles en el sistema.
    
    Returns:
        list: Lista con los nombres de las impresoras disponibles.
    """
    impresoras = []
    try:
        # Enumera todas las impresoras disponibles en el sistema
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        for printer in printers:
            impresoras.append(printer[2])  # El nombre de la impresora está en la tercera posición
    except Exception as e:
        print(f"Error al obtener las impresoras: {e}")
    
    return impresoras

def imprimir_archivo(nombre_impresora, ruta_archivo, num_copias=1):
    """
    Imprime un archivo utilizando la impresora especificada.
    
    Args:
        nombre_impresora: Nombre de la impresora a utilizar.
        ruta_archivo: Ruta del archivo a imprimir.
        num_copias: Número de copias a imprimir.
        
    Returns:
        bool: True si se imprimió correctamente, False en caso contrario.
    """
    try:
        # Establecer la impresora predeterminada
        win32print.SetDefaultPrinter(nombre_impresora)
        
        # Imprimir el archivo
        # Esta es una versión simplificada, puede necesitar más código según el tipo de archivo
        with open(ruta_archivo, 'rb') as file:
            win32print.StartDocPrinter(win32print.OpenPrinter(nombre_impresora), 1, ('Documento', None, 'RAW'))
            win32print.WritePrinter(win32print.OpenPrinter(nombre_impresora), file.read())
            win32print.EndDocPrinter(win32print.OpenPrinter(nombre_impresora))
        
        return True
    except Exception as e:
        print(f"Error al imprimir: {e}")
        return False
    
def get_print_config(logger=None, force_refresh=False):
    """
    Obtiene la configuración de impresión, utilizando caché si está disponible.
    
    Args:
        logger: Objeto Logger para registrar eventos (opcional).
        force_refresh: Fuerza una actualización desde la base de datos.
        
    Returns:
        tuple: Configuración de impresión.
    """
    global _print_config_cache, _db_manager_instance
    
    # Si hay caché y no se requiere actualización, usar la caché
    if _print_config_cache is not None and not force_refresh:
        return _print_config_cache
    
    # Si no hay instancia de DatabaseManager, crearla
    if _db_manager_instance is None:
        _db_manager_instance = DatabaseManager(log_function=logger.log_message if logger else None)
    
    try:
        # Obtener la configuración de la base de datos
        _print_config_cache = _db_manager_instance.get_print_config()
        if logger:
            logger.log_message("Configuración de impresión cargada desde la base de datos", "INFO")
        return _print_config_cache
    except Exception as e:
        if logger:
            logger.log_message(f"Error al cargar configuración de impresión: {e}", "ERROR")
        return None
    
def procesar_respuesta_api(respuesta_api, logger=None, ruta_acrobat=None, print_config=None):
    """
    Procesa la respuesta de la API y realiza acciones de impresión y/o descarga
    según la configuración en la base de datos. Usa Adobe Acrobat Reader para imprimir en Windows.
    
    Args:
        respuesta_api: Diccionario con la respuesta de la API.
        logger: Objeto Logger para registrar eventos (opcional).
        ruta_acrobat: Ruta al ejecutable de Adobe Acrobat Reader (opcional).
        print_config: Configuración de impresión previa (opcional).
        
    Returns:
        bool: True si se procesó correctamente, False en caso contrario.
    """
    try:
        # Verificar si la respuesta es válida y contiene un PDF path
        if not respuesta_api or 'PDFPATH' not in respuesta_api:
            if logger:
                logger.log_message("La respuesta de la API no contiene un path de PDF válido", "ERROR")
            return False
        
        pdf_url = respuesta_api['PDFPATH']
        folio = respuesta_api.get('FOLIO', 'sin_folio')
        
        if logger:
            logger.log_message(f"Procesando PDF desde: {pdf_url} (Folio: {folio})", "INFO")
        
        # Usar la configuración pasada o obtenerla de caché/BD
        if print_config is None:
            print_config = get_print_config(logger)
            
        if not print_config:
            if logger:
                logger.log_message("No se encontró configuración de impresión", "WARNING")
            return False
            
        hab_printer, printer_name, num_copias, hab_desc_local, ruta_descargas = print_config
        
        # Descargar el PDF desde la URL
        try:
            response = requests.get(pdf_url, stream=True)
            response.raise_for_status()  # Lanzará una excepción si hay error HTTP
            
            # Crear un archivo temporal para el PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_path = temp_file.name
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
            
            if logger:
                logger.log_message(f"PDF descargado temporalmente en: {temp_path}", "INFO")
            
            # Procesar según configuración
            resultado = True
            
            # Si está habilitada la descarga local
            if hab_desc_local:
                if not os.path.exists(ruta_descargas):
                    os.makedirs(ruta_descargas, exist_ok=True)
                
                nombre_archivo = f"{folio}.pdf"
                ruta_destino = os.path.join(ruta_descargas, nombre_archivo)
                
                try:
                    # Copiar el archivo temporal a la ruta de destino
                    with open(temp_path, 'rb') as src, open(ruta_destino, 'wb') as dst:
                        dst.write(src.read())
                    
                    if logger:
                        logger.log_message(f"PDF guardado en: {ruta_destino}", "INFO")
                except Exception as e:
                    if logger:
                        logger.log_message(f"Error al guardar PDF en destino: {e}", "ERROR")
                    resultado = False
            
            # Si está habilitada la impresión y estamos en Windows
            if hab_printer and os.name == 'nt':  # Solo para Windows
                try:
                    # Primero configuramos la impresora predeterminada
                    win32print.SetDefaultPrinter(printer_name)
                    
                    # Buscar SumatraPDF en ubicaciones comunes
                    sumatra_paths = [
                        r"C:\Program Files\SumatraPDF\SumatraPDF.exe",
                        r"C:\Program Files (x86)\SumatraPDF\SumatraPDF.exe",
                        os.path.join(os.environ.get('PROGRAMFILES', r'C:\Program Files'), 'SumatraPDF', 'SumatraPDF.exe'),
                        os.path.join(os.environ.get('PROGRAMFILES(X86)', r'C:\Program Files (x86)'), 'SumatraPDF', 'SumatraPDF.exe')
                    ]
                    
                    sumatra_path = None
                    for path in sumatra_paths:
                        if os.path.isfile(path):
                            sumatra_path = path
                            break
                    
                    # Si encontramos SumatraPDF, usarlo para imprimir en modo silencioso
                    if sumatra_path:
                        if logger:
                            logger.log_message(f"Imprimiendo con SumatraPDF en: {printer_name}", "INFO")
                        
                        for _ in range(int(num_copias)):
                            # SumatraPDF con parámetros de impresión silenciosa
                            # -print-to impresora -print-settings "opciones" -silent archivo.pdf
                            comando = [
                                sumatra_path, 
                                "-print-to", printer_name, 
                                "-silent", 
                                "-exit-when-done",
                                temp_path
                            ]
                            proceso = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            stdout, stderr = proceso.communicate()
                            
                            # Esperar a que el trabajo de impresión se complete
                            time.sleep(1)
                        
                        if logger:
                            logger.log_message(f"PDF enviado a imprimir ({num_copias} copias) en: {printer_name} usando SumatraPDF", "INFO")
                    
                    # Si no encontramos SumatraPDF, intentar con Adobe Acrobat si está disponible
                    elif ruta_acrobat and os.path.isfile(ruta_acrobat):
                        if logger:
                            logger.log_message(f"SumatraPDF no encontrado, usando Adobe Acrobat para imprimir", "WARNING")
                        
                        for _ in range(int(num_copias)):
                            # Adobe Acrobat con parámetros de impresión silenciosa
                            comando = [ruta_acrobat, "/t", temp_path, printer_name]
                            proceso = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            _, stderr = proceso.communicate()
                            time.sleep(2)
                        
                        if logger:
                            logger.log_message(f"PDF enviado a imprimir ({num_copias} copias) en: {printer_name} usando Adobe Acrobat", "INFO")
                    
                    # Si no encontramos ni SumatraPDF ni Adobe Acrobat, usar el método nativo de Windows
                    else:
                        if logger:
                            logger.log_message("SumatraPDF y Adobe Acrobat no encontrados, usando método nativo para imprimir", "WARNING")
                        
                        for _ in range(int(num_copias)):
                            os.startfile(temp_path, "print")
                            time.sleep(1)  # Breve pausa entre trabajos de impresión
                        
                        if logger:
                            logger.log_message(f"PDF enviado a imprimir ({num_copias} copias) en: {printer_name} usando método nativo", "INFO")
                except Exception as e:
                    if logger:
                        logger.log_message(f"Error al imprimir: {e}", "ERROR")
                    resultado = False
            
            # Limpieza: eliminar el archivo temporal
            try:
                os.unlink(temp_path)
            except Exception as e:
                if logger:
                    logger.log_message(f"Error al eliminar archivo temporal: {e}", "WARNING")
            
            return resultado
            
        except requests.exceptions.RequestException as e:
            if logger:
                logger.log_message(f"Error al descargar PDF: {e}", "ERROR")
            return False
            
    except Exception as e:
        if logger:
            logger.log_message(f"Error general al procesar respuesta de API: {e}", "ERROR")
        return False


def invalidar_cache():
    """
    Invalida la caché de configuración para forzar una recarga desde la base de datos.
    """
    global _print_config_cache
    _print_config_cache = None