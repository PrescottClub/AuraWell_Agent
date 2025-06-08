# tests/database/test_base.py
import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, Mapped, mapped_column
from aurawell.database.base import Base


# 定义测试模型
class TestModel(Base):
    __tablename__ = "test_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(default="default")
    value: Mapped[int] = mapped_column(default=0)


@pytest.fixture(scope="module")
def engine():
    """内存SQLite引擎"""
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="function")
def session(engine):
    """每次测试独立的数据库会话"""
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)


def test_timestamp_creation(session):
    """测试时间戳自动生成"""
    # 创建对象但未提交
    obj = TestModel()
    session.add(obj)

    # 刷新但不提交，验证时间戳已生成
    session.flush()
    assert isinstance(obj.created_at, datetime)
    assert isinstance(obj.updated_at, datetime)
    assert abs(obj.created_at.microsecond - obj.updated_at.microsecond) < 1000
    assert obj.created_at.tzinfo == timezone.utc

    # 提交后时间戳应保持不变
    pre_commit_time = obj.created_at
    session.commit()
    assert obj.created_at.microsecond == pre_commit_time.microsecond
    assert obj.created_at.tzinfo == pre_commit_time.tzinfo


def test_timestamp_update(session):
    """测试更新时间戳"""
    obj = TestModel()
    session.add(obj)
    session.commit()

    # 记录初始时间
    original_created = obj.created_at
    original_updated = obj.updated_at

    # 模拟短暂延迟
    delay = timedelta(milliseconds=10)

    # 更新对象属性
    obj.name = "updated"
    session.flush()

    # 验证时间戳变化
    assert abs(obj.created_at.microsecond - original_created.microsecond) < 1000
    assert obj.updated_at > original_updated
    assert obj.updated_at.tzinfo == timezone.utc


def test_to_dict_method(session):
    """测试字典转换"""
    obj = TestModel(name="test", value=42)
    session.add(obj)
    session.flush()

    data = obj.to_dict()

    # 验证字段完整性
    assert set(data.keys()) == {"id", "name", "value", "created_at", "updated_at"}
    assert data["name"] == "test"
    assert data["value"] == 42
    assert data["created_at"] == obj.created_at

    # 验证类型正确性
    assert isinstance(data["created_at"], datetime)
    assert isinstance(data["updated_at"], datetime)


def test_update_from_dict_method(session):
    """测试字典更新"""
    obj = TestModel()
    session.add(obj)
    session.flush()

    # 有效更新
    update_data = {"name": "new_name", "value": 100}
    obj.update_from_dict(update_data)

    assert obj.name == "new_name"
    assert obj.value == 100

    # 无效字段应被忽略
    obj.update_from_dict({"invalid_field": "value", "name": "valid"})
    assert not hasattr(obj, "invalid_field")
    assert obj.name == "valid"


def test_repr_method(session):
    """测试对象表示"""
    # 无ID情况
    obj = TestModel()
    assert repr(obj) == "<TestModel []>"

    # 有ID情况
    session.add(obj)
    session.flush()
    assert repr(obj) == f"<TestModel (id={obj.id})>"


def test_legacy_declarative_base():
    """测试向后兼容性"""
    from aurawell.database.base import DeclarativeBase
    assert DeclarativeBase is Base


def test_timezone_handling(session):
    """测试时区处理"""
    # 创建不同时区的时间
    local_time = datetime.now(timezone(timedelta(hours=8)))
    obj = TestModel(created_at=local_time)
    session.add(obj)
    session.flush()
    session.refresh(obj)
    # 应自动转换为UTC
    assert obj.created_at.tzinfo == timezone.utc
    assert obj.created_at.hour == (local_time.hour - 8) % 24


def test_server_defaults(session):
    """测试数据库层面的默认值"""
    # 直接插入跳过Python默认值
    stmt = TestModel.__table__.insert().values(name="server_default_test")
    session.execute(stmt)
    session.commit()

    obj = session.scalar(select(TestModel))

    # 验证数据库生成的默认值
    assert isinstance(obj.created_at, datetime)
    assert isinstance(obj.updated_at, datetime)
    assert obj.value == 0
