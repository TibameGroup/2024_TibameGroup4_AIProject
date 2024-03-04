import json
from datetime import datetime, timedelta, timezone

# 當前日期與時間
# now = datetime.now().strftime('%Y-%m-%dt%H:%M')
time_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
time_tw = time_utc.astimezone(timezone(timedelta(hours=8)))# + timedelta(minutes=12)
now = time_tw.strftime('%Y-%m-%dt%H:%M')

# 只能紀錄4天
initialTime = (time_tw - timedelta(days=4)).strftime('%Y-%m-%dt%H:%M')
endTime = (time_tw + timedelta(hours=6)).strftime('%Y-%m-%dt%H:%M')
with open('./config/config.json', 'r') as file:
    config = json.load(file)
YoloLiffUrl = config["YoloLiffUrl"]

def textMessage(text):
    # https://developers.line.biz/en/reference/messaging-api/#text-message
    # emoji: https://developers.line.biz/en/docs/messaging-api/emoji-list/#line-emoji-definitions
    messages = {"type": "text", 
                "text": text
                }
    return messages
def addFriendConfirmation(friendName):
    # 確認訊息的內容
    messages = {
        "type": "template",
        "altText": "確認加好友",
        "template": {
            "type": "confirm",
            "text": f"是否要成為{friendName}好友?", #####
            "actions": [
                {
                    "type": "message",
                    "label": "接受",
                    "text": "@接受"
                },
                {
                    "type": "message",
                    "label": "拒絕",
                    "text": "@拒絕"
                }
            ]
        }
    }
    return messages
    
class QuickReply:
    def friendDiary(self, text, friends, mongoConn): # 好友日記
        messages = {
            "type": "text",  # 1
            "text": text,
            "quickReply": {  # 2
                "items": [
                ]
            }
        }
        for friendId in friends:
            # print(messages["quickReply"]["items"])
            friendDatas = mongoConn.mongoSearch(userId=friendId, collectionName="UserDatas") 
            # print(friendDatas)
            if len(friendDatas) > 0:
                friendName = friendDatas[0]["userName"] if friendDatas[0]["userName"] else "預設" # 朋友名稱
                messages["quickReply"]["items"].append(
                    {
                        "type": "action",  
                        "action": {
                            "type": "uri",
                            "label": friendName,
                            "uri": f"{config['EndPoint']}/diary/healthDiary?userId={friendId}&isfriend=true"
                            # "uri": f"{config['EndPoint']}/diary?userId={friendId}"
                        }
                    }
                )
        return messages
    def YoloensureQuickReply(self, text, userId, repeat=False): # Yolo抓取營養網站導引
        data_noinsertNutri = json.dumps({'action':'noinsertNutri'}) # 將dict轉為json
        messages = {
            "type": "text",  # 1
            "text": text,
            "quickReply": {  # 2
                "items": [
                    {
                        "type": "action",  
                        "action": {
                            "type": "uri",
                            "label": "開始",
                            "uri": f"{YoloLiffUrl}/?userId={userId}"
                        }
                    },
                    {
                        "type": "action",
                        "action": {
                            "type": "postback",
                            "label": "取消",
                            "data": data_noinsertNutri
                        }
                    }
                ]
            }
        }
        
        return messages
    def diaryQuickReply(self, text, userId): # 飲食分析
        messages = {
            "type": "text",  # 1
            "text": text,
            "quickReply": {  # 2
                "items": [
                    {
                        "type": "action",  
                        "action": {
                            "type": "uri",
                            "label": "前往",
                            "uri": f"{config['EndPoint']}/diary?userId={userId}"
                        }
                    }
                ]
            }
        }
        return messages
    def renameQuickReply(self, text):
        data_rename = json.dumps({'action':'rename'}) # 將dict轉為json
        data_norename = json.dumps({'action':'norename'})
        messages = {
            "type": "text",  # 1
            "text": text,
            "quickReply": {  # 2
                "items": [
                    {
                        "type": "action",  
                        "action": {
                            "type": "postback",
                            "label": "填寫",
                            "data": data_rename
                        }
                    },
                    {
                        "type": "action",
                        "action": {
                            "type": "postback",
                            "label": "否",
                            "data": data_norename
                        }
                    }
                ]
            }
        }
        return messages
    def cameraQuickReply(self):
        # https://developers.line.biz/en/docs/messaging-api/using-quick-reply/#set-quick-reply-buttons
        messages = {
            "type": "text",  # 1
            "text": "請選擇圖片來源",
            "quickReply": {  # 2
                "items": [
                    {
                        "type": "action",  # 3
                        "imageUrl": "https://i.imgur.com/m8DAjpb.png",
                        "action": {
                            "type": "camera",
                            "label": "相機",
                        }
                    },
                    {
                        "type": "action",
                        "imageUrl": "https://i.imgur.com/TG0eaUV.png",
                        "action": {
                            "type": "cameraRoll",
                            "label": "相簿",
                        }
                    }
                ]
            }
        }
        return messages
    def addProdInfos(self, barcodeValue=None, testPerson=False): # 條碼 -> 新增產品資料
        data_insertProd = json.dumps({'action':'insertProd'}) # 將dict轉為json
        data_noInsertProd = json.dumps({'action':'noInsertProd'}) 
        data_insertBarcode = json.dumps({'action':'insertBarcode', 'barcodeValue': barcodeValue})
        # https://developers.line.biz/en/docs/messaging-api/using-quick-reply/#set-quick-reply-buttons
        messages = {
            "type": "text",  # 1
            "text": "尚無該商品的資料!\n請問是否新增該產品資料?",
            "quickReply": {  # 2
                "items": [
                    {
                        "type": "action",  # 3
                        "action": {
                            "type": "postback",
                            "label": "新增產品熱量資料",
                            "data": data_insertProd
                        }
                    },
                    {
                        "type": "action",
                        "action": {
                            "type": "postback",
                            "label": "否",
                            "data": data_noInsertProd
                        }
                    }
                ]
            }
        }
        if testPerson:
            items = {
                        "type": "action",  # 3
                        "action": {
                            "type": "postback",
                            "label": "新增條碼資料",
                            "data": data_insertBarcode
                        }
                    }
            messages['quickReply']['items'].append(items)
            messages['text'] += "\n\n測試人員此處請按*新增條碼資料*。"
        return messages
    # 新增飲食紀錄，選擇時間
    def sizeItem(self, prod): 
        """Datetime picker action: https://developers.line.biz/en/reference/messaging-api/#datetime-picker-action"""
        data_dietInfo_0_5 = json.dumps({"action":"dietInfo", "prod": prod, "UNIT": "0.5"})
        data_dietInfo_1_0 = json.dumps({"action":"dietInfo", "prod": prod, "UNIT": "1.0"})
        data_dietInfo_1_5 = json.dumps({"action":"dietInfo", "prod": prod, "UNIT": "1.5"})
        data_dietInfo_2_0 = json.dumps({"action":"dietInfo", "prod": prod, "UNIT": "2.0"})
        data_dietInfo_2_5 = json.dumps({"action":"dietInfo", "prod": prod, "UNIT": "2.5"})
        data_dietInfo_3_0 = json.dumps({"action":"dietInfo", "prod": prod, "UNIT": "3.0"})
        data = [data_dietInfo_0_5, data_dietInfo_1_0, data_dietInfo_1_5, data_dietInfo_2_0, data_dietInfo_2_5, data_dietInfo_3_0]
        items = list()
        nums = [float(i) / 2.0 for i in range(1, 7, 1)]
        for i in range(len(nums)):
            items.append({
                        "type": "action",
                        "imageUrl": "https://i.imgur.com/hZhvTUU.png",
                        "action": {
                            "type": "datetimepicker",
                            "label": f"{nums[i]}份",
                            "data": data[i],
                            "mode": "datetime",
                            "initial": now,
                            "max": endTime,
                            "min": initialTime
                            },
                        })
        return items

    def addDietInfo(self, prod):
        # https://developers.line.biz/en/docs/messaging-api/using-quick-reply/#set-quick-reply-buttons
        messages = {
            "type": "text",  # 1
            "text": "請選擇食物份量",
            "quickReply": {  # 2
                "items":  
                    self.sizeItem(prod)
            }
        }
        return messages

class Flex():
    # https://developers.line.biz/en/reference/messaging-api/#flex-message
    # 設計 Flex: https://developers.line.biz/flex-simulator/?status=success
    # Postback Action: https://developers.line.biz/en/docs/messaging-api/actions/#postback-action
    def __init__(self) -> None:
        self.messages = {"type": "flex",
                         "altText": "menu"}
    # 產品查詢頁面
    def MainSearchProd(self):
        data_nameSearch = json.dumps({'action':'nameSearch'}) # 將dict轉為json
        data_barcodeSearch = json.dumps({'action':'barcodeSearch'}) # 將dict轉為json
        data_imageSearch = json.dumps({'action':'imageSearch'})

        self.messages["contents"] = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "size": "full",
                "aspectMode": "cover",
                "action": {
                    "type": "uri",
                    "uri": "http://linecorp.com/"
                },
                "url": "https://i.imgur.com/bQ48OKe.jpg",
                "aspectRatio": "5:3"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "separator",
                        "color": "#FFFFFF",
                        "margin": "xl"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "名稱查詢",
                            "data": data_nameSearch
                        },
                        "position": "relative",
                        "style": "secondary",
                        "offsetTop": "none",
                        "offsetBottom": "none",
                        "offsetStart": "none",
                        "offsetEnd": "none",
                        "margin": "none",
                        "height": "sm"
                    },
                    {
                        "type": "separator",
                        "color": "#FFFFFF",
                        "margin": "md"
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "height": "sm",
                        "action": {
                            "type": "postback",
                            "label": "條碼查詢",
                            "data": data_barcodeSearch
                        },
                        "position": "relative"
                    },
                    {
                        "type": "separator",
                        "color": "#FFFFFF",
                        "margin": "md"
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "height": "sm",
                        "action": {
                            "type": "postback",
                            "label": "圖片查詢",
                            "data": data_imageSearch
                        },
                        "position": "relative"
                    },
                    {
                        "type": "separator",
                        "color": "#FFFFFF",
                        "margin": "xl"
                    }
                ],
                "flex": 0
            }
        }
        return self.messages
    # 產品詳細資訊
    def detailInfo(self, prod):
        data_dietRecord = json.dumps({"prod": {"PRODNAME":prod["PRODNAME"], "LEVEL": prod['LEVEL'], "HEAT": prod["HEAT"], "PROTEIN": prod["PROTEIN"], "TOTALFAT": prod["TOTALFAT"], "CARBOHYDRATE": prod["CARBOHYDRATE"], "SUGAR": prod["SUGAR"], "SODIUM": prod["SODIUM"]}, 'action':'dietRecord' })
        prod['LEVEL'] = prod['LEVEL'] if prod['LEVEL'] else " "
        prod['G_ML_NUM'] = prod['G_ML_NUM'] if prod['G_ML_NUM'] else " "
        prod['SATFAT'] = prod['SATFAT'] if prod['SATFAT'] else "-"
        prod['TRANSFAT'] = prod['TRANSFAT'] if prod['TRANSFAT'] else "-"
        for key, value in prod.items():
            if value is None:
                prod[key] = "0"
        
        self.messages["contents"] = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "營養成分表",
                        "weight": "bold",
                        "color": "#1DB446",
                        "size": "sm"
                    },
                    {
                        "type": "text",
                        "text": prod["PRODNAME"],
                        "weight": "bold",
                        "size": "xl",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": f"每份規格{prod['G_ML_NUM']}{prod['G_ML']}",
                        "size": "xs",
                        "color": "#aaaaaa",
                        "wrap": True,
                        "offsetTop": "md",
                        "margin": "xs"
                    },
                    {
                        "type": "text",
                        "text": f"本包裝含{prod['UNIT']}份",
                        "size": "xs",
                        "color": "#aaaaaa",
                        "wrap": True,
                        "offsetTop": "md",
                        "margin": "xs"
                    },
                    {
                        "type": "text",
                        "text": f"分級{prod['LEVEL']}",
                        "size": "xs",
                        "color": "#aaaaaa",
                        "wrap": True,
                        "offsetTop": "md",
                        "margin": "xs"
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "xs",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "margin": "md",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "熱量",
                                                "align": "start",
                                                "size": "md"
                                            }
                                        ],
                                        "width": "85px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": prod['HEAT'],
                                                "align": "end",
                                                "size": "md"
                                            }
                                        ],
                                        "width": "130px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "大卡",
                                                "size": "md",
                                                "align": "end"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "margin": "md",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "蛋白質",
                                                "align": "start",
                                                "size": "md"
                                            }
                                        ],
                                        "width": "85px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": prod['PROTEIN'],
                                                "align": "end",
                                                "size": "md"
                                            }
                                        ],
                                        "width": "130px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "公克",
                                                "size": "md",
                                                "align": "end"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "margin": "md",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "脂肪",
                                                "align": "start",
                                                "size": "md"
                                            }
                                        ],
                                        "width": "85px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": prod['TOTALFAT'],
                                                "align": "end",
                                                "size": "md"
                                            }
                                        ],
                                        "width": "130px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "公克",
                                                "size": "md",
                                                "align": "end"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "margin": "md",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [],
                                        "width": "15px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "飽和脂肪",
                                                "align": "start",
                                                "size": "md"
                                            }
                                        ],
                                        "width": "85px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": prod['SATFAT'],
                                                "align": "end",
                                                "size": "md"
                                            }
                                        ],
                                        "width": "115px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "公克",
                                                "size": "md",
                                                "align": "end"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "margin": "md",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [],
                                        "width": "15px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "反式脂肪",
                                                "align": "start",
                                                "size": "md"
                                            }
                                        ],
                                        "width": "85px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": prod['TRANSFAT'],
                                                "align": "end",
                                                "size": "md"
                                            }
                                        ],
                                        "width": "115px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "公克",
                                                "size": "md",
                                                "align": "end"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "margin": "md",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "碳水化合物",
                                                "align": "start",
                                                "size": "md"
                                            }
                                        ],
                                        "width": "85px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": prod['CARBOHYDRATE'],
                                                "align": "end",
                                                "size": "md"
                                            }
                                        ],
                                        "width": "130px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "公克",
                                                "size": "md",
                                                "align": "end"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "margin": "md",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [],
                                        "width": "15px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "糖",
                                                "align": "start",
                                                "size": "md"
                                            }
                                        ],
                                        "width": "85px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": prod['SUGAR'],
                                                "align": "end",
                                                "size": "md"
                                            }
                                        ],
                                        "width": "115px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "公克",
                                                "size": "md",
                                                "align": "end"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "margin": "md",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "鈉",
                                                "align": "start",
                                                "size": "md"
                                            }
                                        ],
                                        "width": "85px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": prod['SODIUM'],
                                                "align": "end",
                                                "size": "md"
                                            }
                                        ],
                                        "width": "130px"
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "毫克",
                                                "size": "md",
                                                "align": "end"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": []
                            }
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": "#FFFFFF"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "紀錄飲食",
                            "data": data_dietRecord,
                        }
                        ,
                        "margin": "sm",
                        "height": "sm",
                        "style": "secondary"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": []
                    }
                ]
            },
            "styles": {
                "footer": {
                    "separator": True
                }
            }
        }
        return self.messages
    
    # 產品簡短頁面
    def briefInfo(self, prod):
        prod['URL'] = "https://foodsafety.family.com.tw/product_img/" + prod['URL'] if prod['URL'] else 'https://i.imgur.com/eMClSTJ.jpeg'
        for key, value in prod.items():
            if value is None:
                prod[key] = "0"

        data_detailInfo = json.dumps({'CMNO':prod['CMNO'], 'action':'detailInfo'})
        data_dietRecordBrief = json.dumps({'CMNO':prod['CMNO'], 'action':'dietRecordBrief'})
        bubble = {
                    "type": "bubble",
                    "size": "hecto",
                    "header": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": []
                    },
                    "hero": {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "image",
                                "url": prod['URL'],
                                "margin": "none",
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": prod['PRODNAME'],
                                "weight": "bold",
                                "gravity": "center",
                                "wrap": True,
                                "align": "start",
                                "size": "lg",
                                "margin": "none",
                                "offsetEnd": "md"
                            }
                            ]
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "separator",
                                "margin": "md",
                                "color": "#FFFFFF"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": "總熱量：",
                                        "size": "md",
                                        "color": "#111111"
                                    }
                                    ],
                                    "width": "80px"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": str(round(float(prod['HEAT'])*float(prod['UNIT']), 1)),
                                        "size": "md",
                                        "color": "#111111",
                                        "align": "end"
                                    }
                                    ],
                                    "width": "90px"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": "大卡",
                                        "align": "center",
                                        "size": "md"
                                    }
                                    ]
                                }
                                ]
                            },
                            {
                                "type": "separator",
                                "margin": "md",
                                "color": "#FFFFFF"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": "本包裝：",
                                        "size": "md",
                                        "color": "#111111"
                                    }
                                    ],
                                    "width": "80px"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": f"含{prod['UNIT']}份",
                                        "size": "md",
                                        "color": "#111111",
                                        "align": "end"
                                    }
                                    ],
                                    "width": "125px"
                                }
                                ]
                            },
                            {
                                "type": "separator",
                                "margin": "md",
                                "color": "#FFFFFF"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": "總共：",
                                        "size": "md",
                                        "color": "#111111"
                                    }
                                    ],
                                    "width": "80px"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": str(round(float(prod['G_ML_NUM'])*float(prod['UNIT']), 1)),
                                        "size": "md",
                                        "color": "#111111",
                                        "align": "end"
                                    }
                                    ],
                                    "width": "90px"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": prod['G_ML'],
                                        "align": "center",
                                        "size": "md"
                                    }
                                    ]
                                }
                                ]
                            },
                            {
                                "type": "separator",
                                "margin": "md",
                                "color": "#FFFFFF"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": "分級：",
                                        "size": "md",
                                        "color": "#111111"
                                    }
                                    ],
                                    "width": "80px"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": prod['LEVEL'],
                                        "size": "md",
                                        "color": "#111111",
                                        "align": "end"
                                    }
                                    ],
                                    "width": "125px"
                                }
                                ]
                            },
                            {
                                "type": "separator",
                                "margin": "md",
                                "color": "#FFFFFF"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "postback",
                                    "label": "紀錄飲食",
                                    "data": data_dietRecordBrief
                                },
                                "margin": "sm",
                                "height": "sm",
                                "style": "secondary"
                            },
                            {
                                "type": "separator",
                                "margin": "md",
                                "color": "#FFFFFF"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "postback",
                                    "label": "查詢營養表",
                                    "data": data_detailInfo
                                },
                                "margin": "sm",
                                "height": "sm",
                                "style": "secondary"
                            }
                        ]
                    }
                    }
        return bubble 
    
    def BriefInfos(self, prodList, moreProd=False, iter=0, searchName=None):
        briefInfoList = []
        for i in range(len(prodList)):
            briefInfoList.append(
                #  [key]:[value]，若[value]為None時，使用預設值 
                self.briefInfo(prod=prodList[i])
            )
        self.messages["contents"] = {
            "type": "carousel",
            "contents": briefInfoList
            }
        if moreProd:
            data_moreProd = json.dumps({"action":"moreProd", "iter": iter, "searchName": searchName})
            self.messages["quickReply"] = {  # 2
                "items": [
                    {
                        "type": "action",  # 3
                        "action": {
                            "type": "postback",
                            "label": "更多商品",
                            "data": data_moreProd
                        }
                    }
                    ]
                }
            
        return self.messages

    # 好友添加
    def friendAdd(self, QRCodeUrl, scanUrl):
        self.messages["contents"] = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": "添加好友",
                        "weight": "bold",
                        "size": "sm",
                        "color": "#1DB446"
                    },
                    {
                        "type": "text",
                        "text": "請好友掃描此條碼，\n即可互相添加為好友。",
                        "color": "#aaaaaa",
                        "margin": "md",
                        "size": "xs",
                        "align": "start",
                        "wrap": True
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "image",
                                "url": QRCodeUrl,
                                "size": "3xl",
                                "margin": "md"
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "lg",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [],
                                "width": "65px"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "uri",
                                    "label": "掃描",
                                    "uri": scanUrl
                                },
                                "height": "sm",
                                "style": "primary",
                                "margin": "md",
                                "color": "#53726C"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [],
                                "width": "65px"
                            }
                        ]
                    }
                ]
            }
        }
        return self.messages