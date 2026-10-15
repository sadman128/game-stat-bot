import re
import time
import datetime
import pytz
import logging
import mysql.connector
from mysql.connector import pooling
from contextlib import contextmanager

from config import config

logger = logging.getLogger(__name__)

# Connection pool for safe concurrent queries
_pool = None

def get_pool():
    global _pool
    if _pool is None:
        db_cfg = config.get_db_config()
        # Convert port to int if string
        port = int(db_cfg.get("port", 3306))
        pool_cfg = dict(db_cfg)
        pool_cfg["port"] = port
        pool_cfg["pool_name"] = "finalbot_pool"
        pool_cfg["pool_size"] = 5
        pool_cfg["pool_reset_session"] = True
        try:
            _pool = pooling.MySQLConnectionPool(**pool_cfg)
        except Exception as e:
            logger.error(f"Failed to initialize MySQL pool: {e}")
            _pool = None
    return _pool

@contextmanager
def get_database(max_retries=3, retry_delay=5):
    """Context manager for obtaining a database connection with auto-close and retry."""
    conn = None
    attempt = 0
    while attempt < max_retries:
        try:
            pool = get_pool()
            if pool:
                conn = pool.get_connection()
            else:
                db_cfg = dict(config.get_db_config())
                db_cfg["port"] = int(db_cfg.get("port", 3306))
                conn = mysql.connector.connect(**db_cfg)
            break
        except mysql.connector.Error as err:
            attempt += 1
            tz = pytz.timezone(config.TIMEZONE)
            current_time = datetime.datetime.now(tz).strftime("%d/%m/%Y %I:%M %p")
            logger.warning(f"Reconnecting to MySQL ({attempt}/{max_retries}) --- {current_time} Error: {err}")
            if attempt >= max_retries:
                logger.error("Max database connection retries reached.")
                raise err
            time.sleep(retry_delay)

    try:
        yield conn
    finally:
        if conn and conn.is_connected():
            conn.close()

def clean_game_name(gamename: str) -> str:
    """Normalize game name for statistics."""
    gamename = str(gamename)
    if gamename.startswith("PLAYERUNKNOWNS"):
        gamename = "Pubg Battlegrounds"

    gamename = re.sub(r"[\'\":]", "", gamename).strip()
    gamename = gamename.strip(" ")

    gamename = re.sub(r'game', '', gamename, flags=re.IGNORECASE).strip()
    gamename = re.sub(r'tracker', '', gamename, flags=re.IGNORECASE).strip()
    gamename = re.sub(r'app', '', gamename, flags=re.IGNORECASE).strip()
    gamename = re.sub(r'client', '', gamename, flags=re.IGNORECASE).strip()

    return gamename.lower().title()

def update_user_db(user_id: int):
    """Increment user voice time by 1 minute."""
    try:
        with get_database() as db:
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO user(id, time)
                VALUES (%s, 1)
                ON DUPLICATE KEY UPDATE time = time + 1;
            """, (user_id,))
            db.commit()
            cursor.close()
    except mysql.connector.Error as err:
        logger.error(f"update_user_db error for {user_id}: {err}")

def update_game_db(gamename: str):
    """Clean game name and increment game time by 1 minute."""
    gamename = clean_game_name(gamename)
    if not gamename:
        return

    try:
        with get_database() as db:
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO discord (gamename, gametime)
                VALUES (%s, 1)
                ON DUPLICATE KEY UPDATE gametime = gametime + 1;
            """, (gamename,))
            db.commit()
            cursor.close()
    except mysql.connector.Error as err:
        logger.error(f"update_game_db error for {gamename}: {err}")

def get_games():
    """Fetch sorted list of games and cumulative times."""
    try:
        with get_database() as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM discord;")
            result = cursor.fetchall()
            cursor.close()
            return sorted(result, key=lambda l: l[1], reverse=True)
    except mysql.connector.Error as err:
        logger.error(f"get_games error: {err}")
        return []

def get_users():
    """Fetch sorted list of users and cumulative voice times."""
    try:
        with get_database() as db:
            cursor = db.cursor()
            cursor.execute("SELECT id, time FROM user;")
            result = cursor.fetchall()
            cursor.close()
            return sorted(result, key=lambda l: l[1], reverse=True)
    except mysql.connector.Error as err:
        logger.error(f"get_users error: {err}")
        return []

def get_timestring() -> str:
    """Fetch the start timestring from database."""
    try:
        with get_database() as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM timestring;")
            result = cursor.fetchall()
            cursor.close()
            if result and len(result) > 0:
                return result[0][0]
            return "Unknown"
    except mysql.connector.Error as err:
        logger.error(f"get_timestring error: {err}")
        return "Unknown"

def reset_game_stat(current_time: str):
    """Reset game statistics in discord table and update timestring."""
    with get_database() as db:
        cursor = db.cursor()
        cursor.execute("UPDATE discord SET gametime = 0")
        cursor.execute("DELETE FROM timestring")
        cursor.execute("INSERT INTO timestring (oldtime) VALUES (%s);", (current_time,))
        db.commit()
        cursor.close()

def reset_user_stat():
    """Reset user voice statistics in user table."""
    with get_database() as db:
        cursor = db.cursor()
        cursor.execute("UPDATE user SET time = 0")
        db.commit()
        cursor.close()
