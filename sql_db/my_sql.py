"""
pip uninstall mysql-connector-python
pip uninstall mysql-connector
pip install mysql-connector-python

##################
sudo mysql
CREATE DATABASE IF NOT EXISTS popt_db;
CREATE USER 'popt'@'localhost' IDENTIFIED BY '83g6u45908k91HG2jhj5jeGG';
GRANT ALL PRIVILEGES ON popt_db.* TO 'popt'@'localhost';
FLUSH PRIVILEGES;
"""
import time
from config_station import logger
import mysql.connector

from sql_db.sql_Error import MySQLConnectionError

MYSQL_CONN_ATTEMPTS = 3


class SQL_DB:
    def __init__(self, config: dict):
        attempt = 1
        self.conn = None
        # Implement a reconnection routine
        while attempt < MYSQL_CONN_ATTEMPTS + 1:
            try:
                print(f"Try to connect {attempt}")
                self.conn = mysql.connector.connect(**config)
                # return mysql.connector.connect(**config)
                break
            except (mysql.connector.Error, IOError) as err:
                if MYSQL_CONN_ATTEMPTS is attempt:
                    # Attempts to reconnect failed; returning None
                    logger.error(f"MySQL: Failed to connect, exiting without a connection: {err}")
                    print(f"MySQL: Failed to connect, exiting without a connection: {err}")
                    raise MySQLConnectionError("Failed to connect")
                logger.info(
                    f"MySQL: Connection failed: {err}. Retrying ({attempt}/{MYSQL_CONN_ATTEMPTS - 1})..."
                )
                print(
                    f"MySQL: Connection failed: {err}. Retrying ({attempt}/{MYSQL_CONN_ATTEMPTS - 1})..."
                )
                # progressive reconnect delay
                time.sleep(2 ** attempt)
                attempt += 1

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute_query(self, query: str):
        if self.conn:
            if self.conn.is_connected():
                try:
                    with self.conn.cursor() as cursor:
                        print(f"Query: {query}")
                        print(f"cur :{cursor.execute(query)}")
                        return cursor.fetchall()
                except AttributeError:
                    print("MySQL: Version error !")
                    logger.error("MySQL: Version error !")
                    logger.error("MySQL: pip uninstall mysql-connector-python")
                    logger.error("MySQL: pip uninstall mysql-connector")
                    logger.error("MySQL: pip install mysql-connector-python")
                    self.conn.close()
                    raise MySQLConnectionError("MySQL: Version error !")
                # db_conn.close()
        self.conn = None
        print("MYSQL (execute_query): Could not connect")
        logger.error("MYSQL (execute_query): Could not connect")
        raise MySQLConnectionError("MYSQL (execute_query): Could not connect")

    def execute_query_bin(self, query_str: str, query_data: tuple):
        if self.conn:
            if self.conn.is_connected():
                try:
                    # with self.conn.cursor() as cursor:
                    cursor = self.conn.cursor()
                    # print(f"Query: {query_str}")
                    # print(f"QData: {query_data}")
                    cursor.execute(query_str, query_data)
                    return cursor.fetchall()
                except AttributeError:
                    print("MySQL: Version error !")
                    logger.error("MySQL: Version error !")
                    logger.error("MySQL: pip uninstall mysql-connector-python")
                    logger.error("MySQL: pip uninstall mysql-connector")
                    logger.error("MySQL: pip install mysql-connector-python")
                    self.conn.close()
                    raise MySQLConnectionError("MySQL: Version error !")
                except mysql.connector.errors.DataError as e:
                    print(e)
                    print(f"Query: {query_str}")
                    print(f"QData: {query_data}")
                    raise e
                # db_conn.close()
        self.conn = None
        print("MYSQL (execute_query): Could not connect")
        logger.error("MYSQL (execute_query): Could not connect")
        raise MySQLConnectionError("MYSQL (execute_query): Could not connect")

    def commit_query(self):
        if self.conn:
            self.conn.commit()

    def get_all_tables(self):
        """
        SHOW TABLE STATUS FROM popt_db;
        """
        ret = self.execute_query("SHOW TABLE STATUS FROM popt_db;")
        return [i[0] for i in ret]

    def set_bid(self, bid):
        return self.execute_query(f"ALTER TABLE pms_out_msg AUTO_INCREMENT={bid};")

    def get_bid(self):
        return self.execute_query((
            "SELECT `AUTO_INCREMENT` "
            "FROM INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_SCHEMA='popt_db' "
            "AND TABLE_NAME='pms_out_msg';"))
