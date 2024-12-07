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
        return None
    
    def run_script(self, script):
        self.cursor.execute(script)
        if script.strip().lower().startswith("select"):
            result = self.cursor.fetchall()
            logger.debug(f"\nDEBUG: QUERY RESULT: {result}\n")
            logger.info("Select query executed successfully")
            return result
        else:
            affected_rows = self.cursor.rowcount
            self.connection.commit()
            logger.info(f"Script executed successfully, {affected_rows} rows affected")
            return affected_rows

    def close(self):
        self.cursor.close()
        self.connection.close()
        logger.info("Database connection closed")

db = Database()