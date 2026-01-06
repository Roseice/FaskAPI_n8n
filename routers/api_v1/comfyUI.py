from fastapi import APIRouter, Depends, Query
from auth.dependencies import get_current_active_user
import websocket
import uuid
import json
import urllib.request
import urllib.parse
import random
import os
import base64
import requests

server_address = "10.0.0.160:8188"
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    
    # 透過 WebSocket 監聽執行狀態
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break # 執行結束
        else:
            continue

    # 執行結束後，查詢歷史紀錄以取得檔案名稱
    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        if 'images' in node_output:
            images_output = []
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                images_output.append(image_data)
            output_images[node_id] = images_output

    return output_images


router = APIRouter()


@router.get("/")
async def comfyUI(ckpt_name: str, Yprompt: str, Nprompt: str, width: int, height: int, batch_size: int, steps: int, cfg: float):
    """
    ## ComfyUI 生成圖片 API
    - 參數: ckpt_name (string) - 模型名稱
    - 參數: Yprompt (string) - 正向提示詞
    - 參數: Nprompt (string) - 負向提示詞
    - 參數: width (int) - 圖片寬度
    - 參數: height (int) - 圖片高度
    - 參數: batch_size (int) - 批次大小
    - 參數: steps (int) - 生成步數
    - 參數: cfg (float) - CFG 值
    """
    try:
        # 讀取 workflow JSON 檔案
        current_dir = os.path.dirname(__file__)

        # 組合出 json 的絕對路徑
        json_path = os.path.join(current_dir, "workflow_api.json")

        # 使用組合好的路徑開啟檔案
        with open(json_path, "r", encoding="utf-8") as f:
            prompt_workflow = json.load(f)

        # 1. 修改模型名稱
        prompt_workflow["4"]["inputs"]["ckpt_name"] = ckpt_name

        # 2. 修改提示詞、圖片尺寸和批次大小
        prompt_workflow["6"]["inputs"]["text"] = Yprompt # 正向提示詞
        prompt_workflow["7"]["inputs"]["text"] = Nprompt # 負向提示詞
        prompt_workflow["5"]["inputs"]["width"] = width  # 圖片寬度
        prompt_workflow["5"]["inputs"]["height"] = height # 圖片高度
        prompt_workflow["5"]["inputs"]["batch_size"] = batch_size # 批次大小

        # 修改隨機種子 (Seed)，否則每次產圖都會一樣
        prompt_workflow["3"]["inputs"]["seed"] = random.randint(1, 1000000000)

        # 修改步數和 CFG 值
        prompt_workflow["3"]["inputs"]["steps"] = steps
        prompt_workflow["3"]["inputs"]["cfg"] = cfg

        # 3. 建立 WebSocket 連線並發送請求
        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
        images = get_images(ws, prompt_workflow)

        # 4. 存檔
        for node_id in images:
            for image_data in images[node_id]:
                with open(f"output_{node_id}.png", "wb") as f:
                    f.write(image_data)
        
        # 5. 取得圖片數據並轉為 Base64
        base64_image_str = None
        for node_id in images:
            for image_data in images[node_id]:
                # image_data 目前是二進制 (bytes)
                
                # 步驟 A: 將二進制編碼為 Base64 的 bytes
                b64_bytes = base64.b64encode(image_data)
                
                # 步驟 B: 將 bytes 解碼為 UTF-8 字串 (這樣才能放進 JSON)
                base64_image_str = b64_bytes.decode('utf-8')
                
                # 找到第一張圖就跳出 (假設您一次只生成一張)
                break
            if base64_image_str:
                break

        resp = requests.get("https://dzjh-n8n.shengxingamers.com/webhook/74f147ef-312d-4154-babd-79f001a8f3cc", json={"url":base64_image_str}, timeout=10)
        resp.raise_for_status()
        print("圖片生成完畢並已下載！")
        return {"status": "success"}
    except requests.RequestException as e:
        return {"status": "error", "detail": str(e)}