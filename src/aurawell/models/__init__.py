"""
AuraWell Data Models

Contains unified health data models and parsing utilities.
Reorganized into functional modules for better maintainability.
"""

# Explicit imports to avoid circular dependencies
from .health_data_model import (
    UnifiedActivitySummary,
    UnifiedSleepSession,
    UnifiedHeartRateSample,
    NutritionEntry,
    HealthPlatform,
    DataQuality,
)
from .user_profile import UserProfile, UserPreferences, HealthGoal, ActivityLevel, Gender

# Import family-related models
from .family_models import (
    FamilyRole, InviteStatus, DataAccessLevel,
    FamilyCreateRequest, FamilyMember, FamilyInfo, FamilySettings,
    InviteMemberRequest, InviteInfo, AcceptInviteRequest, DeclineInviteRequest,
    UpdateMemberRoleRequest, RemoveMemberRequest, TransferOwnershipRequest,
    LeaveFamilyRequest, DeleteFamilyRequest,
    FamilyPermissionInfo, FamilyActivityLog, FamilySettingsRequest,
    SwitchMemberRequest, ActiveMemberInfo,
    DataSanitizationRule, MemberDataContext, DataPrivacySettings,
    FamilyDataAccessRequest, SanitizedUserData,
    FamilyInfoResponse, FamilyListResponse, FamilyMembersResponse,
    InviteMemberResponse, PendingInviteResponse, FamilyPermissionResponse,
    FamilyActivityLogResponse, FamilySettingsResponse, SwitchMemberResponse,
    FamilyDataAccessResponse,
)

# Import chat-related models  
from .chat_models import (
    ChatRequest, ChatData, ChatResponse, ChatMessage,
    HealthSuggestion, QuickReply, HealthChatRequest, HealthChatResponse,
    EnhancedHealthChatRequest,
    ConversationCreateRequest, ConversationResponse, ConversationListItem,
    ConversationListResponse, ChatHistoryRequest, ChatHistoryResponse,
    ConversationHistoryKey, HealthSuggestionsResponse,
)

# Import dashboard-related models
from .dashboard_models import (
    HealthReportRequest, TrendData, HealthMetricSummary, MemberHealthData,
    HealthAlert, HealthReportData, HealthReportResponse,
    LeaderboardRequest, LeaderboardEntry, LeaderboardStats, LeaderboardData,
    LeaderboardResponse,
    ChallengeParticipant, ChallengeProgress, FamilyChallenge, CompletedChallenge,
    UpcomingChallenge, ChallengeSummary, FamilyChallengesData, FamilyChallengesResponse,
    CreateChallengeRequest, CreateChallengeData, CreateChallengeResponse,
    DashboardMetric, FamilyDashboardData, DashboardResponse,
)
