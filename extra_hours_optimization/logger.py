import logging
import os
from datetime import datetime

def setup_logger():
    # Crear directorio de logs si no existe
    if not os.path.exists('../logs'):
        os.makedirs('../logs')

    # Configurar el formato del log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Configurar el logger principal
    logger = logging.getLogger('extra_hours_optimization')
    logger.setLevel(logging.INFO)

    # Handler para archivo
    file_handler = logging.FileHandler(
        f'../logs/optimization_{datetime.now().strftime("%Y%m%d")}.log'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger 