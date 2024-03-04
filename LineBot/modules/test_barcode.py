import json
def ensureReply(CMNO, barcodeValue, PRODNAME):
    data_ensureYes = json.dumps({'action':'ensureYes', 'barcodeValue':barcodeValue, 'CMNO':CMNO})
    data_ensureNo = json.dumps({'action':'ensureNo'})
    messages = {
        "type": "text",  # 1
        "text": f"條碼資料: {barcodeValue}\n產品名稱: {PRODNAME} \n\n確認資料，正確案*是*",
        "quickReply": {  # 2
            "items": [
                {
                    "type": "action",  # 3
                    "action": {
                        "type": "postback",
                        "label": "是",
                        "data": data_ensureYes
                    }
                },
                {
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": "否",
                        "data": data_ensureNo
                    }
                }
            ]
        }
    }
    return messages
class testBarcodeInfo():
    def __init__(self) -> None:
        self.messages = {"type": "flex",
                         "altText": "test"}
    # def testProdInfo(self, barcodeValue, CMNO, URL="https://i.imgur.com/eMClSTJ.jpeg", PRODNAME=" ", HEAT="0", G_ML_NUM="0", G_ML="公克", NAME=" ", UNIT="1", BARCODE=" "):
    def testProdInfo(self, barcodeValue, prod):
        prod['BARCODE'] = prod['BARCODE'] if prod['BARCODE'] else " "
        prod['NAME'] = prod['NAME'] if prod['NAME'] else " "
        for key, value in prod.items():
            if value is None:
                prod[key] = "0"
        prod['URL'] = "https://foodsafety.family.com.tw/product_img/" + prod['URL'] if prod['URL'] else 'https://i.imgur.com/eMClSTJ.jpeg'

        data_detailInfo = json.dumps({'CMNO':prod['CMNO'], 'action':'detailInfo'})
        data_insertBarcodeValue = json.dumps({'barcodeValue':barcodeValue, 'action':'insertBarcodeValue', 'CMNO':prod['CMNO'], 'PRODNAME': prod['PRODNAME']})
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
                                        "text": "總量：",
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
                                        "text": "條碼：",
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
                                        "text": prod['BARCODE'],
                                        "size": "md",
                                        "color": "#111111",
                                        "align": "end"
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
                                        "text": "人員：",
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
                                        "text": prod['NAME'] ,
                                        "size": "md",
                                        "color": "#111111",
                                        "align": "end"
                                    }
                                    ],
                                    "width": "100px"
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
                                "label": "查詢營養表",
                                "data": data_detailInfo
                                },
                                "margin": "sm",
                                "height": "sm",
                                "style": "link"
                            },
                            {
                                "type": "button",
                                "action": {
                                        "type": "postback",
                                        "label": "登錄Barcode",
                                        "data": data_insertBarcodeValue
                                },
                                "margin": "sm",
                                "height": "sm",
                                "style": "primary"
                            }
                        ]
                    }
                    }
        return bubble

    def testProdInfos(self, prodList, barcodeValue=None, moreProd=False, iter=0, searchName=None):
        testProdInfoList = []
        for i in range(len(prodList)):
            testProdInfoList.append(
                self.testProdInfo(barcodeValue,
                    prod=prodList[i]
                ) if barcodeValue else self.seeProdInfo( # 檢查區，若無Barcode，則顯示"檢查商品seeProdInfo"
                    prod=prodList[i]
                )

            ) 

        self.messages["contents"] = {
            "type": "carousel",
            "contents": testProdInfoList
            }
        # 退出檢查按鈕
        if not barcodeValue:
            data_exitCheck = json.dumps({'action':'exitCheck'})
            self.messages["quickReply"] = {  
                "items": [
                    {
                        "type": "action",  
                        "action": {
                            "type": "postback",
                            "label": "退出檢查",
                            "data": data_exitCheck
                        }
                    }
                    ]
                }
            if moreProd:
                data_moreProd = json.dumps({"action":"moreProd", "iter": iter, "searchName": searchName})
                self.messages["quickReply"]["items"].append(
                        {
                            "type": "action",  
                            "action": {
                                "type": "postback",
                                "label": "更多商品",
                                "data": data_moreProd
                            }
                        })
        # 顯示更多按鈕
        elif moreProd:
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

    # def seeProdInfo(self, CMNO, URL="https://i.imgur.com/eMClSTJ.jpeg", PRODNAME=" ", HEAT="0", G_ML_NUM="0", G_ML="公克", NAME=" ", UNIT="1", BARCODE=" "):
    def seeProdInfo(self, prod):
        prod['BARCODE'] = prod['BARCODE'] if prod['BARCODE'] else " "
        prod['NAME'] = prod['NAME'] if prod['NAME'] else " "
        for key, value in prod.items():
            if value is None:
                prod[key] = "0"
        prod['URL'] = "https://foodsafety.family.com.tw/product_img/" + prod['URL'] if prod['URL'] else 'https://i.imgur.com/eMClSTJ.jpeg'
        data_detailInfo = json.dumps({'CMNO':prod['CMNO'], 'action':'detailInfo'})
        
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
                                        "text": "總量：",
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
                                        "text": "條碼：",
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
                                        "text": prod['BARCODE'],
                                        "size": "md",
                                        "color": "#111111",
                                        "align": "end"
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
                                        "text": "人員：",
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
                                        "text": prod['NAME'] ,
                                        "size": "md",
                                        "color": "#111111",
                                        "align": "end"
                                    }
                                    ],
                                    "width": "100px"
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
                                "label": "查詢營養表",
                                "data": data_detailInfo
                                },
                                "margin": "sm",
                                "height": "sm",
                                "style": "link"
                            }
                        ]
                    }
                    }
        return bubble