/**
 * Mock数据开发工具
 * 提供开发过程中的数据管理和调试功能
 */

import { mockData, mockUtils, resetMockData } from './index';

// 开发工具状态
const devToolsState = {
  isEnabled: import.meta.env.DEV, // 只在开发环境启用
  isVisible: false,
  currentTab: 'data',
};

// 开发工具类
export class MockDevTools {
  constructor() {
    this.state = devToolsState;
    this.init();
  }

  // 初始化开发工具
  init() {
    if (!this.state.isEnabled) return;

    // 添加全局快捷键
    this.addKeyboardShortcuts();

    // 添加控制台命令
    this.addConsoleCommands();

    console.log('🛠️ Mock开发工具已启用');
    console.log('快捷键: Ctrl+Shift+M 打开/关闭开发工具');
    console.log('控制台命令: window.mockDevTools');
  }

  // 添加键盘快捷键
  addKeyboardShortcuts() {
    document.addEventListener('keydown', e => {
      // Ctrl+Shift+M 打开/关闭开发工具
      if (e.ctrlKey && e.shiftKey && e.key === 'M') {
        e.preventDefault();
        this.toggle();
      }

      // Ctrl+Shift+R 重置Mock数据
      if (e.ctrlKey && e.shiftKey && e.key === 'R') {
        e.preventDefault();
        this.resetData();
      }
    });
  }

  // 添加控制台命令
  addConsoleCommands() {
    window.mockDevTools = {
      // 显示/隐藏开发工具
      toggle: () => this.toggle(),

      // 重置数据
      reset: () => this.resetData(),

      // 查看当前数据
      data: () => {
        console.log('📊 当前Mock数据:', mockData);
        return mockData;
      },

      // 导出数据
      export: () => this.exportData(),

      // 导入数据
      import: data => this.importData(data),

      // 添加测试用户
      addTestUser: () => this.addTestUser(),

      // 添加测试健康计划
      addTestPlan: () => this.addTestHealthPlan(),

      // 添加测试聊天记录
      addTestChat: () => this.addTestChatSession(),

      // 清空特定数据
      clear: {
        users: () => {
          mockData.users = [];
          console.log('✅ 用户数据已清空');
        },
        plans: () => {
          mockData.healthPlans = [];
          console.log('✅ 健康计划已清空');
        },
        chats: () => {
          mockData.chatSessions = [];
          console.log('✅ 聊天记录已清空');
        },
        families: () => {
          mockData.families = [];
          console.log('✅ 家庭数据已清空');
        },
      },
    };
  }

  // 切换开发工具显示状态
  toggle() {
    this.state.isVisible = !this.state.isVisible;

    if (this.state.isVisible) {
      this.show();
    } else {
      this.hide();
    }
  }

  // 显示开发工具
  show() {
    // 移除已存在的开发工具面板
    this.hide();

    // 创建开发工具面板
    const panel = this.createPanel();
    document.body.appendChild(panel);

    console.log('🛠️ Mock开发工具已打开');
  }

  // 隐藏开发工具
  hide() {
    const existingPanel = document.getElementById('mock-dev-tools');
    if (existingPanel) {
      existingPanel.remove();
    }
  }

  // 创建开发工具面板
  createPanel() {
    const panel = document.createElement('div');
    panel.id = 'mock-dev-tools';
    panel.innerHTML = `
      <div style="
        position: fixed;
        top: 20px;
        right: 20px;
        width: 400px;
        max-height: 600px;
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
      ">
        <div style="
          padding: 12px 16px;
          border-bottom: 1px solid #eee;
          background: #f8f9fa;
          border-radius: 8px 8px 0 0;
          display: flex;
          justify-content: space-between;
          align-items: center;
        ">
          <h3 style="margin: 0; font-size: 16px; color: #333;">🛠️ Mock开发工具</h3>
          <button onclick="window.mockDevTools.toggle()" style="
            background: none;
            border: none;
            font-size: 18px;
            cursor: pointer;
            padding: 0;
            color: #666;
          ">×</button>
        </div>
        
        <div style="padding: 16px;">
          <div style="margin-bottom: 16px;">
            <button onclick="window.mockDevTools.reset()" style="
              background: #ff4d4f;
              color: white;
              border: none;
              padding: 8px 16px;
              border-radius: 4px;
              cursor: pointer;
              margin-right: 8px;
            ">重置数据</button>
            
            <button onclick="window.mockDevTools.export()" style="
              background: #1890ff;
              color: white;
              border: none;
              padding: 8px 16px;
              border-radius: 4px;
              cursor: pointer;
              margin-right: 8px;
            ">导出数据</button>
          </div>
          
          <div style="margin-bottom: 16px;">
            <h4 style="margin: 0 0 8px 0; color: #333;">快速添加测试数据:</h4>
            <button onclick="window.mockDevTools.addTestUser()" style="
              background: #52c41a;
              color: white;
              border: none;
              padding: 6px 12px;
              border-radius: 4px;
              cursor: pointer;
              margin: 4px 4px 4px 0;
              font-size: 12px;
            ">添加用户</button>
            
            <button onclick="window.mockDevTools.addTestPlan()" style="
              background: #52c41a;
              color: white;
              border: none;
              padding: 6px 12px;
              border-radius: 4px;
              cursor: pointer;
              margin: 4px 4px 4px 0;
              font-size: 12px;
            ">添加计划</button>
            
            <button onclick="window.mockDevTools.addTestChat()" style="
              background: #52c41a;
              color: white;
              border: none;
              padding: 6px 12px;
              border-radius: 4px;
              cursor: pointer;
              margin: 4px 4px 4px 0;
              font-size: 12px;
            ">添加聊天</button>
          </div>
          
          <div style="margin-bottom: 16px;">
            <h4 style="margin: 0 0 8px 0; color: #333;">数据统计:</h4>
            <div style="font-size: 12px; color: #666; line-height: 1.5;">
              用户: ${mockData.users.length} 个<br>
              健康计划: ${mockData.healthPlans.length} 个<br>
              聊天会话: ${mockData.chatSessions.length} 个<br>
              家庭: ${mockData.families.length} 个<br>
              家庭成员: ${mockData.familyMembers.length} 个
            </div>
          </div>
          
          <div style="font-size: 12px; color: #999;">
            快捷键:<br>
            Ctrl+Shift+M: 开关工具<br>
            Ctrl+Shift+R: 重置数据
          </div>
        </div>
      </div>
    `;

    return panel;
  }

  // 重置Mock数据
  resetData() {
    resetMockData();
    console.log('🔄 Mock数据已重置');

    // 刷新开发工具面板
    if (this.state.isVisible) {
      this.show();
    }
  }

  // 导出Mock数据
  exportData() {
    const dataToExport = {
      users: mockData.users,
      healthPlans: mockData.healthPlans,
      chatSessions: mockData.chatSessions,
      families: mockData.families,
      familyMembers: mockData.familyMembers,
      exportTime: new Date().toISOString(),
    };

    const dataStr = JSON.stringify(dataToExport, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `mock-data-${new Date().toISOString().split('T')[0]}.json`;
    a.click();

    URL.revokeObjectURL(url);
    console.log('📥 Mock数据已导出');
  }

  // 导入Mock数据
  importData(data) {
    try {
      if (typeof data === 'string') {
        data = JSON.parse(data);
      }

      if (data.users) mockData.users = data.users;
      if (data.healthPlans) mockData.healthPlans = data.healthPlans;
      if (data.chatSessions) mockData.chatSessions = data.chatSessions;
      if (data.families) mockData.families = data.families;
      if (data.familyMembers) mockData.familyMembers = data.familyMembers;

      console.log('📤 Mock数据已导入');

      // 刷新开发工具面板
      if (this.state.isVisible) {
        this.show();
      }
    } catch (error) {
      console.error('❌ 导入数据失败:', error);
    }
  }

  // 添加测试用户
  addTestUser() {
    const testUser = {
      user_id: mockUtils.generateId('user'),
      username: `test_user_${Date.now()}`,
      email: `test${Date.now()}@example.com`,
      full_name: '测试用户',
      phone: '13800138000',
      date_of_birth: '1990-01-01',
      gender: 'male',
      height: 175,
      weight: 70,
      avatar: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    mockData.users.push(testUser);
    console.log('✅ 已添加测试用户:', testUser);

    // 刷新开发工具面板
    if (this.state.isVisible) {
      this.show();
    }
  }

  // 添加测试健康计划
  addTestHealthPlan() {
    const testPlan = {
      plan_id: mockUtils.generateId('plan'),
      user_id: mockData.currentUser?.user_id || 'user_001',
      title: `测试健康计划 ${Date.now()}`,
      description: '这是一个测试健康计划',
      plan_type: 'general',
      status: 'active',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      recommendations: [
        {
          category: 'diet',
          title: '饮食建议',
          content: '测试饮食建议内容',
          priority: 'high',
        },
      ],
    };

    mockData.healthPlans.push(testPlan);
    console.log('✅ 已添加测试健康计划:', testPlan);

    // 刷新开发工具面板
    if (this.state.isVisible) {
      this.show();
    }
  }

  // 添加测试聊天会话
  addTestChatSession() {
    const testSession = {
      session_id: mockUtils.generateId('session'),
      user_id: mockData.currentUser?.user_id || 'user_001',
      title: `测试聊天 ${Date.now()}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      messages: [
        {
          message_id: mockUtils.generateId('msg'),
          role: 'user',
          content: '这是一条测试消息',
          timestamp: new Date().toISOString(),
        },
        {
          message_id: mockUtils.generateId('msg'),
          role: 'assistant',
          content: '这是AI的测试回复',
          timestamp: new Date().toISOString(),
        },
      ],
    };

    mockData.chatSessions.push(testSession);
    console.log('✅ 已添加测试聊天会话:', testSession);

    // 刷新开发工具面板
    if (this.state.isVisible) {
      this.show();
    }
  }
}

// 创建开发工具实例
export const mockDevTools = new MockDevTools();

export default mockDevTools;
