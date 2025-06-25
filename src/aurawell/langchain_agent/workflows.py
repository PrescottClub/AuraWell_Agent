"""
AuraWell MCP智能工作流配置
定义基于用户意图的自动化工具调用规则
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


class TriggerType(Enum):
    """触发器类型"""
    KEYWORD_MATCH = "keyword_match"
    INTENT_CLASSIFICATION = "intent_classification"
    CONTEXT_BASED = "context_based"


class ExecutionStrategy(Enum):
    """执行策略"""
    PARALLEL = "parallel"          # 并行执行所有工具
    SEQUENTIAL = "sequential"      # 按优先级顺序执行
    CONDITIONAL = "conditional"    # 条件式执行（基于前一个工具结果）
    ADAPTIVE = "adaptive"          # 自适应执行（动态调整）


@dataclass
class ToolAction:
    """工具动作配置"""
    tool_name: str
    action: str
    parameters: Dict[str, Any]
    priority: int = 1
    timeout: float = 10.0
    required: bool = True
    depends_on: Optional[List[str]] = None
    success_condition: Optional[str] = None


@dataclass
class WorkflowTemplate:
    """工作流模板"""
    name: str
    description: str
    triggers: List[str]
    execution_strategy: ExecutionStrategy
    tool_actions: List[ToolAction]
    success_criteria: Dict[str, Any]
    fallback_strategy: Optional[str] = None


# =============================================================================
# 智能工作流定义 (基于.cursorrules规则)
# =============================================================================

INTELLIGENT_WORKFLOWS: Dict[str, WorkflowTemplate] = {
    
    # 健康数据分析工作流
    "health_analysis": WorkflowTemplate(
        name="健康数据分析",
        description="全面分析用户健康数据，生成可视化报告和趋势分析",
        triggers=[
            "分析", "数据", "统计", "趋势", "BMI", "体重", 
            "statistics", "analyze", "trend", "health data"
        ],
        execution_strategy=ExecutionStrategy.PARALLEL,
        tool_actions=[
            ToolAction(
                tool_name="database-sqlite",
                action="query_comprehensive_health_data",
                parameters={
                    "tables": ["health_metrics", "body_measurements", "vital_signs"],
                    "time_range": "3_months",
                    "include_trends": True
                },
                priority=1,
                timeout=15.0
            ),
            ToolAction(
                tool_name="calculator",
                action="calculate_health_metrics",
                parameters={
                    "metrics": ["BMI", "BMR", "TDEE", "body_fat_percentage", "muscle_mass"],
                    "trend_analysis": True
                },
                priority=1,
                timeout=5.0
            ),
            ToolAction(
                tool_name="quickchart",
                action="generate_health_dashboard",
                parameters={
                    "chart_types": ["line_chart", "bar_chart", "gauge_chart"],
                    "metrics": ["weight_trend", "bmi_progression", "activity_levels"],
                    "time_period": "90_days"
                },
                priority=2,
                timeout=10.0
            ),
            ToolAction(
                tool_name="sequential-thinking",
                action="analyze_health_patterns",
                parameters={
                    "analysis_type": "comprehensive_health_assessment",
                    "focus_areas": ["trends", "anomalies", "recommendations"]
                },
                priority=3,
                timeout=20.0
            )
        ],
        success_criteria={
            "min_successful_tools": 2,
            "required_tools": ["calculator"],
            "data_completeness": 0.7
        }
    ),
    
    # 营养规划工作流
    "nutrition_planning": WorkflowTemplate(
        name="智能营养规划",
        description="基于最新科学研究制定个性化营养方案",
        triggers=[
            "饮食", "营养", "meal", "diet", "卡路里", "nutrition", 
            "food", "calories", "减重", "增重", "meal plan"
        ],
        execution_strategy=ExecutionStrategy.SEQUENTIAL,
        tool_actions=[
            ToolAction(
                tool_name="brave-search",
                action="search_latest_nutrition_research",
                parameters={
                    "query_templates": [
                        "latest nutrition research 2024",
                        "personalized diet recommendations",
                        "macronutrient optimization"
                    ],
                    "source_filter": "scientific_papers"
                },
                priority=1,
                timeout=15.0
            ),
            ToolAction(
                tool_name="calculator",
                action="calculate_nutrition_requirements",
                parameters={
                    "calculation_type": "comprehensive_nutrition",
                    "include": ["calories", "macros", "micronutrients", "hydration"],
                    "activity_adjustment": True
                },
                priority=2,
                timeout=8.0,
                depends_on=["brave-search"]
            ),
            ToolAction(
                tool_name="database-sqlite",
                action="analyze_diet_history",
                parameters={
                    "analysis_period": "30_days",
                    "include_patterns": True,
                    "identify_deficiencies": True
                },
                priority=2,
                timeout=10.0
            ),
            ToolAction(
                tool_name="memory",
                action="update_nutrition_profile",
                parameters={
                    "profile_type": "nutrition_preferences",
                    "include_restrictions": True,
                    "update_goals": True
                },
                priority=3,
                timeout=5.0
            ),
            ToolAction(
                tool_name="quickchart",
                action="create_nutrition_visualization",
                parameters={
                    "charts": ["macro_pie_chart", "calorie_timeline", "nutrient_balance"],
                    "comparison_baseline": "recommended_values"
                },
                priority=4,
                timeout=12.0
            )
        ],
        success_criteria={
            "min_successful_tools": 3,
            "required_tools": ["calculator", "database-sqlite"],
            "research_relevance": 0.8
        }
    ),
    
    # 运动健身规划工作流
    "fitness_planning": WorkflowTemplate(
        name="智能健身规划",
        description="制定个性化运动方案，考虑环境因素和个人能力",
        triggers=[
            "运动", "健身", "workout", "fitness", "锻炼", "exercise", 
            "training", "减脂", "增肌", "马拉松", "瑜伽"
        ],
        execution_strategy=ExecutionStrategy.PARALLEL,
        tool_actions=[
            ToolAction(
                tool_name="memory",
                action="retrieve_fitness_profile",
                parameters={
                    "profile_components": [
                        "fitness_level", "exercise_preferences", 
                        "previous_injuries", "available_equipment"
                    ]
                },
                priority=1,
                timeout=5.0
            ),
            ToolAction(
                tool_name="weather",
                action="get_exercise_forecast",
                parameters={
                    "forecast_days": 7,
                    "exercise_types": ["outdoor_running", "cycling", "hiking"],
                    "optimal_conditions": True
                },
                priority=1,
                timeout=8.0
            ),
            ToolAction(
                tool_name="calculator",
                action="calculate_exercise_metrics",
                parameters={
                    "calculations": [
                        "target_heart_rate", "calorie_burn_estimation",
                        "recovery_time", "progression_targets"
                    ],
                    "personalization": True
                },
                priority=2,
                timeout=6.0
            ),
            ToolAction(
                tool_name="quickchart",
                action="generate_fitness_plan_chart",
                parameters={
                    "chart_types": ["weekly_schedule", "progression_graph", "intensity_zones"],
                    "plan_duration": "4_weeks"
                },
                priority=3,
                timeout=10.0
            )
        ],
        success_criteria={
            "min_successful_tools": 2,
            "required_tools": ["memory", "calculator"],
            "plan_feasibility": 0.85
        }
    ),
    
    # 综合健康评估工作流
    "comprehensive_assessment": WorkflowTemplate(
        name="全面健康评估",
        description="360度健康状况评估，生成详细报告和改进建议",
        triggers=[
            "健康评估", "全面分析", "制定计划", "assessment", 
            "comprehensive", "plan", "体检", "健康报告"
        ],
        execution_strategy=ExecutionStrategy.SEQUENTIAL,
        tool_actions=[
            ToolAction(
                tool_name="memory",
                action="compile_health_profile",
                parameters={
                    "include_all_aspects": True,
                    "historical_data": True,
                    "risk_factors": True
                },
                priority=1,
                timeout=10.0
            ),
            ToolAction(
                tool_name="database-sqlite",
                action="comprehensive_data_analysis",
                parameters={
                    "analysis_scope": "full_health_picture",
                    "time_range": "1_year",
                    "include_correlations": True
                },
                priority=2,
                timeout=20.0,
                depends_on=["memory"]
            ),
            ToolAction(
                tool_name="calculator",
                action="health_risk_assessment",
                parameters={
                    "risk_categories": [
                        "cardiovascular", "metabolic", "musculoskeletal",
                        "mental_health", "lifestyle"
                    ],
                    "scoring_method": "evidence_based"
                },
                priority=3,
                timeout=15.0,
                depends_on=["database-sqlite"]
            ),
            ToolAction(
                tool_name="sequential-thinking",
                action="generate_health_insights",
                parameters={
                    "insight_types": [
                        "strength_areas", "improvement_opportunities",
                        "risk_mitigation", "goal_recommendations"
                    ],
                    "prioritization": True
                },
                priority=4,
                timeout=25.0,
                depends_on=["calculator"]
            ),
            ToolAction(
                tool_name="quickchart",
                action="create_health_report_visuals",
                parameters={
                    "report_components": [
                        "health_score_gauge", "risk_assessment_radar",
                        "progress_timeline", "goal_roadmap"
                    ],
                    "professional_format": True
                },
                priority=5,
                timeout=15.0
            )
        ],
        success_criteria={
            "min_successful_tools": 4,
            "required_tools": ["memory", "calculator", "sequential-thinking"],
            "assessment_completeness": 0.9
        }
    ),
    
    # 健康研究查询工作流
    "research_query": WorkflowTemplate(
        name="健康研究查询",
        description="搜索和分析最新健康科学研究，提供循证建议",
        triggers=[
            "搜索", "research", "最新", "科学", "study", "研究", 
            "文献", "evidence", "论文", "实验"
        ],
        execution_strategy=ExecutionStrategy.SEQUENTIAL,
        tool_actions=[
            ToolAction(
                tool_name="brave-search",
                action="search_scientific_literature",
                parameters={
                    "search_domains": [
                        "pubmed.ncbi.nlm.nih.gov", "scholar.google.com",
                        "cochranelibrary.com", "bmj.com"
                    ],
                    "publication_date": "2023-2024",
                    "study_types": ["randomized_controlled_trial", "meta_analysis", "systematic_review"]
                },
                priority=1,
                timeout=20.0
            ),
            ToolAction(
                tool_name="fetch",
                action="extract_research_content",
                parameters={
                    "content_types": ["abstract", "methodology", "results", "conclusions"],
                    "quality_filter": True
                },
                priority=2,
                timeout=15.0,
                depends_on=["brave-search"]
            ),
            ToolAction(
                tool_name="memory",
                action="store_research_findings",
                parameters={
                    "knowledge_graph_update": True,
                    "evidence_strength_rating": True,
                    "practical_applications": True
                },
                priority=3,
                timeout=8.0,
                depends_on=["fetch"]
            )
        ],
        success_criteria={
            "min_successful_tools": 2,
            "required_tools": ["brave-search"],
            "research_quality": 0.8
        }
    ),
    
    # 用户画像管理工作流
    "user_profile_management": WorkflowTemplate(
        name="用户健康画像管理",
        description="构建和更新个性化用户健康档案",
        triggers=[
            "画像", "profile", "个性化", "preferences", "偏好", 
            "档案", "个人信息", "健康档案"
        ],
        execution_strategy=ExecutionStrategy.PARALLEL,
        tool_actions=[
            ToolAction(
                tool_name="memory",
                action="comprehensive_profile_analysis",
                parameters={
                    "analysis_dimensions": [
                        "demographic", "health_metrics", "lifestyle",
                        "preferences", "goals", "constraints"
                    ],
                    "update_frequency": "dynamic"
                },
                priority=1,
                timeout=10.0
            ),
            ToolAction(
                tool_name="database-sqlite",
                action="profile_data_integration",
                parameters={
                    "data_sources": ["health_records", "activity_logs", "survey_responses"],
                    "data_validation": True,
                    "privacy_compliance": True
                },
                priority=1,
                timeout=12.0
            ),
            ToolAction(
                tool_name="sequential-thinking",
                action="profile_insights_generation",
                parameters={
                    "insight_categories": [
                        "behavior_patterns", "health_trends",
                        "personalization_opportunities", "risk_factors"
                    ],
                    "actionable_recommendations": True
                },
                priority=2,
                timeout=18.0
            )
        ],
        success_criteria={
            "min_successful_tools": 2,
            "required_tools": ["memory"],
            "profile_completeness": 0.8
        }
    )
}


# =============================================================================
# 工作流执行配置
# =============================================================================

EXECUTION_SETTINGS = {
    "default_timeout": 30.0,
    "max_parallel_tools": 5,
    "retry_attempts": 2,
    "fallback_enabled": True,
    "logging_level": "INFO",
    "performance_monitoring": True
}


# =============================================================================
# 智能触发器配置
# =============================================================================

class WorkflowMatcher:
    """工作流匹配器 - 根据用户输入智能选择最适合的工作流"""
    
    @staticmethod
    def match_workflow(user_input: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        匹配最适合的工作流
        
        Args:
            user_input: 用户输入文本
            context: 上下文信息
            
        Returns:
            List[str]: 匹配的工作流名称列表（按相关性排序）
        """
        user_input_lower = user_input.lower()
        workflow_scores = {}
        
        for workflow_name, workflow in INTELLIGENT_WORKFLOWS.items():
            score = 0
            matched_triggers = []
            
            # 计算触发词匹配分数
            for trigger in workflow.triggers:
                if trigger.lower() in user_input_lower:
                    score += len(trigger)  # 更长的触发词权重更高
                    matched_triggers.append(trigger)
            
            # 考虑上下文因素
            if context:
                # 如果用户之前有相关历史，提高相关工作流的分数
                if context.get('recent_intent') == workflow_name:
                    score *= 1.2
                
                # 基于用户偏好调整分数
                user_preferences = context.get('user_preferences', {})
                if workflow_name in user_preferences.get('preferred_workflows', []):
                    score *= 1.1
            
            if score > 0:
                workflow_scores[workflow_name] = {
                    'score': score,
                    'matched_triggers': matched_triggers,
                    'confidence': min(score / len(user_input_lower), 1.0)
                }
        
        # 按分数排序
        sorted_workflows = sorted(
            workflow_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        return [workflow_name for workflow_name, _ in sorted_workflows[:3]]  # 返回前3个匹配
    
    @staticmethod
    def get_workflow_confidence(workflow_name: str, user_input: str) -> float:
        """获取工作流匹配的置信度"""
        if workflow_name not in INTELLIGENT_WORKFLOWS:
            return 0.0
        
        workflow = INTELLIGENT_WORKFLOWS[workflow_name]
        user_input_lower = user_input.lower()
        
        matched_triggers = sum(1 for trigger in workflow.triggers if trigger.lower() in user_input_lower)
        total_triggers = len(workflow.triggers)
        
        return matched_triggers / total_triggers if total_triggers > 0 else 0.0


# =============================================================================
# 工作流执行结果评估
# =============================================================================

class WorkflowEvaluator:
    """工作流执行结果评估器"""
    
    @staticmethod
    def evaluate_workflow_success(
        workflow_name: str,
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        评估工作流执行成功度
        
        Args:
            workflow_name: 工作流名称
            execution_result: 执行结果
            
        Returns:
            Dict[str, Any]: 评估结果
        """
        if workflow_name not in INTELLIGENT_WORKFLOWS:
            return {"success": False, "reason": "Unknown workflow"}
        
        workflow = INTELLIGENT_WORKFLOWS[workflow_name]
        criteria = workflow.success_criteria
        
        # 检查成功标准
        successful_tools = len([
            result for result in execution_result.get('results', {}).values()
            if isinstance(result, dict) and result.get('success', False)
        ])
        
        min_required = criteria.get('min_successful_tools', 1)
        required_tools = criteria.get('required_tools', [])
        
        success = successful_tools >= min_required
        
        # 检查必需工具
        missing_required = []
        for required_tool in required_tools:
            if required_tool not in execution_result.get('results', {}):
                missing_required.append(required_tool)
                success = False
        
        return {
            "success": success,
            "successful_tools_count": successful_tools,
            "required_tools_missing": missing_required,
            "completion_rate": successful_tools / len(workflow.tool_actions),
            "meets_criteria": success
        } 