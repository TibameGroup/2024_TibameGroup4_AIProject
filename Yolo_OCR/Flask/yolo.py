from flask import Flask, request, render_template
import cv2 
import os 
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import re
from google.cloud import vision

upload_folder = "./img"
allowed_extensions = {'jpg','png','jpeg'}
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "googleVisionOCRKey.json"

app = Flask(__name__)
app.config['upload_folder'] = upload_folder

template={  1: "UNIT",
            2: "HEAT",
            3: "PROTEIN",
            4: "TOTALFAT",
            5: "SATFAT",
            6: "TRANSFAT",
            7: "CARBOHYDRATE",
            8: "SUGAR",
            9: "SODIUM",
            0: "G_ML_NUM" }

def allowed_file(filename) :
    return '.' in filename  and  filename.rsplit('.')[1].lower() in allowed_extensions

# 圖片前處理
def Preprocessing(file) :
    filename = secure_filename(file.filename)
    imgPath = os.path.join(app.config['upload_folder'], filename)
    file.save(imgPath)
    img = cv2.imread(imgPath)
    img = cv2.resize(img, (640,640))
    cv2.imwrite(imgPath, img)
    return imgPath

# 使用 Yolo 抓取營養標示位置
def predict(imgPath) :
    # model = YOLO('yolov8n.pt')  # load an official model
    model = YOLO('./yolov8Model.pt')  # load a custom model
    results = model(imgPath)  # predict on an image
    return results

def boxDetection(results, template=template) :
    boxesList = []
    categoriesList = []
    boxes = results[0].boxes.xyxy.numpy()
    cls = results[0].boxes.cls.numpy()
    for box in boxes :
        boxesList.append(box)
    for c in cls :
        categoriesList.append(template[c])
    return boxesList, categoriesList

# 圖片裁切完的座標
def cropImage(contours, imgPath) :
    img = cv2.imread(imgPath)
    i = 0
    imgPathList = []
    for contour in contours :
        img = img.copy()
        x1 = int(contour[0]) -3
        x2 = int(contour[2]) +3
        y1 = int(contour[1]) -2
        y2 = int(contour[3]) +2
        crop_img = img[y1:y2, x1:x2] 
        cv2.imwrite(imgPath+str(i)+".jpg", crop_img)
        imgPathList.append(imgPath+str(i)+".jpg")
        i += 1
    return imgPathList

def ocr(imgpaths, categories) :
    client = vision.ImageAnnotatorClient()
    idx = 0
    results = []
    for input_path in imgpaths: 
        with open(input_path, "rb") as image_file:
            content = image_file.read()
            image = vision.Image(content=content)
            response = client.text_detection(image=image)
            texts = response.text_annotations
            for text in texts:
                matchs = re.findall(r'(\d+(\.\d+)?\s*(毫升|毫克|公克|大卡|份))\b', text.description)
                # matchs = re.findall(r'飽和脂肪|糖|本包裝含\s+(\d+)\s*份|碳水化合物|鈉|反式脂肪|脂肪|每一份量\d+公克|蛋白質|熱量)\s*(\d+(\.\d+)?)\s*公克|毫克|大卡')
                if matchs and categories[idx] != "G_ML_NUM":
                    matchs = matchs[0][0].replace("公克", "").replace("大卡", "").replace("毫克", "").replace("份", "").replace("毫升", "")
                    results.append({categories[idx]:matchs})
                elif matchs and len(matchs[0]) >= 3 and categories[idx] == "G_ML_NUM":
                    unit = matchs[0][2]
                    results.append({"G_ML":unit })
                    matchs = matchs[0][0].replace("公克", "").replace("大卡", "").replace("毫克", "").replace("份","").replace("毫升","")
                    results.append({categories[idx]:matchs})
            idx += 1
        os.remove(input_path)
    return match(results)
def match(results):
    nutrition = {
        "G_ML_NUM":"null",
        "G_ML":"null",
        "UNIT":"null",
        "HEAT":"null",
        "PROTEIN":"null",
        "TOTALFAT":"null",
        "SATFAT":"null",
        "TRANSFAT":"null",
        "CARBOHYDRATE":"null",
        "SUGAR":"null",
        "SODIUM":"null",
    }
    for result in results :
        nutritionName=list(result.keys())[0]
        if nutritionName in nutrition :
            nutrition[nutritionName]=result[nutritionName]       
    return nutrition

@app.route('/')
def upload_form():
    return render_template('upload_form.html')
@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST" :
        if 'file' not in request.files :
            return "Not file"    
        file = request.files['file']
        if file.filename == "" :
            return "NO filename"
        if file and allowed_file(file.filename) :
            imgPath = Preprocessing(file) 
            results = predict(imgPath)
            contours, categories = boxDetection(results)
            imgpaths = cropImage(contours,imgPath)
            data = ocr(imgpaths,categories)
            os.remove(imgPath)
            # print(data)
            return data

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
    
