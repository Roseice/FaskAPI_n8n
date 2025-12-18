from fastapi import APIRouter
from db.mysql import MySQLClient
import requests

router = APIRouter()
db = MySQLClient()

@router.get("/trigger-n8n")
async def trigger_n8n(prompt: str,n8n_webhook_url: str):
    """
    ## 啓動 n8n Webhook
    - 參數: prompt (string)
    - 參數: n8n_webhook_url (string) - n8n Webhook 的完整 URL
    - 回傳 n8n 的回應結果
    """
    try:
        payload = {"prompt": prompt}
        resp = requests.get(n8n_webhook_url, json=payload, timeout=10)
        resp.raise_for_status()
        return {"status": "success", "n8n_response": resp.json()}
    except requests.RequestException as e:
        return {"status": "error", "detail": str(e)}

@router.post("/create-database")
async def create_database(database_name: str):
    """
    ## 建立資料庫
    - 參數: database_name (string) - 資料庫名稱
    - 回傳建立資料庫的結果
    """
    try:
        db.execute("CREATE DATABASE IF NOT EXISTS `{}`;".format(database_name))
        return {"message": "CREATE DATABASE"}
    except pymysql.MySQLError as e:
        return {"status": "db_error","error_code": e.args[0],"error_message": e.args[1]}

    except Exception as e:
        return {"status": "error","detail": str(e)}

@router.post("/create-tables")
async def create_tables(database_name: str,table_name: str):
    """
    ## 建立資料表
    - 參數: database_name (string) - 資料庫名稱
    - 參數: table_name (string) - 資料表名稱
    - 回傳建立資料表的結果
    """
    try:
        db = MySQLClient(database=database_name)

        db.execute("""
        CREATE TABLE IF NOT EXISTS `{}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """.format(table_name))
        return {"status": "tables created"}
    except pymysql.MySQLError as e:
        return {"status": "db_error","error_code": e.args[0],"error_message": e.args[1]}

    except Exception as e:
        return {"status": "error","detail": str(e)}