#!/bin/bash

# AuraWell 家庭-Agent 线语义化提交脚本
# 按照 Phase I → IV 顺序执行

set -e  # 出错时退出

echo "🚀 Starting AuraWell Family-Agent Line Commits"
echo "================================================"

# Phase I: 基础配置 - 健康常量管理
echo "📦 Phase I: Adding health constants centralized management..."
git add aurawell/config/health_constants.py
git commit -m "feat(config): add health constants centralized management

- Create unified health constants configuration
- Extract steps, sleep, calories, heart rate constants  
- Add family, challenge, and report constants
- Provide type-safe constant access functions
- Support for test data generation constants"

echo "✅ Phase I completed"

# Phase II: 服务重构 - 消除魔术数字
echo "🔧 Phase II: Refactoring services to use health constants..."
git add aurawell/services/report_service.py aurawell/services/family_service.py  
git commit -m "refactor(services): extract magic numbers to health constants

- Replace hardcoded values in report_service.py
- Use health constants for steps, calories, sleep metrics
- Replace family limits with configurable constants
- Improve maintainability and consistency
- Add proper imports with fallback handling"

echo "✅ Phase II completed"

# Phase III: 数据库配置 - 修复初始化问题
echo "🗄️ Phase III: Adding database configuration checker..."
git add aurawell/database/db_init_checker.py
git commit -m "feat(database): add database configuration checker and auto-fix

- Create DatabaseConfigChecker for validation
- Auto-detect and fix SQLAlchemy URL parsing issues
- Support SQLite and PostgreSQL configuration  
- Generate environment variable templates
- Command-line tool for database setup verification"

echo "✅ Phase III completed"

# Phase IV: 工具优化
echo "🛠️ Phase IV: Enhancing family tools..."
if git diff --cached --quiet aurawell/langchain_agent/tools/family_tools.py; then
    echo "ℹ️ No changes to family_tools.py - skipping commit"
else
    git add aurawell/langchain_agent/tools/family_tools.py
    git commit -m "feat(tools): enhance family tools with better error handling

- Improve DataComparisonTool robustness
- Add better error messages for GoalSharingTool  
- Enhance logging and debugging information
- Maintain backward compatibility"
fi

echo "✅ Phase IV completed"

# Phase V: WebSocket 接口优化
echo "🔌 Phase V: Improving WebSocket interface..."
if git diff --cached --quiet aurawell/interfaces/websocket_interface.py; then
    echo "ℹ️ No changes to websocket_interface.py - skipping commit"
else
    git add aurawell/interfaces/websocket_interface.py
    git commit -m "feat(websocket): improve WebSocket interface stability

- Better connection management and error handling
- Enhanced family member switching support
- Improved message streaming reliability
- Better integration with health advice service"
fi

echo "✅ Phase V completed"

# Phase VI: 文档更新
echo "📚 Phase VI: Updating documentation..."
if [ -f "PHASE_IV_COMPLETION_REPORT.md" ] && [ -f "WEBSOCKET_USAGE.md" ] && [ -f "CHANGELOG_PHASE_IV.md" ]; then
    git add PHASE_IV_COMPLETION_REPORT.md WEBSOCKET_USAGE.md CHANGELOG_PHASE_IV.md
    git commit -m "docs: update Phase IV completion and WebSocket usage docs

- Update completion report with latest changes
- Enhance WebSocket usage documentation  
- Update changelog with family-agent improvements
- Add database configuration troubleshooting"
else
    echo "ℹ️ Documentation files not found or no changes - skipping commit"
fi

echo "✅ Phase VI completed"

echo ""
echo "🎉 All commits completed successfully!"
echo "📊 Commit Summary:"
git log --oneline -6

echo ""
echo "🧪 Running final verification..."
python -c "
try:
    from aurawell.config.health_constants import HEALTH_CONSTANTS
    print('✅ Health constants import successful')
    
    from aurawell.database.db_init_checker import check_and_fix_database_config
    print('✅ Database checker import successful')
    
    print('🎯 All core modules verified!')
except Exception as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

echo "✅ Family-Agent line refactoring completed successfully!" 