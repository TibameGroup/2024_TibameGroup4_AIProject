from flask import render_template, Blueprint, Flask, request, jsonify
import json
from dbs.mongo import Mongo
from modules.LineMessageHandle import Handle
from modules.LineMessage import Flex, textMessage, addFriendConfirmation, QuickReply

with open('./config/config.json', 'r') as file:
    config = json.load(file)
ChannelAccessToken = config['ChannelAccessToken']
ChannelSecret = config['ChannelSecret']
# 處理訊息事件
handle = Handle(ChannelSecret, ChannelAccessToken)
replyMessage = handle.replyMessage
quickReply = QuickReply()

friendLiffID = config["friendLiffID"]
friend_app = Blueprint('friend_app', __name__, template_folder='templates')

mongoConn = Mongo()

@friend_app.route('/QRCode', methods=['POST', 'GET'])
def friend_liff():
    if request.method == 'POST':
        try:
            # 如果是 POST 請求，獲取從前端傳來的 JSON 數據
            data = request.get_json()
            # 在這裡處理接收到的 JSON 數據
            return handle_received_data(data)
            
        except Exception as e:
            print(f'Error handling POST request: {e}')
            return {'error': 'Internal Server Error'}, 500  # 返回 500 錯誤
    return render_template("friend.html", friendLiffID=friendLiffID)

def handle_received_data(data):
    # 在這裡處理接收到的 JSON 數據
    # print('Handling received data:', data)
    friendId, myId, myName = data['friendId'], data['myId'], data["myName"]
    checkQRcode = mongoConn.mongoSearch(userId=friendId, collectionName="UserDatas")
    friendList = mongoConn.mongoSearch(userId=myId, collectionName="UserDatas")[0]['Friends']
    if len(checkQRcode) > 0:
        if friendId in friendList:
            return jsonify({'message': 'Already friends!'})
        else:
            mongoConn.updateDatas(myId, collectionName="UserDatas", data={"friendShip": friendId})
            mongoConn.updateDatas(friendId, collectionName="UserDatas", data={"friendShip": myId})
            handle.pushMessage(friendId, [addFriendConfirmation(myName)])
            return jsonify({'message': 'Success'})
    else:
        print("User not in Mongo!")
        return jsonify({'message': 'User not in Mongo!'})

if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(friend_app)
    app.run(debug=True)
 


