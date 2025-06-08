# tests/DataBaseTests/test_connection.py
import pytest
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy import text, event
from aurawell.database.connection import (
    DatabaseManager,
    get_database_manager,
    init_database,
    close_database
)

# 只使用内存数据库
TEST_MEMORY_URL = "sqlite+aiosqlite:///:memory:"

# 减少SQLAlchemy日志输出
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


@pytest.fixture
def mock_settings(monkeypatch):
    """正确模拟配置设置"""
    monkeypatch.setattr("aurawell.database.connection.AuraWellSettings.DATABASE_URL", TEST_MEMORY_URL)
    monkeypatch.setattr("aurawell.database.connection.AuraWellSettings.DEBUG", True)


# 修复：使用非异步fixture返回同步创建的对象
@pytest.fixture
def db_manager(mock_settings):
    """数据库管理器测试夹具（内存数据库）"""
    # 创建管理器并同步初始化
    manager = DatabaseManager()

    async def init():
        await manager.initialize()

    # 同步运行异步初始化
    asyncio.run(init())

    yield manager

    async def close():
        await manager.close()

    # 同步运行异步清理
    asyncio.run(close())


# 修复：全局管理器使用同步fixture
@pytest.fixture
def global_db_manager(mock_settings):
    """测试全局管理器（内存数据库）"""
    # 初始化
    asyncio.run(init_database())
    yield
    # 清理
    asyncio.run(close_database())


# 修复：所有测试使用同步fixture
@pytest.mark.asyncio
async def test_database_manager_initialization(db_manager):
    """测试数据库管理器初始化"""
    assert db_manager._initialized is True
    assert isinstance(db_manager.engine, AsyncEngine)
    assert db_manager.session_factory is not None
    assert db_manager.database_url == TEST_MEMORY_URL


@pytest.mark.asyncio
async def test_get_session(db_manager):
    """测试会话获取"""
    async with db_manager.get_session() as session:
        assert isinstance(session, AsyncSession)
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_health_check(db_manager):
    """测试健康检查"""
    assert await db_manager.health_check() is True


@pytest.mark.asyncio
async def test_connection_close(db_manager):
    """测试连接关闭"""
    await db_manager.close()
    assert db_manager.engine is None
    assert db_manager.session_factory is None
    assert db_manager._initialized is False


@pytest.mark.asyncio
async def test_sqlite_pragma_configuration(db_manager):
    """测试SQLite PRAGMA设置"""
    async with db_manager.get_session() as session:
        # 检查外键约束
        result = await session.execute(text("PRAGMA foreign_keys;"))
        assert result.scalar() == 1
        # 检查日志模式
        result = await session.execute(text("PRAGMA journal_mode;"))
        journal_mode = result.scalar().lower()

        # 内存数据库使用'memory'，文件数据库使用'wal'
        if ":memory:" in db_manager.database_url:
            assert journal_mode == "memory"
        else:
            assert journal_mode == "wal"



@pytest.mark.asyncio
async def test_table_creation(db_manager):
    """测试表创建逻辑"""
    from aurawell.database.base import Base
    assert len(Base.metadata.tables) > 0


# 修复：使用同步fixture
@pytest.mark.asyncio
async def test_global_functions(global_db_manager):
    """测试全局管理函数"""
    manager = get_database_manager()
    assert manager._initialized is True

    async with manager.get_session() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    await close_database()
    # 重新获取管理器验证状态
    new_manager = get_database_manager()
    assert not new_manager._initialized
    await new_manager.close()


@pytest.mark.asyncio
async def test_concurrent_sessions(db_manager):
    """测试并发会话处理"""

    async def use_session():
        async with db_manager.get_session() as session:
            await session.execute(text("SELECT 1"))
            await asyncio.sleep(0.01)

    tasks = [asyncio.create_task(use_session()) for _ in range(5)]
    await asyncio.gather(*tasks)


@pytest.mark.asyncio
async def test_error_handling_in_session(db_manager):
    """测试会话中的错误处理"""
    with pytest.raises(Exception):
        async with db_manager.get_session() as session:
            await session.execute(text("INVALID SQL"))

    # 验证新会话可用
    async with db_manager.get_session() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_connection_reuse(db_manager):
    """测试连接池重用"""
    # 创建会话但不使用async with
    session1 = db_manager.session_factory()
    session2 = db_manager.session_factory()

    assert session1.bind is session2.bind

    await session1.close()
    await session2.close()


# 修改 test_base_class_connection_events 测试
def test_base_class_connection_events(db_manager):
    """测试连接事件监听器是否注册"""
    # 检查管理器是否注册了SQLite监听器
    assert db_manager.has_sqlite_listener()

    # 额外的验证：检查监听器是否正常工作
    async def verify_listener():
        async with db_manager.get_session() as session:
            result = await session.execute(text("PRAGMA foreign_keys;"))
            assert result.scalar() == 1

    asyncio.run(verify_listener())


# 修复：移除不必要的fixture依赖
@pytest.mark.asyncio
async def test_auto_initialize_on_session_request(mock_settings):  # 添加mock_settings
    """测试首次会话请求时自动初始化"""
    # 直接创建管理器，不调用initialize
    manager = DatabaseManager()
    assert not manager._initialized

    # 请求会话应触发初始化
    async with manager.get_session() as session:
        assert manager._initialized
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    await manager.close()

