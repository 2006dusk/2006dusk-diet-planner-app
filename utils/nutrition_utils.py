# -*- coding: utf-8 -*-
"""
营养计算工具模块
提供基础的营养计算功能
"""

def bmr(weight: float, height: float, age: int, gender: str) -> float:
    """Mifflin-St Jeor 基础代谢"""
    if gender == '男':
        return 10 * weight + 6.25 * height - 5 * age + 5
    return 10 * weight + 6.25 * height - 5 * age - 161


def tdee(bmr_value: float, activity: float = 1.375) -> float:
    """总消耗，默认轻度活动量"""
    return bmr_value * activity


def macro_split(calories: float, ratio=(0.5, 0.3, 0.2)):
    """返回 (carbs, protein, fat) 克数"""
    c, p, f = ratio
    return (calories * c / 4, calories * p / 4, calories * f / 9)


def calculate_bmi(weight: float, height: float) -> float:
    """计算BMI指数"""
    height_in_m = height / 100  # 转换为米
    return weight / (height_in_m ** 2)


def recommend_calories(bmr_value: float, goal: str = "maintain") -> float:
    """根据目标推荐每日热量摄入
    goal: 'lose' 减重, 'maintain' 维持, 'gain' 增重
    """
    if goal == "lose":
        return bmr_value * 0.8  # 减少20%热量摄入
    elif goal == "gain":
        return bmr_value * 1.2   # 增加20%热量摄入
    else:
        return bmr_value  # 维持当前热量摄入


def calculate_food_nutrition(food, quantity=1.0):
    """根据食物数据和数量计算营养成分
    food: 食物数据字典
    quantity: 食物数量（根据单位而定）
    返回: 包含热量、蛋白质、脂肪、碳水化合物的字典
    """
    # 获取食物的单位
    unit = food.get("unit", "100g")
    
    # 确保所有营养成分都存在且不是None
    for key in ["calories", "protein", "fat", "carbs", "fiber"]:
        if food.get(key) is None:
            food[key] = 0
    
    # 根据单位计算营养成分
    if unit == "份":
        # 对于成品菜，直接按份数计算
        return {
            "calories": food["calories"] * quantity,
            "protein": food["protein"] * quantity,
            "fat": food["fat"] * quantity,
            "carbs": food["carbs"] * quantity,
            "fiber": food.get("fiber", 0) * quantity
        }
    else:
        # 对于按重量计算的食物（如水果、主食），按100g为基准计算
        # quantity在这里表示克数
        factor = quantity / 100.0
        return {
            "calories": food["calories"] * factor,
            "protein": food["protein"] * factor,
            "fat": food["fat"] * factor,
            "carbs": food["carbs"] * factor,
            "fiber": food.get("fiber", 0) * factor
        }


def calculate_body_fat_percentage(weight, height, age, gender, waist, neck=0, hip=0):
    """使用美国海军公式计算体脂率
    weight: 体重(公斤)
    height: 身高(厘米)
    age: 年龄
    gender: 性别('男' 或 '女')
    waist: 腰围(厘米)
    neck: 颈围(厘米)
    hip: 臀围(厘米，仅女性需要)
    返回: 体脂率百分比
    """
    # 如果腰围为0，则无法计算体脂率
    if waist <= 0:
        return None
        
    # 转换为英寸
    weight_lbs = weight * 2.20462
    height_inches = height * 0.393701
    waist_inches = waist * 0.393701
    neck_inches = neck * 0.393701 if neck > 0 else 0
    
    if gender == '男':
        # 男性体脂率计算公式
        if neck_inches <= 0:
            return None
        body_fat_percentage = 86.010 * (waist_inches - neck_inches) / height_inches - 70.041 * (height_inches / 100) + 36.76
    else:
        # 女性体脂率计算公式
        hip_inches = hip * 0.393701 if hip > 0 else 0
        if neck_inches <= 0 or hip_inches <= 0:
            return None
        body_fat_percentage = 163.205 * (waist_inches + hip_inches - neck_inches) / height_inches - 97.684 * (height_inches / 100) - 78.387
    
    return max(0, body_fat_percentage)  # 确保结果不为负数


def get_activity_multiplier(activity_level):
    """根据活动水平获取TDEE乘数
    activity_level: 活动水平('low', 'medium', 'high')
    返回: TDEE乘数
    """
    activity_multipliers = {
        "low": 1.2,      # 久坐不动
        "medium": 1.55,   # 中等活动
        "high": 1.9       # 高度活动
    }
    return activity_multipliers.get(activity_level, 1.2)