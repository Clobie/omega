# utils/log.py

import logging
import os

os.makedirs('./logs', exist_ok=True)

# Create handlers for different log types
error_handler = logging.FileHandler('./logs/error.log', 'a', 'utf-8')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

warning_handler = logging.FileHandler('./logs/warning.log', 'a', 'utf-8')
warning_handler.setLevel(logging.WARNING)
warning_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

info_handler = logging.FileHandler('./logs/info.log', 'a', 'utf-8')
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

debug_handler = logging.FileHandler('./logs/debug.log', 'a', 'utf-8')
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Set up the main logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add handlers
logger.addHandler(info_handler)
logger.addHandler(warning_handler)
logger.addHandler(error_handler)
logger.addHandler(debug_handler)
logger.addHandler(logging.StreamHandler())