import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { HealthPlanAPI } from '../api/healthPlan.js';
import {
  normalizePlan,
  normalizePlanList,
  normalizeApiResponse,
  normalizeProgress,
} from '../utils/healthPlanUtils.js';

export const useHealthPlanStore = defineStore('healthPlan', () => {
  // 状态
  const plans = ref([]);
  const currentPlan = ref(null);
  const planTemplates = ref([]);
  const loading = ref(false);
  const error = ref('');
  const generatingPlan = ref(false);

  // 计算属性
  const activePlans = computed(() => {
    return plans.value.filter(plan => plan.status === 'active');
  });

  const completedPlans = computed(() => {
    return plans.value.filter(plan => plan.status === 'completed');
  });

  const currentPlanProgress = computed(() => {
    if (!currentPlan.value) return 0;
    return normalizeProgress(currentPlan.value.progress);
  });

  // 方法
  const fetchPlans = async () => {
    loading.value = true;
    error.value = '';
    try {
      const response = await HealthPlanAPI.getPlans();
      if (response.data) {
        // 使用工具函数标准化响应数据
        const normalizedResponse = normalizeApiResponse(response);
        if (Array.isArray(normalizedResponse.data)) {
          plans.value = normalizePlanList(normalizedResponse.data);
        } else if (normalizedResponse.data.plans) {
          plans.value = normalizePlanList(normalizedResponse.data.plans);
        } else {
          plans.value = [];
        }
      }
    } catch (err) {
      error.value = '获取健康计划失败';
      console.error('获取健康计划失败:', err);
    } finally {
      loading.value = false;
    }
  };

  const fetchPlanDetail = async planId => {
    loading.value = true;
    error.value = '';
    try {
      const response = await HealthPlanAPI.getPlanDetail(planId);
      if (response.data) {
        // 使用工具函数标准化响应数据
        const normalizedResponse = normalizeApiResponse(response);
        const planData =
          normalizedResponse.data.plan || normalizedResponse.data;
        currentPlan.value = normalizePlan(planData);
        return currentPlan.value;
      }
      return null;
    } catch (err) {
      error.value = '获取计划详情失败';
      console.error('获取计划详情失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const generatePlan = async planRequest => {
    generatingPlan.value = true;
    error.value = '';
    try {
      const response = await HealthPlanAPI.generatePlan(planRequest);

      // 处理不同的响应格式
      let planData = null;

      if (response.plan) {
        // 新的API响应格式：plan字段包含计划数据
        planData = response.plan;
      } else if (response.data && response.data.plan) {
        // 旧的API响应格式：data.plan包含计划数据
        planData = response.data.plan;
      } else if (response.data) {
        // 直接在data字段中的计划数据
        planData = response.data;
      }

      if (planData) {
        // 标准化计划数据
        const normalizedPlan = normalizePlan(planData);

        // 如果响应中包含推荐信息，添加到计划中
        if (response.recommendations) {
          normalizedPlan.recommendations = response.recommendations;
        }

        // 添加到计划列表的开头
        plans.value.unshift(normalizedPlan);
        currentPlan.value = normalizedPlan;

        // 重新获取计划列表以确保数据同步
        await fetchPlans();

        return normalizedPlan;
      }

      console.warn('API响应中未找到计划数据:', response);
      return null;
    } catch (err) {
      error.value = '生成健康计划失败';
      console.error('生成健康计划失败:', err);
      throw err;
    } finally {
      generatingPlan.value = false;
    }
  };

  const updatePlan = async (planId, planData) => {
    loading.value = true;
    error.value = '';
    try {
      const response = await HealthPlanAPI.updatePlan(planId, planData);
      if (response.data) {
        const index = plans.value.findIndex(
          plan => plan.plan_id === planId || plan.id === planId
        );
        if (index !== -1) {
          plans.value[index] = response.data;
        }
        if (
          currentPlan.value &&
          (currentPlan.value.plan_id === planId ||
            currentPlan.value.id === planId)
        ) {
          currentPlan.value = response.data;
        }
      }
      return response.data;
    } catch (err) {
      error.value = '更新健康计划失败';
      console.error('更新健康计划失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const deletePlan = async planId => {
    loading.value = true;
    error.value = '';
    try {
      await HealthPlanAPI.deletePlan(planId);
      plans.value = plans.value.filter(
        plan => plan.plan_id !== planId && plan.id !== planId
      );
      if (
        currentPlan.value &&
        (currentPlan.value.plan_id === planId ||
          currentPlan.value.id === planId)
      ) {
        currentPlan.value = null;
      }
    } catch (err) {
      error.value = '删除健康计划失败';
      console.error('删除健康计划失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const exportPlan = async (planId, format = 'pdf') => {
    loading.value = true;
    error.value = '';
    try {
      const response = await HealthPlanAPI.exportPlan(planId, format);

      // 创建下载链接
      const blob = new Blob([response.data], {
        type: format === 'pdf' ? 'application/pdf' : 'application/octet-stream',
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `health-plan-${planId}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      return response;
    } catch (err) {
      error.value = '导出健康计划失败';
      console.error('导出健康计划失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const savePlanFeedback = async (planId, feedback) => {
    loading.value = true;
    error.value = '';
    try {
      const response = await HealthPlanAPI.saveFeedback(planId, feedback);
      return response;
    } catch (err) {
      error.value = '保存计划反馈失败';
      console.error('保存计划反馈失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const fetchPlanProgress = async planId => {
    loading.value = true;
    error.value = '';
    try {
      const response = await HealthPlanAPI.getPlanProgress(planId);
      if (
        response.data &&
        currentPlan.value &&
        (currentPlan.value.plan_id === planId ||
          currentPlan.value.id === planId)
      ) {
        // 正确处理进度数据 - 只更新progress字段，不覆盖整个对象
        if (
          typeof response.data === 'object' &&
          response.data.overall_progress !== undefined
        ) {
          currentPlan.value.progress = response.data.overall_progress;
        } else if (typeof response.data === 'number') {
          currentPlan.value.progress = response.data;
        }
      }
      return response.data;
    } catch (err) {
      error.value = '获取计划进度失败';
      console.error('获取计划进度失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const updatePlanProgress = async (planId, progressData) => {
    loading.value = true;
    error.value = '';
    try {
      const response = await HealthPlanAPI.updatePlanProgress(
        planId,
        progressData
      );
      if (
        response.data &&
        currentPlan.value &&
        (currentPlan.value.plan_id === planId ||
          currentPlan.value.id === planId)
      ) {
        // 正确处理进度数据更新
        if (
          typeof response.data === 'object' &&
          response.data.overall_progress !== undefined
        ) {
          currentPlan.value.progress = response.data.overall_progress;
        } else if (typeof response.data === 'number') {
          currentPlan.value.progress = response.data;
        }
      }
      return response.data;
    } catch (err) {
      error.value = '更新计划进度失败';
      console.error('更新计划进度失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const fetchPlanTemplates = async () => {
    loading.value = true;
    error.value = '';
    try {
      const response = await HealthPlanAPI.getPlanTemplates();
      if (response.data) {
        // 处理不同的响应格式
        if (Array.isArray(response.data)) {
          planTemplates.value = response.data;
        } else if (response.data.templates) {
          planTemplates.value = response.data.templates;
        } else {
          planTemplates.value = [];
        }
      }
    } catch (err) {
      error.value = '获取计划模板失败';
      console.error('获取计划模板失败:', err);
    } finally {
      loading.value = false;
    }
  };

  const createFromTemplate = async (templateId, customData) => {
    generatingPlan.value = true;
    error.value = '';
    try {
      const response = await HealthPlanAPI.createFromTemplate(
        templateId,
        customData
      );
      if (response.data) {
        // 处理不同的响应格式
        const planData = response.data.plan || response.data;
        plans.value.unshift(planData);
        currentPlan.value = planData;
        return planData;
      }
      return null;
    } catch (err) {
      error.value = '基于模板创建计划失败';
      console.error('基于模板创建计划失败:', err);
      throw err;
    } finally {
      generatingPlan.value = false;
    }
  };

  const clearCurrentPlan = () => {
    currentPlan.value = null;
  };

  const clearError = () => {
    error.value = '';
  };

  return {
    // 状态
    plans,
    currentPlan,
    planTemplates,
    loading,
    error,
    generatingPlan,

    // 计算属性
    activePlans,
    completedPlans,
    currentPlanProgress,

    // 方法
    fetchPlans,
    fetchPlanDetail,
    generatePlan,
    updatePlan,
    deletePlan,
    exportPlan,
    savePlanFeedback,
    fetchPlanProgress,
    updatePlanProgress,
    fetchPlanTemplates,
    createFromTemplate,
    clearCurrentPlan,
    clearError,
  };
});
