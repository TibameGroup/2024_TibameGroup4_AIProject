import qrcode
from PIL import Image
import requests
import json

# Rich Menu 的最大數量： 每個 LINE 帳號（Channel）最多可以擁有 1000 個 Rich Menu。
with open('./config/config.json', 'r') as file:
    config = json.load(file)
friendLiffUrl = config['friendLiffUrl']

class Menu:
    def __init__(self, ChannelAccessToken):
        self.ChannelAccessToken = ChannelAccessToken
    def menu_a(self, richMenuAname="menuA", richMenuAliasId="m_alias_id"):
        """創建Menu A，return menu id"""
        data_nextPage = json.dumps({'action':'nextPage'}) # 將dict轉為json
        Headers = {'Content-Type': 'application/json', 
                   'Authorization': 'Bearer {}'.format(self.ChannelAccessToken)}
        url = "https://api.line.me/v2/bot/richmenu" # line 收 richMenu網址
        body = {
                'size': {'width': 2500, 'height': 1686},  
                'selected': 'false',                       
                'name': richMenuAname,                             
                'chatBarText': '開啟一天',                   
                'areas':[                                  
                    {
                    "bounds": {"x": 0, "y": 0, "width": 2500, "height": 800},
                    "action": {"type": "message", "text": "@紀錄飲食"}       
                    },
                    {
                    "bounds": {"x": 100, "y": 900, "width": 700, "height": 700},
                    "action": {"type": "message", "text": "@熱量估算"}
                    },
                    {
                    "bounds": {"x": 900, "y": 900, "width": 700, "height": 700},
                    "action": {"type": "message", "text": "@飲食日記"}
                    },
                    {
                    "bounds": {"x": 1700, "y": 900, "width": 700, "height": 700},
                    'action': {
                                "type": "richmenuswitch",
                                "richMenuAliasId": richMenuAliasId,
                                "data": data_nextPage}
                    }
        
                ]
            }
        response = requests.request('POST', url=url, headers=Headers, 
                                    data=json.dumps(body).encode('utf-8'))
        # 檢視 POST 請求狀態
        if response.status_code != 200:
            print('sendMenuA ErrorStatus: ' + str(response.status_code)) 
            return 
        else:
            richMenuId_a = response.text.split(":")[1].replace("}","")[1:-1]
            return richMenuId_a
        
    def menu_m(self, richMenuName):
        """創建Menu M，return menu id"""
        Headers = {'Content-Type': 'application/json', 
                   'Authorization': 'Bearer {}'.format(self.ChannelAccessToken)}
        url = "https://api.line.me/v2/bot/richmenu" # line 收 richMenu網址
        body = {
                'size': {'width': 2500, 'height': 1686},    
                'selected': 'true',                        
                'name': richMenuName,                           
                'chatBarText': '友情日常',                    
                'areas':[         
                    {
                    "bounds": {"x": 0, "y": 0, "width": 2500, "height": 1686},
                    "action": {"type": "message", "text": "讀取中"}
                    }
                ]
            }
        response = requests.request('POST', url=url, headers=Headers, 
                                    data=json.dumps(body).encode('utf-8'))
        # 檢視 POST 請求狀態
        if response.status_code != 200:
            print('sendMenuMiddle ErrorStatus: ' + str(response.status_code)) 
            return 
        else:
            richMenuId_M = response.text.split(":")[1].replace("}","")[1:-1]
            return richMenuId_M
        
    def menu_b(self, richMenuBname, richMenuAliasId="a_alias_id"):
        """創建Menu B，return menu id"""
        data_prevPage = json.dumps({'action':'prevPage'}) # 將dict轉為json
        Headers = {'Content-Type': 'application/json', 
                   'Authorization': 'Bearer {}'.format(self.ChannelAccessToken)}
        url = "https://api.line.me/v2/bot/richmenu" # line 收 richMenu網址
        body = {
                'size': {'width': 2500, 'height': 1686},    
                'selected': 'true',                        
                'name': richMenuBname,                           
                'chatBarText': '友情日常',                    
                'areas':[         
                    {
                    "bounds": {"x": 0, "y": 0, "width": 1500, "height": 1686},
                    "action": {"type": "message", "text": "@QRcode"}
                    },
                    {
                    "bounds": {"x": 1700, "y": 200, "width": 900, "height": 250},
                    "action": { "type": "richmenuswitch",
                                "richMenuAliasId": richMenuAliasId,
                                "data": data_prevPage}
                    },
                    {
                    "bounds": {"x": 1700, "y": 700, "width": 900, "height": 250},
                    # "action": {"type": "message", "text": "@Scan"}
                    "action": {"type": "uri", "label": "新增好友","uri": friendLiffUrl}                    
                    },
                    {
                    "bounds": {"x": 1700, "y": 1200, "width": 900, "height": 250},
                    "action": {"type": "message", "text": "@好友查看"}
                    }
                ]
            }
        response = requests.request('POST', url=url, headers=Headers, 
                                    data=json.dumps(body).encode('utf-8'))
        # 檢視 POST 請求狀態
        if response.status_code != 200:
            print('sendMenuB ErrorStatus: ' + str(response.status_code)) 
            return 
        else:
            richMenuId_b = response.text.split(":")[1].replace("}","")[1:-1]
            return richMenuId_b
        
    def uploadMenuImg(self, menuId, menuImagePath):
        """上傳Menu圖片"""
        url = f"https://api-data.line.me/v2/bot/richmenu/{menuId}/content"
        Headers = {"Authorization": f"Bearer {self.ChannelAccessToken}",
                   "Content-Type": "image/png"
                   }
        # 將圖片檔案讀取為二進位數據
        with open(menuImagePath, "rb") as f:
            image = f.read()
        response = requests.post(url, headers=Headers, data=image)
        if response.status_code != 200:
            print(f"上傳Menu圖片錯誤，狀態碼: {response.status_code}")
        else:
            return 'ok'

    def setMenuAlias(self, richMenuId, richMenuAliasId):
        """設定 Menu 別名"""
        Headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {self.ChannelAccessToken}'}
        url = "https://api.line.me/v2/bot/richmenu/alias"
        body = {"richMenuAliasId": richMenuAliasId,
                "richMenuId": richMenuId}
        response = requests.request('POST', url=url, headers=Headers, json=body)
        if response.status_code != 200:
            print(f'Set Menu alias: {richMenuId} ErrorStatus: {str(response.status_code)}') 
            print(response.text)
        else:
            return 'ok'
        
    def setUserMenu(self, richMenuId, userId = 'all'):
        """指定使用者推送 menu，預設為全體"""
        url = f"https://api.line.me/v2/bot/user/{userId}/richmenu/{richMenuId}"
        Headers = {'Authorization': 'Bearer {}'.format(self.ChannelAccessToken)}
        response = requests.request('POST', url=url, headers=Headers)
        if response.status_code != 200:
            print(f'Set Menu: {richMenuId} in User: {userId} ErrorStatus: {str(response.status_code)}') 
        else:
            return 'ok'
    
    def delRichMenu(self, richMenuId):
        """刪除 menu"""
        url = f"https://api.line.me/v2/bot/richmenu/{richMenuId}"
        Headers = {'Authorization': 'Bearer {}'.format(self.ChannelAccessToken)}
        response = requests.delete(url=url, headers=Headers)
        if response.status_code != 200:
            print(f'Delete Menu: {richMenuId} ErrorStatus: {str(response.status_code)}') 
        else:
            print(f'Delete Menu: {richMenuId} Success!') 
            return 'ok'
    def deleteRichMenuAlias(self, richMenuAliasId):
        """刪除richMenuAliasId"""
        url = f'https://api.line.me/v2/bot/richmenu/alias/{richMenuAliasId}'
        Headers = {
            'Authorization': f'Bearer {self.ChannelAccessToken}',
        }
        response = requests.delete(url=url, headers=Headers)
        if response.status_code != 200:
            print(f'Delete Menu: {richMenuAliasId} ErrorStatus: {str(response.status_code)}') 
        else:
            print(f'Delete Menu: {richMenuAliasId} Success!') 
            return 'ok'
        
    def getRichMenusId(self):
        """取得 rich Menu 的所有 id"""
        HEADERS = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.ChannelAccessToken}'
        }
        url = 'https://api.line.me/v2/bot/richmenu/list'
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            richMenusId = response.json()['richmenus']
            return richMenusId
        else:
            return None
    def getRichMenuIdByName(self, menus, menuName):
        """使用menu名稱查找id"""
        for menu in menus:
            if menu.get('name') == menuName:
                return menu['richMenuId']
        return None
        
    def setDefaultMenu(self, menuAImagePath="./image/menuImg/vision1_a.jpg", menuMImagePath="./image/menuImg/vision1_m.jpg"):
        """設定預設Menu"""
        # 主選單
        menuAId = self.menu_a(richMenuAname="menuA")
        self.uploadMenuImg(menuId=menuAId, menuImagePath=menuAImagePath)
        self.setMenuAlias(richMenuId=menuAId, richMenuAliasId="a_alias_id")
        # Loading選單
        menuMiddleId = self.menu_m(richMenuName="menuMiddle")
        self.uploadMenuImg(menuId=menuMiddleId, menuImagePath=menuMImagePath)
        self.setMenuAlias(richMenuId=menuMiddleId, richMenuAliasId="m_alias_id")
        # 發送全體
        self.setUserMenu(richMenuId=menuMiddleId, userId = 'all')
        self.setUserMenu(richMenuId=menuAId, userId = 'all')
        print('設定預設Menu成功')
    
    def setNextMenu(self, menuName, menuImagePath):
        """設定下一頁Menu"""
        menuBId = self.menu_b(richMenuBname=menuName) # 建立B模板
        self.uploadMenuImg(menuId=menuBId, menuImagePath=menuImagePath) # 上傳B圖片
        # self.setMenuAlias(richMenuId=menuBId, richMenuAliasId=userId[1:]) # 設定B暱稱
        self.setUserMenu(richMenuId=menuBId, userId=menuName) # 推送B menu
        print('設定下一頁Menu成功')
        

class Menu_img:
    def userId_qrcode(self, userId):
        qr = qrcode.QRCode(version=1, 
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,border=4)
        qr.add_data(userId)   # 要轉換成 QRCode 的文字
        qr.make(fit=True) 
        img = qr.make_image(fill_color="#CF9257", back_color="#FFFBF4")   
        new_size = (1686, 1686)  
        img = img.resize(new_size)                                              
        img.save(f'./image/menuImg/vision1_b_left_{userId}.jpg') 
        return "ok"
        
    def merge_img(self, userId):
        image1 = Image.open(f'./image/menuImg/vision1_b_left_{userId}.jpg')
        image2 = Image.open('./image/menuImg/vision1_b_right.jpg')
        width1, height1 = image1.size
        width2, height2 = image2.size
        new_width = width1 + width2
        new_height = max(height1 , height2)
        new_image = Image.new('RGB', (new_width, new_height), (255, 255, 255))
        new_image.paste(image1, (0, (new_height - height1) // 2))
        new_image.paste(image2, (width1,(new_height - height2) // 2))
        new_image.save(f'./image/menuImg/vision1_b_left_{userId}.jpg')
        return "ok"        

    def img_process(self, userId):
        self.userId_qrcode(userId)
        self.merge_img(userId)
        print("產生QRCODE成功")
        return "ok"