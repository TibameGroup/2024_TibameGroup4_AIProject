from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import json
from datetime import datetime, timedelta
import re

with open('./config/config.json', 'r') as file:
    config = json.load(file)
port = int(config['MongoPort'])
host = config['MongoHost']
# host = "mongodb://localhost:27017/"

class Mongo():
    def __init__(self):
        """連接mongoDB的class物件值"""
        try:
            self.conn = MongoClient(host=host, port=port, username=config['MongoUser'], password=config["MongoPassword"])
            # self.conn = MongoClient(host=host, port=port) 
            # 選擇資料庫（如果不存在，將會創建）
            self.db = self.conn[config["MongoDatabase"]]
            # db_names = self.conn.list_database_names()
            # print(db_names)
            # print(self.conn.address)
            print('Mongo Succesful connect!')
        except ConnectionFailure as e:
            print(f"Mongo ConnectionError: {e}")

    def mongoInsertDatas(self, data, listData=False, collectionName="dietRecord"):
        """data: dict()"""
        # 選擇box（如果不存在，將會創建）
        collection = self.db[collectionName]
        # # 更改主鍵為userId
        data["_id"] = data["userId"]
        try:
            result = collection.insert_one(data)
            # 顯示插入的data的ID
            print(f"Inserted {result} in {collectionName}.")
        except:
            print(f"Insert Error! userId = {data['userId']} has exists.")
    
    def mongoSearch(self, userId, listName=None, listMatch=None, collectionName="dietRecord", findAll=False):
        """userId: str()"""
        # 選擇box（如果不存在，將會創建）
        collection = self.db[collectionName]
        
        # 查詢資料
        if findAll:
            result = collection.find()
            records = []
            # # 顯示查詢結果
            for res in result:
                records.append(res)
            return records
        else:
            # 建立查詢條件
            query = {"userId": userId}
            if listMatch:
                query[listName] = {
                    "$elemMatch": listMatch
                }
                result = collection.find_one(query, {f"{listName}.$": 1})
                # 投影操作符，表示只返回 prodList 数组中的第一个元素（$ 是一个占位符，表示匹配数组的第一个元素）。1 表示要包含这个字段。
                # 輸出為 Dict
                return result
            else:
                result = collection.find(query)
                records = []
                # # 顯示查詢結果
                for res in result:
                    records.append(res)
                return records
    
    def deleteDatas(self, userId, collectionName="dietRecord", all=False):
        """刪除使用者的資料"""
        collection = self.db[collectionName]
        if all:
            result = collection.delete_many({})
            if result.deleted_count > 0:
                print(f'Mongo Delete All data: {result.deleted_count} Successful!')
            else:
                print(f'Mongo Delete All Error!')
        else:
            # 定義刪除的條件
            criteria = {
                "userId": userId
            }
            result = collection.delete_one(criteria)
            if result.deleted_count > 0:
                print(f'Mongo Delete userId = {userId}, data counts = {result.deleted_count} data Successful!')
            else:
                print(f"Mongo Delete userId = {userId} Error!")
    
    def updateDatas(self, userId, data={}, sortKey=1, listName=None, collectionName="dietRecord"):
        """更新使用者的資料"""
        collection = self.db[collectionName]
        target = {"userId": userId}
        if listName:
            result = collection.update_one(target, {"$push": data}) # push 可以用於append List資料
            collection.update_one(target, {"$push": {listName: {"$each": [], "$sort": sortKey}}}) # 排序資料
        else:
            result = collection.update_one(target, {"$set": data})
        # if result.modified_count > 0:
        #     print(f'Mongo Update user={userId}, update counts={result.modified_count} data Successful!')
        if result.modified_count <= 0:
            print(f"Mongo Update user={userId} data, counts = 0")

    def defaultStatus(self, userId, collectionName="UserDatas"):
        """初始化，添加使用者資訊 status=None, barcodeValue=None, HeatCalInfo=None"""
        # 添加使用者資訊
        data = {"userId": userId, 
                "MenuStage": {"Status": None, 
                              "BarcodeValue": None, 
                              'HeatCalInfo': None},
                "friendShip": None,
                "Friends": [],
                "userName": None,
                "userGender": None,
                "userBirthYear": None,
                "userHeight": None,
                "activityLevel": None,
                "highProteinDiet": None}
        self.mongoInsertDatas(data=data, collectionName=collectionName)

    def insertBasicData(self, userData, collectionName="UserDatas"):
        """初始化，搜尋使用者的紀錄。若無此使用者則新增"""
        # userDatas = self.mongoSearch(userId=userData['userId'], collectionName=collectionName)
        # 更新原有使用者資訊
        data = {"userName": userData['userName'],
                "userGender": userData['userGender'],
                "userBirthYear": userData['userBirthYear'],
                "userHeight": userData['userHeight'],
                "userWeight": userData['userWeight'],
                "activityLevel": userData['activityLevel'],
                "highProteinDiet": userData['highProteinDiet']}
        self.updateDatas(userId=userData['userId'], collectionName=collectionName, data=data)

    def insertDietData(self, userId, prod={}, collectionName="dietRecord"):
        """初始化，搜尋使用者的紀錄。若無此使用者則新增List"""
        userDatas = self.mongoSearch(userId=userId, collectionName=collectionName)
        if userDatas:
            # 更新原有使用者資訊
            # prodList 添加
            self.updateDatas(userId=userId, data={"prodList": prod}, sortKey={"DATETIME": 1}, listName="prodList", collectionName=collectionName)

            # dayRecords
            matchingRecord = self.mongoSearch(userId=userId, listName="dayRecords", listMatch={"DATETIME": prod["DATETIME"].split("T")[0]}, collectionName="dietRecord")
            # dayRecords = userDatas[0]['dayRecords']
            # matchingRecord = [record for record in dayRecords if record["DATETIME"] == str(prod['DATETIME']).split("T")[0]]
            if matchingRecord: # 如果已有紀錄
                AllRecords = self.mongoSearch(userId=userId, collectionName="dietRecord")
                matchingRecord = matchingRecord['dayRecords'][0]
                listIndex = AllRecords[0]["dayRecords"].index(matchingRecord)
                matchingRecord["HEATS"] = str(round((float(matchingRecord["HEATS"]) + float(prod['HEAT'])*float(prod['UNIT'])), 1))
                matchingRecord["PROTEINS"] = str(round((float(matchingRecord['PROTEINS']) + float(prod['PROTEIN'])*float(prod['UNIT'])), 1))
                matchingRecord["TOTALFATS"] = str(round((float(matchingRecord['TOTALFATS']) + float(prod['TOTALFAT'])*float(prod['UNIT'])), 1))
                matchingRecord["CARBOHYDRATES"] = str(round((float(matchingRecord['CARBOHYDRATES']) + float(prod['CARBOHYDRATE'])*float(prod['UNIT'])), 1))
                matchingRecord["SUGARS"] = str(round((float(matchingRecord['SUGARS']) + float(prod['SUGAR'])*float(prod['UNIT'])), 1))
                matchingRecord["SODIUMS"] = str(round((float(matchingRecord['SODIUMS']) + float(prod['SODIUM'])*float(prod['UNIT'])), 1))
                data = {f"dayRecords.{str(listIndex)}": matchingRecord}
                self.updateDatas(userId=userId, data=data, collectionName="dietRecord")
            else:
                dayRecords = {
                    "DATETIME": str(prod['DATETIME']).split("T")[0],
                    "HEATS": str(round(float(prod['HEAT'])*float(prod['UNIT']), 1)),
                    "PROTEINS": str(round(float(prod['PROTEIN'])*float(prod['UNIT']), 1)),
                    "TOTALFATS": str(round(float(prod['TOTALFAT'])*float(prod['UNIT']), 1)),
                    "CARBOHYDRATES": str(round(float(prod['CARBOHYDRATE'])*float(prod['UNIT']), 1)),
                    "SUGARS": str(round(float(prod['SUGAR'])*float(prod['UNIT']), 1)),
                    "SODIUMS": str(round(float(prod['SODIUM'])*float(prod['UNIT']), 1))
                }
                # dayRecords = sorted(dayRecords, key=lambda x: x['DATETIME']) # 依照時間排序 
                data = {"dayRecords": dayRecords}
                self.updateDatas(userId=userId, data=data, sortKey={"DATETIME": 1}, listName="dayRecords", collectionName="dietRecord")
        else:
            # 添加使用者資訊
            data = {"userId": userId, 
                    "prodList": [prod],
                    "dayRecords": [{
                        "DATETIME": str(prod['DATETIME']).split("T")[0],
                        "HEATS": str(round(float(prod['HEAT'])*float(prod['UNIT']), 1)),
                        "PROTEINS": str(round(float(prod['PROTEIN'])*float(prod['UNIT']), 1)),
                        "TOTALFATS": str(round(float(prod['TOTALFAT'])*float(prod['UNIT']), 1)),
                        "CARBOHYDRATES": str(round(float(prod['CARBOHYDRATE'])*float(prod['UNIT']), 1)),
                        "SUGARS": str(round(float(prod['SUGAR'])*float(prod['UNIT']), 1)),
                        "SODIUMS": str(round(float(prod['SODIUM'])*float(prod['UNIT']), 1))
                        }]
                    }
            self.mongoInsertDatas(data=data, collectionName=collectionName)
    def removeProd(self, userId, prod, collectionName="dietRecord"):
        collection = self.db[collectionName]
        # 刪除ProdList
        # 定義條件
        criteria = {
            "userId": userId
        }
        # 使用 $pull 操作符來移除符合條件的元素
        result = collection.update_one(criteria, {"$pull": {"prodList": prod}})
        if result.modified_count <= 0:
            print(f"Mongo Update user={userId} data, counts = 0")
        # 刪除dayRecords
        matchingRecord = self.mongoSearch(userId=userId, listName="dayRecords", listMatch={"DATETIME": prod["DATETIME"].split("T")[0]}, collectionName="dietRecord")
        if matchingRecord: # 如果已有紀錄
                matchingRecord = matchingRecord['dayRecords'][0]
                # 找出該記錄的 index ，以便後續DayRecords加減操作
                AllRecords = self.mongoSearch(userId=userId, collectionName="dietRecord")
                listIndex = AllRecords[0]["dayRecords"].index(matchingRecord) 
                # 檢查 ProdList 當天是否還有資料
                afterRecords = self.mongoSearch(userId=userId, listName="prodList", listMatch = {"DATETIME": {"$regex": prod["DATETIME"].split("T")[0]}}, collectionName="dietRecord")
                if not afterRecords: # 若全部刪除當天資料(避免刪除到最後剩小數點誤差)
                    result = collection.update_one(criteria, {"$pull": {"dayRecords": {"DATETIME": prod["DATETIME"].split("T")[0]}}})
                    if result.modified_count <= 0:
                        print(f"Mongo Update user={userId} data, counts = 0")
                else:
                    matchingRecord["HEATS"] = str(round((float(matchingRecord["HEATS"]) - float(prod['HEAT'])*float(prod['UNIT'])), 1))
                    matchingRecord["PROTEINS"] = str(round((float(matchingRecord['PROTEINS']) - float(prod['PROTEIN'])*float(prod['UNIT'])), 1))
                    matchingRecord["TOTALFATS"] = str(round((float(matchingRecord['TOTALFATS']) - float(prod['TOTALFAT'])*float(prod['UNIT'])), 1))
                    matchingRecord["CARBOHYDRATES"] = str(round((float(matchingRecord['CARBOHYDRATES']) - float(prod['CARBOHYDRATE'])*float(prod['UNIT'])), 1))
                    matchingRecord["SUGARS"] = str(round((float(matchingRecord['SUGARS']) - float(prod['SUGAR'])*float(prod['UNIT'])), 1))
                    matchingRecord["SODIUMS"] = str(round((float(matchingRecord['SODIUMS']) - float(prod['SODIUM'])*float(prod['UNIT'])), 1))
                    data = {f"dayRecords.{str(listIndex)}": matchingRecord}
                    self.updateDatas(userId=userId, data=data, collectionName="dietRecord")

if __name__ == "__main__":
    # 使用class連接
    conn = Mongo()

    # # 不使用class連接
    # conn = MongoClient(host=host, port=port, username=config['MongoUser'], password=config["MongoPassword"])
    # db = conn[config["MongoDatabase"]]
    # collection = db["dietRecord"]

    # 搜尋使用者資料
    # userDatas = conn.mongoSearch(userId="U0c002208c30c59e13b23a19112ed2527", collectionName="UserDatas") # 使用者狀態
    # if userDatas:
    #     print("yes")
    # else:
    #     print("no")

    # userData = {'userId': 'U0c002208c30c59e13b23a19112ed2527', 'userGender': 'female', 'userBirthYear': '1998', 'userHeight': '188', 'userWeight': '50', 'activityLevel': 'sedentary', 'highProteinDiet': 'no'}
    # conn.insertBasicData(userData)
    # res = conn.mongoSearch(userId='U0c002208c30c59e13b23a19112ed2527', collectionName="UserDatas")
    # print(res)

    # # 加入測試資料
    # data = {"userId": "2", 
    #         "MenuStage": {"Status": "insertTest",
    #             "BarcodeValue": "123"}}
    # conn.mongoInsertDatas(data=data, collectionName="dietRecord")
    
    # 刪除資料
    # conn.deleteDatas(userId="U836e0e635ef0c3665af41408cec37a9e", collectionName="UserDatas")
    # conn.removeProd(userId="U0c002208c30c59e13b23a19112ed2527", prod={"PRODNAME": "萬丹巧克力牛奶", "DATETIME": "2024-02-19T20:01"}, collectionName="dietRecord")
    # result = collection.update_one({"userId": "U0c002208c30c59e13b23a19112ed2527"}, {"$pull": {"dayRecords": {'DATETIME': '2024-02-21'}}})

    # # 更新資料
    # data = {'MenuStage': {'Status': None, 'BarcodeValue': None}}
    # conn.updateDatas(userId="2", collectionName="dietRecord", data=data)
    # conn.updateDatas(userId='U0c002208c30c59e13b23a19112ed2527', data={"Friends": "測試"}, listName="Friends", collectionName="UserDatas")

    # 搜尋資料
    # userDatas = conn.mongoSearch(userId="U0c002208c30c59e13b23a19112ed2527", collectionName="dietRecord")#[0]['Friends']#, findAll=True)
    # print(userDatas)
    # if userDatas:
    #     for userData in userDatas:
    #         print(userData)
    # else:
    #     print('No data')
    # print(userDatas[0]['MenuStage']['BarcodeValue'])

    # records = conn.mongoSearch(userId="U0c002208c30c59e13b23a19112ed2527", collectionName="dietRecord", findAll=True)
    # print(records)

    # records = conn.mongoSearch(userId="U0c002208c30c59e13b23a19112ed2527", listName="prodList", listMatch={'PRODNAME': '麥香紅茶TP375', "DATETIME": "2024-02-22T14:42"}, collectionName="dietRecord")
    # print(records['prodList'][0])

    # 模糊查詢List，若無回傳None
    # records = conn.mongoSearch(userId="U0c002208c30c59e13b23a19112ed2527", listName="prodList", listMatch = {"DATETIME": {"$regex": '2024-02-24'}}, collectionName="dietRecord")
    # print(records)
    # records2 = conn.mongoSearch(userId="U0c002208c30c59e13b23a19112ed2527", collectionName="dietRecord")
    # print(records2)
    
    # userId = "U0c002208c30c59e13b23a19112ed2527"
    # prod = {'PRODNAME': '測試', 'LEVEL': 'D', 'HEAT': '405.0', 'PROTEIN': '5.9', 'TOTALFAT': '25.9', 'CARBOHYDRATE': '37.0', 'SUGAR': '9.4', 'SODIUM': '265.0', 'DATETIME': '2024-02-22T02:00', 'UNIT': '2.0'}
    # AllRecords = conn.mongoSearch(userId=userId, collectionName="dietRecord")
    # matchingRecord = conn.mongoSearch(userId=userId, listName="dayRecords", listMatch={"DATETIME": prod["DATETIME"].split("T")[0]}, collectionName="dietRecord")
    # matchingRecord = matchingRecord['dayRecords'][0]
    # # print(matchingRecord)
    # listIndex = AllRecords[0]["dayRecords"].index(matchingRecord)
    # # print(type(listIndex))
    # matchingRecord["HEATS"] = str(round((float(matchingRecord["HEATS"]) + float(prod['HEAT'])*float(prod['UNIT'])), 1))
    # matchingRecord["PROTEINS"] = str(round((float(matchingRecord['PROTEINS']) + float(prod['PROTEIN'])*float(prod['UNIT'])), 1))
    # matchingRecord["TOTALFATS"] = str(round((float(matchingRecord['TOTALFATS']) + float(prod['TOTALFAT'])*float(prod['UNIT'])), 1))
    # matchingRecord["CARBOHYDRATES"] = str(round((float(matchingRecord['CARBOHYDRATES']) + float(prod['CARBOHYDRATE'])*float(prod['UNIT'])), 1))
    # matchingRecord["SUGARS"] = str(round((float(matchingRecord['SUGARS']) + float(prod['SUGAR'])*float(prod['UNIT'])), 1))
    # matchingRecord["SODIUMS"] = str(round((float(matchingRecord['SODIUMS']) + float(prod['SODIUM'])*float(prod['UNIT'])), 1))
    # print(matchingRecord)
    # data = {f"dayRecords.{str(listIndex)}": matchingRecord}
    # print(data)
    # conn.updateDatas(userId=userId, data=data, collectionName="dietRecord")