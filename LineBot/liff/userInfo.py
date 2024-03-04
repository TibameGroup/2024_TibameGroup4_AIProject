from flask import render_template, Flask, Blueprint, request
import json
from dbs.mongo import Mongo
# from mongo import mongoInsertRecord

mongoConn = Mongo()
Users_app = Blueprint('Users_app', __name__, template_folder='templates')
with open('./config/config.json', 'r') as file:
    config = json.load(file)
diaryLiffID = config["diaryLiffID"]

@Users_app.route("/user", methods=['POST', 'GET']) 
def User_index() :
    if request.method == 'POST':
        data = request.json  
        try:
            mongoConn.insertBasicData(data)
        except:
            print("insert user basic Datas Error!")
        return "OK"
    return render_template("user.html", diaryLiffID=diaryLiffID)

if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(Users_app)
    app.run(debug=True)