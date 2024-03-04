from flask import Flask, Blueprint, render_template, jsonify, request
import base64
import requests
import json
import random
from dbs.mongo import Mongo
from dbs.mysql import Sql 
from dbs.levelCal import calculate_and_get_level
from modules.LineMessageHandle import deletePhotos

sql = Sql()
sqlConn = sql.connectSql()
mongoConn = Mongo() 
# print("435",sqlConn)

Values_app = Blueprint('Values_app', __name__, template_folder='templates')

with open('./config/config.json', 'r') as file:
    config = json.load(file)
YoloLiffID = config["YoloLiffID"]
YoloOcrURL = config["YoloOcrURL"]

# 設定文件儲存路徑
UPLOAD_FOLDER = './image/yoloImg'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@Values_app.route('/')
def index():
    return render_template('nutritionValue2.html', YoloLiffID=YoloLiffID)

@Values_app.route('/get_file_content', methods=['POST'])
def get_file_content():
    userInfo = request.json
    userId = userInfo.get('userId')
    print(userId)
    imgPath = f"{UPLOAD_FOLDER}/{userId}.jpg"
    # imgPath = f"{UPLOAD_FOLDER}/example.jpg"

    # Yolo與OCR計算
    url = YoloOcrURL # Yolo與OCR計算的VM網址
    # 要上傳的圖片文件
    files = {'file': open(imgPath, 'rb')}  # 替換成實際的圖片文件路徑
    # 對YOLO與OCR的程式發送POST請求
    response = requests.post(url, files=files)
    nutrition = response.json()

    # 取得YOLO與OCR的程式結果與回應
    if response.status_code == 200:
        print('Yolo Image uploaded successfully!')
        print(response.json())  # 如果Flask應用程式返回JSON，可以使用json()方法解析
    else:
        print('Error uploading image:', response.status_code, response.text)

    # 讀取圖片並以 base64 編碼
    with open(imgPath, 'rb') as file:
        image_data = base64.b64encode(file.read()).decode('utf-8')
    data = {
        "image": image_data,
        "G_ML_NUM": nutrition.get('G_ML_NUM', '').strip(),
        "G_ML": nutrition.get('G_ML', '').strip(),
        "UNIT": nutrition.get('UNIT', '').strip(),
        "HEAT": nutrition.get('HEAT', '').strip(),
        "PROTEIN": nutrition.get('PROTEIN', '').strip(),
        "TOTALFAT": nutrition.get('TOTALFAT', '').strip(),
        "SATFAT": nutrition.get('SATFAT', '').strip(),
        "TRANSFAT": nutrition.get('TRANSFAT', '').strip(),
        "CARBOHYDRATE": nutrition.get('CARBOHYDRATE', '').strip(),
        "SUGAR": nutrition.get('SUGAR', '').strip(),
        "SODIUM": nutrition.get('SODIUM', '').strip(),
    }
    
    return jsonify(data)

@Values_app.route("/nutritionValues", methods=["POST"] ) 
def nutritionValues() :
    if request.method == 'POST':
        data = request.get_json()
        userId = data['userId']
        print(userId)
        userInfo = mongoConn.mongoSearch(userId=userId, collectionName="UserDatas")
        barcodeValue = userInfo[0]["MenuStage"]["BarcodeValue"]
        # 編輯產品編號，CMNO
        random_digits = ''.join(random.choices('0123456789', k=6))
        CMNO = "C" + random_digits
        while True :
            # sql查詢有沒有此商品編號
            checkCmno = sql.sqlData(sqlConn, CMNO=CMNO)
            if checkCmno != []: 
                random_digits = ''.join(random.choices('0123456789', k=6))
                CMNO = "C" + random_digits
            else :
                break
        # 產品標籤資料
        data = request.json 
        
        data = data['formData']
        # print(data)
        data["BARCODE"] = barcodeValue
        data["CMNO"] = CMNO
        # print(data)
        data["LEVEL"] = calculate_and_get_level(data)[1]
        print(data)
        result = []
        for key, val in data.items():
            result.append(val.strip())
        # 儲存置資料庫
        sql.insertProduct(sqlConn, result) 
        data = {'MenuStage': {'Status': None, 'BarcodeValue': None, 'HeatCalInfo': None}}
        mongoConn.updateDatas(userId=userId, collectionName="UserDatas", data=data)
        deletePhotos(f"./image/yoloImg/{userId}.jpg") # 刪除圖片
        return "ok" 
    return "upload error" 

if __name__ == "__main__":
    app.register_blueprint(Values_app)
    app.run(debug=True)
