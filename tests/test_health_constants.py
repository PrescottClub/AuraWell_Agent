"""
Unit tests for health_constants module

Tests the get_health_constant and get_category_constants functions
to verify correct retrieval of constants and handling of missing keys.
"""

import pytest
from src.aurawell.config.health_constants import (
    get_health_constant,
    get_category_constants,
    HEALTH_CONSTANTS,
)


class TestGetHealthConstant:
    """Test cases for get_health_constant function"""

    def test_get_existing_constant_exact_match(self):
        """Test retrieving existing constant with exact key match"""
        result = get_health_constant("steps", "DEFAULT_DAILY_TARGET")
        assert result == 10000

    def test_get_existing_constant_lowercase_key(self):
        """Test retrieving constant with lowercase key"""
        result = get_health_constant("steps", "default_daily_target")
        assert result == 10000

    def test_get_existing_constant_mixed_case(self):
        """Test retrieving constant with mixed case key"""
        result = get_health_constant("steps", "Default_Daily_Target")
        assert result == 10000

    def test_get_existing_constant_camel_case(self):
        """Test retrieving constant with camelCase key"""
        result = get_health_constant("steps", "defaultDailyTarget")
        assert result == 10000

    def test_get_nonexistent_category(self):
        """Test retrieving from non-existent category returns default"""
        result = get_health_constant("nonexistent", "some_key", "default_value")
        assert result == "default_value"

    def test_get_nonexistent_key(self):
        """Test retrieving non-existent key returns default"""
        result = get_health_constant("steps", "NONEXISTENT_KEY", "default_value")
        assert result == "default_value"

    def test_get_nonexistent_key_no_default(self):
        """Test retrieving non-existent key without default returns None"""
        result = get_health_constant("steps", "NONEXISTENT_KEY")
        assert result is None

    def test_get_sleep_constants(self):
        """Test retrieving sleep-related constants"""
        result = get_health_constant("sleep", "RECOMMENDED_HOURS")
        assert result == 8.0
        
        result = get_health_constant("sleep", "recommended_hours")
        assert result == 8.0

    def test_get_calories_constants(self):
        """Test retrieving calories-related constants"""
        result = get_health_constant("calories", "DAILY_INTAKE_BASE")
        assert result == 2000
        
        result = get_health_constant("calories", "daily_intake_base")
        assert result == 2000

    def test_get_heart_rate_constants(self):
        """Test retrieving heart rate constants"""
        result = get_health_constant("heart_rate", "RESTING_HR_NORMAL")
        assert result == 68

    def test_get_nested_constants(self):
        """Test retrieving nested constants like HR_ZONE_MULTIPLIERS"""
        result = get_health_constant("heart_rate", "HR_ZONE_MULTIPLIERS")
        expected = {
            "rest": 1.0,
            "fat_burn": 1.2,
            "cardio": 1.5,
            "peak": 1.8,
        }
        assert result == expected

    def test_get_list_constants(self):
        """Test retrieving list constants"""
        result = get_health_constant("challenges", "CHALLENGE_TYPES")
        expected = ["activity", "nutrition", "sleep", "weight_loss", "consistency"]
        assert result == expected

    def test_empty_category_string(self):
        """Test handling empty category string"""
        result = get_health_constant("", "some_key", "default")
        assert result == "default"

    def test_empty_key_string(self):
        """Test handling empty key string"""
        result = get_health_constant("steps", "", "default")
        assert result == "default"

    def test_none_category(self):
        """Test handling None category"""
        result = get_health_constant(None, "some_key", "default")
        assert result == "default"

    def test_none_key(self):
        """Test handling None key"""
        result = get_health_constant("steps", None, "default")
        assert result == "default"


class TestGetCategoryConstants:
    """Test cases for get_category_constants function"""

    def test_get_existing_category(self):
        """Test retrieving existing category constants"""
        result = get_category_constants("steps")
        expected = {
            "DEFAULT_DAILY_TARGET": 10000,
            "LOW_ACTIVITY_THRESHOLD": 5000,
            "MODERATE_ACTIVITY_BASE": 8500,
            "HIGH_ACTIVITY_BASE": 12000,
            "EXCELLENT_ACTIVITY_BASE": 15000,
            "VARIANCE_SAMPLES": [8500, 9200, 7800],
        }
        assert result == expected

    def test_get_nonexistent_category(self):
        """Test retrieving non-existent category returns empty dict"""
        result = get_category_constants("nonexistent")
        assert result == {}

    def test_get_sleep_category(self):
        """Test retrieving sleep category constants"""
        result = get_category_constants("sleep")
        assert "RECOMMENDED_HOURS" in result
        assert "MINIMUM_HOURS" in result
        assert "OPTIMAL_HOURS" in result
        assert result["RECOMMENDED_HOURS"] == 8.0

    def test_get_all_categories(self):
        """Test that all expected categories exist"""
        expected_categories = [
            "steps", "sleep", "calories", "heart_rate", "weight",
            "trends", "challenges", "reports", "alerts", "family", "test_data"
        ]
        
        for category in expected_categories:
            result = get_category_constants(category)
            assert isinstance(result, dict)
            assert len(result) > 0

    def test_category_constants_immutability(self):
        """Test that returned constants are not accidentally modified"""
        result1 = get_category_constants("steps")
        result2 = get_category_constants("steps")
        
        # Modify result1
        result1["NEW_KEY"] = "new_value"
        
        # result2 should not be affected
        assert "NEW_KEY" not in result2

    def test_empty_category_string(self):
        """Test handling empty category string"""
        result = get_category_constants("")
        assert result == {}

    def test_none_category(self):
        """Test handling None category"""
        result = get_category_constants(None)
        assert result == {}


class TestHealthConstantsIntegrity:
    """Test cases for overall health constants integrity"""

    def test_all_categories_exist(self):
        """Test that all expected categories exist in HEALTH_CONSTANTS"""
        expected_categories = [
            "steps", "sleep", "calories", "heart_rate", "weight",
            "trends", "challenges", "reports", "alerts", "family", "test_data"
        ]
        
        for category in expected_categories:
            assert category in HEALTH_CONSTANTS

    def test_constants_are_not_empty(self):
        """Test that all categories have at least one constant"""
        for category, constants in HEALTH_CONSTANTS.items():
            assert len(constants) > 0, f"Category {category} is empty"

    def test_numeric_constants_are_valid(self):
        """Test that numeric constants have valid values"""
        # Test some key numeric constants
        assert get_health_constant("steps", "DEFAULT_DAILY_TARGET") > 0
        assert get_health_constant("sleep", "RECOMMENDED_HOURS") > 0
        assert get_health_constant("calories", "DAILY_INTAKE_BASE") > 0
        assert get_health_constant("heart_rate", "RESTING_HR_NORMAL") > 0

    def test_list_constants_are_valid(self):
        """Test that list constants are properly formatted"""
        challenge_types = get_health_constant("challenges", "CHALLENGE_TYPES")
        assert isinstance(challenge_types, list)
        assert len(challenge_types) > 0
        
        variance_samples = get_health_constant("steps", "VARIANCE_SAMPLES")
        assert isinstance(variance_samples, list)
        assert len(variance_samples) > 0

    def test_dict_constants_are_valid(self):
        """Test that dictionary constants are properly formatted"""
        hr_zones = get_health_constant("heart_rate", "HR_ZONE_MULTIPLIERS")
        assert isinstance(hr_zones, dict)
        assert len(hr_zones) > 0
        assert all(isinstance(v, (int, float)) for v in hr_zones.values())
