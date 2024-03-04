import numpy as np
# from functools import lru_cache

def calculate_and_get_level(data):
    # 單位換算成每100g(ml)
    HEAT_ = (float(data['HEAT']) / float(data['G_ML_NUM'])) * 100
    PROTEIN_ = (float(data['PROTEIN']) / float(data['G_ML_NUM'])) * 100
    TOTALFAT_ = (float(data['TOTALFAT']) / float(data['G_ML_NUM'])) * 100
    SATFAT_ = (float(data['SATFAT']) / float(data['G_ML_NUM'])) * 100
    TRANSFAT_ = (float(data['TRANSFAT']) / float(data['G_ML_NUM'])) * 100
    CARBOHYDRATE_ = (float(data['CARBOHYDRATE']) / float(data['G_ML_NUM'])) * 100
    SUGAR_ = (float(data['SUGAR']) / float(data['G_ML_NUM'])) * 100
    SODIUM_ = (400 * float(data['SODIUM'])) if data['SODIUM'] else (float(data['SODIUM']) / float(data['G_ML_NUM'])) * 100

    # 輸入正確的資料數值篩選
    if (HEAT_ > 900 and
            (PROTEIN_ + TOTALFAT_ + CARBOHYDRATE_) > 100 and
            all(x > 0 for x in [HEAT_, PROTEIN_, TOTALFAT_, SATFAT_, TRANSFAT_, CARBOHYDRATE_, SUGAR_, SODIUM_]) and
            HEAT_ <= (PROTEIN_ * 4 + TOTALFAT_ * 9 + CARBOHYDRATE_ * 4) and
            TOTALFAT_ <= (SATFAT_ + TRANSFAT_) and
            CARBOHYDRATE_ < SUGAR_ and
            SODIUM_ > 40000):
        raise ValueError("輸入錯誤數值")

    # 計算分數
    if data['G_ML'] == "公克":
        score = count_general_score(HEAT_, PROTEIN_, SATFAT_, SUGAR_, SODIUM_)
        level = get_general_CLASS(score)
    elif data['G_ML'] == "毫升":
        score = count_beverage_score(HEAT_, PROTEIN_, SATFAT_, SUGAR_, SODIUM_)
        level = get_beverage_CLASS(score, HEAT_, CARBOHYDRATE_, SODIUM_)
    else:
        raise ValueError("輸入錯誤的單位")

    return score, level

# def calculate_point(value, intervals, points):
#     index = np.searchsorted(intervals, value)
#     return points[index-1]

def map_to_interval(value, intervals):
    index = np.searchsorted(intervals, value, side='right') - 2
    return index

def count_general_score(HEAT, PROTEIN, SATFAT, SUGAR, SODIUM):
    # 定義各指標的區間
    heat_intervals = np.arange(80, 801, 80)
    satfat_intervals = np.arange(1, 11, 1)
    sugar_intervals = np.array([3.4, 6.8, 10, 14, 17, 20, 24, 27, 31, 34, 37, 41, 44, 48, 51])
    sodium_intervals = np.arange(80, 1601, 80)
    protein_intervals = np.array([2.4, 4.8, 7.2, 9.6, 12, 14, 17])

    # 計算各指標的分數
    heat_score = map_to_interval(HEAT, heat_intervals)
    satfat_score = map_to_interval(SATFAT, satfat_intervals)
    sugar_score = map_to_interval(SUGAR, sugar_intervals)
    sodium_score = map_to_interval(SODIUM, sodium_intervals)
    protein_score = map_to_interval(PROTEIN, protein_intervals)

    # 總分計算
    score = heat_score + satfat_score + sugar_score + sodium_score - protein_score

    return score

def count_beverage_score(HEAT, PROTEIN, SATFAT, SUGAR, SODIUM):
    # 定義各指標的區間
    heat_intervals = [float('-inf'), 7.2, 21.5, 35.9, 50.2, 57.4, 64.5, 71.7, 78.9, 86.1, 93.2, float('inf')]
    satfat_intervals = np.arange(1, 11, 1)
    sugar_intervals = [float('-inf'), 0.5, 2, 3.5, 5, 6, 7, 8, 9, 10, 11, float('inf')]
    sodium_intervals = np.arange(80, 1601, 80)
    protein_intervals = np.arange(1.2, 3.1, 0.3)

    # 計算各指標的分數
    heat_score = map_to_interval(HEAT, heat_intervals)
    satfat_score = map_to_interval(SATFAT, satfat_intervals)
    sugar_score = map_to_interval(SUGAR, sugar_intervals)
    sodium_score = map_to_interval(SODIUM, sodium_intervals)
    protein_score = map_to_interval(PROTEIN, protein_intervals)

    # 總分計算
    score = heat_score + satfat_score + sugar_score + sodium_score - protein_score

    return score

def get_general_CLASS(score):
    classes = ['A', 'B', 'C', 'D', 'E']
    interval = [float('-inf'), 1, 3, 11, 19, float('inf')]
    index = np.searchsorted(interval, score)-1
    return classes[index]

def get_beverage_CLASS(score, HEAT, CARBOHYDRATE, SODIUM):
    if score != -1 or HEAT != 0 or CARBOHYDRATE != 0 or SODIUM != 0:
        classes = ['B', 'C', 'D', 'E']
        interval = [float('-inf'), 3, 7, 10, float('inf')]
        index = np.searchsorted(interval, score) - 1
    else:
        classes = ['A']
        index = 0

    return classes[index]

if __name__ == "__main__":
    data = {'PRODNAME': '測試', 'G_ML_NUM': '1', 'UNIT': '2', 'HEAT': '230.4', 'PROTEIN': '3', 'TOTALFAT': '8.0', 'SATFAT': '1.2', 'TRANSFAT': '0', 'CARBOHYDRATE': '24.4', 'SUGAR': '20.8', 'SODIUM': '4', 'G_ML': '毫升', 'barcode': '4710063337802', 'CMNO': 'C702705'}
    # data = {'PRODNAME': '測試', 'G_ML_NUM': '1', 'UNIT': '2', 'HEAT': '230.4', 'PROTEIN': '3', 'TOTALFAT': '8.0', 'SATFAT': '1.2', 'TRANSFAT': '0', 'CARBOHYDRATE': '24.4', 'SUGAR': '20.8', 'SODIUM': '72', 'G_ML': '公克', 'barcode': '4710063337802', 'CMNO': 'C313802'}
    res = calculate_and_get_level(data)
    print(res[1])
    # G_ML_NUM, UNIT, HEAT, PROTEIN, TOTALFAT, SATFAT, TRANSFAT
