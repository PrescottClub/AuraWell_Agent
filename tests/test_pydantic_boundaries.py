"""
Comprehensive Pydantic Boundary Testing for AuraWell Family-Agent Modules

Tests edge cases, validation boundaries, and data integrity for all Pydantic models
used in family-related functionality.
"""

import pytest
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError

from src.aurawell.models.family_models import (
    FamilyRole,
    DataAccessLevel,
    FamilyCreateRequest,
    FamilyMember,
    FamilyInfo,
    InviteMemberRequest,
    DataPrivacySettings,
)


class TestFamilyCreateRequestBoundaries:
    """Test boundary conditions for FamilyCreateRequest model"""

    def test_valid_family_name_boundaries(self):
        """Test valid family name edge cases"""
        # Minimum length (1 character)
        request = FamilyCreateRequest(name="A")
        assert request.name == "A"

        # Maximum length (100 characters)
        long_name = "A" * 100
        request = FamilyCreateRequest(name=long_name)
        assert request.name == long_name
        assert len(request.name) == 100

    def test_invalid_family_name_boundaries(self):
        """Test invalid family name edge cases"""
        # Empty string
        with pytest.raises(ValidationError) as exc_info:
            FamilyCreateRequest(name="")
        assert "Family name cannot be empty" in str(exc_info.value)

        # Whitespace only
        with pytest.raises(ValidationError) as exc_info:
            FamilyCreateRequest(name="   ")
        assert "Family name cannot be empty" in str(exc_info.value)

        # Too long (101 characters)
        with pytest.raises(ValidationError) as exc_info:
            FamilyCreateRequest(name="A" * 101)
        assert "String should have at most 100 characters" in str(exc_info.value)

    def test_family_description_boundaries(self):
        """Test family description validation boundaries"""
        # Valid description at max length (500 characters)
        long_desc = "A" * 500
        request = FamilyCreateRequest(name="Test Family", description=long_desc)
        assert len(request.description) == 500

        # Too long description (501 characters)
        with pytest.raises(ValidationError) as exc_info:
            FamilyCreateRequest(name="Test Family", description="A" * 501)
        assert "String should have at most 500 characters" in str(exc_info.value)

        # None description (should be allowed)
        request = FamilyCreateRequest(name="Test Family", description=None)
        assert request.description is None

    def test_name_whitespace_trimming(self):
        """Test that family names are properly trimmed"""
        request = FamilyCreateRequest(name="  Test Family  ")
        assert request.name == "Test Family"


class TestFamilyMemberBoundaries:
    """Test boundary conditions for FamilyMember model"""

    def test_valid_family_member_creation(self):
        """Test valid family member creation with all fields"""
        now = datetime.now(timezone.utc)
        member = FamilyMember(
            user_id="user123",
            username="testuser",
            display_name="Test User",
            email="test@example.com",
            role=FamilyRole.MEMBER,
            joined_at=now,
            last_active=now,
            is_active=True,
        )
        assert member.user_id == "user123"
        assert member.role == FamilyRole.MEMBER
        assert member.is_active is True

    def test_family_member_minimal_fields(self):
        """Test family member with only required fields"""
        now = datetime.now(timezone.utc)
        member = FamilyMember(
            user_id="user123",
            username="testuser",
            role=FamilyRole.MEMBER,
            joined_at=now,
        )
        assert member.display_name is None
        assert member.email is None
        assert member.last_active is None
        assert member.is_active is True  # Default value

    def test_family_role_enum_validation(self):
        """Test FamilyRole enum validation"""
        now = datetime.now(timezone.utc)

        # Valid roles
        for role in [
            FamilyRole.OWNER,
            FamilyRole.MANAGER,
            FamilyRole.MEMBER,
            FamilyRole.VIEWER,
        ]:
            member = FamilyMember(
                user_id="user123", username="testuser", role=role, joined_at=now
            )
            assert member.role == role

    def test_datetime_timezone_handling(self):
        """Test datetime timezone handling"""
        # UTC timezone
        utc_time = datetime.now(timezone.utc)
        member = FamilyMember(
            user_id="user123",
            username="testuser",
            role=FamilyRole.MEMBER,
            joined_at=utc_time,
        )
        assert member.joined_at.tzinfo is not None

        # Naive datetime (should be handled gracefully)
        naive_time = datetime.now()
        member = FamilyMember(
            user_id="user123",
            username="testuser",
            role=FamilyRole.MEMBER,
            joined_at=naive_time,
        )
        assert member.joined_at is not None


class TestInviteMemberRequestBoundaries:
    """Test boundary conditions for InviteMemberRequest model"""

    def test_valid_email_formats(self):
        """Test various valid email formats"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@numbers.com",
        ]

        for email in valid_emails:
            request = InviteMemberRequest(email=email)
            assert request.email == email

    def test_invalid_email_formats(self):
        """Test invalid email formats"""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            "",
            "   ",
        ]

        for email in invalid_emails:
            with pytest.raises(ValidationError):
                InviteMemberRequest(email=email)

    def test_role_default_value(self):
        """Test default role assignment"""
        request = InviteMemberRequest(email="test@example.com")
        assert request.role == FamilyRole.MEMBER  # Should default to MEMBER

    def test_custom_message_boundaries(self):
        """Test custom message validation"""
        # Valid message at max length
        long_message = "A" * 500
        request = InviteMemberRequest(
            email="test@example.com", custom_message=long_message
        )
        assert len(request.custom_message) == 500

        # None message (should be allowed)
        request = InviteMemberRequest(email="test@example.com")
        assert request.custom_message is None


class TestFamilyInfoBoundaries:
    """Test boundary conditions for FamilyInfo model"""

    def test_member_count_boundaries(self):
        """Test member count validation"""
        now = datetime.now(timezone.utc)

        # Minimum member count (1)
        family = FamilyInfo(
            family_id="family123",
            name="Test Family",
            owner_id="user123",
            created_at=now,
            updated_at=now,
            member_count=1,
        )
        assert family.member_count == 1

        # Large member count
        family = FamilyInfo(
            family_id="family123",
            name="Test Family",
            owner_id="user123",
            created_at=now,
            updated_at=now,
            member_count=1000,
        )
        assert family.member_count == 1000

    def test_datetime_consistency(self):
        """Test datetime field consistency"""
        now = datetime.now(timezone.utc)
        later = now + timedelta(hours=1)

        family = FamilyInfo(
            family_id="family123",
            name="Test Family",
            owner_id="user123",
            created_at=now,
            updated_at=later,
            member_count=1,
        )
        assert family.created_at < family.updated_at


class TestDataPrivacySettingsBoundaries:
    """Test boundary conditions for DataPrivacySettings model"""

    def test_privacy_level_validation(self):
        """Test privacy level enum validation"""
        for level in DataAccessLevel:
            settings = DataPrivacySettings(
                user_id="user123",
                family_id="family123",
                data_access_level=level,
                allowed_data_types=["health", "activity"],
                data_retention_days=30,
            )
            assert settings.data_access_level == level

    def test_data_retention_boundaries(self):
        """Test data retention days validation"""
        # Minimum retention (1 day)
        settings = DataPrivacySettings(
            user_id="user123",
            family_id="family123",
            data_access_level=DataAccessLevel.FULL,
            allowed_data_types=["health"],
            data_retention_days=1,
        )
        assert settings.data_retention_days == 1

        # Maximum retention (365 days)
        settings = DataPrivacySettings(
            user_id="user123",
            family_id="family123",
            data_access_level=DataAccessLevel.FULL,
            allowed_data_types=["health"],
            data_retention_days=365,
        )
        assert settings.data_retention_days == 365

    def test_allowed_data_types_validation(self):
        """Test allowed data types list validation"""
        # Empty list
        settings = DataPrivacySettings(
            user_id="user123",
            family_id="family123",
            data_access_level=DataAccessLevel.NONE,
            allowed_data_types=[],
            data_retention_days=30,
        )
        assert settings.allowed_data_types == []

        # Multiple data types
        data_types = ["health", "activity", "sleep", "nutrition"]
        settings = DataPrivacySettings(
            user_id="user123",
            family_id="family123",
            data_access_level=DataAccessLevel.FULL,
            allowed_data_types=data_types,
            data_retention_days=30,
        )
        assert settings.allowed_data_types == data_types


@pytest.fixture
def sample_family_data():
    """Fixture providing sample family data for testing"""
    now = datetime.now(timezone.utc)
    return {
        "family_id": "family123",
        "name": "Test Family",
        "description": "A test family for unit testing",
        "owner_id": "user123",
        "created_at": now,
        "updated_at": now,
        "member_count": 3,
        "is_active": True,
    }


@pytest.fixture
def sample_member_data():
    """Fixture providing sample member data for testing"""
    now = datetime.now(timezone.utc)
    return {
        "user_id": "user123",
        "username": "testuser",
        "display_name": "Test User",
        "email": "test@example.com",
        "role": FamilyRole.MEMBER,
        "joined_at": now,
        "last_active": now,
        "is_active": True,
    }
