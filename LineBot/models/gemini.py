"""
At the command line, only need to run once to install the package via pip:

$ pip install google-generativeai
"""
import re
from pathlib import Path
import google.generativeai as genai
import asyncio
import json

with open('./config/config.json', 'r') as file:
    config = json.load(file)
KEY = config["GeminiKey"]

genai.configure(api_key=KEY)

# Set up the model
generation_config = {
  "temperature": 0.2,
  "top_p": 1,
  "top_k": 32,
  "max_output_tokens": 4096,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

model = genai.GenerativeModel(model_name="gemini-pro-vision",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

# 非同步修改處
async def geminiCalEnergy(path):
    # Validate that an image is present
    if not (img := Path(path)).exists():
        raise FileNotFoundError(f"Could not find image: {img}")

    image_parts = [
        {
            "mime_type": "image/jpeg",
            "data": Path(path).read_bytes()
        },
    ]

    prompt_parts = [
        image_parts[0],
        " \nTell me detailed nutritional facts, and only give me information on calories, protein, fat, carbohydrates, sugar, and sodium in order. ",
    ]
    try :
        # start = time.time()
        # 非同步函式
        loop = asyncio.get_event_loop()
        # Gemini 搭配非同步取得結果
        response = await loop.run_in_executor(None, model.generate_content, prompt_parts)
        # end = time.time()
        # 未正規化結果
        print("Gemini 回傳值: \n", response.text)
        regular = Regular()
        try:
            # 正規化Gemini結果
            result = (regular.standardization(response.text))
            return [result, response.text]
        except:
            # 正規化失敗
            print(f"Can't standardization:  {response.text}")
            return response.text
    except Exception as error :
        print(error)

class Regular():
    def __init__(self):
        self.nutritionValues = {
            "LEVEL": None,
            "G_ML_NUM": None,
            "G_ML": "公克",
            "UNIT": "1",
            "HEAT": None,
            "PROTEIN": None,
            "TOTALFAT": None,
            "SATFAT": None,
            "TRANSFAT": None,
            "CARBOHYDRATE": None,
            "SUGAR": None,
            "SODIUM": None}
    def standardization(self, geminiDatas):
        patternAll = re.compile(r"Total\sFat|Saturated\sFat|Total\sCarbohydrates|[\d\w,]+") # 取出匹配英文、數字或,的字串(不取空白，且出現一次以上) 
        split_list = geminiDatas.split("\n")

        for row in split_list:
            regularText = patternAll.findall(row) # 取出英文及數字
            self.processData(regularText)
        return (self.nutritionValues)

    def processData(self, value):
        nutritionMapping = {
            'Calories': 'HEAT',
            'Protein': 'PROTEIN',
            'Fat': 'TOTALFAT',
            'Total Fat': 'TOTALFAT',
            'Saturated Fat': 'SATFAT',
            'Trans Fat': 'TRANSFAT',
            'Carbohydrates': 'CARBOHYDRATE',
            'Total Carbohydrates': 'CARBOHYDRATE',
            'Sugar': 'SUGAR',
            'Sugars': 'SUGAR',
            'Sodium': 'SODIUM',
        }
        if len(value) >= 2 and value[0] in nutritionMapping:
            nutrition_key = nutritionMapping[value[0]]
            self.nutritionValues[nutrition_key] = re.sub(r'[gm,\s]', '', value[1]) # 去除 g mg 

if __name__ == "__main__":
    path = r".\image\geminiImg\example4.jpg"
    res = asyncio.run(geminiCalEnergy(path))
    print("Gemini 回傳值正規化: \n", res)
    # print(type(res))
