def process_and_post_txt(file_path, config_data, logger=None):
    """
    Procesa un archivo TXT y envía los datos a la API.
    Soporta DTE tipo 39 (Boleta) y tipo 33 (Factura).
    
    Args:
        file_path: Ruta al archivo TXT.
        config_data: Diccionario con datos de configuración ya cargados.
        logger: Objeto Logger para registrar eventos (opcional).
        
    Returns:
        dict: Respuesta de la API o información de error.
    """
    
    # Extraer los campos de configuración
    rut_empresa = config_data["rut_empresa"]
    razon_social = config_data["razon_social"]
    giro = config_data["giro"]
    act_economica = config_data["act_economica"]
    direccion = config_data["direccion"]
    comuna = config_data["comuna"]
    telefono = config_data["telefono"]
    codsuc_sii = config_data["codsuc_sii"]
    email = config_data["email"]
    apikey = config_data["apikey"]
    tpv = config_data["tpv"]
    
    try:
        # Leer el archivo
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Procesar las secciones del archivo
        sections = {}
        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith("->"):
                current_section = line.strip("->").strip("<-")
                sections[current_section] = []
            elif current_section:
                sections[current_section].append(line)
        
        # Determinar el tipo de DTE
        tipo_dte = None
        
        # Para Boleta (DTE 39)
        if "Boleta" in sections:
            boleta_data = sections["Boleta"][0].split(";") if sections.get("Boleta") else []
            tipo_dte = int(boleta_data[0]) if boleta_data else 39
        
        # Para Factura (DTE 33)
        elif "Encabezado" in sections:
            encabezado_data = sections["Encabezado"][0].split(";") if sections.get("Encabezado") else []
            tipo_dte = int(encabezado_data[0]) if encabezado_data else 33
        
        # Si es una Boleta (DTE 39)
        if tipo_dte == 39:
            return process_boleta(sections, config_data, logger)
        
        # Si es una Factura (DTE 33)
        elif tipo_dte == 33:
            return process_factura(sections, config_data, logger)
        
        else:
            error_msg = f"Tipo de DTE no reconocido: {tipo_dte}"
            if logger:
                logger.log_message(error_msg, "ERROR")
            return {"success": False, "error": error_msg}

    except Exception as e:
        if logger:
            logger.log_message(f"Error al procesar el archivo o realizar la solicitud: {e}", "ERROR")
        return {"success": False, "error": str(e)}


def process_boleta(sections, config_data, logger=None):
    """
    Procesa un archivo TXT de Boleta (DTE 39) y envía los datos a la API.
    
    Args:
        sections: Diccionario con las secciones del archivo.
        config_data: Diccionario con datos de configuración.
        logger: Objeto Logger para registrar eventos (opcional).
        
    Returns:
        dict: Respuesta de la API o información de error.
    """
    import requests
    
    # Extraer los campos de configuración
    rut_empresa = config_data["rut_empresa"]
    razon_social = config_data["razon_social"]
    giro = config_data["giro"]
    act_economica = config_data["act_economica"]
    direccion = config_data["direccion"]
    comuna = config_data["comuna"]
    telefono = config_data["telefono"]
    codsuc_sii = config_data["codsuc_sii"]
    email = config_data["email"]
    apikey = config_data["apikey"]
    tpv = config_data["tpv"]
    
    try:
        # Extraer datos de la sección "Boleta"
        boleta = sections.get("Boleta", [])
        boleta_data = boleta[0].split(";") if boleta else []

        # Extraer datos de la sección "BoletaTotales"
        boleta_totales = sections.get("BoletaTotales", [])
        totales_data = boleta_totales[0].split(";") if boleta_totales else []
        monto_totales_original = int(totales_data[3])
        monto_totales = monto_totales_original

        # Extraer detalles de la sección "BoletaDetalle"
        boleta_detalle = sections.get("BoletaDetalle", [])
        detalle_items = []
        
        # Contador para mantener el número de línea de detalle actualizado
        nro_linea_detalle = len(boleta_detalle) + 1
        
        # Procesar cada línea del detalle original
        for line in boleta_detalle:
            parts = line.split(";")
            if len(parts) >= 6:
                precio_item = int(parts[5])
                monto_item = int(parts[7])
                monto_condesc = monto_item
                
                # Por defecto no hay descuento
                descuento_pct = 0
                descuento_monto = 0
                
                # Guardamos el ítem con una bandera para identificar que no es un recargo
                detalle_items.append({
                    "NroLinDet": int(parts[0]),
                    "NmbItem": parts[2],
                    "QtyItem": int(parts[4]),
                    "PrcItem": precio_item,
                    "MontoItem": monto_condesc,
                    "DescuentoPct": descuento_pct,
                    "DescuentoMonto": descuento_monto,
                    "IndExe": int(parts[3]),
                    "UnmdItem": parts[9],
                    "es_recargo": False  # Bandera para identificar que no es un recargo
                })
        
        # Verificar si existe la sección "BoletaDescRec"
        boleta_desc_rec = sections.get("BoletaDescRec", [])
        
        if boleta_desc_rec:
            for line in boleta_desc_rec:
                desc_rec_parts = line.split(";")
                if len(desc_rec_parts) >= 6:
                    tipo_dr = desc_rec_parts[1]  # D para descuento, R para recargo
                    descripcion_dr = desc_rec_parts[2]
                    tipo_valor_dr = desc_rec_parts[3]  # $ para monto fijo, % para porcentaje
                    valor_dr = int(desc_rec_parts[4])
                    tipo_exento_dr = int(desc_rec_parts[5])
                    
                    if tipo_dr == "D":  # Es un descuento
                        if tipo_valor_dr == "$":  # Es un monto fijo
                            # Para descuentos fijos, calculamos el porcentaje que representa del total
                            porcentaje_total = (valor_dr / monto_totales_original) * 100
                            
                            # Acumulamos el total de ítems no recargo para distribuir proporcional
                            total_items_no_recargo = sum(item["MontoItem"] for item in detalle_items 
                                                    if not item.get("es_recargo", False))
                            
                            for item in detalle_items:
                                # Verificamos que no sea un recargo antes de aplicar el descuento
                                if not item.get("es_recargo", False):
                                    # Calculamos la proporción de este ítem respecto al total
                                    proporcion = item["MontoItem"] / total_items_no_recargo if total_items_no_recargo > 0 else 0
                                    # Calculamos el monto de descuento para este ítem
                                    descuento_monto_item = round(valor_dr * proporcion)
                                    # Calculamos el porcentaje de descuento para este ítem específico
                                    item_porcentaje_descuento = (descuento_monto_item / item["MontoItem"]) * 100 if item["MontoItem"] > 0 else 0
                                    
                                    item["DescuentoPct"] = round(item_porcentaje_descuento, 1)
                                    item["DescuentoMonto"] = descuento_monto_item
                                    item["MontoItem"] = item["MontoItem"] - descuento_monto_item
                            
                            # Restar el descuento del total
                            monto_totales -= valor_dr
                            
                        elif tipo_valor_dr == "%":  # Es un porcentaje
                            porcentaje_descuento = valor_dr  # Ya es directamente el porcentaje
                            
                            # Aplicar el descuento solo a ítems que NO son recargos
                            for item in detalle_items:
                                # Verificamos que no sea un recargo antes de aplicar el descuento
                                if not item.get("es_recargo", False):
                                    item_monto = item["MontoItem"]
                                    descuento_monto_item = round(item_monto * (porcentaje_descuento / 100))
                                    item["DescuentoPct"] = round(porcentaje_descuento, 1)
                                    item["DescuentoMonto"] = descuento_monto_item
                                    item["MontoItem"] = item_monto - descuento_monto_item
                            
                            # Calcular el monto total del descuento y restarlo del total
                            monto_descuento = round(monto_totales_original * (porcentaje_descuento / 100))
                            monto_totales -= monto_descuento
                    elif tipo_dr == "R":  # Es un recargo
                        # Añadir el recargo como un nuevo ítem, con bandera es_recargo
                        detalle_items.append({
                            "NroLinDet": nro_linea_detalle,
                            "NmbItem": descripcion_dr,
                            "QtyItem": 1,
                            "PrcItem": valor_dr,
                            "MontoItem": valor_dr,
                            "DescuentoPct": 0,
                            "DescuentoMonto": 0,
                            "IndExe": tipo_exento_dr,
                            "UnmdItem": "UND",  # Unidad por defecto
                            "es_recargo": True  # Bandera para identificar que es un recargo
                        })
                        
                        # Incrementar el contador de líneas
                        nro_linea_detalle += 1
                        
                        # Sumar el recargo al total
                        monto_totales += valor_dr


        # Limpiamos los items antes de construir el body para quitar la bandera es_recargo
        for item in detalle_items:
            if "es_recargo" in item:
                del item["es_recargo"]
        
        # Construir el cuerpo del request
        body = {
            "response": ["80MM", "PDFPATH"],
            "dte": {
                "Encabezado": {
                    "IdDoc": {
                        "IndServicio": int(boleta_data[3]),
                        "TipoDTE": int(boleta_data[0]),
                        "Folio": int(boleta_data[1]),
                        "FchEmis": boleta_data[2],
                        "FmaPago": 1,
                        "MedioPago": "EF",
                        "MntBruto": 1
                    },
                    "Emisor": {
                        "RUTEmisor": rut_empresa,
                        "RznSocEmisor": razon_social,
                        "GiroEmisor": giro,
                        "Acteco": act_economica,
                        "DirOrigen": direccion,
                        "CmnaOrigen": comuna,
                        "Telefono": telefono,
                        "CdgSIISucur": codsuc_sii,
                        "Email": email
                    },
                    "Receptor": {
                        "RUTRecep": boleta_data[8],
                        "RznSocRecep": boleta_data[10],
                        "GiroRecep": boleta_data[11],
                        "DirRecep": boleta_data[12],
                        "CmnaRecep": boleta_data[13]
                    },
                    "Totales": {
                        "MntNeto": 0,
                        "TasaIVA": 19,
                        "IVA": 0,
                        "MntTotal": monto_totales,
                        "MontoPeriodo": 0,
                        "VlrPagar": 0,
                        "MntExe": 0,
                        "MontoNF": 0
                    }
                },
                "Detalle": detalle_items,
                "Referencia": None,
                "DscRcgGlobal": None
            },
            "TEDXML": "",
            "TPVMobil": "",
            "IdMsg": 0
        }
        # print(body)
        return enviar_request_api(body, apikey, logger)

    except Exception as e:
        if logger:
            logger.log_message(f"Error al procesar la boleta: {e}", "ERROR")
        return {"success": False, "error": str(e)}


def process_factura(sections, config_data, logger=None):
    """
    Procesa un archivo TXT de Factura (DTE 33) y envía los datos a la API.
    
    Args:
        sections: Diccionario con las secciones del archivo.
        config_data: Diccionario con datos de configuración.
        logger: Objeto Logger para registrar eventos (opcional).
        
    Returns:
        dict: Respuesta de la API o información de error.
    """
    import requests
    
    # Extraer los campos de configuración
    rut_empresa = config_data["rut_empresa"]
    razon_social = config_data["razon_social"]
    giro = config_data["giro"]
    act_economica = config_data["act_economica"]
    direccion = config_data["direccion"]
    comuna = config_data["comuna"]
    telefono = config_data["telefono"]
    codsuc_sii = config_data["codsuc_sii"]
    email = config_data["email"]
    apikey = config_data["apikey"]
    tpv = config_data["tpv"]
    
    try:
        # Extraer datos de la sección "Encabezado"
        encabezado = sections.get("Encabezado", [])
        encabezado_data = encabezado[0].split(";") if encabezado else []
        
        # Extraer datos de la sección "Totales"
        totales = sections.get("Totales", [])
        totales_data = totales[0].split(";") if totales else []
        
        # Extraer detalles de la sección "Detalle"
        detalle = sections.get("Detalle", [])
        detalle_items_lines = detalle
        detalle_items = []

        # Extraer detalles de la sección "Detalle"
        referencia = sections.get("Referencia", [])
        referencia_data = referencia[0].split(";") if referencia else []
        
        # Procesar cada línea del detalle
        for line in detalle_items_lines:
            parts = line.split(";")
            if len(parts) >= 13:  # Verificar que tenga suficientes campos
                try:
                    nro_linea = int(parts[0])
                    descripcion = parts[2]
                    cantidad = float(parts[3])
                    precio = float(parts[4])
                    valor_exento = float(parts[9]) if parts[9] else 0
                    valor = float(parts[10])
                    desc_larga = parts[13]
                    # Determinar si es exento (1) o no (0)
                    ind_exe = 1 if valor_exento > 0 else 0
                    
                    # Añadir a la lista de ítems
                    detalle_items.append({
                        "NroLinDet": nro_linea,
                        "NmbItem": descripcion,
                        "DscItem": desc_larga if desc_larga else None,
                        "QtyItem": cantidad,
                        "PrcItem": precio,
                        "MontoItem": valor,
                        "DescuentoPct": 0,
                        "DescuentoMonto": 0,
                        "IndExe": ind_exe,
                        "UnmdItem": "un"
                    })
                except (ValueError, IndexError) as e:
                    if logger:
                        logger.log_message(f"Error al procesar línea de detalle: {line} - {e}", "ERROR")
    
        
        # Construir el cuerpo del request
        body = {
            "response": ["80MM", "PDFPATH"],
            "dte": {
                "Encabezado": {
                    "IdDoc": {
                        "IndServicio": 3,
                        "TipoDTE": 33,  # Factura
                        "Folio": int(referencia_data[2]),
                        "FchEmis": encabezado_data[2],
                        "FmaPago": 1,
                        "MedioPago": "EF",  # Efectivo por defecto
                        "MntBruto": 0
                    },
                    "Emisor": {
                        "RUTEmisor": rut_empresa,
                        "RznSocEmisor": razon_social,
                        "GiroEmisor": giro,
                        "Acteco": act_economica,
                        "DirOrigen": direccion,
                        "CmnaOrigen": comuna,
                        "Telefono": telefono,
                        "CdgSIISucur": codsuc_sii,
                        "Email": email
                    },
                    "Receptor": {
                        "RUTRecep": encabezado_data[5],
                        "RznSocRecep": encabezado_data[6],
                        "GiroRecep": encabezado_data[7],
                        "DirRecep": encabezado_data[8],
                        "CmnaRecep": encabezado_data[9],
                        "CiudadRecep": encabezado_data[10] if len(encabezado_data) > 10 else "",
                        "CorreoRecep": encabezado_data[11] if len(encabezado_data) > 11 else ""
                    },
                    "Totales": {
                        "MntNeto": float(totales_data[4]) if totales_data[4] else 0,
                        "MntExe": float(totales_data[5]) if totales_data[5] else 0,
                        "TasaIVA": int(totales_data[6]) if totales_data[6] else 19,
                        "IVA": float(totales_data[7]) if totales_data[7] else 0,
                        "MntTotal": float(totales_data[8]) if totales_data[8] else 0
                    }
                },
                "Detalle": detalle_items,
                "Referencia": None,
                "DscRcgGlobal": None
            },
            "TEDXML": "",
            "TPVMobil": "",
            "IdMsg": 0
        }        
        print(body)
        return enviar_request_api(body, apikey, logger)

    except Exception as e:
        if logger:
            logger.log_message(f"Error al procesar la factura: {e}", "ERROR")
        return {"success": False, "error": str(e)}


def enviar_request_api(body, apikey, logger=None):
    """
    Envía la solicitud a la API y procesa la respuesta.
    
    Args:
        body: Cuerpo del request en formato JSON.
        apikey: Clave API para la autenticación.
        logger: Objeto Logger para registrar eventos (opcional).
        
    Returns:
        dict: Respuesta de la API o información de error.
    """
    import requests
    
    try:
        # Headers para la solicitud
        headers = {
            "apikey": apikey
        }

        # URL de la API
        url = "https://api.qpos.io/cl/online/api/v1/edidte/Document"

        # Realizar la solicitud POST
        response = requests.post(url, headers=headers, json=body)
        if logger:
            logger.log_message("Solicitud a API realizada con éxito.")
            
        # Manejar la respuesta
        if response.status_code == 200:
            respuesta_json = response.json()
            
            # Procesar la respuesta para impresión/descarga si es necesario
            if respuesta_json.get('PDFPATH'):
                from utils.printer import procesar_respuesta_api
                # Llamamos a procesar_respuesta_api con la configuración de impresión
                procesar_respuesta_api(respuesta_json, logger)
                
            return respuesta_json
        else:
            if logger:
                logger.log_message(f"Error en la solicitud a API: {response.status_code} - {response.text}", "ERROR")
            return {
                "success": False, 
                "status_code": response.status_code, 
                "message": response.text
            }
    
    except Exception as e:
        if logger:
            logger.log_message(f"Error al enviar solicitud a API: {e}", "ERROR")
        return {"success": False, "error": str(e)}