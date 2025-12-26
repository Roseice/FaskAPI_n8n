from fastapi import APIRouter, Depends, Query
from auth.dependencies import get_current_active_user
from db.mysql import MySQLClient
from pydantic import BaseModel
import requests

router = APIRouter()
db = MySQLClient()

class N8nPromptRequest(BaseModel):
    prompt: str
    n8n_webhook_url: str

class N8nimgRequest(BaseModel):
    prompt: str
    n8n_webhook_url: str
    url: str

@router.post("/trigger-n8n-img")
async def trigger_n8n_img(request: N8nimgRequest):
    """
    ## 啓動 n8n 提示詞改圖
    - 參數: prompt (string) - 提示詞
    - 參數: n8n_webhook_url (string) - n8n Webhook URL
    - 參數: url (string) - 圖片下載網址
    - 回傳 n8n 的回應結果
    """
    try:
        resp = requests.get(request.n8n_webhook_url, json={"prompt":request.prompt,"url":request.url}, timeout=10)
        resp.raise_for_status()
        return {"status": "success", "n8n_response": resp.json()}
    except requests.RequestException as e:
        return {"status": "error", "detail": str(e)}

@router.post("/trigger-n8n-prompt")
async def trigger_n8n_prompt(request: N8nPromptRequest):
    """
    ## 啓動 n8n 文字提示詞生圖
    - 參數: prompt (string)
    - 參數: n8n_webhook_url (string) - n8n Webhook 的完整 URL
    - 回傳 n8n 的回應結果
    """
    try:
        payload = {"prompt": request.prompt}
        resp = requests.get(request.n8n_webhook_url, json=payload, timeout=10)
        resp.raise_for_status()
        return {"status": "success", "n8n_response": resp.json()}
    except requests.RequestException as e:
        return {"status": "error", "detail": str(e)}