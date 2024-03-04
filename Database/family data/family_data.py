#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
from bs4 import BeautifulSoup
import re
import time
import random


# In[ ]:


path = 'all_id.txt'
f = open(path, 'r')
id_list = f.read().split('\n')
f.close()


# In[ ]:


path = 'error.txt'
f = open(path, 'r')
id_error = f.read().split('\n')
f.close()


# In[ ]:


#刪除全形空白\u3000
#變換英文全行文字
import unicodedata
def stop():
    t = random.randint(0,15)
    return  t

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

def clean_text(text):
    return remove_whitespace_regex(fullwidth_to_halfwidth(text))

def process_nutrient(nutrient):
    nutrient.pop('CAFFEINE', None)
    sodium_value = nutrient.pop('SODIUM', None)
    nutrient.update({'SODIUM': sodium_value})
    return nutrient


# In[ ]:


url="https://foodsafety.family.com.tw/Web_FFD_2022/ws/QueryFsProductByItem"
# len(id_list)
dict_all = []
error = []
for i in range(0,len(id_list)):
    save_dict = {}
    id = id_list[i]
    if id in id_error:
        continue
    from_data = {"CMNO": id}
    response = requests.post(url,data=from_data)
    data = response.json()
    time.sleep(stop())

    # 無資料id儲存
    if data['RESULT_DESC'] == '查無資料':
        print(id,' 404')
        error.append(id)
        continue

    #熱量容量暫存
    check = data['LIST'][0]['NOTE'].split(';')[1][-2:]
    if str(check) == '盎司' or data['LIST'][0]['CATEGORY_NAME'] == '現做飲料':
        error.append(id)
        continue
    
    temp_num =  [float(s) for s in re.findall(r"-?\d+\.?\d*", data['LIST'][0]['NOTE'])]
    save_dict = {
        'CMNO': id,
        'PRODNAME': clean_text(data['LIST'][0]['PRODNAME']),
        'G_ML_NUM': temp_num[1],
        'G_ML': data['LIST'][0]['NOTE'].split(';')[1][-2:],
        'UNIT': temp_num[2],
        'HEAT': temp_num[0],
        **process_nutrient(data['LIST'][0]['NUTRIENTS'][0]),
        'url': data['LIST'][0]['PROD_PIC']
    }

    if str(check) != '毫升' and str(check) != '公克':
        if str(check) == '公斤':
            save_dict['G_ML_NUM'] *= 1000
            save_dict['G_ML'] = '公克'
        else :
            print(id," 單位:",check)
            error.append(id)

    dict_all.append(save_dict)
    if i % 100 == 0:
        print(i,': -------save--------')


# In[ ]:


len(dict_all)


# In[ ]:


# with open("dict.txt", "w",encoding='utf-8') as outfile:          #Open file to write
#     for dict in dict_all:
#         outfile.write(str(dict)) 


# In[ ]:


# with open("error_0103.txt", "w",encoding='utf-8') as outfile:          #Open file to write
#     for e in error:
#         outfile.write(str(e)+"\n") 

