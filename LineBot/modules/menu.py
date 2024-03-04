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
    def menu_a(self, richMenuName="menuA", richMenuAliasId="b_alias_id"):
        """創建Menu A，return menu id"""
        data_nextPage = json.dumps({'action':'nextPage'}) # 將dict轉為json
        Headers = {'Content-Type': 'application/json', 
                   'Authorization': 'Bearer {}'.format(self.ChannelAccessToken)}
        url = "https://api.line.me/v2/bot/richmenu" # line 收 richMenu網址
        body = {
                'size': {'width': 2500, 'height': 1686},  
                'selected': 'false',                       
                'name': richMenuName,                             
                'chatBarText': '開啟一天',                   
                'areas':[                                  
                    {
                    "bounds": {"x": 145, "y": 300, "width": 1015, "height": 1300},
                    "action": {"type": "message", "text": "@產品查詢"}       
                    },
                    {
                    "bounds": {"x": 1400, "y": 300, "width": 1000, "height": 1300},
                    "action": {"type": "message", "text": "@熱量估算"}
                    },
                    {
                    "bounds": {"x": 1280, "y": 0, "width": 1170, "height": 270},
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
        
    def menu_b(self, richMenuName="menuB", richMenuAliasId="a_alias_id"):
        """創建Menu B，return menu id"""
        data_prevPage = json.dumps({'action':'prevPage'}) # 將dict轉為json
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
                    "bounds": {"x": 90, "y": 400, "width": 750, "height": 1170},
                    "action": {"type": "message", "text": "@飲食日記"}
                    },
                    {
                    "bounds": {"x": 880, "y": 400, "width": 750, "height": 1170},
                    "action": {"type": "message", "text": "@飲食分析"}
                    },
                    {
                    "bounds": {"x": 1670, "y": 95, "width": 750, "height": 745},
                    "action": {"type": "message", "text": "@好友日記"}                    
                    },
                    {
                    "bounds": {"x": 1670, "y": 900, "width": 750, "height": 745},
                    "action": {"type": "message", "text": "@好友添加"}
                    },
                    {
                    "bounds": {"x": 0, "y": 0, "width": 1235, "height": 270},
                    'action': {
                                "type": "richmenuswitch",
                                "richMenuAliasId": richMenuAliasId,
                                "data": data_prevPage}
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
    def getMenuIdAlias(self):
        url = 'https://api.line.me/v2/bot/richmenu/list'

        HEADERS = {
            'Authorization': f'Bearer {self.ChannelAccessToken}'
        }
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            rich_menus = response.json()['richmenus']
            for rich_menu in rich_menus:
                print("Menu ID:", rich_menu['richMenuId'])
                print("Menu Alias:", rich_menu['name'])
                print("-----------")
            return rich_menus
        else:
            print(f"Failed to retrieve Rich Menus. Status code: {response.status_code}")
            print(response.text)
        return None
    def getRichMenuIdByName(self, menus, menuName):
        """使用menu名稱查找id"""
        for menu in menus:
            if menu.get('name') == menuName:
                return menu['richMenuId']
        return None
        
    def setDefaultMenu(self, menuAImagePath="./image/menuImg/vision2_a.jpg", menuBImagePath="./image/menuImg/vision2_b.jpg"):
        """設定預設Menu"""
        # 主選單
        menuAId = self.menu_a(richMenuName="menuA")
        self.uploadMenuImg(menuId=menuAId, menuImagePath=menuAImagePath)
        self.setMenuAlias(richMenuId=menuAId, richMenuAliasId="a_alias_id")
        # Loading選單
        menuMiddleId = self.menu_b(richMenuName="menuB")
        self.uploadMenuImg(menuId=menuMiddleId, menuImagePath=menuBImagePath)
        self.setMenuAlias(richMenuId=menuMiddleId, richMenuAliasId="b_alias_id")
        # 發送全體
        self.setUserMenu(richMenuId=menuMiddleId, userId = 'all')
        self.setUserMenu(richMenuId=menuAId, userId = 'all')
        print('設定預設Menu成功')
    