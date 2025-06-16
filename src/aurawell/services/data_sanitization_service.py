"""
Data Sanitization Service

Handles data privacy, sanitization, and access control for family members.
Ensures proper data isolation based on family roles and permissions.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from copy import deepcopy

from ..models.api_models import (
    FamilyRole,
    DataAccessLevel,
    MemberDataContext,
    DataSanitizationRule,
    SanitizedUserData,
    DataPrivacySettings,
)
from ..services.family_service import FamilyService
from ..core.exceptions import AuthorizationError, ValidationError

logger = logging.getLogger(__name__)


class DataSanitizationService:
    """Service for data sanitization and access control"""

    def __init__(self, family_service: FamilyService):
        self.family_service = family_service
        self._sanitization_rules = self._initialize_sanitization_rules()

    def _initialize_sanitization_rules(self) -> Dict[str, List[DataSanitizationRule]]:
        """Initialize default sanitization rules for different access levels"""
        return {
            DataAccessLevel.BASIC: [
                DataSanitizationRule(
                    field_name="email",
                    access_level=DataAccessLevel.BASIC,
                    sanitization_type="mask",
                    replacement_value="***@***.***",
                ),
                DataSanitizationRule(
                    field_name="phone",
                    access_level=DataAccessLevel.BASIC,
                    sanitization_type="mask",
                    replacement_value="***-***-****",
                ),
                DataSanitizationRule(
                    field_name="weight_kg",
                    access_level=DataAccessLevel.BASIC,
                    sanitization_type="aggregate",
                    replacement_value="weight_range",
                ),
                DataSanitizationRule(
                    field_name="detailed_health_metrics",
                    access_level=DataAccessLevel.BASIC,
                    sanitization_type="remove",
                ),
            ],
            DataAccessLevel.LIMITED: [
                DataSanitizationRule(
                    field_name="email",
                    access_level=DataAccessLevel.LIMITED,
                    sanitization_type="mask",
                    replacement_value="***@domain.com",
                ),
                DataSanitizationRule(
                    field_name="detailed_conversation_history",
                    access_level=DataAccessLevel.LIMITED,
                    sanitization_type="aggregate",
                    replacement_value="conversation_summary",
                ),
            ],
            DataAccessLevel.FULL: [],  # No sanitization for full access
        }

    async def create_member_data_context(
        self,
        requester_user_id: str,
        target_user_id: str,
        target_member_id: Optional[str] = None,
        family_id: Optional[str] = None,
    ) -> MemberDataContext:
        """Create member data context for access control"""
        try:
            # Determine access level based on family relationship
            if requester_user_id == target_user_id:
                # Self-access - full access
                access_level = DataAccessLevel.FULL
                requester_role = None
            elif family_id and target_member_id:
                # Family member access - check permissions
                requester_role = await self._get_requester_role(
                    requester_user_id, family_id
                )
                access_level = self._determine_access_level(requester_role)
            else:
                # No relationship - basic access only
                access_level = DataAccessLevel.BASIC
                requester_role = None

            # Get sanitization rules for this access level
            sanitization_rules = self._sanitization_rules.get(access_level, [])

            # Determine allowed fields based on access level
            allowed_fields = self._get_allowed_fields(access_level, requester_role)

            return MemberDataContext(
                user_id=target_user_id,
                member_id=target_member_id,
                family_id=family_id,
                requester_role=requester_role,
                data_access_level=access_level,
                allowed_fields=allowed_fields,
                sanitization_rules=sanitization_rules,
            )

        except Exception as e:
            logger.error(f"Failed to create member data context: {e}")
            # Default to most restrictive access
            return MemberDataContext(
                user_id=target_user_id,
                member_id=target_member_id,
                family_id=family_id,
                data_access_level=DataAccessLevel.BASIC,
                allowed_fields=["display_name", "basic_info"],
                sanitization_rules=self._sanitization_rules[DataAccessLevel.BASIC],
            )

    async def sanitize_user_data(
        self, raw_data: Dict[str, Any], data_context: MemberDataContext
    ) -> SanitizedUserData:
        """Sanitize user data based on access context"""
        try:
            sanitized_data = deepcopy(raw_data)
            sanitized_fields = []

            # Apply sanitization rules
            for rule in data_context.sanitization_rules:
                if rule.field_name in sanitized_data:
                    sanitized_data, field_sanitized = self._apply_sanitization_rule(
                        sanitized_data, rule
                    )
                    if field_sanitized:
                        sanitized_fields.append(rule.field_name)

            # Filter allowed fields
            if data_context.allowed_fields:
                filtered_data = {}
                for field in data_context.allowed_fields:
                    if field in sanitized_data:
                        filtered_data[field] = sanitized_data[field]
                sanitized_data = filtered_data

            # Create sanitized response
            return SanitizedUserData(
                user_id=data_context.user_id,
                member_id=data_context.member_id,
                display_name=sanitized_data.get("display_name"),
                basic_health_info=self._extract_basic_health_info(sanitized_data),
                activity_summary=self._extract_activity_summary(sanitized_data),
                goals_summary=self._extract_goals_summary(sanitized_data),
                data_access_level=data_context.data_access_level,
                sanitized_fields=sanitized_fields,
                last_updated=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Failed to sanitize user data: {e}")
            raise ValidationError(f"Data sanitization failed: {str(e)}")

    async def check_data_access_permission(
        self,
        requester_user_id: str,
        target_user_id: str,
        data_types: List[str],
        family_id: Optional[str] = None,
    ) -> bool:
        """Check if requester has permission to access target user's data"""
        try:
            # Self-access is always allowed
            if requester_user_id == target_user_id:
                return True

            # Family member access requires family context
            if not family_id:
                return False

            # Check if both users are family members
            requester_is_member = await self.family_service.is_family_member(
                family_id, requester_user_id
            )
            target_is_member = await self.family_service.is_family_member(
                family_id, target_user_id
            )

            if not (requester_is_member and target_is_member):
                return False

            # Get requester's role and permissions
            requester_role = await self._get_requester_role(
                requester_user_id, family_id
            )

            # Check data type permissions
            return self._check_data_type_permissions(requester_role, data_types)

        except Exception as e:
            logger.error(f"Failed to check data access permission: {e}")
            return False

    def _apply_sanitization_rule(
        self, data: Dict[str, Any], rule: DataSanitizationRule
    ) -> tuple[Dict[str, Any], bool]:
        """Apply a single sanitization rule to data"""
        if rule.field_name not in data:
            return data, False

        if rule.sanitization_type == "mask":
            data[rule.field_name] = rule.replacement_value or "***"
        elif rule.sanitization_type == "remove":
            del data[rule.field_name]
        elif rule.sanitization_type == "aggregate":
            data[rule.field_name] = self._aggregate_field_value(
                data[rule.field_name], rule.replacement_value
            )
        elif rule.sanitization_type == "anonymize":
            data[rule.field_name] = self._anonymize_field_value(data[rule.field_name])

        return data, True

    def _aggregate_field_value(self, value: Any, aggregate_type: str) -> Any:
        """Aggregate field value for privacy"""
        if aggregate_type == "weight_range":
            if isinstance(value, (int, float)):
                # Convert to weight range
                if value < 50:
                    return "< 50kg"
                elif value < 70:
                    return "50-70kg"
                elif value < 90:
                    return "70-90kg"
                else:
                    return "> 90kg"
        elif aggregate_type == "conversation_summary":
            if isinstance(value, list):
                return f"Total conversations: {len(value)}"

        return "aggregated_data"

    def _anonymize_field_value(self, value: Any) -> str:
        """Anonymize field value"""
        return f"anonymized_{hash(str(value)) % 10000}"

    async def _get_requester_role(
        self, requester_user_id: str, family_id: str
    ) -> Optional[FamilyRole]:
        """Get requester's role in the family"""
        try:
            family_info = await self.family_service.get_family_info(
                family_id, requester_user_id
            )

            # Find requester's role in family members
            # This is a simplified implementation - in real scenario,
            # you'd query the family members table
            if family_info.owner_id == requester_user_id:
                return FamilyRole.OWNER
            else:
                # Default to viewer for now - should be retrieved from database
                return FamilyRole.VIEWER

        except Exception as e:
            logger.error(f"Failed to get requester role: {e}")
            return None

    def _determine_access_level(self, role: Optional[FamilyRole]) -> DataAccessLevel:
        """Determine access level based on family role"""
        if role == FamilyRole.OWNER:
            return DataAccessLevel.FULL
        elif role == FamilyRole.MANAGER:
            return DataAccessLevel.LIMITED
        elif role == FamilyRole.VIEWER:
            return DataAccessLevel.BASIC
        else:
            return DataAccessLevel.BASIC

    def _get_allowed_fields(
        self, access_level: DataAccessLevel, role: Optional[FamilyRole]
    ) -> List[str]:
        """Get allowed fields based on access level and role"""
        base_fields = ["display_name", "username"]

        if access_level == DataAccessLevel.FULL:
            return []  # Empty list means all fields allowed
        elif access_level == DataAccessLevel.LIMITED:
            return base_fields + [
                "age",
                "gender",
                "activity_level",
                "basic_health_metrics",
                "goals_summary",
                "achievements_summary",
            ]
        else:  # BASIC
            return base_fields + ["age", "activity_level"]

    def _check_data_type_permissions(
        self, role: Optional[FamilyRole], data_types: List[str]
    ) -> bool:
        """Check if role has permission for requested data types"""
        if role == FamilyRole.OWNER:
            return True  # Owner can access all data types
        elif role == FamilyRole.MANAGER:
            # Manager can access most data types except sensitive ones
            restricted_types = ["detailed_conversation_history", "private_notes"]
            return not any(dt in restricted_types for dt in data_types)
        elif role == FamilyRole.VIEWER:
            # Viewer can only access basic data types
            allowed_types = ["basic_health_info", "activity_summary", "goals_summary"]
            return all(dt in allowed_types for dt in data_types)
        else:
            return False

    def _extract_basic_health_info(
        self, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Extract basic health information"""
        basic_fields = ["age", "gender", "height_cm", "activity_level"]
        basic_info = {}

        for field in basic_fields:
            if field in data:
                basic_info[field] = data[field]

        return basic_info if basic_info else None

    def _extract_activity_summary(
        self, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Extract activity summary"""
        activity_fields = ["daily_steps", "weekly_exercise_hours", "activity_level"]
        activity_info = {}

        for field in activity_fields:
            if field in data:
                activity_info[field] = data[field]

        return activity_info if activity_info else None

    def _extract_goals_summary(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract goals summary"""
        if "goals" in data and isinstance(data["goals"], list):
            return {
                "total_goals": len(data["goals"]),
                "active_goals": len(
                    [g for g in data["goals"] if g.get("status") == "active"]
                ),
                "completed_goals": len(
                    [g for g in data["goals"] if g.get("status") == "completed"]
                ),
            }
        return None
