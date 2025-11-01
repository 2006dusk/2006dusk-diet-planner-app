# -*- coding: utf-8 -*-
"""
饮食计划生成模块
负责生成和管理饮食计划的核心逻辑
"""

import os
import random
from nutrition import bmr, tdee, calculate_bmi, recommend_calories, calculate_food_nutrition
from recipe_core import daily_plan, random_recipe, find_foods_by_calories, calculate_meal_nutrition, staple_foods, \
    fruits, snacks, create_meal_from_foods, all_foods, grouped_foods, get_grouped_foods, prepared_dishes


class PlanGenerator:
    """饮食计划生成器"""

    def __init__(self):
        """初始化饮食计划生成器"""
        self.current_plan = []
        self.goal_options = ["lose", "maintain", "gain"]
        self.current_goal_index = 1  # 默认为维持(maintain)

    def generate_plan(self, weight, height, age, gender, goal):
        """生成饮食计划"""
        try:
            # 解析输入数据
            weight_val = float(weight) if weight is not None else 0
            height_val = float(height) if height is not None else 0
            age_val = int(age) if age is not None else 0
            gender_val = "男" if gender == "男" else "女"

            # 确定目标
            if goal == "lose":
                goal_val = "lose"
            elif goal == "maintain":
                goal_val = "maintain"
            else:
                goal_val = "gain"

            # 计算基础代谢率和总消耗
            bmr_val = bmr(weight_val, height_val, age_val, gender_val)
            tdee_val = tdee(bmr_val)

            # 根据目标推荐热量摄入
            recommended_calories = recommend_calories(tdee_val, goal_val)

            # 计算BMI
            bmi_val = calculate_bmi(weight_val, height_val)

            # 计算推荐的宏量营养素分布
            target_nutrition = self._calculate_target_nutrition(recommended_calories, weight_val)

            # 生成每日饮食计划框架（只包含营养需求，不包含具体食物）
            self.current_plan = self._generate_nutrition_only_plan(recommended_calories, target_nutrition)

            # 计算总营养成分
            total_nutrition = target_nutrition.copy()

            # 确保计划总热量与推荐热量一致
            total_nutrition["calories"] = recommended_calories

            return {
                "plan": self.current_plan,
                "bmr": bmr_val,
                "tdee": tdee_val,
                "recommended_calories": recommended_calories,
                "bmi": bmi_val,
                "total_nutrition": total_nutrition,
                "goal": goal_val
            }
        except Exception as e:
            raise Exception(f"生成计划时出错: {str(e)}")

    def _calculate_target_nutrition(self, calories, weight):
        """计算目标营养成分分布"""
        # 根据体重计算蛋白质需求（每公斤体重1.2-1.8克）
        protein_grams = weight * 1.5  # 中等值

        # 根据热量计算脂肪需求（占总热量的20-35%）
        fat_calories = calories * 0.25
        fat_grams = fat_calories / 9  # 每克脂肪9千卡

        # 根据剩余热量计算碳水化合物需求
        used_calories = (protein_grams * 4) + (fat_grams * 9)  # 蛋白质每克4千卡
        carbs_calories = calories - used_calories
        carbs_grams = carbs_calories / 4  # 每克碳水4千卡

        # 纤维需求（一般为碳水化合物的10%）
        fiber_grams = carbs_grams * 0.1

        return {
            "calories": calories,
            "protein": protein_grams,
            "fat": fat_grams,
            "carbs": carbs_grams,
            "fiber": fiber_grams
        }

    def _generate_nutrition_only_plan(self, total_calories, target_nutrition):
        """生成仅包含营养需求的计划框架"""
        # 定义四餐的热量分配比例
        meal_ratios = {
            "breakfast": 0.25,
            "lunch": 0.35,
            "snack": 0.15,
            "dinner": 0.25
        }

        plan = []
        meal_types = ["breakfast", "lunch", "snack", "dinner"]

        # 为每餐生成营养需求
        for meal_type in meal_types:
            # 计算当前餐次的目标热量
            target_calories = total_calories * meal_ratios.get(meal_type, 0.25)

            # 计算当前餐次的目标营养成分
            meal_target_nutrition = {
                "protein": target_nutrition.get("protein", 0) * meal_ratios.get(meal_type, 0.25),
                "fat": target_nutrition.get("fat", 0) * meal_ratios.get(meal_type, 0.25),
                "carbs": target_nutrition.get("carbs", 0) * meal_ratios.get(meal_type, 0.25),
                "fiber": target_nutrition.get("fiber", 0) * meal_ratios.get(meal_type, 0.25)
            }

            # 创建餐食框架（仅包含营养需求，不包含具体食物）
            meal = {
                "name": f"{'早餐' if meal_type == 'breakfast' else '午餐' if meal_type == 'lunch' else '下午茶' if meal_type == 'snack' else '晚餐'}",
                "calories": 0,  # 实际热量为0，因为没有选择具体食物
                "protein": 0,  # 实际蛋白质为0
                "fat": 0,  # 实际脂肪为0
                "carbs": 0,  # 实际碳水为0
                "fiber": 0,  # 实际纤维为0
                "meal_type": meal_type,
                "components": [],  # 空的食物组件列表
                "target_calories": target_calories,
                "target_protein": meal_target_nutrition["protein"],
                "target_fat": meal_target_nutrition["fat"],
                "target_carbs": meal_target_nutrition["carbs"],
                "target_fiber": meal_target_nutrition["fiber"]
            }

            plan.append(meal)

        return plan

    def generate_random_plan(self, weight, height, age, gender, goal):
        """随机生成饮食计划"""
        try:
            # 解析输入数据
            weight_val = float(weight) if weight is not None else 0
            height_val = float(height) if height is not None else 0
            age_val = int(age) if age is not None else 0
            gender_val = "男" if gender == "男" else "女"

            # 确定目标
            if goal == "lose":
                goal_val = "lose"
            elif goal == "maintain":
                goal_val = "maintain"
            else:
                goal_val = "gain"

            # 计算基础代谢率和总消耗
            bmr_val = bmr(weight_val, height_val, age_val, gender_val)
            tdee_val = tdee(bmr_val)

            # 根据目标推荐热量摄入
            recommended_calories = recommend_calories(tdee_val, goal_val)

            # 计算BMI
            bmi_val = calculate_bmi(weight_val, height_val)

            # 计算推荐的宏量营养素分布
            target_nutrition = self._calculate_target_nutrition(recommended_calories, weight_val)

            # 生成每日饮食计划（包含随机食物）
            self.current_plan = self._generate_random_plan_with_foods(recommended_calories, target_nutrition)

            # 计算总营养成分
            total_nutrition = target_nutrition.copy()

            # 确保计划总热量与推荐热量一致
            total_nutrition["calories"] = recommended_calories

            return {
                "plan": self.current_plan,
                "bmr": bmr_val,
                "tdee": tdee_val,
                "recommended_calories": recommended_calories,
                "bmi": bmi_val,
                "total_nutrition": total_nutrition,
                "goal": goal_val
            }
        except Exception as e:
            raise Exception(f"随机生成计划时出错: {str(e)}")

    def _generate_random_plan_with_foods(self, total_calories, target_nutrition):
        """生成包含随机食物的完整计划，合理分配三餐热量"""
        # 定义四餐的热量分配比例
        meal_ratios = {
            "breakfast": 0.25,
            "lunch": 0.35,
            "snack": 0.15,
            "dinner": 0.25
        }

        plan = []
        meal_types = ["breakfast", "lunch", "snack", "dinner"]
        meal_names = ["早餐", "午餐", "下午茶", "晚餐"]

        # 为每餐生成随机食物
        for i, meal_type in enumerate(meal_types):
            # 计算当前餐次的目标热量
            target_calories = total_calories * meal_ratios.get(meal_type, 0.25)
            
            # 为每餐生成随机食物组合，允许10%的热量浮动
            min_calories = target_calories * 0.9
            max_calories = target_calories * 1.1
            
            # 尝试生成符合热量范围的食物组合
            foods = []
            attempts = 0
            while attempts < 50:  # 增加尝试次数到50次以提高成功率
                # 根据餐次类型使用不同的策略
                if meal_type == "breakfast":
                    # 早餐使用主食+菜肴的组合
                    foods = self._generate_meal_with_staple_and_dish(target_calories, "breakfast")
                elif meal_type == "lunch":
                    # 午餐使用主食+菜肴的组合
                    foods = self._generate_meal_with_staple_and_dish(target_calories, "lunch")
                elif meal_type == "dinner":
                    # 晚餐使用主食+菜肴的组合
                    foods = self._generate_meal_with_staple_and_dish(target_calories, "dinner")
                else:  # snack (下午茶)
                    # 下午茶使用水果或零食
                    foods = self._generate_snack_foods(target_calories)
                
                # 计算总热量
                total_food_calories = sum(item.get("food", {}).get("calories", 0) * item.get("quantity", 1.0) for item in foods if item.get("food", {}).get("calories", 0) > 0)
                
                # 检查是否在目标范围内
                if min_calories <= total_food_calories <= max_calories and total_food_calories > 0:
                    break
                
                attempts += 1
            
            # 如果多次尝试后仍未找到合适的组合，则使用更宽松的热量范围
            if not foods:
                # 扩大热量范围到20%
                min_calories = target_calories * 0.8
                max_calories = target_calories * 1.2
                
                # 再次尝试生成食物
                if meal_type in ["breakfast", "lunch", "dinner"]:
                    foods = self._generate_meal_with_staple_and_dish(target_calories, meal_type)
                else:  # snack
                    foods = self._generate_snack_foods(target_calories)
                
                # 重新计算总热量
                total_food_calories = sum(item.get("food", {}).get("calories", 0) * item.get("quantity", 1.0) for item in foods if item.get("food", {}).get("calories", 0) > 0)
                if not (min_calories <= total_food_calories <= max_calories and total_food_calories > 0):
                    # 如果仍然不符合，则使用最后一次生成的食物
                    pass  # 使用已生成的食物
            
            # 创建完整餐食
            meal = create_meal_from_foods(foods)
            if meal:
                meal["meal_type"] = meal_type
                meal["name"] = meal_names[i]
            else:
                # 如果创建失败，创建一个空的餐食
                meal = {
                    "name": meal_names[i],
                    "calories": 0,
                    "protein": 0,
                    "fat": 0,
                    "carbs": 0,
                    "fiber": 0,
                    "meal_type": meal_type,
                    "components": foods
                }
            
            plan.append(meal)

        # 检查总热量是否在计划热量的10%范围内
        total_plan_calories = sum(meal.get("calories", 0) for meal in plan)
        if not (total_calories * 0.9 <= total_plan_calories <= total_calories * 1.1):
            # 如果总热量超出范围，重新调整各餐次的食物
            calories_ratio = total_calories / total_plan_calories if total_plan_calories > 0 else 1
            for meal in plan:
                # 调整每餐的食物份数以符合总热量要求
                for component in meal.get("components", []):
                    component["quantity"] *= calories_ratio
                
                # 重新计算餐食营养成分
                # 注意：create_meal_from_foods期望接收的是食物列表，而不是components
                updated_meal = create_meal_from_foods(meal.get("components", []))
                if updated_meal:
                    meal.update(updated_meal)

        return plan

    def _generate_meal_with_staple_and_dish(self, target_calories, meal_type):
        """生成包含主食和菜肴的餐食"""
        # 根据餐次类型筛选食物
        if meal_type == "breakfast":
            staple_options = [food for food in staple_foods if food.get("meal_type") in [meal_type, "any"]]
            dish_options = [food for food in prepared_dishes if food.get("meal_type") in [meal_type, "any"]]
        elif meal_type == "lunch":
            staple_options = [food for food in staple_foods if food.get("meal_type") in [meal_type, "any"]]
            dish_options = [food for food in prepared_dishes if food.get("meal_type") in [meal_type, "any"]]
        elif meal_type == "dinner":
            staple_options = [food for food in staple_foods if food.get("meal_type") in [meal_type, "any"]]
            dish_options = [food for food in prepared_dishes if food.get("meal_type") in [meal_type, "any"]]
        else:
            # 默认情况
            staple_options = staple_foods
            dish_options = prepared_dishes
        
        # 如果筛选后为空，则使用全部食物
        if not staple_options:
            staple_options = staple_foods
        if not dish_options:
            dish_options = prepared_dishes
            
        foods = []
        
        # 确保至少有一个主食和一个菜肴
        if staple_options:
            # 选择主食（约占总热量的50-60%）
            staple_target_calories = target_calories * random.uniform(0.5, 0.6)
            staple = self._select_food_by_calories(staple_options, staple_target_calories)
            if staple:
                # 计算主食的合适份数
                staple_calories = staple.get("calories", 0)
                if staple_calories > 0:
                    staple_quantity = min(2.0, max(0.5, staple_target_calories / staple_calories))
                    foods.append({
                        "food": staple,
                        "quantity": staple_quantity
                    })
        
        if dish_options:
            # 选择菜肴（约占总热量的40-50%）
            dish_target_calories = target_calories * random.uniform(0.4, 0.5)
            dish = self._select_food_by_calories(dish_options, dish_target_calories)
            if dish:
                # 计算菜肴的合适份数
                dish_calories = dish.get("calories", 0)
                if dish_calories > 0:
                    dish_quantity = min(2.0, max(0.5, dish_target_calories / dish_calories))
                    foods.append({
                        "food": dish,
                        "quantity": dish_quantity
                    })
        
        return foods

    def _generate_snack_foods(self, target_calories):
        """生成下午茶食物"""
        # 下午茶使用水果或零食
        snack_options = fruits + snacks
        if not snack_options:
            snack_options = fruits + snacks  # 确保有选项
            
        foods = []
        if snack_options:
            snack = self._select_food_by_calories(snack_options, target_calories)
            if snack:
                # 计算零食的合适份数
                snack_calories = snack.get("calories", 0)
                if snack_calories > 0:
                    snack_quantity = min(2.0, max(0.5, target_calories / snack_calories))
                    foods.append({
                        "food": snack,
                        "quantity": snack_quantity
                    })
        
        return foods

    def _select_food_by_calories(self, food_list, target_calories):
        """根据目标热量选择食物"""
        if not food_list:
            return None
            
        # 过滤掉热量为0或负数的食物
        valid_foods = [food for food in food_list if food.get("calories", 0) > 0]
        if not valid_foods:
            return None
            
        # 计算每个食物与目标热量的差异
        food_diffs = [(food, abs(food.get("calories", 0) - target_calories)) for food in valid_foods]
        
        # 选择热量最接近目标的食物
        best_food, _ = min(food_diffs, key=lambda x: x[1])
        return best_food

    def add_food_to_meal(self, meal_index, food_data):
        """向餐食中添加食物"""
        print(f"DEBUG: add_food_to_meal called with meal_index={meal_index}, food_data={food_data}")
        print(f"DEBUG: current_plan={self.current_plan}")
        print(f"DEBUG: current_plan length={len(self.current_plan) if self.current_plan else 'None'}")
        if self.current_plan and 0 <= meal_index < len(self.current_plan):
            print(f"DEBUG: meal_index is valid, current_plan length={len(self.current_plan)}")
            meal = self.current_plan[meal_index]
            print(f"DEBUG: meal data={meal}")
            # 确保components存在
            if "components" not in meal:
                meal["components"] = []
                print("DEBUG: Created empty components list")

            # 使用传入的食物数据创建完整食物数据结构
            food_data_copy = food_data.copy() if isinstance(food_data, dict) else {}  # 复制以避免修改原始数据
            print(f"DEBUG: food_data_copy={food_data_copy}")

            meal["components"].append({
                "food": food_data_copy,
                "quantity": 1.0
            })
            print(f"DEBUG: Added food to components, components count={len(meal['components'])}")

            # 重新计算餐食营养成分
            updated_meal = create_meal_from_foods(meal["components"])
            print(f"DEBUG: create_meal_from_foods returned: {updated_meal}")
            if updated_meal:
                # 更新当前计划中的餐食
                self.current_plan[meal_index] = updated_meal
                print("DEBUG: Updated meal in current_plan")
                return updated_meal
            else:
                print("DEBUG: create_meal_from_foods returned None")
        else:
            print("DEBUG: Invalid meal_index or current_plan is None/empty")
        return None

    def replace_food_in_meal(self, meal_index, position, food_data):
        """替换餐食中的指定位置食物"""
        print(
            f"DEBUG: replace_food_in_meal called with meal_index={meal_index}, position={position}, food_data={food_data}")
        print(f"DEBUG: current_plan={self.current_plan}")
        print(f"DEBUG: current_plan length={len(self.current_plan) if self.current_plan else 'None'}")
        if self.current_plan and 0 <= meal_index < len(self.current_plan):
            print(f"DEBUG: meal_index is valid, current_plan length={len(self.current_plan)}")
            meal = self.current_plan[meal_index]
            print(f"DEBUG: meal data={meal}")
            # 确保components存在
            if "components" not in meal:
                meal["components"] = []
                print("DEBUG: Created empty components list")

            # 使用传入的食物数据创建完整食物数据结构
            food_data_copy = food_data.copy() if isinstance(food_data, dict) else {}  # 复制以避免修改原始数据
            print(f"DEBUG: food_data_copy={food_data_copy}")

            # 确保位置有效
            if 0 <= position < len(meal["components"]):
                # 替换指定位置的食物
                print(f"DEBUG: Replacing food at position {position}")
                meal["components"][position] = {
                    "food": food_data_copy,
                    "quantity": 1.0
                }
            else:
                # 如果位置超出范围，添加新食物
                print(f"DEBUG: Position {position} out of range, appending new food")
                meal["components"].append({
                    "food": food_data_copy,
                    "quantity": 1.0
                })

            # 重新计算餐食营养成分
            updated_meal = create_meal_from_foods(meal["components"])
            print(f"DEBUG: create_meal_from_foods returned: {updated_meal}")
            if updated_meal:
                updated_meal["meal_type"] = meal.get("meal_type", "any")
                self.current_plan[meal_index] = updated_meal
                print("DEBUG: Updated meal in current_plan")

            # 修复：返回更新后的单个餐次而不是整个计划
            return updated_meal
        else:
            print(f"DEBUG: meal_index out of range: {meal_index} or current_plan is empty")
        return None

    def get_meal_info(self, meal_index):
        """获取指定餐次的信息，用于局部更新"""
        if 0 <= meal_index < len(self.current_plan):
            return self.current_plan[meal_index]
        return None

    def remove_food_from_meal(self, meal_index, position):
        """从餐食中删除指定位置的食物"""
        if 0 <= meal_index < len(self.current_plan):
            meal = self.current_plan[meal_index]
            # 确保components存在
            if "components" not in meal:
                meal["components"] = []

            # 确保位置有效
            if 0 <= position < len(meal["components"]):
                # 删除指定位置的食物
                meal["components"].pop(position)

                # 重新计算餐食营养成分
                updated_meal = create_meal_from_foods(meal["components"])
                if updated_meal:  # 确保更新成功
                    updated_meal["meal_type"] = meal.get("meal_type", "any")
                    self.current_plan[meal_index] = updated_meal
                else:
                    # 如果更新失败，创建一个空餐食
                    self.current_plan[meal_index] = {
                        "name": "未选择食物",
                        "calories": 0,
                        "protein": 0,
                        "fat": 0,
                        "carbs": 0,
                        "fiber": 0,
                        "meal_type": meal.get("meal_type", "any"),
                        "components": []
                    }

                # 返回更新后的单个餐次
                return self.current_plan[meal_index]
        return None

    def switch_goal(self, user_data):
        """切换目标"""
        # 切换到下一个目标
        self.current_goal_index = (self.current_goal_index + 1) % len(self.goal_options)

        # 更新用户数据中的目标
        goal = self.goal_options[self.current_goal_index]
        user_data["goal"] = goal

        return goal