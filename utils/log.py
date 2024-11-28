# utils/log.py

import logging
import os

os.makedirs('./logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/app.log', 'a', 'utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)