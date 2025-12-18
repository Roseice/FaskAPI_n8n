import pymysql


class MySQLClient:
    def __init__(
        self,
        host="10.0.0.226",
        port=3306,
        user="root",
        password="mysql_6mfxaB",
        database=None,
        charset="utf8mb4",
    ):
        self.config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
            "charset": charset,
            "autocommit": True,
        }

    def connect(self):
        return pymysql.connect(**self.config)

    def execute(self, sql: str):
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
        finally:
            conn.close()

    def query(self, sql: str):
        conn = self.connect()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conn.close()