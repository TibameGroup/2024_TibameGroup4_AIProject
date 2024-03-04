import requests
#from bs4 import BeautifulSoup
import re
import time
import random
from sql_newclass  import officialInsert
import sql_newclass

path = r'./all_id.txt'
f = open(path, 'r')
id_list = f.read().split('\n')
f.close()

# path = 'error.txt'
# f = open(path, 'r')
# id_error = f.read().split('\n')
# f.close()

import unicodedata
stop = random.randint(0,3)
def fullwidth_to_halfwidth(s):
    """
    將字串中的全形文字轉換為半形文字
    """
    return ''.join([unicodedata.normalize('NFKC', char) for char in s])

def remove_whitespace_regex(text):
    """
    使用正則表達式刪除字符串中的空白格
    """
    return re.sub(r'\s', '', text)

url="https://foodsafety.family.com.tw/Web_FFD_2022/ws/QueryFsProductByItem"

dict_all = []
error = []
#len(id_list)-1
for i in range(0,len(id_list)):
    save_dict = {}
    id = id_list[i]
    # if id in id_error:
    #     continue
    from_data = {"CMNO": id}
    response = requests.post(url,data=from_data)
    data = response.json()
    time.sleep(stop)

    #無資料id儲存
    if data['RESULT_DESC'] == '查無資料':
        print(id,' 404')
        error.append(id)
        continue

    #熱量容量暫存
    temp_string = data['LIST'][0]['NOTE']
    check = temp_string.split(';')[1][-2:]
    if str(check) == '盎司' or data['LIST'][0]['CATEGORY_NAME'] == '現做飲料':
        error.append(id)
        continue
   
    # save商品名稱 並轉成半形
    save_dict['PRODNAME'] = remove_whitespace_regex(fullwidth_to_halfwidth(data['LIST'][0]['PRODNAME']))
    save_dict['G_ML'],save_dict['UNIT'] = [float(s) for s in re.findall(r"-?\d+\.?\d*", temp_string)][1:]
    save_dict['HEAT'] =  [float(s) for s in re.findall(r"-?\d+\.?\d*", temp_string)][0]
    
    if str(check) != '毫升' and str(check) != '公克':
        if str(check) == '公斤':
            save_dict['G_ML'] *= 1000
        else :
            print(id," 單位:",check)
            error.append(id)

    temp = data['LIST'][0]['NUTRIENTS'][0]
    temp.pop('CAFFEINE') 
    temp_SODIUM = temp['SODIUM']
    temp.pop('SODIUM') 
    save_dict.update(temp)
    save_dict['SODIUM'] = temp_SODIUM
    #
    officialInsert([save_dict])
    #dict_all.append(save_dict)
   
    if i % 100 == 0:
        print(i,': -------save--------')
        
print(dict_all)
# officialInsert(dict_all)

#產品重複