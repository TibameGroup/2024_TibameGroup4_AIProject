
from PIL import Image 
import numpy as np
import requests 
import json
import asyncio

Headers = {"content-type": "application/json"}
with open('./config/config.json', 'r') as file:
    config = json.load(file)
URL = config["CnnModelURL"]
with open('./config/cnnProd.json', 'r') as file:
    prodNum = json.load(file)

async def cnnModel(imgPath, width=320, height=320):
    img = Image.open(imgPath) # 匯入圖片
    # 圖片大小改成模行輸入大小
    resized_image = img.resize((width, height)) 
    # print(resized_image)
    # 轉換為 NumPy 數組
    resized_image = np.array(resized_image)
    
    data = {"instances": [{"input_21": resized_image.tolist()}]}
    
    # 查看回傳資料
    # 非同步
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None,  lambda : requests.post(URL, data=json.dumps(data), headers=Headers))
    if response.status_code == 200:
        probability = response.json()
        num = np.argmax(probability['predictions'][0])
        numP = probability['predictions'][0][num]
        # print(numP)
        if numP < 0.88:
            return "找不到對應商品"
        else :
            return prodNum[str(num)]
    else:
        print("Error:", response.status_code, ", ", response.text)
if __name__ == "__main__":
    result = cnnModel(imgPath="./image/cnnImg/2012202120248.jpg", width=320, height=320)
    print(result)
