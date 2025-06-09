import pytest
from datetime import datetime, date, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 导入被测试的模型
from aurawell.database.models import (
    Base, UserProfileDB, ActivitySummaryDB, SleepSessionDB,
    HeartRateSampleDB, NutritionEntryDB, AchievementProgressDB,
    PlatformConnectionDB
)


# 创建内存数据库引擎
@pytest.fixture(scope="module")
def engine():
    return create_engine("sqlite:///:memory:")


# 初始化数据库会话，并且每一次测试完毕后清除所有临时数据
@pytest.fixture
def db_session(engine):
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    # 清除所有数据而非仅回滚
    session.rollback()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()


# 创建基础用户数据
@pytest.fixture
def sample_user(db_session):
    user = UserProfileDB(
        user_id="user_123",
        display_name="Test User",
        email="test@example.com"
    )
    db_session.add(user)
    db_session.commit()
    return user


# 测试用户模型
class TestUserProfileDB:
    def test_create_user(self, db_session):
        user = UserProfileDB(
            user_id="user_456",
            email="new@example.com"
        )
        db_session.add(user)
        db_session.commit()
        assert user.user_id == "user_456"

    def test_email_uniqueness(self, db_session, sample_user):
        duplicate_user = UserProfileDB(
            user_id="user_789",
            email=sample_user.email
        )
        db_session.add(duplicate_user)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_json_fields_defaults(self, db_session):
        user = UserProfileDB(user_id="user_defaults")
        db_session.add(user)
        db_session.commit()
        assert user.notification_preferences == {}
        assert user.connected_platforms == []

    def test_relationship_access(self, sample_user):
        assert isinstance(sample_user.activity_summaries, list)
        assert isinstance(sample_user.sleep_sessions, list)


# 测试活动摘要模型
class TestActivitySummaryDB:
    def test_create_activity(self, db_session, sample_user):
        activity = ActivitySummaryDB(
            user_id=sample_user.user_id,
            date=date.today(),
            source_platform="TestPlatform",
            recorded_at=datetime.utcnow()
        )
        db_session.add(activity)
        db_session.commit()
        assert activity.id is not None

    def test_unique_constraint(self, db_session, sample_user):
        common_data = {
            "user_id": sample_user.user_id,
            "date": date(2023, 1, 1),
            "source_platform": "FitTrack",
            "recorded_at": datetime.utcnow()
        }

        act1 = ActivitySummaryDB(**common_data)
        db_session.add(act1)
        db_session.commit()

        act2 = ActivitySummaryDB(**common_data)
        db_session.add(act2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_relationship(self, db_session, sample_user):
        activity = ActivitySummaryDB(
            user_id=sample_user.user_id,
            date=date.today(),
            source_platform="Test",
            recorded_at=datetime.utcnow()
        )
        db_session.add(activity)
        db_session.commit()

        assert activity.user.user_id == sample_user.user_id
        assert activity in sample_user.activity_summaries


# 测试睡眠模型
class TestSleepSessionDB:
    def test_sleep_duration_calculation(self, db_session, sample_user):
        sleep = SleepSessionDB(
            user_id=sample_user.user_id,
            date=date.today(),
            bedtime_utc=datetime(2023, 1, 1, 22, 0),
            wake_time_utc=datetime(2023, 1, 2, 6, 30),
            source_platform="SleepTracker",
            recorded_at=datetime.utcnow()
        )
        db_session.add(sleep)
        db_session.commit()

        assert sleep.total_sleep_minutes == 510  # 8.5小时

    def test_midnight_crossing_sleep(self, db_session, sample_user):
        """测试跨午夜的睡眠时长计算"""
        sleep = SleepSessionDB(
            user_id=sample_user.user_id,
            date=date.today(),
            bedtime_utc=datetime(2023, 1, 1, 23, 0),
            wake_time_utc=datetime(2023, 1, 1, 6, 30),  # 第二天早上
            source_platform="SleepTracker",
            recorded_at=datetime.utcnow()
        )
        db_session.add(sleep)
        db_session.commit()

        # 7.5小时睡眠 (23:00到06:30)
        assert sleep.total_sleep_minutes == 450

    def test_missing_times(self, db_session, sample_user):
        """测试缺少就寝/起床时间的情况"""
        sleep = SleepSessionDB(
            user_id=sample_user.user_id,
            date=date.today(),
            source_platform="SleepTracker",
            recorded_at=datetime.utcnow()
        )
        db_session.add(sleep)
        db_session.commit()

        assert sleep.total_sleep_minutes is None

    def test_invalid_times(self, db_session, sample_user):
        """测试无效时间组合（起床时间在就寝时间之前）"""
        sleep = SleepSessionDB(
            user_id=sample_user.user_id,
            date=date.today(),
            bedtime_utc=datetime(2023, 1, 1, 10, 0),
            wake_time_utc=datetime(2023, 1, 1, 9, 0),  # 无效时间
            source_platform="SleepTracker",
            recorded_at=datetime.utcnow()
        )
        db_session.add(sleep)
        db_session.commit()

        # 应该处理为跨午夜的情况
        assert sleep.total_sleep_minutes == 1380  # 23小时


# 测试心率模型
class TestHeartRateSampleDB:
    def test_timestamp_index(self, db_session, sample_user):
        hr = HeartRateSampleDB(
            user_id=sample_user.user_id,
            timestamp_utc=datetime.utcnow(),
            bpm=72,
            source_platform="HRMonitor",
            recorded_at=datetime.utcnow()
        )
        db_session.add(hr)
        db_session.commit()
        assert hr.id > 0


# 测试成就进度模型
class TestAchievementProgressDB:
    def test_progress_calculation(self, db_session, sample_user):
        achievement = AchievementProgressDB(
            user_id=sample_user.user_id,
            achievement_type="Steps",
            achievement_level="Gold",
            current_value=5000,
            target_value=10000,
            last_updated=datetime.utcnow()
        )
        db_session.add(achievement)
        db_session.commit()

        assert achievement.progress_percentage == 50.0
        assert not achievement.is_unlocked
        assert achievement.unlocked_at is None

        # 测试成就解锁 - 只需修改当前值
        achievement.current_value = 10000
        db_session.commit()

        assert achievement.progress_percentage == 100.0
        assert achievement.is_unlocked
        assert achievement.unlocked_at is not None

    def test_auto_unlock(self, db_session, sample_user):
        """测试当前值超过目标值时自动解锁"""
        achievement = AchievementProgressDB(
            user_id=sample_user.user_id,
            achievement_type="Steps",
            achievement_level="Gold",
            current_value=15000,
            target_value=10000,
            last_updated=datetime.utcnow()
        )
        db_session.add(achievement)
        db_session.commit()

        assert achievement.is_unlocked
        assert achievement.unlocked_at is not None
        assert achievement.progress_percentage == 150.0

    def test_zero_target_value(self, db_session, sample_user):
        """测试目标值为0的情况"""
        achievement = AchievementProgressDB(
            user_id=sample_user.user_id,
            achievement_type="Steps",
            achievement_level="Gold",
            current_value=5000,
            target_value=0,  # 无效目标值
            last_updated=datetime.utcnow()
        )
        db_session.add(achievement)
        db_session.commit()

        assert achievement.progress_percentage == 0.0
        assert not achievement.is_unlocked

    def test_current_value_update(self, db_session, sample_user):
        """测试修改当前值自动更新进度和时间戳"""
        achievement = AchievementProgressDB(
            user_id=sample_user.user_id,
            achievement_type="Steps",
            achievement_level="Gold",
            current_value=0,
            target_value=10000,
            last_updated=datetime.utcnow() - timedelta(days=1)
        )
        db_session.add(achievement)
        db_session.commit()

        original_updated = achievement.last_updated

        # 修改当前值
        achievement.current_value = 7500
        db_session.commit()

        assert achievement.progress_percentage == 75.0
        assert achievement.last_updated > original_updated

    def test_unlock_without_value_change(self, db_session, sample_user):
        """测试手动解锁但不修改当前值的情况"""
        achievement = AchievementProgressDB(
            user_id=sample_user.user_id,
            achievement_type="Steps",
            achievement_level="Gold",
            current_value=10000,
            target_value=10000,
            last_updated=datetime.utcnow()
        )
        db_session.add(achievement)
        db_session.commit()

        # 手动设置解锁状态
        achievement.is_unlocked = True
        db_session.commit()

        # 进度和解锁时间应该保持不变
        assert achievement.progress_percentage == 100.0
        assert achievement.unlocked_at is not None

    def test_negative_target_value(self, db_session, sample_user):
        achievement = AchievementProgressDB(
            user_id=sample_user.user_id,
            achievement_type="Steps",
            achievement_level="Gold",
            current_value=5000,
            target_value=-100,  # 负值
            last_updated=datetime.utcnow()
        )
        db_session.add(achievement)
        db_session.commit()
        assert achievement.progress_percentage == 0.0

# 测试平台连接模型
class TestPlatformConnectionDB:
    def test_token_encryption_field(self, db_session, sample_user):
        conn = PlatformConnectionDB(
            user_id=sample_user.user_id,
            platform_name="FitService",
            platform_user_id="fit_123",
            access_token="secret_token",
            refresh_token="refresh_secret"
        )
        db_session.add(conn)
        db_session.commit()

        # 验证文本字段存储（实际加密需在业务层实现）
        assert conn.access_token == "secret_token"
        assert conn.refresh_token == "refresh_secret"

    def test_platform_uniqueness(self, db_session, sample_user):
        conn1 = PlatformConnectionDB(
            user_id=sample_user.user_id,
            platform_name="MyFitness",
            platform_user_id="fit_123"
        )
        db_session.add(conn1)
        db_session.commit()

        conn2 = PlatformConnectionDB(
            user_id=sample_user.user_id,
            platform_name="MyFitness",  # 相同平台
            platform_user_id="fit_456"
        )
        db_session.add(conn2)
        with pytest.raises(IntegrityError):
            db_session.commit()
