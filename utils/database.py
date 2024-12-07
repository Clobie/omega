# utils/database.py

import os
import discord
import psycopg2
from psycopg2 import sql
from core.omega import omega

class Database:
    def __init__(self):
        self.connection = self.connect_to_db()
        self.cursor = self.connection.cursor()
        omega.logger.info("Database initiated")

    def connect_to_db(self):
        try:
            conn = psycopg2.connect(
                dbname=omega.cfg.DB_NAME,
                user=omega.cfg.DB_USER,
                password=omega.cfg.DB_PASS,
                host=omega.cfg.DB_HOST,
                port=omega.cfg.DB_PORT
            )
            omega.logger.info("Successfully connected to the database")
            return conn
        except Exception as e:
            omega.logger.error(f"Database connection error: {e}")
            raise

    def run_script_from_file(self, filepath):
        omega.logger.info(f"Running SQL script from file: {filepath}")
        with open(filepath, 'r') as file:
            script = file.read()
            self.cursor.execute(script)
            if script.strip().lower().startswith("select"):
                result = self.cursor.fetchall()
                omega.logger.info("Select query executed successfully")
                return result
            self.connection.commit()
            omega.logger.info("Script executed successfully")
            return None
    
    def run_script(self, script):
        omega.logger.info("Running script directly")
        self.cursor.execute(script)
        if script.strip().lower().startswith("select"):
            result = self.cursor.fetchall()
            omega.logger.info("Select query executed successfully")
            return result
        self.connection.commit()
        omega.logger.info("Script executed successfully")
        return None

    def close(self):
        self.cursor.close()
        self.connection.close()
        omega.logger.info("Database connection closed")

db = Database()