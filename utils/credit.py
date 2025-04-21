# utils/credit.py

import os
import discord
from utils.config import cfg
from utils.log import logger
from utils.status import status
from utils.common import common
from utils.database import db

class Credit:
    def __init__(self):
        logger.info("Credit class initialized.")

    def init_user(self, user_id):
        logger.debug(f"Initializing user with ID: {user_id}")
        init_credits = cfg.NEW_USER_CREDITS
        query = (
            "INSERT INTO discord_users (user_id, credits) "
            "VALUES (%s, %s) "
            "ON CONFLICT (user_id) DO NOTHING"
        )
        db.run_script(query, (user_id, init_credits,))
        logger.info(f"User {user_id} initialized with {init_credits} credits.")
        return init_credits

    def convert_cost_to_credits(self, cost):
        logger.debug(f"Converting cost {cost} to credits.")
        if cost < 0:
            logger.warning("Cost is negative, returning minimum credits (1).")
            return 1
        credits_per_cent = 10
        credits = cost * 100 * credits_per_cent
        logger.info(f"Converted cost {cost} to {credits} credits.")
        return max(1, round(credits))

    def get_user_credits(self, user_id):
        logger.debug(f"Fetching credits for user ID: {user_id}")
        query = (
            "SELECT credits FROM discord_users WHERE user_id = %s;"
        )
        result = db.run_script(query, (user_id,))
        if not result:
            logger.info(f"No credits found for user {user_id}, initializing user.")
            return self.init_user(user_id)
        
        credit_value = round(result[0][0], 2)
        logger.info(f"User {user_id} has {credit_value} credits.")
        return int(credit_value) if credit_value.is_integer() else credit_value
    
    def get_server_credits(self, server_id):
        logger.debug(f"Fetching credits for server ID: {server_id}")
        query = (
            "SELECT credits FROM discord_servers WHERE server_id = %s;"
        )
        result = db.run_script(query, (server_id,))
        if not result:
            logger.info(f"No credits found for server {server_id}, initializing server.")
            self.init_user(server_id)
            return 0
        credit_value = result[0][0]
        logger.info(f"Server {server_id} has {credit_value} credits.")
        return int(round(credit_value, 2)) if round(credit_value, 2) == round(credit_value) else round(credit_value, 2)

    def user_spend(self, user_id, amount):
        logger.debug(f"User {user_id} attempting to spend {amount} credits.")
        from_credits = self.get_user_credits(user_id)
        if from_credits is None or from_credits < amount:
            logger.warning(f"User {user_id} has insufficient credits.")
            return False
        query = (
            "UPDATE discord_users "
            "SET credits = credits - %s "
            "WHERE user_id = %s "
            "RETURNING credits;"
        )
        new_credits = db.run_script(query, (amount, user_id,))
        logger.info(f"User {user_id} spent {amount} credits. Remaining: {new_credits}.")
        return new_credits is not None
    
    def server_spend(self, server_id, amount):
        logger.debug(f"Server {server_id} attempting to spend {amount} credits.")
        from_credits = self.get_server_credits(server_id)
        if from_credits is None or from_credits < amount:
            logger.warning(f"Server {server_id} has insufficient credits.")
            return False
        query = (
            "UPDATE discord_servers "
            "SET credits = credits - %s "
            "WHERE server_id = %s "
            "RETURNING credits;"
        )
        new_credits = db.run_script(query, (amount, server_id))
        logger.info(f"Server {server_id} spent {amount} credits. Remaining: {new_credits}.")
        return new_credits is not None
    
    def get_leaderboard(self, total=None):
        logger.debug(f"Fetching leaderboard with total: {total}")
        if total is None:
            total = 10
        else:
            total = total if total <= 25 else 10
        query = (
            f"SELECT user_id, credits FROM discord_users ORDER BY credits DESC LIMIT %s;"
        )
        result = db.run_script(query, (total,))
        leaderboard_str = "\n".join([
            f"<@{user_id}>: {int(round(credits, 2)) if round(credits, 2) == round(credits) else round(credits, 2)} credits" 
            for user_id, credits in result
        ])
        logger.info("Leaderboard fetched successfully.")
        return leaderboard_str
    
    def give_user_credits(self, user_from, user_to, amount):
        logger.debug(f"Transferring {amount} credits from user {user_from} to user {user_to}.")
        if amount <= 0:
            logger.warning("Amount must be greater than 0.")
            return False
        from_credits = self.get_user_credits(user_from)
        to_credits = self.get_user_credits(user_to)

        if from_credits is None or to_credits is None:
            logger.warning("One of the users does not exist.")
            return False
        
        if from_credits < amount:
            logger.warning(f"User {user_from} has insufficient credits.")
            return False

        query = (
            "WITH deducted AS ("
            "    UPDATE discord_users "
            "    SET credits = credits - %s "
            "    WHERE user_id = %s "
            "    RETURNING credits "
            "), "
            "added AS ("
            "    UPDATE discord_users "
            "    SET credits = credits + %s "
            "    WHERE user_id = %s "
            "    RETURNING credits "
            ") "
            "SELECT (SELECT credits FROM deducted) AS from_credits, "
            "       (SELECT credits FROM added) AS to_credits;"
        )
        db.run_script(query, (amount, user_from, amount, user_to,))
        logger.info(f"Transferred {amount} credits from user {user_from} to user {user_to}.")
        return True
    
    def gift_user_credits(self, user_to, amount):
        logger.debug(f"Gifting {amount} credits to user {user_to}.")
        if amount <= 0:
            logger.warning("Amount must be greater than 0.")
            return False
        to_credits = self.get_user_credits(user_to)
        if to_credits is None:
            logger.warning(f"User {user_to} does not exist.")
            return False
        query = (
            "UPDATE discord_users "
            "SET credits = credits + %s "
            "WHERE user_id = %s "
            "RETURNING credits;"
        )
        new_credits = db.run_script(query, (amount, user_to,))
        logger.info(f"Gifted {amount} credits to user {user_to}. New balance: {new_credits}.")
        return new_credits is not None
    
    def take_user_credits(self, user_from, amount):
        logger.debug(f"Taking {amount} credits from user {user_from}.")
        if amount <= 0:
            logger.warning("Amount must be greater than 0.")
            return False
        from_credits = self.get_user_credits(user_from)
        if from_credits is None:
            logger.warning(f"User {user_from} does not exist.")
            return False
        if from_credits < amount:
            logger.info(f"User {user_from} has less credits than {amount}. Taking all available credits.")
            amount = from_credits
        query = (
            "UPDATE discord_users "
            "SET credits = credits - %s "
            "WHERE user_id = %s "
            "RETURNING credits;"
        )
        new_credits = db.run_script(query, (amount, user_from))
        logger.info(f"Took {amount} credits from user {user_from}. Remaining: {new_credits}.")
        return new_credits is not None

credit = Credit()