"""
Health Calculations Utilities

This module provides various health-related calculation functions including
BMI, calorie requirements, heart rate zones, and other health metrics.
"""

import math
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List, Tuple, Union

# Import from shared enums module to avoid duplication
from ..models.enums import (
    Gender,
    ActivityLevel,
    HealthGoal,
    BMICategory,
    HeartRateZone
)


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """
    Calculate Body Mass Index (BMI)
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        
    Returns:
        BMI value
        
    Raises:
        ValueError: If weight or height are invalid
    """
    if weight_kg <= 0:
        raise ValueError("Weight must be positive")
    if height_cm <= 0:
        raise ValueError("Height must be positive")
    
    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)


def get_bmi_category(bmi: float) -> BMICategory:
    """
    Get BMI category based on WHO standards
    
    Args:
        bmi: BMI value
        
    Returns:
        BMI category
    """
    if bmi < 18.5:
        return BMICategory.UNDERWEIGHT
    elif 18.5 <= bmi < 25:
        return BMICategory.NORMAL
    elif 25 <= bmi < 30:
        return BMICategory.OVERWEIGHT
    elif 30 <= bmi < 35:
        return BMICategory.OBESE_CLASS_1
    elif 35 <= bmi < 40:
        return BMICategory.OBESE_CLASS_2
    else:
        return BMICategory.OBESE_CLASS_3


def calculate_bmr(
    weight_kg: float,
    height_cm: float,
    age_years: int,
    gender: Gender
) -> float:
    """
    Calculate Basal Metabolic Rate (BMR) using Mifflin-St Jeor equation
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        age_years: Age in years
        gender: Gender
        
    Returns:
        BMR in calories per day
    """
    if weight_kg <= 0 or height_cm <= 0 or age_years <= 0:
        raise ValueError("All parameters must be positive")
    
    # Mifflin-St Jeor equation
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years
    
    if gender == Gender.MALE:
        bmr += 5
    else:  # FEMALE
        bmr -= 161
    
    return round(bmr, 1)


def calculate_tdee(bmr: float, activity_level: ActivityLevel) -> float:
    """
    Calculate Total Daily Energy Expenditure (TDEE)
    
    Args:
        bmr: Basal Metabolic Rate
        activity_level: Activity level
        
    Returns:
        TDEE in calories per day
    """
    activity_multipliers = {
        ActivityLevel.SEDENTARY: 1.2,
        ActivityLevel.LIGHTLY_ACTIVE: 1.375,
        ActivityLevel.MODERATELY_ACTIVE: 1.55,
        ActivityLevel.VERY_ACTIVE: 1.725,
        ActivityLevel.EXTREMELY_ACTIVE: 1.9
    }
    
    multiplier = activity_multipliers.get(activity_level, 1.2)
    return round(bmr * multiplier, 1)


def calculate_calorie_goal(
    tdee: float,
    health_goal: HealthGoal,
    goal_rate: float = 0.5
) -> float:
    """
    Calculate daily calorie goal based on health objective
    
    Args:
        tdee: Total Daily Energy Expenditure
        health_goal: Health goal
        goal_rate: Target rate (kg per week for weight goals)
        
    Returns:
        Daily calorie goal
    """
    # 1 kg of fat ≈ 7700 calories
    calories_per_kg = 7700
    weekly_calorie_deficit = goal_rate * calories_per_kg
    daily_adjustment = weekly_calorie_deficit / 7
    
    if health_goal == HealthGoal.WEIGHT_LOSS:
        return round(tdee - daily_adjustment, 0)
    elif health_goal == HealthGoal.WEIGHT_GAIN:
        return round(tdee + daily_adjustment, 0)
    else:
        # Maintenance for other goals
        return round(tdee, 0)


def calculate_ideal_weight_range(height_cm: float, gender: Gender) -> Tuple[float, float]:
    """
    Calculate ideal weight range based on BMI 18.5-25
    
    Args:
        height_cm: Height in centimeters
        gender: Gender (for reference, but BMI calculation is same)
        
    Returns:
        Tuple of (min_weight, max_weight) in kg
    """
    if height_cm <= 0:
        raise ValueError("Height must be positive")
    
    height_m = height_cm / 100
    min_weight = 18.5 * (height_m ** 2)
    max_weight = 25 * (height_m ** 2)
    
    return round(min_weight, 1), round(max_weight, 1)


def calculate_max_heart_rate(age: int) -> int:
    """
    Calculate maximum heart rate using age-predicted formula
    
    Args:
        age: Age in years
        
    Returns:
        Maximum heart rate in BPM
    """
    if age <= 0:
        raise ValueError("Age must be positive")
    
    # Traditional formula: 220 - age
    # More recent formula: 207 - (0.7 × age) - we'll use the traditional one
    return 220 - age


def calculate_heart_rate_zones(max_hr: int) -> Dict[HeartRateZone, Tuple[int, int]]:
    """
    Calculate heart rate training zones
    
    Args:
        max_hr: Maximum heart rate
        
    Returns:
        Dictionary mapping zones to (min_hr, max_hr) tuples
    """
    zones = {
        HeartRateZone.RECOVERY: (int(max_hr * 0.5), int(max_hr * 0.6)),
        HeartRateZone.AEROBIC_BASE: (int(max_hr * 0.6), int(max_hr * 0.7)),
        HeartRateZone.AEROBIC: (int(max_hr * 0.7), int(max_hr * 0.8)),
        HeartRateZone.ANAEROBIC: (int(max_hr * 0.8), int(max_hr * 0.9)),
        HeartRateZone.MAXIMUM: (int(max_hr * 0.9), max_hr)
    }
    
    return zones


def calculate_steps_to_calories(steps: int, weight_kg: float) -> float:
    """
    Estimate calories burned from step count
    
    Args:
        steps: Number of steps
        weight_kg: Body weight in kg
        
    Returns:
        Estimated calories burned
    """
    if steps < 0 or weight_kg <= 0:
        raise ValueError("Steps and weight must be positive")
    
    # Rough estimation: 0.04-0.05 calories per step per kg body weight
    # Using 0.045 as average
    calories_per_step_per_kg = 0.045
    
    return round(steps * weight_kg * calories_per_step_per_kg, 1)


def calculate_sleep_efficiency(
    time_in_bed_minutes: int,
    actual_sleep_minutes: int
) -> float:
    """
    Calculate sleep efficiency percentage
    
    Args:
        time_in_bed_minutes: Total time in bed
        actual_sleep_minutes: Actual sleep time
        
    Returns:
        Sleep efficiency as percentage (0-100)
    """
    if time_in_bed_minutes <= 0:
        raise ValueError("Time in bed must be positive")
    if actual_sleep_minutes < 0:
        raise ValueError("Sleep time cannot be negative")
    if actual_sleep_minutes > time_in_bed_minutes:
        raise ValueError("Sleep time cannot exceed time in bed")
    
    efficiency = (actual_sleep_minutes / time_in_bed_minutes) * 100
    return round(efficiency, 1)


def calculate_hydration_goal(weight_kg: float, activity_level: ActivityLevel) -> float:
    """
    Calculate daily water intake goal in liters
    
    Args:
        weight_kg: Body weight in kg
        activity_level: Activity level
        
    Returns:
        Daily water goal in liters
    """
    if weight_kg <= 0:
        raise ValueError("Weight must be positive")
    
    # Base calculation: 35ml per kg body weight
    base_ml = weight_kg * 35
    
    # Adjust for activity level
    activity_adjustments = {
        ActivityLevel.SEDENTARY: 1.0,
        ActivityLevel.LIGHTLY_ACTIVE: 1.1,
        ActivityLevel.MODERATELY_ACTIVE: 1.2,
        ActivityLevel.VERY_ACTIVE: 1.3,
        ActivityLevel.EXTREMELY_ACTIVE: 1.4
    }
    
    multiplier = activity_adjustments.get(activity_level, 1.0)
    total_ml = base_ml * multiplier
    
    # Convert to liters and round
    return round(total_ml / 1000, 1)


def calculate_body_fat_percentage(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: Gender,
    waist_cm: Optional[float] = None,
    neck_cm: Optional[float] = None,
    hip_cm: Optional[float] = None
) -> Optional[float]:
    """
    Calculate body fat percentage using Navy method (if measurements available)
    or estimate from BMI
    
    Args:
        weight_kg: Weight in kg
        height_cm: Height in cm
        age: Age in years
        gender: Gender
        waist_cm: Waist circumference in cm (optional)
        neck_cm: Neck circumference in cm (optional)
        hip_cm: Hip circumference in cm (optional, for females)
        
    Returns:
        Estimated body fat percentage or None if insufficient data
    """
    # Navy method calculation if measurements available
    if waist_cm and neck_cm:
        if gender == Gender.MALE:
            # Male formula
            body_fat = (86.010 * math.log10(waist_cm - neck_cm)) - (70.041 * math.log10(height_cm)) + 36.76
        else:  # FEMALE
            if hip_cm:
                # Female formula
                body_fat = (163.205 * math.log10(waist_cm + hip_cm - neck_cm)) - (97.684 * math.log10(height_cm)) - 78.387
            else:
                body_fat = None
        
        if body_fat is not None:
            return round(max(0, min(100, body_fat)), 1)
    
    # Fallback: estimate from BMI (less accurate)
    bmi = calculate_bmi(weight_kg, height_cm)
    
    if gender == Gender.MALE:
        body_fat = (1.20 * bmi) + (0.23 * age) - 16.2
    else:  # FEMALE
        body_fat = (1.20 * bmi) + (0.23 * age) - 5.4
    
    return round(max(0, min(100, body_fat)), 1)


def calculate_protein_goal(
    weight_kg: float,
    activity_level: ActivityLevel,
    health_goal: HealthGoal
) -> float:
    """
    Calculate daily protein goal in grams
    
    Args:
        weight_kg: Body weight in kg
        activity_level: Activity level
        health_goal: Health goal
        
    Returns:
        Daily protein goal in grams
    """
    if weight_kg <= 0:
        raise ValueError("Weight must be positive")
    
    # Base protein requirement: 0.8g per kg body weight
    base_protein = weight_kg * 0.8
    
    # Adjust for activity level
    if activity_level in [ActivityLevel.VERY_ACTIVE, ActivityLevel.EXTREMELY_ACTIVE]:
        base_protein *= 1.4  # 1.2-1.6g per kg for active individuals
    elif activity_level == ActivityLevel.MODERATELY_ACTIVE:
        base_protein *= 1.2
    
    # Adjust for health goals
    if health_goal == HealthGoal.MUSCLE_GAIN:
        base_protein *= 1.3  # Higher protein for muscle building
    elif health_goal == HealthGoal.WEIGHT_LOSS:
        base_protein *= 1.2  # Higher protein to preserve muscle during weight loss
    
    return round(base_protein, 1)


def calculate_training_load_score(
    duration_minutes: int,
    average_heart_rate: int,
    max_heart_rate: int
) -> int:
    """
    Calculate training load score for a workout session
    
    Args:
        duration_minutes: Workout duration
        average_heart_rate: Average heart rate during workout
        max_heart_rate: Maximum heart rate
        
    Returns:
        Training load score (0-1000+)
    """
    if duration_minutes <= 0 or average_heart_rate <= 0 or max_heart_rate <= 0:
        raise ValueError("All parameters must be positive")
    
    if average_heart_rate > max_heart_rate:
        average_heart_rate = max_heart_rate
    
    # Calculate intensity factor (percentage of max HR)
    intensity_factor = average_heart_rate / max_heart_rate
    
    # Training load = duration × intensity factor²
    training_load = duration_minutes * (intensity_factor ** 2)
    
    return round(training_load)


def calculate_recovery_time(training_load: int, fitness_level: float = 1.0) -> int:
    """
    Estimate recovery time needed after workout
    
    Args:
        training_load: Training load score
        fitness_level: Fitness level multiplier (0.5-2.0)
        
    Returns:
        Estimated recovery time in hours
    """
    if training_load < 0:
        raise ValueError("Training load cannot be negative")
    
    # Base recovery formula
    base_recovery_hours = math.sqrt(training_load) / 2
    
    # Adjust for fitness level (fitter people recover faster)
    adjusted_recovery = base_recovery_hours / fitness_level
    
    return round(max(1, adjusted_recovery))


def calculate_vo2_max_estimate(
    running_speed_kmh: float,
    heart_rate: int,
    age: int
) -> Optional[float]:
    """
    Estimate VO2 max from running data (simplified method)
    
    Args:
        running_speed_kmh: Running speed in km/h
        heart_rate: Heart rate during run
        age: Age in years
        
    Returns:
        Estimated VO2 max in ml/kg/min or None if data insufficient
    """
    if running_speed_kmh <= 0 or heart_rate <= 0 or age <= 0:
        return None
    
    # Simplified estimation formula
    # VO2 = 15.3 × (max_HR / resting_HR)
    # We'll use a simplified approach based on speed and HR
    
    max_hr = calculate_max_heart_rate(age)
    hr_ratio = heart_rate / max_hr
    
    # Very rough estimation
    vo2_max = (running_speed_kmh * 3.5) + (hr_ratio * 20)
    
    return round(max(20, min(80, vo2_max)), 1)  # Reasonable VO2 max range 