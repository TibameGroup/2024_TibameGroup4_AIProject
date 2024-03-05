import math
def calculate_nutrition(height, weight, age, gender, activity_level, workout):
    # 營養需求基準值，單位為卡路里
    calorie_needs = 0
    protein_needs = 0
    carbohydrate_needs = 0
    fat_needs = 0

    # 基本代謝率 (BMR) 的計算
    if gender.lower() == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
        # bmr = 66.5 + (13.75 * weight) + (5.003 * height) - (6.755 * age)

    elif gender.lower() == 'female':
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
        # bmr = 655.1 + (9.563 * weight) + (1.85 * height) - (4.676 * age)

    else:
        raise ValueError("Invalid gender. Please enter 'male' or 'female'.")

    # 根據活動量調整總熱量需求 'sedentary (不運動)', 'lightly_active(一周運動1-2天)', 'moderately_active(一周運動2-4天)', 'very_active'(一周運動3-5天), 'extra_active(一周運動6天以上或者從事勞力工作或運動員)'
    if activity_level == 'sedentary':
        calorie_needs = bmr * 1.2
    elif activity_level == 'lightly_active':
        calorie_needs = bmr * 1.375
    elif activity_level == 'moderately_active':
        calorie_needs = bmr * 1.55
    elif activity_level == 'very_active':
        calorie_needs = bmr * 1.725
    elif activity_level == 'extra_active':
        calorie_needs = bmr * 1.9
    else:
    
        raise ValueError("Invalid activity level. Please enter 'sedentary', 'lightly_active', 'moderately_active', 'very_active', or 'extra_active'.")
    
    if workout == "yes": #推薦有運動的人的熱量分配
    
        protein_needs = calorie_needs * 0.3 / 4 # 健身人建議攝取的蛋白質為總熱量的30% 每克蛋白質約含有 4 卡路里
        carbohydrate_needs = calorie_needs * 0.4 / 4  # 健身建議攝取的碳水化合物為總熱量的 40%，每克碳水化合物約含有 4 卡路里
        fat_needs = calorie_needs * 0.3 / 9  # 建議攝取的脂肪為總熱量的 30%，每克脂肪約含有 9 卡路里

    else:
    # 推薦普通沒運動的人的熱量分配
        protein_needs = weight * 1.2  # 建議攝取的蛋白質為體重的 1.2 克/公斤 每克蛋白質約含有 4 卡路里
        carbohydrate_needs = calorie_needs * 0.55 / 4  # 建議攝取的碳水化合物為總熱量的 55%，每克碳水化合物約含有 4 卡路里
        fat_needs = calorie_needs * 0.3 / 9  # 建議攝取的脂肪為總熱量的 30%，每克脂肪約含有 9 卡路里
    calorie_needs = math.ceil(calorie_needs)
    protein_needs = math.ceil(protein_needs)
    carbohydrate_needs = math.ceil(carbohydrate_needs)
    fat_needs = math.ceil(fat_needs)
    # 將計算結果以字典形式返回
    nutrition_dict = {
        '熱量': calorie_needs,
        '蛋白質': protein_needs,
        '脂肪': fat_needs,
        '碳水化合物': carbohydrate_needs
    }

    return nutrition_dict

if __name__ == "__main__":
    # 例子: 輸入身高、體重、年齡、性別、活動量
    height = 160  # 身高 (公分)
    weight = 53   # 體重 (公斤)
    age = 26      # 年齡
    gender = 'male'  # 性別 ('male' 或 'female')
    activity_level = 'sedentary'  # 活動量 ('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active')
    workout = "no"

    # 計算營養需求
    result = calculate_nutrition(height, weight, age, gender, activity_level, workout)

    # 顯示結果
    print(result)
