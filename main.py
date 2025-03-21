#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Punto de entrada principal para la aplicación.
"""

import os
import sys
from gui.app import create_app

def main():
    """Función principal que inicia la aplicación."""
    app = create_app()
    app.mainloop()

if __name__ == "__main__":
    main()