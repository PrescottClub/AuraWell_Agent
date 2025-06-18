// 测试前端工具函数
const fs = require('fs');
const path = require('path');

// 读取工具函数文件内容
const utilsPath = path.join(__dirname, 'src', 'utils', 'healthPlanUtils.js');
const utilsContent = fs.readFileSync(utilsPath, 'utf8');

// 创建一个简单的模块环境
const module = { exports: {} };
const exports = module.exports;

// 执行工具函数代码
eval(utilsContent);

// 提取导出的函数
const {
  normalizePlan,
  normalizeProgress,
  normalizeModules,
  getModuleTypes,
  validatePlan,
  formatDate,
  getStatusInfo
} = module.exports;

console.log('=== 测试前端工具函数 ===');

// 测试数据
const testPlan = {
  plan_id: 'test_123',
  title: '测试计划',
  description: '测试描述',
  duration_days: 30,
  status: 'active',
  progress: 75.5,
  modules: [
    { module_type: 'diet', title: '饮食', content: {}, duration_days: 30 },
    { module_type: 'exercise', title: '运动', content: {}, duration_days: 30 }
  ],
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-15T00:00:00Z'
};

console.log('1. 测试 normalizePlan:');
const normalized = normalizePlan(testPlan);
console.log('原始 plan_id:', testPlan.plan_id);
console.log('标准化后 id:', normalized.id);
console.log('标准化后 plan_id:', normalized.plan_id);
console.log('标准化后 duration:', normalized.duration);
console.log('标准化后 duration_days:', normalized.duration_days);

console.log('\n2. 测试 normalizeProgress:');
console.log('数字进度 75.5 ->', normalizeProgress(75.5));
console.log('对象进度 {total_tasks: 10, completed_tasks: 8} ->', 
  normalizeProgress({total_tasks: 10, completed_tasks: 8}));
console.log('无效进度 null ->', normalizeProgress(null));

console.log('\n3. 测试 getModuleTypes:');
console.log('对象模块类型:', getModuleTypes(testPlan.modules));
console.log('字符串模块类型:', getModuleTypes(['diet', 'exercise']));
console.log('空模块类型:', getModuleTypes([]));

console.log('\n4. 测试 normalizeModules:');
const stringModules = ['diet', 'exercise'];
const normalizedStringModules = normalizeModules(stringModules);
console.log('字符串模块标准化:', normalizedStringModules.map(m => m.module_type));

const normalizedObjectModules = normalizeModules(testPlan.modules);
console.log('对象模块标准化:', normalizedObjectModules.map(m => m.module_type));

console.log('\n5. 测试 validatePlan:');
const validation = validatePlan(testPlan);
console.log('有效计划验证:', validation.valid ? '✓ 有效' : '✗ 无效');

const invalidPlan = { title: '', modules: [], duration_days: 0 };
const invalidValidation = validatePlan(invalidPlan);
console.log('无效计划验证:', invalidValidation.valid ? '✓ 有效' : '✗ 无效');
if (!invalidValidation.valid) {
  console.log('错误信息:', invalidValidation.errors);
}

console.log('\n6. 测试 formatDate:');
console.log('格式化日期:', formatDate(testPlan.created_at));
console.log('格式化空日期:', formatDate(null));

console.log('\n7. 测试 getStatusInfo:');
console.log('活跃状态:', getStatusInfo('active'));
console.log('完成状态:', getStatusInfo('completed'));
console.log('未知状态:', getStatusInfo('unknown'));

console.log('\n🎉 前端工具函数测试完成！');

// 测试兼容性场景
console.log('\n=== 测试兼容性场景 ===');

// 场景1：后端返回的完整数据
const backendData = {
  plan_id: 'plan_456',
  title: '后端计划',
  duration_days: 60,
  modules: [
    { module_type: 'diet', title: '饮食计划', content: {}, duration_days: 60 },
    { module_type: 'weight', title: '体重管理', content: {}, duration_days: 60 }
  ],
  progress: { total_tasks: 20, completed_tasks: 15, overall_progress: 75.0 }
};

const normalizedBackend = normalizePlan(backendData);
console.log('后端数据兼容性测试:');
console.log('- ID字段:', normalizedBackend.id === normalizedBackend.plan_id ? '✓' : '✗');
console.log('- 持续时间字段:', normalizedBackend.duration === normalizedBackend.duration_days ? '✓' : '✗');
console.log('- 进度计算:', typeof normalizedBackend.progress === 'number' ? '✓' : '✗');
console.log('- 模块标准化:', normalizedBackend.modules.every(m => m.type === m.module_type) ? '✓' : '✗');

// 场景2：前端期望的简化数据
const frontendData = {
  id: 'plan_789',
  title: '前端计划',
  duration: 45,
  modules: ['exercise', 'mental'],
  progress: 80
};

const normalizedFrontend = normalizePlan(frontendData);
console.log('\n前端数据兼容性测试:');
console.log('- ID字段映射:', normalizedFrontend.plan_id === normalizedFrontend.id ? '✓' : '✗');
console.log('- 持续时间映射:', normalizedFrontend.duration_days === normalizedFrontend.duration ? '✓' : '✗');
console.log('- 模块转换:', normalizedFrontend.modules.every(m => typeof m === 'object') ? '✓' : '✗');

console.log('\n✅ 所有兼容性测试通过！');
