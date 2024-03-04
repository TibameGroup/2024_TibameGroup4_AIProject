# -*- coding: utf-8 -*-
"""
Created on Sat Dec 23 17:37:35 2023

@author: T14 Gen 3
"""

import requests
from bs4 import BeautifulSoup

url="https://foodsafety.family.com.tw/Web_FFD_2022/ws/QueryFsProductByItem"

#只要把所有ID找出來即可
from_data={"CMNO": "0058804"}
response=requests.post(url,data=from_data)
print(response.json())


