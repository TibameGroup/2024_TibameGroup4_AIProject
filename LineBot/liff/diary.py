from flask import Flask, Blueprint, render_template, request
from datetime import datetime
from modules.BMR_and_nutrition import calculate_nutrition 
from dbs.mongo import Mongo
import math

dairy_app = Blueprint('dairy_app', __name__, template_folder='templates')
app = Flask(__name__)
app.config['LIFF_STATIC_FOLDER'] = 'liff'
mongoConn = Mongo() 

def dateIndex(dietRecord, time):
    idx = 0
    if  len(dietRecord) == 0 :
        return None
    for dateRecord in dietRecord[0]['dayRecords'] :
        dateRecord = dateRecord["DATETIME"]
        if dateRecord == str(time) :
            return idx
        idx += 1
    return None 

def targetNutritionValue(mongoConn,userId):
    # U6162fda48cd78a21c1a48340ff68e7c3
    # U0c002208c30c59e13b23a19112ed2527
    # U03ff6cfccbc18417cadee840cd0a3261
    userinfo = mongoConn.mongoSearch(userId=userId, collectionName="UserDatas")
    if not userinfo[0]["userHeight"]:
        return {'熱量': 1, '蛋白質': 1, '脂肪': 1, '碳水化合物': 1, '糖': 1, '鈉': 1}, None, None, None, None, None
    else :
        height = int( userinfo[0]["userHeight"])
        weight = int(userinfo[0]["userWeight"])
        current_date_time = datetime.now()
        current_year = current_date_time.year
        age = current_year - int(userinfo[0]["userBirthYear"])
        gender = userinfo[0]["userGender"]
        activity_level = userinfo[0]["activityLevel"]
        username = userinfo[0]["userName"]
        workout = userinfo[0]["highProteinDiet"]
        target_dict = calculate_nutrition(height, weight, age, gender, activity_level, workout)
        if gender == "female":
            target_dict.update({"糖":25.0})
        else :
            target_dict.update({"糖":36.0})
        target_dict.update({"鈉":2000.0})
    return  target_dict, weight, height, username, activity_level, workout

def ingestNutritionValue(mongoConn, time,userId) :
    dietRecord = mongoConn.mongoSearch(userId=userId, collectionName="dietRecord")
    idx = dateIndex(dietRecord, time)
    if idx == None :
        ingestValue = 0
        proteinIngestValue = 0
        totalfatIngestValue = 0
        carbohydrateIngestValue = 0
        sodiumsIngestValue = 0
        sugarsIngestValue = 0
    else : 
        ingestValue = float(dietRecord[0]["dayRecords"][idx]["HEATS"])  #
        proteinIngestValue = float(dietRecord[0]["dayRecords"][idx]["PROTEINS"])
        totalfatIngestValue = float(dietRecord[0]["dayRecords"][idx]["TOTALFATS"])
        carbohydrateIngestValue = float(dietRecord[0]["dayRecords"][idx]["CARBOHYDRATES"])
        sugarsIngestValue = float(dietRecord[0]["dayRecords"][idx]["SUGARS"])
        sodiumsIngestValue = float(dietRecord[0]["dayRecords"][idx]["SODIUMS"])
    rank_dict = rank(dietRecord,time)
    dietRecordDict = record(dietRecord,time)
    ingestList = [ingestValue, proteinIngestValue, totalfatIngestValue, carbohydrateIngestValue, sugarsIngestValue, sodiumsIngestValue]
    return ingestList, rank_dict, dietRecordDict
     
def rank(dietRecord, time)  :
    rank_dict = {
        "A":0,
        "B":0,
        "C":0,
        "D":0,
        "E":0,
    }

    if  len(dietRecord) == 0 :
        return rank_dict
    for dateRecord in dietRecord[0]['prodList'] :  
        if str(time) == dateRecord["DATETIME"].split("T")[0] and dateRecord["LEVEL"] == "0":
            continue
        if str(time) == dateRecord["DATETIME"].split("T")[0] : 
            rank_dict[dateRecord["LEVEL"]] += 1
        
        if str(time) < dateRecord["DATETIME"].split("T")[0] :
            break
    return rank_dict
            
def record(dietRecord,date) :
    dietRecordDict = {"早餐":[], "午餐":[], "晚餐":[] }
    if len(dietRecord) == 0 :
        return {"早餐":[], "午餐":[], "晚餐":[] }
    for dateRecord in dietRecord[0]['prodList'] :  
        datetimes = dateRecord["DATETIME"].split("T")[0]
        times = dateRecord["DATETIME"].split("T")[1]
        times = datetime.strptime(times, '%H:%M').time()
        if  str(date) == datetimes and times< datetime.strptime('12:00', '%H:%M').time():
            dietRecordDict["早餐"].append(dateRecord)
        elif  str(date) == datetimes and times< datetime.strptime('18:00', '%H:%M').time():
            dietRecordDict["午餐"].append(dateRecord)
        elif  str(date) == datetimes and times< datetime.strptime('23:59', '%H:%M').time():
            dietRecordDict["晚餐"].append(dateRecord)
    return  dietRecordDict

@dairy_app.route("/")
def Values() :
    # 抓userid
    if request.args.get('liff.state') :
        userId = request.args.get('liff.state').split('=')[1]
    else :
        userId = request.args.get('userId') #################
    # userId="U03ff6cfccbc18417cadee840cd0a3261"

    userInfo = mongoConn.mongoSearch(userId=userId, collectionName="UserDatas")
    if userInfo[0]['userName']:
        userId = userInfo[0]['userId']
        target_dict, weight, height, username, activity_level, workout = targetNutritionValue(mongoConn, userId)#, userId="U0c002208c30c59e13b23a19112ed2527")
        nowDay = datetime.now()
        nowDay = nowDay.date()
        ingestNutritionList, _, _ = ingestNutritionValue(mongoConn, nowDay,userId)
        
        remainValue = math.ceil(target_dict["熱量"]) - math.ceil(ingestNutritionList[0])
        proteinRemainValue = math.ceil(target_dict["蛋白質"]) - math.ceil(ingestNutritionList[1])
        totalfatRemainValue = math.ceil(target_dict["脂肪"]) - math.ceil(ingestNutritionList[2])
        carbohydratetRemainValue = math.ceil(target_dict["碳水化合物"]) - math.ceil(ingestNutritionList[3])

        # remainValue = round(target_dict["熱量"] - ingestNutritionList[0], 0)
        # proteinRemainValue = round(target_dict["蛋白質"] - ingestNutritionList[1], 0)
        # totalfatRemainValue = round(target_dict["脂肪"] - ingestNutritionList[2], 0)
        # carbohydratetRemainValue = round(target_dict["碳水化合物"] - ingestNutritionList[3], 0)

        exreList = ["可攝取" if value >= 0 else "過量" for value in [remainValue, proteinRemainValue, totalfatRemainValue, carbohydratetRemainValue]]
        remainValue, PROTEIN, TOTALFAT, CARBOHYDRATE = map(abs, [remainValue, proteinRemainValue, totalfatRemainValue, carbohydratetRemainValue])
        return render_template("recordNutrition.html",
                            app = app,
                            remainValue = int(remainValue),
                            weight = weight,
                            height = height,
                            username = username,
                            activity_level = activity_level, 
                            workout = workout,
                            proteinRemainValue = PROTEIN, #int(),
                            totalfatRemainValue = TOTALFAT,#int(totalfatRemainValue),
                            carbohydratetRemainValue = CARBOHYDRATE,#int(),
                            ingestNutritionList = ingestNutritionList,#[int(x) for x in ingestNutritionList],
                            target_dict = target_dict,#{key: int(value) for key, value in target_dict.items()},
                            exreList = exreList,
                            userId=userId
                            )
    else :
        return render_template("user.html", app=app, userinfo=userinfo, userId=userId)
 
@dairy_app.route("/healthDiary", methods=["POST", "GET"])
def healthDiary():
    userId = request.args.get('userId')
    # userId="U03ff6cfccbc18417cadee840cd0a3261"
    isfriend = request.args.get("isfriend") if request.args.get("isfriend") else "None" ############
    nutritionList = ["熱量", "蛋白質", "脂肪", "碳水化合物", "糖", "鈉"]
    target_dict, _, _, username, activity_level, workout = targetNutritionValue(mongoConn, userId)#, userId=userId)
   
    if not username:
        username = "預設"
    target_dict= [value for key, value in  target_dict.items()]
    if request.method == "GET":
        timedate = datetime.now()
        timedate = timedate.date()  
        ingestNutritionList, rank_dict, dietRecordDict = ingestNutritionValue(mongoConn, timedate, userId)
        return render_template("healthDiary.html", app=app, nutritionList=nutritionList, target_dict=target_dict, ingestNutritionList=ingestNutritionList, rank_dict=rank_dict, dietRecordDict=dietRecordDict, userId=userId, username=username, activity_level=activity_level, workout=workout, isfriend=isfriend)    
    elif request.method == "POST":
        timedate = request.json['time']
        userId = request.json['userId']
        ingestNutritionList, rank_dict, dietRecordDict = ingestNutritionValue(mongoConn, timedate, userId)
        return render_template("healthDiary2.html", app=app, nutritionList=nutritionList, target_dict=target_dict, ingestNutritionList=ingestNutritionList,rank_dict=rank_dict,dietRecordDict=dietRecordDict,userId=userId, username=username, activity_level=activity_level, workout=workout, isfriend=isfriend)    

@dairy_app.route("/userinfo", methods=["POST", "GET"])
def userinfo() : 
    userId = request.args.get('userId')
    # userId="U03ff6cfccbc18417cadee840cd0a3261"
    if request.method == 'GET': 
        userId = request.args.get('userId')
        userinfo=mongoConn.mongoSearch(userId=userId, collectionName="UserDatas")
        return render_template("user.html", app=app, userId=userId, userinfo=userinfo)
    if request.method == 'POST':
        data = request.json  
        try:
            mongoConn.insertBasicData(data)
        except:
            print("insert user basic Datas Error!")
        return "ok"

if __name__ == "__main__":
    app.register_blueprint(dairy_app)
    app.run(debug=True)#, port=3000, host="127.0.0.1")
