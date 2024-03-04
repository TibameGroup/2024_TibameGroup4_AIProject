import hashlib
import hmac
import base64
import requests
import os
import qrcode

# 錯誤訊息
class InvalidSignatureError(Exception):
    def __init__(self, message = 'Invalid signature. signature='):
        self.message = message
        super().__init__(self.message)

class Handle():
    def __init__(self, ChannelSecret, ChannelAccessToken):
        self.ChannelSecret = ChannelSecret
        self.ChannelAccessToken = ChannelAccessToken
    
    def verifySignature(self, signature, body):
        """ 
        驗證回傳內容是否來自 Line
        """
        # encode 只能使用 JSON 字串
        hash = hmac.new(self.ChannelSecret.encode('utf-8'), body.encode('utf-8'), hashlib.sha256).digest()
        signatureCalc = base64.b64encode(hash).decode('utf-8')

        return signature == signatureCalc

    def lineSign(self, signature, body):
        """
        檢查 ChannelSecret 是否有效
        """
        # 比對Line Bot 伺服器使用 ChannelSecret 所計算的簽名與 signature 值，確保訊息是由 Line 伺服器發送的。
        if not self.verifySignature(signature=signature, body=body):
            raise InvalidSignatureError('Invalid signature. signature=' + signature)
        else:
            return "ok"
    
    def replyMessage(self, replyToken, messages):
        """
        回覆訊息
        payload = dict() = [{"type": "text", "text": "Enter your content"}]
        """
        # Line官方文件: https://developers.line.biz/en/reference/messaging-api/#send-reply-message

        # print(payload) # 查看傳送內容 json 檔
        Headers = {'Content-Type': 'application/json', 
                'Authorization': 'Bearer {}'.format(self.ChannelAccessToken)}
        url = 'https://api.line.me/v2/bot/message/reply' # Line 收取回覆訊息網址

        # 文字內容
        payload = {'replyToken': replyToken,
                'messages': messages}

        # 傳送POST請求給LINE(url)
        response = requests.post(url, headers=Headers, json=payload)
        # 檢視 POST 請求狀態失敗代碼
        if response.status_code != 200:
            print('replyMessage ErrorStatus: ' + str(response.status_code)) 
    """
    預計改成send_message(userinfo中的frend_id, confirmation_message)
    """
    def pushMessage(self, toUserId, messages):
        Headers = {'Content-Type': 'application/json', 
                'Authorization': 'Bearer {}'.format(self.ChannelAccessToken)}
        url = "https://api.line.me/v2/bot/message/push"
        payload = {
            "to": toUserId, 
            "messages": messages}
        
        # 使用 LINE Messaging API 發送訊息 
        response = requests.post(url, headers=Headers, json=payload)
        # 檢視 POST 請求狀態失敗代碼
        if response.status_code != 200:
            print('pushMessage ErrorStatus: ', response.text)
    def handleEvent(self, eventType, messageType=None):
        """
        裝飾器，用於設定不同的事件類別
        """
        def decorator(func):
            def wrapper(events):
                # 雙重確認事件類別，確認主程式的if else是否填寫正確，指向正確的decorator
                if messageType:
                    if events[0]['message']['type'] == messageType:
                        return func(events)
                    
                else: 
                    if events[0]['type'] == eventType: 
                        return func(events)
                # return func(events)
            return wrapper
        return decorator
    
    # userId轉換QRCode
    def userIdToQrcode(self, userId):
        """產生QRCode圖片，回傳圖片路徑"""
        qr = qrcode.QRCode(version=1, 
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,border=4)
        qr.add_data(userId)   # 要轉換成 QRCode 的文字
        qr.make(fit=True) 
        img = qr.make_image(fill_color="#CF9257", back_color="#FFFFFF")   
        new_size = (1686, 1686)  
        img = img.resize(new_size)     
        imgPath = f'image/userIdImg/{userId}.jpg'                                         
        img.save(f"./{imgPath}") 
        # print("QRCODE Product Sucess!")
        return imgPath
    # 儲存圖片
    def saveImageMessage(self, messageId, imgName, imgfolder="image/"):
        """messageId: LineBot所回傳使用者訊息的圖片Id, replyToken: 訊息令牌"""
        # 用於取得圖片資訊的 Header
        HEADER = {'Authorization': 'Bearer {}'.format(self.ChannelAccessToken)}
        # 從 id 取得圖片內容
        # LineBot官方文件: https://developers.line.biz/en/reference/messaging-api/#getting-content
        content_contentUrl = f"https://api-data.line.me/v2/bot/message/{messageId}/content"
        # Request 官方文件: https://requests.readthedocs.io/en/latest/user/quickstart/#make-a-request
        response = requests.get(content_contentUrl, headers=HEADER) # 利用 url 抓取圖片資訊

        if response.status_code == 200:
            # 若成功抓取到圖片，將圖片存取下來
            filepath = f"./{imgfolder}{imgName}.jpg"
            with open(filepath, "wb") as f:
                f.write(response.content)
            print("Image Saved!")
            return filepath
        else:
            print('ImageGet ErrorStatus:', response.status_code)
            print('Fail to get image')

# 刪除圖片
def deletePhotos(imgPath):
    """imgPath: 圖片路徑"""
    try:
        # 檢查目錄是否存在
        if not os.path.exists(imgPath):
            print(f"Directory '{imgPath}' does not exist.")
            return

        # # 取得目錄的所有檔案
        # files = os.listdir(directoryPath)

        # # 篩選照片
        # photos = [file for file in files if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg')]

        # 删除照片
        # for photo in photos:
        #     photoPath = os.path.join(directoryPath, photo)
        #     os.remove(photoPath)
        #     print(f"DeletedImage: {photoPath}")
        os.remove(imgPath)
        print(f"DeletedImage: {imgPath}")
    except Exception as e:
        print(f"DeletedImage Error: {e}")
    
    