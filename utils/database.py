# utils/database.py

import os
import discord
import psycopg2
from psycopg2 import sql
from utils.config import cfg
from utils.log import logger

class Database:
    def __init__(self):
        self.connection = self.connect_to_db()
        self.cursor = self.connection.cursor()
        logger.info("Database initiated")

    def connect_to_db(self):
        try:
            conn = psycopg2.connect(
                dbname=cfg.DB_NAME,
                user=cfg.DB_USER,
                password=cfg.DB_PASS,
                host=cfg.DB_HOST,
                port=cfg.DB_PORT
            )
            logger.info("Successfully connected to the database")
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise

    def run_script_from_file(self, filepath):
        logger.info(f"Running SQL script from file: {filepath}")
        with open(filepath, 'r') as file:
            script = file.read()
            self.cursor.execute(script)
            if script.strip().lower().startswith("select"):
                result = self.cursor.fetchall()
                logger.info("Select query executed successfully")
                return result
            self.connection.commit()
            logger.info("Script executed successfully")
            return None
    
    def run_script(self, script):
        logger.info("Running script directly")
        self.cursor.execute(script)
        if script.strip().lower().startswith("select"):
            result = self.cursor.fetchall()
            logger.info("Select query executed successfully")
            return result
        self.connection.commit()
        logger.info("Script executed successfully")
        return None

    def close(self):
        self.cursor.close()
        self.connection.close()
        logger.info("Database connection closed")

db = Database()