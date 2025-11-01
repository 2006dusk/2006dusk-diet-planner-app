import random
import json
from pathlib import Path
from typing import List, Dict

# 尝试导入 pypinyin，如果失败则使用备用方案
try:
    from pypinyin import lazy_pinyin
    PINYIN_AVAILABLE = True
except ImportError:
    print("警告：未安装 pypinyin 库，将使用备用中文排序方法")
    PINYIN_AVAILABLE = False

# 获取数据文件路径
DATA_DIR = Path(__file__).parent / "data"
PREDEFINED_FOODS_DIR = DATA_DIR / "predefined_foods"
USER_DATA_DIR = DATA_DIR / "user_data"

FRUITS_FILE = PREDEFINED_FOODS_DIR / "fruits.json"
STAPLE_FOODS_FILE = PREDEFINED_FOODS_DIR / "staple_foods.json"
PREPARED_DISHES_FILE = PREDEFINED_FOODS_DIR / "prepared_dishes.json"
SNACKS_FILE = PREDEFINED_FOODS_DIR / "snacks.json"

def load_food_data():
    """加载所有食物数据"""
    # 确保目录存在
    if not PREDEFINED_FOODS_DIR.exists():
        raise FileNotFoundError(f"预定义食物数据目录不存在: {PREDEFINED_FOODS_DIR}")
    
    # 检查各个文件是否存在
    missing_files = []
    if not FRUITS_FILE.exists():
        missing_files.append("fruits.json")
    if not STAPLE_FOODS_FILE.exists():
        missing_files.append("staple_foods.json")
    if not PREPARED_DISHES_FILE.exists():
        missing_files.append("prepared_dishes.json")
    if not SNACKS_FILE.exists():
        missing_files.append("snacks.json")
        
    if missing_files:
        raise FileNotFoundError(f"以下食物数据文件缺失: {', '.join(missing_files)}")
    
    try:
        with open(FRUITS_FILE, 'r', encoding='utf-8') as f:
            fruits = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"加载水果数据时出错: {e}")
        fruits = []
    
    try:
        with open(STAPLE_FOODS_FILE, 'r', encoding='utf-8') as f:
            staple_foods = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"加载主食数据时出错: {e}")
        staple_foods = []
    
    try:
        with open(PREPARED_DISHES_FILE, 'r', encoding='utf-8') as f:
            prepared_dishes = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"加载预制菜品数据时出错: {e}")
        prepared_dishes = []
    
    # 加载零食数据
    try:
        with open(SNACKS_FILE, 'r', encoding='utf-8') as f:
            snacks = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"加载零食数据时出错: {e}")
        snacks = []
    
    return fruits, staple_foods, prepared_dishes, snacks

# 加载食物数据
fruits, staple_foods, prepared_dishes, snacks = load_food_data()

def get_first_letter(food_name):
    """获取食物名称的首字母，支持中英文"""
    # 确保food_name是字符串类型
    if not isinstance(food_name, str):
        # 如果不是字符串，尝试获取其name属性或转换为字符串
        if hasattr(food_name, 'name') and isinstance(food_name.name, str):
            food_name = food_name.name
        elif isinstance(food_name, (list, tuple)) and len(food_name) > 0:
            # 如果是列表或元组，取第一个元素
            first_item = food_name[0]
            if isinstance(first_item, str):
                food_name = first_item
            elif hasattr(first_item, 'name') and isinstance(first_item.name, str):
                food_name = first_item.name
            else:
                food_name = str(first_item)
        else:
            food_name = str(food_name)
    
    # 如果是英文字母直接返回
    if food_name and food_name[0].isalpha() and ord(food_name[0]) < 128:
        return food_name[0].upper()
    elif food_name and PINYIN_AVAILABLE:  # 添加对空字符串的检查和pypinyin可用性检查
        # 使用拼音库处理中文字
        try:
            pinyin_first_letter = lazy_pinyin(food_name[0], style=0)[0][0].upper()
            return pinyin_first_letter.upper()
        except Exception:
            # 如果拼音处理失败，返回默认值
            return 'A'
    elif food_name:  # 没有pypinyin库时的备用方案
        # 简单的中文字符到字母的映射
        # 这里只处理常见的汉字，实际应用中可能需要更完整的映射
        chinese_to_alpha = {
            '阿': 'A', '八': 'B', '嚓': 'C', '哒': 'D', '峨': 'E', '发': 'F', '噶': 'G',
            '哈': 'H', '击': 'J', '喀': 'K', '垃': 'L', '妈': 'M', '拿': 'N', '哦': 'O',
            '啪': 'P', '期': 'Q', '然': 'R', '撒': 'S', '塔': 'T', '哇': 'W', '西': 'X',
            '压': 'Y', '匝': 'Z'
        }
        first_char = food_name[0]
        # 尝试在映射中查找
        for key, value in chinese_to_alpha.items():
            if first_char >= key:
                result = value
            else:
                break
        # 如果没找到，返回默认值
        return result if 'result' in locals() else 'A'
    else:
        return 'A'  # 默认返回'A'


def get_grouped_foods(foods_list):
    """将食物按首字母分组"""
    grouped = {}
    for food in foods_list:
        try:
            # 确保food是字典类型且包含name键
            if not isinstance(food, dict):
                print(f"跳过无效食物数据: {food}")
                continue
            if 'name' not in food or not isinstance(food['name'], str):
                print(f"跳过缺少name字段或name不是字符串的食物: {food}")
                continue
            first_letter = get_first_letter(food['name'])
            if first_letter not in grouped:
                grouped[first_letter] = []
            grouped[first_letter].append(food)
        except Exception as e:
            print(f"处理食物 {food} 时出错: {e}")
            # 使用默认分组
            if 'A' not in grouped:
                grouped['A'] = []
            grouped['A'].append(food)
    # 按照字母顺序排序分组
    return dict(sorted(grouped.items()))


# 合并所有食物数据，用于自选食物功能
all_foods_original = fruits + staple_foods + prepared_dishes + snacks

# 按首字母排序所有食物，添加错误处理
try:
    # 确保所有食物都有name字段且为字符串
    valid_foods = [food for food in all_foods_original if isinstance(food, dict) and 'name' in food]
    all_foods = sorted(valid_foods, key=lambda x: get_first_letter(x['name']))
except Exception as e:
    print(f"排序食物时出错: {e}")
    all_foods = all_foods_original

# 生成分组的食物数据
grouped_foods = get_grouped_foods(all_foods)

def random_recipe(meal: str = None):
    """根据餐次随机选择食谱"""
    # 合并所有准备好的菜肴
    all_recipes = prepared_dishes
    
    # 如果指定了餐次，则筛选对应餐次的食谱
    if meal is not None:
        pool = [r for r in all_recipes if r.get('meal_type') == meal]
    else:
        pool = all_recipes
    
    # 如果有符合条件的食谱，则随机选择一个
    if pool:
        return random.choice(pool)
    else:
        # 如果没有符合条件的食谱，返回默认选项
        return {
            "name": "营养餐",
            "calories": 300,
            "protein": 20,
            "fat": 10,
            "carbs": 35,
            "meal_type": meal or "lunch"
        }


def create_meal_from_foods(foods_list):
    """根据食物列表创建餐食"""
    print(f"DEBUG: create_meal_from_foods called with foods_list={foods_list}")
    if not foods_list:
        # 如果没有食物，返回空餐食
        print("DEBUG: foods_list is empty, returning default meal")
        return {
            "name": "未选择食物",
            "calories": 0,
            "protein": 0,
            "fat": 0,
            "carbs": 0,
            "fiber": 0,
            "meal_type": "unknown",
            "components": []
        }
    
    # 初始化营养成分，确保初始值为0而不是None
    total_nutrition = {
        "calories": 0,
        "protein": 0,
        "fat": 0,
        "carbs": 0,
        "fiber": 0
    }
    
    # 构建餐名
    meal_name = ""
    components = []
    
    for i, item in enumerate(foods_list):
        print(f"DEBUG: Processing item {i}: {item}")
        # 检查item是否为字典且包含必要字段
        if not isinstance(item, dict) or "food" not in item or "quantity" not in item:
            print(f"DEBUG: Invalid item format, skipping: {item}")
            continue
            
        food = item["food"]
        quantity = item["quantity"]
        print(f"DEBUG: food={food}, quantity={quantity}")
        
        # 确保quantity是数字类型且大于0，默认为0
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            try:
                quantity = float(quantity)
                if quantity <= 0:
                    quantity = 0
            except (ValueError, TypeError):
                quantity = 0
        
        # 只处理数量大于0的食物
        if quantity > 0:
            # 确保所有营养成分都存在且不是None，避免后续计算出错
            for key in ["calories", "protein", "fat", "carbs", "fiber"]:
                if food.get(key) is None:
                    food[key] = 0
            
            # 计算营养成分（根据份数）
            total_nutrition["calories"] += (food.get("calories", 0) or 0) * quantity
            total_nutrition["protein"] += (food.get("protein", 0) or 0) * quantity
            total_nutrition["fat"] += (food.get("fat", 0) or 0) * quantity
            total_nutrition["carbs"] += (food.get("carbs", 0) or 0) * quantity
            total_nutrition["fiber"] += (food.get("fiber", 0) or 0) * quantity
            
            # 添加到餐名中
            if meal_name:  # 如果餐名不为空，添加分隔符
                meal_name += " + "
            meal_name += food.get("name", "未知食物")
            if quantity != 1.0:
                meal_name += f"({quantity:.1f}份)"
            
            # 添加到组件列表
            # 确保食物数据完整
            if "unit" not in food:
                food["unit"] = "份"
            if "meal_type" not in food:
                food["meal_type"] = "any"
                
            components.append({
                "food": food,
                "quantity": quantity
            })
    
    # 如果没有有效食物，返回空餐食
    if not components:
        return {
            "name": "未选择食物",
            "calories": 0,
            "protein": 0,
            "fat": 0,
            "carbs": 0,
            "fiber": 0,
            "meal_type": "unknown",
            "components": []
        }
    
    # 确定餐次类型（从第一个食物获取）
    meal_type = "any"
    if foods_list and foods_list[0]["food"]:
        meal_type = foods_list[0]["food"].get("meal_type", "any")
    
    # 创建餐食对象
    meal = {
        "name": meal_name,
        "calories": round(total_nutrition["calories"], 1),
        "protein": round(total_nutrition["protein"], 1),
        "fat": round(total_nutrition["fat"], 1),
        "carbs": round(total_nutrition["carbs"], 1),
        "fiber": round(total_nutrition["fiber"], 1),
        "meal_type": meal_type,
        "components": components
    }
    
    print(f"DEBUG: create_meal_from_foods returning meal={meal}")
    return meal


def select_food_combination(food_categories, target_calories, target_nutrition=None, max_items=3):
    """从多个食物类别中选择符合目标热量和营养的食物组合
    food_categories: 食物类别列表，每个元素包含食物列表
    target_calories: 目标热量
    target_nutrition: 目标营养成分 {"protein": g, "fat": g, "carbs": g, "fiber": g}
    max_items: 最大食物数量
    返回: 选中的食物和份数列表
    """
    if not food_categories or not any(food_categories):
        return []
    
    # 过滤掉空的食物类别
    food_categories = [cat for cat in food_categories if cat]
    
    # 如果没有食物类别，返回空
    if not food_categories:
        return []
    
    # 确保至少有一个主食和一个菜肴
    # 检查是否有主食类别（第一个类别）
    has_staple = len(food_categories) > 0 and food_categories[0]
    has_dish = len(food_categories) > 1 and food_categories[1]  # 第二个类别是菜肴
    
    # 如果没有主食或菜肴，使用默认策略
    if not has_staple or not has_dish:
        # 使用原有逻辑
        # 根据目标热量确定食物数量偏好
        # 低热量更倾向于少量食物，高热量可以更多样化
        if target_calories < 200:
            # 低热量，倾向于1-2种食物
            num_foods = random.choices([1, 2], weights=[0.7, 0.3])[0]
        elif target_calories < 400:
            # 中等热量，倾向于2-3种食物
            num_foods = random.choices([2, 3], weights=[0.5, 0.5])[0]
        else:
            # 高热量，倾向于3种食物
            num_foods = 3
    else:
        # 有主食和菜肴时，确保至少包含主食和一个菜肴
        num_foods = max(2, min(3, int(target_calories / 200)))  # 根据热量确定食物数量，至少2个
    
    # 限制食物数量不超过最大项目数和可用类别数
    num_foods = min(num_foods, max_items, len(food_categories))
    
    if num_foods == 0:
        return []
    
    selected_foods = []
    remaining_calories = target_calories
    
    # 如果提供了目标营养成分，则使用营养优化算法
    if target_nutrition:
        # 计算每种营养素的权重
        total_nutrition_target = sum(target_nutrition.values())
        if total_nutrition_target > 0:
            nutrition_weights = {k: v/total_nutrition_target for k, v in target_nutrition.items() if v > 0}
        else:
            nutrition_weights = None
    else:
        nutrition_weights = None
    
    # 如果有主食类别，优先选择主食类食物
    if has_staple and num_foods >= 1:
        staple_foods = food_categories[0]
        # 根据目标热量选择主食
        if staple_foods:
            if nutrition_weights:
                # 使用营养优化选择主食
                staple = _select_food_by_nutrition(staple_foods, target_calories * 0.5, nutrition_weights)
            else:
                # 引入随机权重来选择主食，而不是总是选择最接近的
                if len(staple_foods) > 1:
                    # 计算每个食物的随机权重，基于热量差异和随机因子
                    weights = []
                    valid_foods = []  # 只包含有效的食物
                    for food in staple_foods:
                        # 确保food是一个字典且有'calories'键
                        if not isinstance(food, dict) or 'calories' not in food or food.get('calories', 0) <= 0:
                            continue  # 跳过无效食物
                        valid_foods.append(food)
                        calorie_diff = abs((food.get('calories', 0) or 0) - target_calories * 0.5)
                        # 权重与热量差异成反比，但加入随机因子增加多样性
                        base_weight = 1 / (1 + calorie_diff/100)
                        random_factor = random.uniform(0.5, 1.5)  # 添加随机因子
                        weights.append(base_weight * random_factor)
                    
                    # 根据权重选择食物
                    if valid_foods and weights:
                        staple = random.choices(valid_foods, weights=weights)[0]
                    elif staple_foods:
                        # 过滤掉热量为0或负数的食物
                        valid_staple_foods = [food for food in staple_foods if food.get('calories', 0) > 0]
                        staple = valid_staple_foods[0] if valid_staple_foods else None
                    else:
                        staple = None
                else:
                    # 确保主食热量大于0
                    staple = staple_foods[0] if staple_foods and staple_foods[0].get('calories', 0) > 0 else None
                    
            if staple is not None:  # 只有当staple有效时才添加
                staple_calories = staple.get('calories', 1) or 1
                staple_quantity = min(1.5, max(0.5, target_calories * 0.4 / staple_calories))
                selected_foods.append({
                    "food": staple,
                    "quantity": staple_quantity
                })
                remaining_calories -= staple_calories * staple_quantity
                num_foods -= 1
    
    # 选择菜肴类食物
    if has_dish and num_foods >= 1:
        dish_foods = food_categories[1]  # 第二个类别是菜肴
        # 从菜肴类别中选择食物
        if dish_foods:
            if nutrition_weights:
                # 使用营养优化选择菜肴
                dish = _select_food_by_nutrition(dish_foods, remaining_calories / max(1, num_foods), nutrition_weights)
            else:
                # 引入随机权重来选择菜肴
                if len(dish_foods) > 1:
                    # 计算每个食物的随机权重，基于热量差异和随机因子
                    weights = []
                    valid_foods = []  # 只包含有效的食物
                    for food in dish_foods:
                        # 确保food是一个字典且有'calories'键
                        if not isinstance(food, dict) or 'calories' not in food or food.get('calories', 0) <= 0:
                            continue  # 跳过无效食物
                        valid_foods.append(food)
                        calorie_diff = abs((food.get('calories', 0) or 0) - remaining_calories / max(1, num_foods))
                        # 权重与热量差异成反比，但加入随机因子增加多样性
                        base_weight = 1 / (1 + calorie_diff/100)
                        random_factor = random.uniform(0.5, 1.5)  # 添加随机因子
                        weights.append(base_weight * random_factor)
                    
                    # 根据权重选择食物
                    if valid_foods and weights:
                        dish = random.choices(valid_foods, weights=weights)[0]
                    elif dish_foods:
                        # 过滤掉热量为0或负数的食物
                        valid_dish_foods = [food for food in dish_foods if food.get('calories', 0) > 0]
                        dish = valid_dish_foods[0] if valid_dish_foods else None
                    else:
                        dish = None
                else:
                    # 确保菜肴热量大于0
                    dish = dish_foods[0] if dish_foods and dish_foods[0].get('calories', 0) > 0 else None
                    
            if dish is not None:  # 只有当dish有效时才添加
                dish_calories = dish.get('calories', 1) or 1
                dish_quantity = min(2.0, max(0.5, remaining_calories * 0.5 / dish_calories))
                selected_foods.append({
                    "food": dish,
                    "quantity": dish_quantity
                })
                remaining_calories -= dish_calories * dish_quantity
                num_foods -= 1
    
    # 从剩余类别中选择其他食物（如水果等）
    # 如果是下午茶（没有主食），则从所有类别中选择
    if has_staple and has_dish:
        available_categories = food_categories[2:]  # 跳过主食和菜肴类别
    elif has_staple:
        available_categories = food_categories[1:]  # 跳过主食类别
    elif has_dish:
        available_categories = food_categories[2:]  # 跳过菜肴类别（如果菜肴是第一个）
    else:
        available_categories = food_categories  # 所有类别都可用（下午茶情况）
    
    # 过滤掉空的类别
    available_categories = [cat for cat in available_categories if cat]
    # 限制类别数量以提高性能
    available_categories = available_categories[:min(len(available_categories), max_items)]
    random.shuffle(available_categories)  # 随机打乱类别顺序以增加多样性
    remaining_categories = available_categories[:num_foods] if num_foods > 0 else []
    
    # 优化：限制每个类别中处理的食物数量
    MAX_FOODS_PER_CATEGORY = 10  # 每个类别最多处理10个食物
    
    for i, food_list in enumerate(remaining_categories):
        # 限制每个类别中处理的食物数量以提高性能
        if len(food_list) > MAX_FOODS_PER_CATEGORY:
            food_list = random.sample(food_list, MAX_FOODS_PER_CATEGORY)
        
        # 过滤掉热量为0或负数的食物
        food_list = [food for food in food_list if food.get("calories", 0) > 0]
        
        if not food_list or remaining_calories <= 0:
            continue
            
        # 根据剩余热量和位置分配目标热量
        if i == len(remaining_categories) - 1:
            # 最后一项使用剩余的所有热量
            target_food_calories = remaining_calories
        else:
            # 灵活分配剩余热量，添加随机因素
            min_calories = remaining_calories * 0.3
            max_calories = remaining_calories * 0.7
            target_food_calories = random.uniform(min_calories, max_calories)
        
        # 选择食物
        if target_food_calories > 0 and len(food_list) > 0:
            if nutrition_weights:
                # 使用营养优化选择食物
                best_food = _select_food_by_nutrition(food_list, target_food_calories, nutrition_weights)
            else:
                # 使用随机权重而不是总是选择最接近的
                if len(food_list) > 1:
                    # 计算每个食物的权重
                    weights = []
                    valid_foods = []  # 只包含有效的食物
                    for food in food_list:
                        # 确保food是一个字典且有'calories'键
                        if not isinstance(food, dict) or 'calories' not in food or food.get('calories', 0) <= 0:
                            continue  # 跳过无效食物
                        valid_foods.append(food)
                        calorie_diff = abs((food.get('calories', 0) or 0) - target_food_calories)
                        # 权重与热量差异成反比，但加入随机因子
                        base_weight = 1 / (1 + calorie_diff/100)
                        random_factor = random.uniform(0.5, 1.5)  # 添加随机因子
                        weights.append(base_weight * random_factor)
                    
                    # 根据权重选择食物
                    if valid_foods and weights:
                        best_food = random.choices(valid_foods, weights=weights)[0]
                    elif food_list:
                        # 过滤掉热量为0或负数的食物
                        valid_food_list = [food for food in food_list if food.get('calories', 0) > 0]
                        best_food = valid_food_list[0] if valid_food_list else None
                    else:
                        best_food = None
                else:
                    # 确保食物热量大于0
                    best_food = food_list[0] if food_list and food_list[0].get('calories', 0) > 0 else None
            
            # 只有当best_food有效时才继续处理
            if best_food is not None:
                # 计算合适的份数 (0.5到2份之间)
                food_calories = best_food.get('calories', 0) or 0
                if food_calories > 0:
                    quantity = min(2.0, max(0.5, target_food_calories / food_calories))
                else:
                    quantity = 1.0
                    
                if quantity > 0:  # 确保数量大于0
                    selected_foods.append({
                        "food": best_food,
                        "quantity": quantity
                    })
                    
                    remaining_calories -= (best_food.get('calories', 0) or 0) * quantity
    
    # 如果还有剩余热量且已选择了一些食物，尝试调整已选食物的份数
    if remaining_calories > 10 and selected_foods:  # 降低阈值到10卡路里
        # 增加已选食物的份数来利用剩余热量
        last_item = selected_foods[-1]
        last_food_calories = last_item["food"].get("calories", 0) or 0
        if last_food_calories > 0:
            additional_quantity = min(0.5, remaining_calories / last_food_calories)  # 限制增加量
            last_item["quantity"] += additional_quantity
    elif remaining_calories < -10 and selected_foods:  # 如果热量超出了目标
        # 减少已选食物的份数来调整热量
        last_item = selected_foods[-1]
        last_food_calories = last_item["food"].get("calories", 0) or 0
        if last_food_calories > 0:
            reduce_quantity = min(0.5, -remaining_calories / last_food_calories)
            last_item["quantity"] = max(0.5, last_item["quantity"] - reduce_quantity)
    
    # 确保返回的食物列表格式正确
    validated_foods = []
    for item in selected_foods:
        if isinstance(item, dict) and "food" in item and "quantity" in item:
            food = item["food"]
            quantity = item["quantity"]
            # 确保食物有效且数量大于0
            if isinstance(food, dict) and 'calories' in food and food['calories'] > 0 and quantity > 0:
                validated_foods.append(item)
    
    # 再次检查总热量是否在目标范围内，如果不在范围内，进行微调
    total_selected_calories = sum(item["food"].get("calories", 0) * item["quantity"] for item in validated_foods)
    if not (target_calories * 0.9 <= total_selected_calories <= target_calories * 1.1) and validated_foods:
        # 微调最后一项食物的份数以符合热量要求
        adjustment_ratio = target_calories / total_selected_calories
        last_item = validated_foods[-1]
        last_item["quantity"] *= adjustment_ratio
        # 确保调整后的份数在合理范围内
        last_item["quantity"] = min(2.0, max(0.5, last_item["quantity"]))
    
    return validated_foods


def _select_food_by_nutrition(food_list, target_calories, nutrition_weights):
    """根据营养成分权重选择食物"""
    if not food_list:
        return None
    
    # 计算每个食物的综合得分
    scores = []
    valid_foods = []
    
    for food in food_list:
        if not isinstance(food, dict) or 'calories' not in food:
            continue
            
        valid_foods.append(food)
        
        # 计算热量匹配度得分（越接近目标热量得分越高）
        calorie_score = 1.0 / (1.0 + abs(food.get('calories', 0) - target_calories) / 100)
        
        # 计算营养成分匹配度得分
        nutrition_score = 0
        for nutrient, weight in nutrition_weights.items():
            if nutrient in food and food[nutrient] > 0:
                # 根据目标营养素权重计算得分
                nutrition_score += weight * (food[nutrient] / food.get('calories', 1))
        
        # 综合得分（热量匹配度占70%，营养匹配度占30%）
        total_score = 0.7 * calorie_score + 0.3 * nutrition_score
        scores.append(total_score)
    
    # 根据得分选择食物
    if valid_foods and scores:
        return random.choices(valid_foods, weights=scores)[0]
    
    # 如果计算失败，返回第一个有效食物
    return valid_foods[0] if valid_foods else None


def daily_plan(calories: float, meals_count=4, include_snack=True, target_nutrition=None):
    """根据目标热量生成每日饮食计划"""
    # 定义四餐的热量分配比例（包括下午茶）
    meal_ratios = {
        "breakfast": 0.25,
        "lunch": 0.35,
        "snack": 0.15,
        "dinner": 0.25
    }
    
    # 确保有足够的餐次数据
    meal_types = list(meal_ratios.keys())
    if meals_count > len(meal_types):
        # 如果需要的餐次多于预定义的餐次类型，则重复使用
        meal_types = (meal_types * ((meals_count // len(meal_types)) + 1))[:meals_count]
    
    plan = []
    
    # 为每餐生成计划
    for i in range(meals_count):
        # 获取当前餐次类型
        meal_type = meal_types[i] if i < len(meal_types) else "lunch"
        
        # 计算当前餐次的目标热量
        target_calories = calories * meal_ratios.get(meal_type, 1.0/meals_count)
        
        # 计算当前餐次的目标营养成分（如果有提供）
        meal_target_nutrition = None
        if target_nutrition:
            meal_target_nutrition = {
                "protein": target_nutrition.get("protein", 0) * meal_ratios.get(meal_type, 1.0/meals_count),
                "fat": target_nutrition.get("fat", 0) * meal_ratios.get(meal_type, 1.0/meals_count),
                "carbs": target_nutrition.get("carbs", 0) * meal_ratios.get(meal_type, 1.0/meals_count),
                "fiber": target_nutrition.get("fiber", 0) * meal_ratios.get(meal_type, 1.0/meals_count)
            }
        
        # 根据餐次类型筛选食物
        if meal_type == "any":
            staple_options = staple_foods
            fruit_options = fruits
            snack_options = snacks
        elif meal_type == "snack":
            # 下午茶只包含水果和零食
            staple_options = []  # 下午茶不包含主食
            fruit_options = [food for food in fruits if food.get("meal_type") in [meal_type, "any"]]
            snack_options = [food for food in snacks if food.get("meal_type") in [meal_type, "any"]]
            
            # 如果筛选后为空，则使用全部水果和零食
            if not fruit_options:
                fruit_options = fruits
            if not snack_options:
                snack_options = snacks
        else:
            staple_options = [food for food in staple_foods if food.get("meal_type") in [meal_type, "any"]]
            fruit_options = [food for food in fruits if food.get("meal_type") in [meal_type, "any"]]
            snack_options = [food for food in snacks if food.get("meal_type") in [meal_type, "any"]]
        
        # 如果筛选后为空，则使用全部食物（除了下午茶的特殊情况）
        if meal_type != "snack":  # 下午茶已经特殊处理过
            if not staple_options:
                staple_options = staple_foods
            if not fruit_options:
                fruit_options = fruits
            if not snack_options:
                snack_options = snacks
        # 对于下午茶，确保至少有一个选项
        elif meal_type == "snack":
            if not fruit_options and not snack_options:
                # 如果都没有，使用所有水果和零食
                fruit_options = fruits
                snack_options = snacks
            
        # 构建食物类别列表
        # 对于下午茶(snack)，不包含主食类别
        if meal_type == "snack":
            food_categories = [fruit_options, snack_options]
        else:
            food_categories = [staple_options, fruit_options, snack_options]
        
        # 选择食物组合
        try:
            selected_foods = select_food_combination(
                food_categories, 
                target_calories, 
                meal_target_nutrition,
                max_items=3
            )
        except Exception as e:
            print(f"选择食物组合时出错: {e}")
            selected_foods = []
        
        # 创建餐食
        try:
            meal = create_meal_from_foods(selected_foods)
            if meal:
                meal["meal_type"] = meal_type
                # 添加目标营养成分信息（仅当提供了目标营养成分时）
                if meal_target_nutrition:
                    meal["target_calories"] = target_calories
                    meal["target_protein"] = meal_target_nutrition["protein"]
                    meal["target_fat"] = meal_target_nutrition["fat"]
                    meal["target_carbs"] = meal_target_nutrition["carbs"]
                plan.append(meal)
            # 如果没有生成餐食但应该有（比如下午茶），则创建一个空餐食
            elif meal_type == "snack":
                plan.append({
                    "name": "未选择食物", 
                    "calories": 0, 
                    "protein": 0, 
                    "fat": 0, 
                    "carbs": 0, 
                    "fiber": 0, 
                    "meal_type": meal_type,
                    "components": []
                })
        except Exception as e:
            print(f"创建餐食时出错: {e}")
            # 添加默认餐食以避免程序崩溃
            plan.append({
                "name": "默认餐食", 
                "calories": 0, 
                "protein": 0, 
                "fat": 0, 
                "carbs": 0, 
                "fiber": 0, 
                "meal_type": meal_type,
                "components": []
            })
    
    # 如果需要添加零食（额外的零食，不是作为餐食组成部分的零食）
    # 只有当不包含下午茶时才添加额外零食
    if include_snack and "snack" not in meal_types:
        # 计算剩余热量（用于额外零食）
        used_calories = sum(meal.get('calories', 0) for meal in plan)
        remaining_calories = calories - used_calories
        
        if remaining_calories > 50:  # 只有当剩余热量大于50千卡时才添加零食
            # 从零食中选择合适的
            snack_options = [snack for snack in snacks if snack.get('calories', 0) <= remaining_calories]
            if snack_options:
                best_snack = min(snack_options, key=lambda s: abs(s.get('calories', 0) - remaining_calories * 0.5))
                # 为零食添加餐次类型
                best_snack["meal_type"] = "snack"
                # 将零食插入到午餐和晚餐之间（索引为2的位置）
                plan.insert(2, best_snack)
    
    return plan


def get_food_by_category(category):
    """根据类别获取食物"""
    if category == "fruits":
        return fruits
    elif category == "staple_foods":
        return staple_foods
    elif category == "prepared_dishes":
        return prepared_dishes
    elif category == "snacks":
        return snacks
    else:
        return []


def search_food_by_name(name, category=None):
    """根据名称搜索食物"""
    if category:
        foods = get_food_by_category(category)
    else:
        foods = fruits + staple_foods + prepared_dishes + snacks
    
    # 搜索匹配的食物
    results = [food for food in foods if name in food["name"]]
    return results


def find_foods_by_calories(target_calories, tolerance=50, category=None):
    """根据目标热量查找食物"""
    if category:
        foods = get_food_by_category(category)
    else:
        foods = fruits + staple_foods + prepared_dishes + snacks
    
    # 查找热量在目标范围内的食物
    results = [food for food in foods 
               if abs(food["calories"] - target_calories) <= tolerance and food["calories"] > 0]
    
    # 如果没有找到足够食物，扩大搜索范围
    if len(results) < 3:  # 降低最低要求到3个
        expanded_results = [food for food in foods 
                           if abs(food["calories"] - target_calories) <= tolerance * 2 and food["calories"] > 0]
        results = expanded_results
    
    # 如果仍然没有找到足够食物，返回所有食物中的随机样本
    if len(results) < 3:  # 降低最低要求到3个
        # 从所有食物中随机选择最多10个
        all_foods = [food for food in (fruits + staple_foods + prepared_dishes + snacks) if food.get("calories", 0) > 0]
        if all_foods:
            results = random.sample(all_foods, min(10, len(all_foods)))
        else:
            results = []
    
    return results


def optimize_meal_plan(meal_plan, preferences=None):
    """根据用户偏好优化饮食计划"""
    # 这里可以实现更复杂的优化逻辑
    # 例如根据口味偏好、营养均衡等进行优化
    return meal_plan


def calculate_meal_nutrition(meal_plan):
    """计算整个饮食计划的营养成分总和"""
    total_nutrition = {
        "calories": 0,
        "protein": 0,
        "fat": 0,
        "carbs": 0,
        "fiber": 0
    }
    
    # 检查meal_plan是否为列表
    if not isinstance(meal_plan, list):
        print(f"DEBUG: meal_plan is not a list: {type(meal_plan)}")
        return total_nutrition
    
    for meal in meal_plan:
        # 确保meal是字典类型
        if not isinstance(meal, dict):
            print(f"DEBUG: meal is not a dict: {type(meal)}")
            continue
            
        # 确保所有营养成分都存在且不是None
        for key in ["calories", "protein", "fat", "carbs", "fiber"]:
            if meal.get(key) is None:
                meal[key] = 0
                
        total_nutrition["calories"] += meal.get("calories", 0) or 0
        total_nutrition["protein"] += meal.get("protein", 0) or 0
        total_nutrition["fat"] += meal.get("fat", 0) or 0
        total_nutrition["carbs"] += meal.get("carbs", 0) or 0
        total_nutrition["fiber"] += meal.get("fiber", 0) or 0
    
    # 确保所有值都是数字类型
    for key in total_nutrition:
        if total_nutrition[key] is None:
            total_nutrition[key] = 0
        # 确保是数字类型
        try:
            total_nutrition[key] = float(total_nutrition[key])
        except (ValueError, TypeError):
            total_nutrition[key] = 0
    
    return total_nutrition
