# AuraWell 测试说明

## 当前测试状态

由于负责测试的团队成员还未加入项目，目前只保留了核心功能的单元测试。

## 现有测试

### ✅ test_health_constants.py
- **功能**: 测试健康常量配置模块
- **覆盖范围**: 
  - `get_health_constant()` 函数的各种调用场景
  - `get_category_constants()` 函数的边界条件
  - 键名大小写转换和格式化
  - 错误处理和默认值返回
  - 数据完整性验证
- **测试用例数**: 28个
- **状态**: ✅ 全部通过

## 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/test_health_constants.py -v

# 生成测试覆盖率报告
python -m pytest tests/ --cov=src/aurawell --cov-report=html
```

## 测试开发计划

等待测试团队成员加入后，将补充以下测试：

### 🔄 计划中的测试模块

1. **API接口测试**
   - REST API端点测试
   - 请求/响应验证
   - 错误处理测试
   - 认证和权限测试

2. **WebSocket测试**
   - 连接建立和断开
   - 消息发送和接收
   - 心跳机制测试
   - 错误恢复测试

3. **服务层测试**
   - 家庭管理服务
   - 健康建议服务
   - 报告生成服务
   - 仪表盘服务

4. **数据库测试**
   - 模型验证测试
   - 数据持久化测试
   - 查询性能测试
   - 数据迁移测试

5. **集成测试**
   - 端到端功能测试
   - 多用户场景测试
   - 并发访问测试
   - 性能压力测试

## 测试规范

### 测试文件命名
- 单元测试: `test_<module_name>.py`
- 集成测试: `test_integration_<feature>.py`
- 性能测试: `test_performance_<scenario>.py`

### 测试用例命名
- 功能测试: `test_<function_name>_<scenario>`
- 边界测试: `test_<function_name>_boundary_<condition>`
- 错误测试: `test_<function_name>_error_<error_type>`

### 测试覆盖率目标
- 单元测试覆盖率: ≥ 90%
- 集成测试覆盖率: ≥ 80%
- 关键路径覆盖率: 100%

## 注意事项

1. **当前状态**: 大部分测试文件已被清理，只保留核心功能测试
2. **测试环境**: 使用模拟数据和服务，避免依赖外部资源
3. **持续集成**: 计划集成到CI/CD流程中，确保代码质量
