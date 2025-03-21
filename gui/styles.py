# -*- coding: utf-8 -*-
"""
Módulo para configurar los estilos de la interfaz gráfica.
"""

from tkinter import ttk

def setup_styles(root):
    """
    Configura los estilos para la interfaz.
    
    Args:
        root: Ventana principal de la aplicación.
        
    Returns:
        ttk.Style: Objeto de estilo configurado.
    """
    style = ttk.Style(root)
    
    # Definir altura de las pestañas y ajustar centrado
    style.configure("TNotebook.Tab", padding=[10, 5], font=('Helvetica', 10), height=30)
    style.configure("TButton", padding=[10, 5], font=('Helvetica', 10), height=30)
    
    # Crear un estilo para el LabelFrame con la fuente que desees
    style.configure("Custom.TLabelframe.Label", font=("Helvetica", 10, "bold"))
    
    # Configurar forgroundcolor para los botones
    style.configure("TButton", foreground="black", padding=2, font=("Arial", 10, "normal"))
    
    return style