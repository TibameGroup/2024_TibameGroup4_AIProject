# from __future__ import unicode_literals
# Python 2 中的一種語法，用於使字符串字面值（string literals）默認為 unicode 字符串。
# Python 3 中，字符串字面值默認就是 unicode 字符串。

"""
Task: 
整體: 
    資料庫連接
    新增變數data儲存使用者輸入到哪一步
    圖片儲存為"使用者ID+第幾張圖片"
    更改 Json 內容判別，將 if else 判別式另外使用裝飾器撰寫
飲食紀錄:
    Barcode查詢 - 相機功能新增(是否增加判定輔助框?) -> LIFF 串接網頁HTML
    圖片查詢 - 相機功能新增/相簿功能 -> 接模型API
    品名查詢 - (使用者輸入功能優化?) -> 調整新增 LineMessage Flex 格式(根據資料庫數量增加Bubble)
熱量估算: 
    新增頁面(選擇相機/照片)，按鈕為Postback，嘗試向使用者分段發送兩次訊息 OR 使用Rich Menu更改圖文選單為Postback
    調整gemini輸出格式、try except
飲食日記:
    LineMessage Flex 格式使用"detailInfo"的Flex介面，調整食用份量

好友綁定:
    使用 UserId 顯示 QRCode，rich menu 跳轉好友功能
測試人員加入條碼:
    加入測試人員資料庫。儲存產品名字、條碼、人員名字
Mongosh:
    連接、儲存飲食紀錄、好友/個人資訊
修改全域變數，使用time函數控制存活時間
"""
from flask import Flask, request, abort # abort: 返回網頁請求訊息狀態碼
import json
import asyncio

# python
from modules.LineMessageHandle import Handle, InvalidSignatureError, deletePhotos
from modules.LineMessage import Flex, textMessage, QuickReply
from modules.menu import Menu
from modules.diaryMessage import DiaryFlex
# from modules.menu_vision1 import Menu, Menu_img
from models.gemini import geminiCalEnergy
from models.scanBarcode import scanBarcode
from models.CnnModel import cnnModel

from dbs.mysql import Sql
from dbs.mongo import Mongo

# HTML
from liff.friend import friend_app as friend_blueprint
from liff.nutritionValue2 import Values_app as Values_blueprint
from liff.diary import dairy_app as diary_blueprint

# barcodeInsert
from modules.test_barcode import testBarcodeInfo, ensureReply

app = Flask(__name__, static_url_path='/image', static_folder='image')# 選擇儲存檔案的路徑資料夾={EndPonint/image}
# ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

# 設定 Liff 網址
# https:// *** ngrok-free.app/friend/QRCode
app.register_blueprint(friend_blueprint, url_prefix='/friend')
# https:// *** ngrok-free.app/uploadValues
app.register_blueprint(Values_blueprint, url_prefix='/uploadValues')
# https:// *** ngrok-free.app/diary
app.register_blueprint(diary_blueprint, url_prefix='/diary')

# 頻道的 Channel Access Token 和 Channel Secret
with open('./config/config.json', 'r') as file:
    config = json.load(file)
ChannelAccessToken = config['ChannelAccessToken']
ChannelSecret = config['ChannelSecret']
EndPoint = config['EndPoint']

# 測試人員的 id 名稱
with open('./config/testPersonId.json', 'r', encoding='utf-8') as file:
    testPersonId = json.load(file)

# 處理訊息事件
handle = Handle(ChannelSecret, ChannelAccessToken)
replyMessage = handle.replyMessage
quickReply = QuickReply()
menu = Menu(ChannelAccessToken)
diary = DiaryFlex()

# 連接資料庫
mongoConn = Mongo() 
sql = Sql()
sqlConn = sql.connectSql()

# Menu 設定
# # 刪全部Menu
# for id in menu.getRichMenusId():
#     menu.delRichMenu(id['richMenuId'])
# # 刪Menu_a的別名
# menu.deleteRichMenuAlias("a_alias_id")
# menu.deleteRichMenuAlias("m_alias_id")
# menu.deleteRichMenuAlias("b_alias_id")
# menus = menu.getMenuIdAlias()
# for m in menus:
#     menu.delRichMenu(m['richMenuId'])
#     # menu.deleteRichMenuAlias(m['name'])
# # # 設定預設Menu，只需執行一次
# menu.setDefaultMenu() 

# 使用 requests package 處理 LineBot 回傳訊息/事件 Json 資料
# LineBot 網址為 Flask - Forwarding: https:.../webhook
@app.route("/webhook", methods=['POST', 'GET'])
def index():
    # 用於 Get 請求，回複 ok
    if request.method == 'GET':
        return 'ok'
    
    # # 取得請求內容資料
    # body = request.json  # 與 request.get_data(as_text=True) 取得資料相同
    # request.get_data(as_text=True): str, 獲取請求的原始內容，並轉換為文本形式。
    body = request.get_data(as_text=True)
    print("Request body: " + str(body))

    # 從
    if 'X-Line-Signature' in request.headers:
        # 取得 X-Line-Signature 標頭的值
        signature = request.headers['X-Line-Signature']

        try:
            # 確保訊息是由 Line 伺服器發送的
            handle.lineSign(signature, body)

            bodyJson = json.loads(body)
            events = bodyJson['events']
            # 處理 Webhook URL 使用 Verify 功能所回傳的 Json events 的 List 資料為空
            if len(events) == 0:
                return 'ok'
            for event in events:
                eventType = event['type']
                if eventType == "postback":
                    handlePostback(events)
                elif eventType == 'message':
                    if event['message']['type'] == 'image':
                        handleImageMessage(events)
                    elif event['message']['type'] == "text":
                        handleTextMessage(events)
        except InvalidSignatureError:
            app.logger.info('Invalid Signature. Please Check your channel secret')
            abort(400)
    else:
        print("test")
    return 'ok'
            
@handle.handleEvent(eventType="postback")
def handlePostback(events):
    # # 記錄不同使用者動作，後面接續文字/圖片訊息才需紀錄
    # 指定該使用者的 replyToken 做回覆
    replyToken = events[0]['replyToken'] 
    userId = events[0]["source"]["userId"]
    # 使用者狀態、初始化
    userDatas = mongoConn.mongoSearch(userId=userId, collectionName="UserDatas") 
    if len(userDatas) > 0:
        userDatas = userDatas[0] # 使用者狀態
    else:
        mongoConn.defaultStatus(userId=userId, collectionName="UserDatas")
        userDatas = mongoConn.mongoSearch(userId=userId, collectionName="UserDatas")[0]

    data = json.loads(events[0]["postback"]["data"]) # 將json轉為dict
    action = data['action']
    if action == "nameSearch": # 名稱查詢
        messages = [textMessage(f"請輸入商品名稱")]
        replyMessage(replyToken, messages)
        data = {'MenuStage': {'Status': None, 'BarcodeValue': None, 'HeatCalInfo': None}}
        mongoConn.updateDatas(userId=userId, collectionName="UserDatas", data=data)
    elif action == "barcodeSearch": # 條碼查詢
        messages = [quickReply.cameraQuickReply()]
        replyMessage(replyToken, messages)
        data = {'MenuStage': {'Status': "barcodeSearch", 'BarcodeValue': None, 'HeatCalInfo': None}}
        mongoConn.updateDatas(userId=userId, collectionName="UserDatas", data=data)
    elif action == "imageSearch": # 圖片查詢
        messages = [quickReply.cameraQuickReply()]
        replyMessage(replyToken, messages)
        data = {'MenuStage': {'Status': "imgSearch", 'BarcodeValue': None, 'HeatCalInfo': None}}
        mongoConn.updateDatas(userId=userId, collectionName="UserDatas", data=data)
    elif action == "detailInfo": # 產品詳細資訊
        prod = sql.sqlData(sqlConn, CMNO=data['CMNO'])[0]
        flex = Flex()
        messages = [flex.detailInfo(prod)]
        replyMessage(replyToken, messages)
    elif action == "noInsertProd": # 不添加營養表至資料庫
        messages = [textMessage("結束")]
        replyMessage(replyToken, messages)
    elif action == "insertProd": # 添加營養表至資料庫
        messages = [textMessage("拍攝營養標籤或是選擇有營養標籤的照片。"), quickReply.cameraQuickReply()]
        replyMessage(replyToken, messages)
        data = {'MenuStage': {'Status': "nutritionValueInsert", 'BarcodeValue': userDatas['MenuStage']['BarcodeValue'], 'HeatCalInfo': None}}
        mongoConn.updateDatas(userId=userId, collectionName="UserDatas", data=data)
    elif action == "moreProd": # 搜尋產品> 更多產品
        iter = data['iter']
        shownums = 8 # 顯示8個產品
        prodList = sql.sqlData(sqlConn, PRODNAME=data['searchName'], limit=[shownums*iter, (iter + 1)*shownums + 1]) # 多取一個商品，判定是否進去下一個迴圈
        userDatas = mongoConn.mongoSearch(userId=userId, collectionName="UserDatas")[0] # 使用者狀態
        if len(prodList) > 0:     
            if len(prodList) > shownums:
                if userDatas['MenuStage']['Status'] != "testPersonCheck" and userDatas['MenuStage']['Status'] != "testPersonInsertBarcode":
                    flex = Flex()
                    messages = [flex.BriefInfos(prodList[0 : shownums], moreProd=True, iter=iter+1, searchName=data['searchName'])]
                elif userDatas['MenuStage']['Status'] == "testPersonCheck" or userDatas['MenuStage']['Status'] == "testPersonInsertBarcode":
                    testInfo = testBarcodeInfo() ################# 測試 ##################
                    messages = [testInfo.testProdInfos(prodList[0 : shownums], barcodeValue = userDatas['MenuStage']['BarcodeValue'], moreProd=True, iter=iter+1, searchName=data['searchName'])]
                replyMessage(replyToken, messages)
            else:
                if userDatas['MenuStage']['Status'] != "testPersonCheck" and userDatas['MenuStage']['Status'] != "testPersonInsertBarcode":
                    flex = Flex()
                    messages = [flex.BriefInfos(prodList[0 : shownums])]
                elif userDatas['MenuStage']['Status'] == "testPersonCheck" or userDatas['MenuStage']['Status'] == "testPersonInsertBarcode":
                    testInfo = testBarcodeInfo() ################# 測試 ##################
                    messages = [testInfo.testProdInfos(prodList[0 : shownums], barcodeValue = userDatas['MenuStage']['BarcodeValue'])]
                replyMessage(replyToken, messages)
    elif action == "dietRecord": # 紀錄飲食
        prod = data['prod']
        for key, value in prod.items():
            if value is None:
                prod[key] = "0"
        messages = [quickReply.addDietInfo(prod=data['prod'])]
        replyMessage(replyToken, messages)
    elif action == "dietRecordBrief": # 簡短介面的紀錄飲食
        prod = sql.sqlData(sqlConn, CMNO=data['CMNO'])[0]
        prod = {"PRODNAME":prod["PRODNAME"], "LEVEL": prod['LEVEL'], "HEAT": prod["HEAT"], "PROTEIN": prod["PROTEIN"], "TOTALFAT": prod["TOTALFAT"], "CARBOHYDRATE": prod["CARBOHYDRATE"], "SUGAR": prod["SUGAR"], "SODIUM": prod["SODIUM"]}
        for key, value in prod.items():
            if value is None:
                prod[key] = "0"
        messages = [quickReply.addDietInfo(prod=prod)]
        replyMessage(replyToken, messages)
    elif action == "dietInfo": # 紀錄飲食> 選擇時間
        prod = data['prod']
        prod['DATETIME'] = events[0]["postback"]["params"]["datetime"]
        prod['UNIT'] = data['UNIT']
        mongoConn.insertDietData(userId=userId, prod=prod, collectionName="dietRecord")
        messages = [textMessage(f"上傳飲食記錄成功！\n\n紀錄內容如下:\n日期: {prod['DATETIME']}\n食物: {prod['PRODNAME']}\n份量: {prod['UNIT']}")]
        replyMessage(replyToken, messages)
    elif action == "noinsertNutri": # 條碼查詢 > 不存在商品 > 不填寫營養資料
        messages = [textMessage(f"已取消填寫營養資料。")]
        replyMessage(replyToken, messages)
    
    elif action == "dietRecordMore": # 飲食日記 > more
        searchDATETIME = data['DATETIME']
        records = mongoConn.mongoSearch(userId=userId, collectionName="dietRecord")
        prodList = records[0]['prodList'] # 每天的飲食項目
        prods = [item for item in prodList if item.get('DATETIME').split('T')[0] == str(searchDATETIME)]
        messages = [diary.morePordButton(prods, searchDATETIME)]
        replyMessage(replyToken, messages)
    elif action == "dietRecordEdit": # 飲食日記 > 編輯記錄
        prod = data['prod']
        prodInfo = mongoConn.mongoSearch(userId=userId, listName="prodList", listMatch=prod, collectionName="dietRecord")['prodList'][0]
        messages = [diary.recordEdit(prodInfo)]
        replyMessage(replyToken, messages) 
    elif action == "dietRecordDel": # 飲食日記 > 刪除記錄
        prod = data['prod']
        mongoConn.removeProd(userId=userId, prod=prod, collectionName="dietRecord")
        messages = [textMessage(f"刪除飲食紀錄成功！\n\n記錄內容如下:\n日期: {prod['DATETIME']}\n食物: {prod['PRODNAME']}")]
        replyMessage(replyToken, messages)
    elif action == "norename": # 熱量估算 > 不更改飲食名稱
        prodInfo = userDatas['MenuStage']['HeatCalInfo']
        flex = Flex()
        messages = [flex.detailInfo(prodInfo[0])]
        # if userId in testPersonId:
        #     messages.append(textMessage(str(prodInfo[1])))
        replyMessage(replyToken, messages)
    elif action == "rename": # 熱量估算 > 更改飲食名稱
        messages = [textMessage("請輸入飲食名稱。")]
        replyMessage(replyToken, messages)
    # elif action == "nextPage": # 好友查看按鍵
    #     start = time.time()
    #     menus = menu.getRichMenusId() # 全部的menuList內容
    #     menuId = menu.getRichMenuIdByName(menus, menuName=userId)
    #     if menuId:
    #         menu.setUserMenu(richMenuId=menuId, userId=userId)
    #     else:
    #         # 生成menu
    #         Menu_img().img_process(userId)
    #         menu.setNextMenu(menuName=userId, menuImagePath=f'./image/menuImg/vision1_b_left_{userId}.jpg')
    #     end = time.time()
    #     print("生成Menu圖片: ", end - start)
    # elif action == "prevPage": # 返回主 Menu
    #     deletePhotos(f'./image/menuImg/vision1_b_left_{userId}.jpg')
    #     # # 刪除 menu
    #     # menus = menu.getRichMenusId() # 全部的menuList內容
    #     # menuId = menu.getRichMenuIdByName(menus, menuName=userId)
    #     # menu.delRichMenu(menuId)

    ############ 測試人員區 #####################
    elif action == "insertBarcode": # 新增條碼資料
        messages = [textMessage("請輸入產品名稱")]
        replyMessage(replyToken, messages)
        # 更新使用者狀態
        data = {'MenuStage': {'Status': 'testPersonInsertBarcode', 'BarcodeValue': data['barcodeValue'], 'HeatCalInfo': None}}
        mongoConn.updateDatas(userId=userId, collectionName="UserDatas", data=data)
    elif action == "insertBarcodeValue": # 登錄Barcode
        messages = [ensureReply(CMNO=data['CMNO'], barcodeValue=data['barcodeValue'], PRODNAME=data['PRODNAME'])]
        replyMessage(replyToken, messages)
    elif action == "ensureYes": # 確認(條碼)資料
        for id, name in testPersonId.items():
            if userId == id:
                personNAME = name
        sql.updateBarcode(sqlConn, CMNO=data['CMNO'], barcodeValue=data['barcodeValue'], personNAME=personNAME)
        messages = [textMessage("登錄成功。")]
        replyMessage(replyToken, messages)
        
        data = {'MenuStage': {'Status': None, 'BarcodeValue': None, 'HeatCalInfo': None}}
        mongoConn.updateDatas(userId=userId, collectionName="UserDatas", data=data)
    elif action == "ensureNo": # 取消(條碼)資料
        messages = [textMessage("結束登錄/檢查。")]
        replyMessage(replyToken, messages)
        data = {'MenuStage': {'Status': None, 'BarcodeValue': None, 'HeatCalInfo': None}}
        mongoConn.updateDatas(userId=userId, collectionName="UserDatas", data=data)
        deletePhotos(f"./image/yoloImg/{userId}.jpg") # 刪除圖片
    elif action == "exitCheck":
        messages = [textMessage("結束檢查。")] 
        replyMessage(replyToken, messages)
        data = {'MenuStage': {'Status': None, 'BarcodeValue': None, 'HeatCalInfo': None}}
        mongoConn.updateDatas(userId=userId, collectionName="UserDatas", data=data)

@handle.handleEvent(eventType="message", messageType="image")
def handleImageMessage(events):
    replyToken = events[0]['replyToken'] 
    userId = events[0]["source"]["userId"]
    # 使用者狀態、初始化
    userDatas = mongoConn.mongoSearch(userId=userId, collectionName="UserDatas") 
    if len(userDatas) > 0:
        userDatas = userDatas[0] # 使用者狀態
    else:
        mongoConn.defaultStatus(userId=userId, collectionName="UserDatas")
        userDatas = mongoConn.mongoSearch(userId=userId, collectionName="UserDatas")[0]
    
    # 非點擊按鈕就上傳圖片 -> 不回應並不保存圖片
    if not userDatas['MenuStage']['Status']:
        messages = [textMessage("請先選擇功能，再上傳圖片哦!")]
        replyMessage(replyToken, messages)
        return 'ok'
      
    # 點擊按鈕後上傳的圖片處理
    # 儲存圖片至本機 
    messageId = events[0]['message']['id'] # 取得圖片 id 
    
    if userDatas['MenuStage']['Status'] == "barcodeSearch": # 條碼查詢
        imgPath = handle.saveImageMessage(messageId=messageId, imgName=replyToken, imgfolder="image/barcodeImg/") # 儲存圖片
        # 辨識barcode
        barcode = scanBarcode(imgPath)
        # 回覆內容
        if len(barcode) == 0:  
            messages = [textMessage("上傳的圖片不清晰，或是圖片不包含條碼。\n請再上傳一次照片!"),
                        quickReply.cameraQuickReply()]
            replyMessage(replyToken, messages)
        else:
            prod = sql.sqlData(sqlConn, BARCODE=str(barcode[1]))
            if len(prod) == 0:
                
                messages = [textMessage(f"條碼資料為 {str(barcode[1])}")] 
                if userId not in testPersonId: # 添加新增營養資料按鈕
                    messages.append(quickReply.addProdInfos(str(barcode[1]), testPerson=False))
                elif userId in testPersonId: # 添加新增條碼資料按鈕
                    messages.append(quickReply.addProdInfos(str(barcode[1]), testPerson=True)) 
                replyMessage(replyToken, messages)
            else:
                prod = prod[0]
                flex = Flex()
                messages = [flex.detailInfo(prod)]

                replyMessage(replyToken, messages)
            data = {'MenuStage': {'Status': 'barcodeSearch', 'BarcodeValue': str(barcode[1]), 'HeatCalInfo': None}}
            mongoConn.updateDatas(userId=userId, collectionName="UserDatas", data=data)
        deletePhotos(imgPath) # 刪除圖片

    elif userDatas['MenuStage']['Status'] == "HeatCaculate": # 熱量估算
        imgPath = handle.saveImageMessage(messageId=messageId, imgName=replyToken, imgfolder="image/geminiImg/") # 儲存圖片
        flex = Flex()
        try:
            prodInfo = asyncio.run(geminiCalEnergy(imgPath))
            prodInfo[0]['PRODNAME'] = "熱量分析"
            data = {'MenuStage': {'Status': "HeatCaculate", 'BarcodeValue': None, 'HeatCalInfo': prodInfo}}
            mongoConn.updateDatas(userId=userId, collectionName="UserDatas", data=data)
            messages = [quickReply.renameQuickReply("感謝您的等待!\n是否要填寫飲食名稱?")]
            replyMessage(replyToken, messages)
        except:
            replyMessage(replyToken,
                        [textMessage("伺服器忙碌中，稍後再嘗試。")])
        deletePhotos(imgPath) # 刪除圖片
    elif userDatas['MenuStage']['Status'] == "imgSearch": # 圖片查詢
        imgPath = handle.saveImageMessage(messageId=messageId, imgName=replyToken, imgfolder="image/cnnImg/") # 儲存圖片
        try:
            prodBarcode = asyncio.run(cnnModel(imgPath))
            if prodBarcode=="找不到對應商品" :
                messages = [textMessage("找不到對應商品")]
            else :
                prod = sql.sqlData(sqlConn, BARCODE=prodBarcode, table='products')
                flex = Flex()
                messages = [flex.detailInfo(prod[0])]
        except:
            messages = [textMessage("伺服器錯誤!")]
            print("Cnn Error.")
        replyMessage(replyToken, messages)
        deletePhotos(imgPath) # 刪除圖片
    elif userDatas['MenuStage']['Status'] == "nutritionValueInsert": # 添加營養標籤
        imgPath = handle.saveImageMessage(messageId=messageId, imgName=userId, imgfolder="image/yoloImg/")
        messages = [quickReply.YoloensureQuickReply("已收到您的圖片!\n請開始填寫營養資料。", userId=userId)]
        replyMessage(replyToken, messages)
    else:
        messages = [textMessage("請先選擇功能，再上傳圖片哦!")]
        replyMessage(replyToken, messages)
        deletePhotos(imgPath) # 刪除圖片

@handle.handleEvent(eventType="message", messageType="text")
def handleTextMessage(events):
    replyToken = events[0]['replyToken'] 
    userId = events[0]["source"]["userId"]
    # 使用者狀態、初始化
    userDatas = mongoConn.mongoSearch(userId=userId, collectionName="UserDatas") 
    if len(userDatas) > 0:
        userDatas = userDatas[0] # 使用者狀態
    else:
        mongoConn.defaultStatus(userId=userId, collectionName="UserDatas")
        userDatas = mongoConn.mongoSearch(userId=userId, collectionName="UserDatas")[0]

    # 主選單文字回應
    if events[0]['message']['text'] == "@產品查詢":
        flex = Flex()
        messages = [flex.MainSearchProd()]
        replyMessage(replyToken, messages)
        # 狀態更新
        data = {'MenuStage': {'Status': None, 'BarcodeValue': None, 'HeatCalInfo': None}}
        mongoConn.updateDatas(userId=userId, collectionName="UserDatas", data=data)
    elif events[0]['message']['text'] == "@熱量估算":
        messages = [textMessage("熱量需時間估算。\n請稍後等待。"),
                    quickReply.cameraQuickReply()]
        replyMessage(replyToken, messages)
        # 狀態更新
        data = {'MenuStage': {'Status': "HeatCaculate", 'BarcodeValue': None, 'HeatCalInfo': None}}
        mongoConn.updateDatas(userId=userId, collectionName="UserDatas", data=data)
    elif events[0]['message']['text'] == "@飲食日記":
        # 狀態更新
        data = {'MenuStage': {'Status': "SelfDiary", 'BarcodeValue': None, 'HeatCalInfo': None}}
        mongoConn.updateDatas(userId=userId, collectionName="UserDatas", data=data)
        result = diary.mainDiary(userId, mongoConn)
        if result:
            messages = [result,
                        textMessage("此僅顯示/修改近期三天。\n如需查看先前歷史記錄，\n請至飲食分析查看。")]
        else:
            messages = [textMessage("尚無日記紀錄。\n\n此僅顯示/修改近期三天。\n如需查看先前歷史記錄，\n請至飲食分析查看。")]
        replyMessage(replyToken, messages) 
        
    elif events[0]['message']['text'] == "@飲食分析":
        # 狀態更新
        data = {'MenuStage': {'Status': "DietAnaly", 'BarcodeValue': None, 'HeatCalInfo': None}}
        mongoConn.updateDatas(userId=userId, collectionName="UserDatas", data=data)
        messages = [quickReply.diaryQuickReply(text="前往查看詳細飲食與分析", userId=userId)]
        replyMessage(replyToken, messages) 
    
    elif events[0]['message']['text'] == "@好友日記":
        friends = userDatas["Friends"]
        if len(friends) > 0:
            messages = [] #[textMessage(str(friends))]
            messages.append(quickReply.friendDiary("請選擇要查看的好友。", friends, mongoConn))
        else:
            messages = ([textMessage("尚無好友。")])
        replyMessage(replyToken, messages) 
        # 狀態更新
        data = {'MenuStage': {'Status': "FriendDiary", 'BarcodeValue': None, 'HeatCalInfo': None}}
        mongoConn.updateDatas(userId=userId, collectionName="UserDatas", data=data)
    elif events[0]['message']['text'] == "@好友添加":
        imgPath = handle.userIdToQrcode(userId=userId) # 將 userId 轉為 QRCode 
        flex = Flex()
        messages = [flex.friendAdd(QRCodeUrl=f"{EndPoint}/{imgPath}", scanUrl=config['friendLiffUrl'])]
        replyMessage(replyToken, messages)
        # # 刪除user QRcode照片
        # time.sleep(2)
        # 狀態更新
        data = {'MenuStage': {'Status': "AddFriend", 'BarcodeValue': None, 'HeatCalInfo': None}}
        mongoConn.updateDatas(userId=userId, data=data, collectionName="UserDatas")
    elif events[0]['message']['text'] == "添加營養資料成功。": # YOLO添加營養標籤資料 > 結束
        messages = [textMessage("感謝您幫忙添加資料。")]
        replyMessage(replyToken, messages) 
    elif events[0]['message']['text'] == "@接受": # 好友添加確認 
        if userDatas["friendShip"]:
            friendId = userDatas["friendShip"]     
            if friendId not in userDatas["Friends"]:   
                mongoConn.updateDatas(friendId, data={"Friends": userId}, listName="Friends", collectionName="UserDatas")
                mongoConn.updateDatas(userId, data={"Friends": friendId}, listName="Friends", collectionName="UserDatas")
                messages = [textMessage("添加好友成功。")]
                handle.pushMessage(friendId, messages)
                replyMessage(replyToken, messages) 
            else:
                messages = [textMessage("已經是好友。")]
                handle.pushMessage(friendId, messages)
                replyMessage(replyToken, messages) 
            mongoConn.updateDatas(friendId, data={"friendShip": None}, collectionName="UserDatas")
            mongoConn.updateDatas(userId, data={"friendShip": None}, collectionName="UserDatas")
        else:
            messages = [textMessage("已失效，請重新掃描添加。")]
            replyMessage(replyToken, messages) 
    elif events[0]['message']['text'] == "@拒絕": # 拒絕好友添加
        if userDatas["friendShip"]:
            friendId = userDatas["friendShip"]    
            handle.pushMessage(friendId, [{"type": "text", "text": "添加好友失敗"}])
            mongoConn.updateDatas(friendId, data= {"friendShip":  None}, collectionName="UserDatas")
            mongoConn.updateDatas(userId, data= {"friendShip":  None}, collectionName="UserDatas")
        else:
            messages = [textMessage("已失效，請重新掃描添加。")]
            replyMessage(replyToken, messages) 
    elif userDatas['MenuStage']['Status'] == "HeatCaculate": # 熱量分析 > 改飲食名稱
        prodInfo = userDatas['MenuStage']['HeatCalInfo']
        prodInfo[0]['PRODNAME'] = events[0]['message']['text']
        flex = Flex()
        messages = [flex.detailInfo(prodInfo[0])]
        # if userId in testPersonId:
        #     messages.append(textMessage(str(prodInfo[1])))
        replyMessage(replyToken, messages)
        data = {'MenuStage': {'Status': 'HeatCaculate', 'BarcodeValue': None, 'HeatCalInfo': None}}
        mongoConn.updateDatas(userId=userId, collectionName="UserDatas", data=data)
    ################################ 測試人員顯示，比對測試人員的 ID  #################################
    elif userId in testPersonId:
        if events[0]['message']['text'] == "檢查":
            messages = [textMessage("請輸入要檢查的產品名稱")]
            # print(messages)
            replyMessage(replyToken, messages)
            data = {'MenuStage': {'Status': 'testPersonCheck', 'BarcodeValue': None, 'HeatCalInfo': None}}
            mongoConn.updateDatas(userId=userId, collectionName="UserDatas", data=data)
        elif events[0]['message']['text'] == "未完成":
            prod = sql.searchNullBarcode(conn=sqlConn, table="products")
            showProdNums = 300
            reply = []
            messages = []
            for i in range(len(prod)//showProdNums):
                reply.append(f"列表{i+1}\n")                
                for p in prod[i*showProdNums:(i+1)*showProdNums]:
                    reply[i] += f"{p['PRODNAME']}\n"
                messages.append(textMessage(reply[i]))
            replyMessage(replyToken, messages)
        elif events[0]['message']['text'] == "數量":
            messages = [textMessage(sql.searchNums(conn=sqlConn, table="products"))]
            replyMessage(replyToken, messages)
        elif userDatas['MenuStage']['Status'] == "testPersonCheck" or userDatas['MenuStage']['Status'] == "testPersonInsertBarcode":
            PRODNAME = events[0]['message']['text']
            shownums = 8 # 顯示8個產品
            prodList = sql.sqlData(sqlConn, PRODNAME=PRODNAME, limit=[0, shownums + 1]) # 多取一個商品，判定是否進去下一個迴圈
            if userDatas['MenuStage']['Status'] == "testPersonInsertBarcode":
                if len(prodList) > 0:
                    testInfo = testBarcodeInfo()
                    if len(prodList) > shownums: # 超過8個產品，顯示更多按鈕
                        messages = [testInfo.testProdInfos(prodList[0:shownums], barcodeValue = userDatas['MenuStage']['BarcodeValue'], moreProd=True, iter=1, searchName=PRODNAME)]
                    else:
                        messages = [testInfo.testProdInfos(prodList, barcodeValue = userDatas['MenuStage']['BarcodeValue'])]
                    replyMessage(replyToken, messages)
                else: 
                    messages = [textMessage("查詢不到該商品資料!\n請重新輸入產品名稱。")]
                    replyMessage(replyToken, messages)
            elif userDatas['MenuStage']['Status'] == "testPersonCheck":
                if len(prodList) > 0:
                    testInfo = testBarcodeInfo()
                    if len(prodList) > shownums: # 超過8個產品，顯示更多按鈕
                        messages = [testInfo.testProdInfos(prodList[0:shownums], barcodeValue = None, moreProd=True, iter=1, searchName=PRODNAME)]
                    else:
                        messages = [testInfo.testProdInfos(prodList, barcodeValue = None)]
                    replyMessage(replyToken, messages)
                else:
                    messages = [textMessage("查詢不到該商品資料!\n請重新輸入產品名稱。")]
                    replyMessage(replyToken, messages)
        else: # 名稱查詢
            PRODNAME = events[0]['message']['text']
            shownums = 8 # 顯示8個產品
            prodList = sql.sqlData(sqlConn, PRODNAME=PRODNAME, limit=[0, shownums + 1]) # 多取一個商品，判定是否進去下一個迴圈
            # 正常使用區
            if len(prodList) > 0:
                flex = Flex()
                if len(prodList) > shownums: # 超過8個產品，顯示更多按鈕
                    messages = [flex.BriefInfos(prodList[0:shownums], moreProd=True, iter=1, searchName=PRODNAME)]
                    replyMessage(replyToken, messages)
                else:
                    messages = [flex.BriefInfos(prodList)]
                    replyMessage(replyToken, messages)
            else:
                messages = [textMessage("查詢不到該商品資料!\n請重新輸入產品名稱。")]
                replyMessage(replyToken, messages)

    # 非主選單的文字且非點擊按鈕後所傳的文字 -> 預設為產品名稱查詢
    # 資料庫查詢產品名稱
    else: 
        PRODNAME = events[0]['message']['text']
        shownums = 8 # 顯示8個產品
        prodList = sql.sqlData(sqlConn, PRODNAME=PRODNAME, limit=[0, shownums + 1]) # 多取一個商品，判定是否進去下一個迴圈
        # 正常使用區
        if len(prodList) > 0:
            flex = Flex()
            if len(prodList) > shownums: # 超過8個產品，顯示更多按鈕
                messages = [flex.BriefInfos(prodList[0:shownums], moreProd=True, iter=1, searchName=PRODNAME)]
                replyMessage(replyToken, messages)
            else:
                messages = [flex.BriefInfos(prodList)]
                replyMessage(replyToken, messages)
        else:
            messages = [textMessage("查詢不到該商品資料!\n請重新輸入產品名稱。")]
            replyMessage(replyToken, messages)

if __name__ == "__main__":
    # app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    app.debug = True
    app.run()

# 傳遞資料的 Json 格式
#     json =    {
#                'destination': 'Ue0353e87979b7e9ec2e8088187f786a7', 
#                'events': 
#                    [{  'type': 'message', 
#                        'message': 
#                            {'type': 'image', 
#                             'id': '487902266604126616', 
#                             'quoteToken': '1xrigmg5zXYmOBalEDjGAiIWtdRnOt0nkgTB4sVvSsA6VvDAA3z5UqsjEah0TB0nvzaAKGDC4uwKb21RC1q6mu8U1JwZdk5KeRgaw3V53g61CONAUjMYoTjw2Ey21rd--RfMXiTs7lAMIfl9tqvJfw', 
#                             'contentProvider': {'type': 'line'}}, 
#                        'webhookEventId': '01HJMH87PCCBDTDP22X2VF73SD', 
#                        'deliveryContext': {'isRedelivery': False}, 
#                        'timestamp': 1703643717288, 
#                        'source': {'type': 'user', 'userId': 'U14957e1111e10acdbca91b3ecf2ab8c4'}, 
#                        'replyToken': 'a8c5d23a0b3f4a638436a6e3a8d06596', # 哪個使用者傳遞
#                        'mode': 'active'}]
#                } 

# {
#   "events": [
#     {
#       "type": "follow",
#       "replyToken": "nHuyWiB7yP5Zw52FIkcQobQuGDXCTA",
#       "source": {
#         "userId": "U4af4980629..."
#       },
#       "timestamp": 1462629479859
#     }
#   ]
# }