import json
from datetime import datetime, timedelta

class DiaryFlex():
    # https://developers.line.biz/en/reference/messaging-api/#flex-message
    # 設計 Flex: https://developers.line.biz/flex-simulator/?status=success
    # Postback Action: https://developers.line.biz/en/docs/messaging-api/actions/#postback-action
    def __init__(self) -> None:
        self.messages = {"type": "flex",
                         "altText": "DiaryMenu"}
    def mainDiary(self, userId, mongoConn):
        """飲食紀錄的三天頁面"""
        # 查詢飲食紀錄
        records = mongoConn.mongoSearch(userId=userId, collectionName="dietRecord")
        if not records: # 未添加過紀錄，無List
            return None
        if len(records[0]['prodList']) <= 0: # 刪除資料，List=[]
            return None
        prodList = records[0]['prodList'] # 每天的飲食項目
        dayRecords = records[0]['dayRecords'] # 每天營養(熱量...)加總的總記錄
        recordDates = [] # 三天的日期
        # 獲取當前日期
        now = datetime.now()
        recordDates.append(now.strftime('%Y-%m-%d'))
        # 計算前兩天的日期
        for i in range(1, 3):
            pre_day = now - timedelta(days=i)
            recordDates.append(pre_day.strftime('%Y-%m-%d'))
        if records[0]['prodList'][-1]["DATETIME"].split('T')[0] not in recordDates: # 沒有三天內的記錄
            return None
        DayDiaryList = [] # 多天數的Bubble List
        for recordDate in recordDates:
            prods = [item for item in prodList if item.get('DATETIME').split('T')[0] == str(recordDate)]
            dayRecord = [item for item in dayRecords if item.get('DATETIME') == recordDate]
            if len(prods) > 0:
                DayDiaryList.append(
                    self.DayDiary(prods, dayRecord[0]) # 單天的 Bubble
                )
        self.messages["contents"] = {
            "type": "carousel",
            "contents": DayDiaryList
        }
        return self.messages
    
    def DayDiary(self, prods, dayRecord):
        """飲食紀錄的一天頁面"""
        data_dietRecordMore = json.dumps({"action":"dietRecordMore", "DATETIME": dayRecord['DATETIME']})
        bubble = {
                    "type": "bubble",
                    "size": "hecto",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "飲食摘要",
                                "size": "sm",
                                "color": "#1DB446",
                                "weight": "bold"
                            },
                            {
                                "type": "text",
                                "text": str(dayRecord['DATETIME']),
                                "size": "xl",
                                "weight": "bold",
                                "align": "start",
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Total ",
                                        "weight": "bold",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "align": "start",
                                        "gravity": "center",
                                        "margin": "md"
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
                                                        "text": "熱量"
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
                                                        "text": str(dayRecord['HEATS']),
                                                        "align": "end",
                                                        "gravity": "center"
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
                                                        "text": "大卡",
                                                        "align": "end",
                                                        "gravity": "center"
                                                    }
                                                ]
                                            }
                                        ],
                                        "margin": "md"
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
                                                        "text": "蛋白質"
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
                                                        "text": str(dayRecord['PROTEINS']),
                                                        "align": "end",
                                                        "gravity": "center"
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
                                                        "text": "公克",
                                                        "align": "end",
                                                        "gravity": "center"
                                                    }
                                                ]
                                            }
                                        ],
                                        "margin": "md"
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
                                                        "text": "脂肪"
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
                                                        "text": str(dayRecord['TOTALFATS']),
                                                        "align": "end",
                                                        "gravity": "center"
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
                                                        "text": "公克",
                                                        "align": "end",
                                                        "gravity": "center"
                                                    }
                                                ]
                                            }
                                        ],
                                        "margin": "md"
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
                                                        "text": "碳水化合物"
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
                                                        "text": str(dayRecord['CARBOHYDRATES']),
                                                        "align": "end",
                                                        "gravity": "center"
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
                                                        "text": "公克",
                                                        "align": "end",
                                                        "gravity": "center"
                                                    }
                                                ]
                                            }
                                        ],
                                        "margin": "md"
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
                                                        "text": "鈉"
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
                                                        "text": str(dayRecord['SODIUMS']),
                                                        "align": "end",
                                                        "gravity": "center"
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
                                                        "text": "毫克",
                                                        "align": "end",
                                                        "gravity": "center"
                                                    }
                                                ]
                                            }
                                        ],
                                        "margin": "md"
                                    }
                                ]
                            },
                            {
                                "type": "separator",
                                "margin": "md"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Detail",
                                        "weight": "bold",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "align": "start",
                                        "gravity": "center",
                                        "margin": "md"
                                    },
                                    # 添加產品細項在此
                                ]
                            }
                        ]
                    }
                }
        morePord = {
            "type": "button",
            "action": {
                "type": "postback",
                "label": "more",
                "data": data_dietRecordMore
            },
            "height": "sm",
            "margin": "xs"
        }
        dayDetails = bubble["body"]["contents"][5]["contents"]
        if len(prods) > 3:
            for i in range(0, 3):
                dayDetails.append(self.dayDetail(prods[i]))
            dayDetails.append(morePord)
        else:
            for prod in prods:
                dayDetails.append(self.dayDetail(prod))
        
        return bubble
    def dayDetail(self, prod):
        """產品細項，飲食紀錄的產品項目"""
        data_dietRecordEdit = json.dumps({"action":"dietRecordEdit", "prod": {"PRODNAME": prod["PRODNAME"], "DATETIME": prod["DATETIME"]}})
        prodDiary = {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": str(prod['DATETIME']).split('T')[1],
                            "size": "sm",
                            "gravity": "center",
                            "margin": "xs",
                            "color": "#AFADAB",
                            "weight": "bold"
                        }
                    ],
                    "width": "45px"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": prod['PRODNAME'],
                            "gravity": "center",
                            "align": "center",
                            "size": "md",
                            "decoration": "underline",
                            "color": "#7BA9CB",
                            "weight": "bold"
                        }
                    ],
                    "margin": "sm"
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                        {
                            "type": "icon",
                            "url": "https://cdn4.iconfinder.com/data/icons/social-messaging-ui-coloricon-1/21/30-512.png",
                            "offsetTop": "xs"
                        }
                    ],
                    "width": "20px"
                }
            ],
            "margin": "lg",
            "spacing": "sm",
            "action": {
                "type": "postback",
                "label": "action",
                "data": data_dietRecordEdit
            }
        }
        return prodDiary
    def morePordButton(self, prods, DATETIME):   
        self.messages["contents"] = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "飲食日記",
                        "size": "sm",
                        "color": "#1DB446",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": str(DATETIME),
                        "margin": "md",
                        "size": "xl",
                        "weight": "bold"
                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            # 記錄資料添加
                        ]
                    }
                ]
            }
        }
        dayDetails = self.messages["contents"]["body"]["contents"][3]["contents"]
        for prod in prods:
            dayDetails.append(self.dayDetail(prod))
        return self.messages
    def recordEdit(self, prod):
        data_dietRecordDel = json.dumps({"action":"dietRecordDel", "prod": prod})
        self.messages["contents"] = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "飲食詳細資訊",
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
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "紀錄日期",
                                        "color": "#AFADAB",
                                        "gravity": "center",
                                        "weight": "bold",
                                        "margin": "xs",
                                        "size": "sm"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": str(prod["DATETIME"].split('T')[0]),
                                        "color": "#AFADAB",
                                        "gravity": "center",
                                        "margin": "xs",
                                        "size": "sm",
                                        "weight": "bold",
                                        "align": "end"
                                    }
                                ]
                            },
                            # {
                            #     "type": "separator",
                            #     "margin": "xxl",
                            #     "color": "#FFFFFF"
                            # },
                            # {
                            #     "type": "box",
                            #     "layout": "baseline",
                            #     "contents": [
                            #         {
                            #             "type": "icon",
                            #             "url": "https://cdn4.iconfinder.com/data/icons/social-messaging-ui-coloricon-1/21/30-512.png",
                            #             "offsetTop": "xs"
                            #         }
                            #     ],
                            #     "width": "20px"
                            # }
                        ],
                        "margin": "md",
                        # "action": {
                        #     "type": "message",
                        #     "label": "編輯日期",
                        #     "text": "編輯日期"
                        # }
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
                                        "text": "紀錄時間",
                                        "color": "#AFADAB",
                                        "gravity": "center",
                                        "weight": "bold",
                                        "margin": "xs",
                                        "size": "sm"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": str(prod["DATETIME"].split('T')[1]),
                                        "color": "#AFADAB",
                                        "gravity": "center",
                                        "margin": "xs",
                                        "size": "sm",
                                        "weight": "bold",
                                        "align": "end"
                                    }
                                ]
                            },
                            # {
                            #     "type": "separator",
                            #     "margin": "xxl",
                            #     "color": "#FFFFFF"
                            # },
                            # {
                            #     "type": "box",
                            #     "layout": "baseline",
                            #     "contents": [
                            #         {
                            #             "type": "icon",
                            #             "url": "https://cdn4.iconfinder.com/data/icons/social-messaging-ui-coloricon-1/21/30-512.png",
                            #             "offsetTop": "xs"
                            #         }
                            #     ],
                            #     "width": "20px"
                            # }
                        ],
                        "margin": "md",
                        # "action": {
                        #     "type": "message",
                        #     "label": "編輯時間",
                        #     "text": "編輯時間"
                        # }
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
                                        "text": "紀錄份量",
                                        "color": "#AFADAB",
                                        "gravity": "center",
                                        "weight": "bold",
                                        "margin": "xs",
                                        "size": "sm"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": prod["UNIT"],
                                        "color": "#AFADAB",
                                        "gravity": "center",
                                        "margin": "xs",
                                        "size": "sm",
                                        "weight": "bold",
                                        "align": "end"
                                    }
                                ]
                            },
                            # {
                            #     "type": "separator",
                            #     "margin": "xxl",
                            #     "color": "#FFFFFF"
                            # },
                            # {
                            #     "type": "box",
                            #     "layout": "baseline",
                            #     "contents": [
                            #         {
                            #             "type": "icon",
                            #             "url": "https://cdn4.iconfinder.com/data/icons/social-messaging-ui-coloricon-1/21/30-512.png",
                            #             "offsetTop": "xs"
                            #         }
                            #     ],
                            #     "width": "20px"
                            # }
                        ],
                        "margin": "md",
                        # "action": {
                        #     "type": "message",
                        #     "label": "編輯份量",
                        #     "text": "編輯份量"
                        # }
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
                                                "text": str(round(float(prod["HEAT"])*float(prod['UNIT']), 1)),
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
                                                "text": str(round(float(prod["PROTEIN"])*float(prod['UNIT']), 1)),
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
                                                "text": str(round(float(prod["TOTALFAT"])*float(prod['UNIT']), 1)),
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
                            # {
                            #     "type": "box",
                            #     "layout": "horizontal",
                            #     "margin": "md",
                            #     "contents": [
                            #         {
                            #             "type": "box",
                            #             "layout": "vertical",
                            #             "contents": [],
                            #             "width": "15px"
                            #         },
                            #         {
                            #             "type": "box",
                            #             "layout": "vertical",
                            #             "contents": [
                            #                 {
                            #                     "type": "text",
                            #                     "text": "飽和脂肪",
                            #                     "align": "start",
                            #                     "size": "md"
                            #                 }
                            #             ],
                            #             "width": "85px"
                            #         },
                            #         {
                            #             "type": "box",
                            #             "layout": "vertical",
                            #             "contents": [
                            #                 {
                            #                     "type": "text",
                            #                     "text": "0",
                            #                     "align": "end",
                            #                     "size": "md"
                            #                 }
                            #             ],
                            #             "width": "115px"
                            #         },
                            #         {
                            #             "type": "box",
                            #             "layout": "vertical",
                            #             "contents": [
                            #                 {
                            #                     "type": "text",
                            #                     "text": "公克",
                            #                     "size": "md",
                            #                     "align": "end"
                            #                 }
                            #             ]
                            #         }
                            #     ]
                            # },
                            # {
                            #     "type": "box",
                            #     "layout": "horizontal",
                            #     "margin": "md",
                            #     "contents": [
                            #         {
                            #             "type": "box",
                            #             "layout": "vertical",
                            #             "contents": [],
                            #             "width": "15px"
                            #         },
                            #         {
                            #             "type": "box",
                            #             "layout": "vertical",
                            #             "contents": [
                            #                 {
                            #                     "type": "text",
                            #                     "text": "反式脂肪",
                            #                     "align": "start",
                            #                     "size": "md"
                            #                 }
                            #             ],
                            #             "width": "85px"
                            #         },
                            #         {
                            #             "type": "box",
                            #             "layout": "vertical",
                            #             "contents": [
                            #                 {
                            #                     "type": "text",
                            #                     "text": "0",
                            #                     "align": "end",
                            #                     "size": "md"
                            #                 }
                            #             ],
                            #             "width": "115px"
                            #         },
                            #         {
                            #             "type": "box",
                            #             "layout": "vertical",
                            #             "contents": [
                            #                 {
                            #                     "type": "text",
                            #                     "text": "公克",
                            #                     "size": "md",
                            #                     "align": "end"
                            #                 }
                            #             ]
                            #         }
                            #     ]
                            # },
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
                                                "text": str(round(float(prod["CARBOHYDRATE"])*float(prod['UNIT']), 1)),
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
                                                "text": str(round(float(prod["SUGAR"])*float(prod['UNIT']), 1)),
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
                                                "text": str(round(float(prod["SODIUM"])*float(prod['UNIT']), 1)),
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
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "刪除記錄",
                            "data": data_dietRecordDel
                        },
                        "height": "sm"
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


