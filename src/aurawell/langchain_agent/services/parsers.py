"""
Output Parsers for Health Advice Generation

Ensures structured output with all required health sections.
Enhanced with robust validation and completeness scoring.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class SectionType(Enum):
    """Health advice section types"""

    DIET = "饮食"
    EXERCISE = "运动"
    WEIGHT = "体重"
    SLEEP = "睡眠"
    MENTAL = "心理"


@dataclass
class HealthSection:
    """Enhanced health section with completeness scoring"""

    section_type: SectionType
    content: str
    recommendations: List[str]
    completeness_score: float  # 0.0-1.0


class HealthAdviceSection(BaseModel):
    """Single health advice section (Pydantic model for API compatibility)"""

    title: str
    content: str
    recommendations: List[str] = []
    metrics: Dict[str, Any] = {}


class HealthAdviceResponse(BaseModel):
    """Complete health advice response with all sections"""

    diet: HealthAdviceSection
    exercise: HealthAdviceSection
    weight: HealthAdviceSection
    sleep: HealthAdviceSection
    mental_health: HealthAdviceSection
    summary: Optional[str] = None
    generated_at: str
    user_id: str


class FiveSectionParser:
    """
    Enhanced parser to ensure health advice contains all five required sections:
    1. 饮食 (Diet)
    2. 运动 (Exercise)
    3. 体重 (Weight)
    4. 睡眠 (Sleep)
    5. 心理 (Mental Health)

    Features:
    - Robust validation with completeness scoring
    - Enhanced recommendation extraction
    - Quality assessment for each section
    """

    REQUIRED_SECTIONS = ["### 饮食", "### 运动", "### 体重", "### 睡眠", "### 心理"]

    SECTION_PATTERNS = {
        "diet": r"###\s*饮食\s*\n(.*?)(?=###|\Z)",
        "exercise": r"###\s*运动\s*\n(.*?)(?=###|\Z)",
        "weight": r"###\s*体重\s*\n(.*?)(?=###|\Z)",
        "sleep": r"###\s*睡眠\s*\n(.*?)(?=###|\Z)",
        "mental_health": r"###\s*心理\s*\n(.*?)(?=###|\Z)",
    }

    def __init__(self):
        self.logger = logger
        self.required_sections = [s.value for s in SectionType]
        self.enhanced_patterns = {
            section.value: rf"###\s*{section.value}\s*\n(.*?)(?=###|\Z)"
            for section in SectionType
        }

    def validate_sections(self, response: str) -> Dict[str, bool]:
        """
        Validate that all required sections are present

        Args:
            response: Raw health advice response

        Returns:
            Dict mapping section names to presence status
        """
        validation_result = {}

        for section in self.REQUIRED_SECTIONS:
            validation_result[section] = section in response

        self.logger.info(f"Section validation: {validation_result}")
        return validation_result

    def parse_sections(self, response: str) -> Dict[str, HealthAdviceSection]:
        """
        Parse response into structured sections (legacy method for compatibility)

        Args:
            response: Raw health advice response

        Returns:
            Dict mapping section names to HealthAdviceSection objects
        """
        sections = {}

        for section_key, pattern in self.SECTION_PATTERNS.items():
            # Try multiple pattern variations
            patterns_to_try = [
                pattern,  # Original pattern
                pattern.replace(r"\n", r"\s*\n\s*"),  # Allow whitespace around newlines
                pattern.replace(r"###\s*", r"#{1,4}\s*"),  # Allow 1-4 # symbols
            ]

            content = None
            for try_pattern in patterns_to_try:
                match = re.search(try_pattern, response, re.DOTALL | re.MULTILINE | re.IGNORECASE)
                if match:
                    content = match.group(1).strip()
                    break

            if content:
                # Extract recommendations from DeepSeek's numbered list format
                recommendations = []
                for line in content.split("\n"):
                    line = line.strip()
                    # Handle DeepSeek's format: "1. **标题**：内容"
                    if re.match(r'^\d+\.\s*\*\*.*?\*\*：', line):
                        # Extract the content after the colon
                        match = re.search(r'^\d+\.\s*\*\*(.*?)\*\*：(.*)$', line)
                        if match:
                            title = match.group(1).strip()
                            content_part = match.group(2).strip()
                            # Combine title and content for recommendation
                            recommendation = f"{title}：{content_part}"
                            recommendations.append(recommendation)
                    # Also handle traditional formats for backward compatibility
                    elif (line.startswith("-") or line.startswith("•") or
                          line.startswith("*") or re.match(r'^\d+\.', line)):
                        # Remove the prefix and add to recommendations
                        clean_rec = re.sub(r'^[-•*\d\.]\s*', '', line).strip()
                        if clean_rec:
                            recommendations.append(clean_rec)

                sections[section_key] = HealthAdviceSection(
                    title=self._get_section_title(section_key),
                    content=content,
                    recommendations=recommendations,
                )
            else:
                self.logger.warning(f"Section {section_key} not found in response")
                # Instead of placeholder, try to extract any content related to this section
                fallback_content = self._extract_fallback_content(response, section_key)
                sections[section_key] = HealthAdviceSection(
                    title=self._get_section_title(section_key),
                    content=fallback_content or "内容生成中，请稍后重试...",
                    recommendations=[],
                )

        return sections

    def parse_and_validate(
        self, content: str
    ) -> Tuple[Dict[str, HealthSection], List[str]]:
        """
        Enhanced parsing with validation and completeness scoring

        Args:
            content: Raw health advice response

        Returns:
            Tuple of (parsed_sections, validation_errors)
        """
        sections = {}
        errors = []

        for section_type in SectionType:
            section_name = section_type.value
            pattern = self.enhanced_patterns[section_name]

            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if not match:
                errors.append(f"缺失模块：{section_name}")
                continue

            section_content = match.group(1).strip()

            # Validate content quality
            if len(section_content) < 50:
                errors.append(f"{section_name}模块内容过少（<50字符）")

            # Extract recommendations (bullet points)
            recommendations = self._extract_recommendations(section_content)
            if len(recommendations) < 2:
                errors.append(f"{section_name}模块建议不足（<2条）")

            # Calculate completeness score
            completeness = self._calculate_completeness(section_content, section_type)

            sections[section_name] = HealthSection(
                section_type=section_type,
                content=section_content,
                recommendations=recommendations,
                completeness_score=completeness,
            )

        return sections, errors

    def _extract_recommendations(self, content: str) -> List[str]:
        """Extract bullet point recommendations with enhanced patterns"""
        patterns = [
            r"[•·-]\s*(.+)",  # Bullet points
            r"^\d+\.\s*(.+)",  # Numbered lists
            r"^\*\s*(.+)",  # Asterisk bullets
        ]

        recommendations = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            recommendations.extend([match.strip() for match in matches])

        return list(set(recommendations))  # Remove duplicates

    def _calculate_completeness(self, content: str, section_type: SectionType) -> float:
        """Calculate section completeness score based on expected elements"""

        expected_elements = {
            SectionType.DIET: [
                "热量",
                "营养",
                "食材",
                "时间",
                "蛋白质",
                "碳水",
                "脂肪",
            ],
            SectionType.EXERCISE: ["有氧", "力量", "频次", "强度", "运动", "训练"],
            SectionType.WEIGHT: ["BMI", "目标", "监测", "变化", "体重", "减重", "增重"],
            SectionType.SLEEP: ["时长", "作息", "环境", "质量", "睡眠", "小时"],
            SectionType.MENTAL: ["压力", "情绪", "激励", "支持", "心理", "心态"],
        }

        elements = expected_elements.get(section_type, [])
        if not elements:
            return 1.0

        found_count = sum(1 for element in elements if element in content)
        base_score = found_count / len(elements)

        # Bonus for content length
        length_bonus = min(0.2, len(content) / 500)

        return min(1.0, base_score + length_bonus)

    def should_retry_parse(self, errors: List[str]) -> bool:
        """Determine if parsing should be retried"""
        critical_errors = [error for error in errors if "缺失模块" in error]
        return (
            len(critical_errors) > 0 and len(critical_errors) <= 3
        )  # Retry if 1-3 modules missing

    def is_complete(self, response: str) -> bool:
        """
        Check if response contains all required sections

        Args:
            response: Raw health advice response

        Returns:
            True if all sections are present
        """
        validation = self.validate_sections(response)
        return all(validation.values())

    def get_missing_sections(self, response: str) -> List[str]:
        """
        Get list of missing sections

        Args:
            response: Raw health advice response

        Returns:
            List of missing section names
        """
        validation = self.validate_sections(response)
        return [section for section, present in validation.items() if not present]

    def generate_completion_prompt(
        self, missing_sections: List[str], user_context: Dict[str, Any]
    ) -> str:
        """
        Generate enhanced prompt to complete missing sections

        Args:
            missing_sections: List of missing section names
            user_context: User context information

        Returns:
            Completion prompt for missing sections
        """
        prompt = f"""
请为用户补充以下缺失的健康建议模块：

用户信息：
- 年龄：{user_context.get('age', '未知')}岁
- 性别：{user_context.get('gender', '未知')}
- BMI：{user_context.get('bmi', '未知')}
- 健康目标：{user_context.get('health_goal', '整体健康')}

需要补充的模块：
{', '.join(missing_sections)}

请按照以下格式生成缺失的模块，每个模块至少包含3条具体建议：

"""

        section_templates = {
            "### 饮食": "基于用户BMI和健康目标，提供个性化的饮食建议，包括热量控制、营养配比、推荐食材等。",
            "### 运动": "根据用户体质和目标，制定合适的运动计划，包括运动类型、强度、频次等。",
            "### 体重": "基于用户当前状况，提供科学的体重管理建议和目标设定。",
            "### 睡眠": "针对用户睡眠质量，提供改善睡眠的具体方法和作息建议。",
            "### 心理": "从心理健康角度提供情绪管理、压力缓解的实用建议。",
        }

        for section in missing_sections:
            if section in section_templates:
                prompt += f"\n{section}\n{section_templates[section]}\n"

        return prompt

    def _extract_fallback_content(self, response: str, section_key: str) -> Optional[str]:
        """Extract fallback content when section headers are not found"""
        keywords = {
            "diet": ["饮食", "营养", "食物", "热量", "蛋白质", "碳水", "脂肪"],
            "exercise": ["运动", "锻炼", "训练", "有氧", "力量", "健身"],
            "weight": ["体重", "BMI", "减重", "增重", "目标"],
            "sleep": ["睡眠", "作息", "休息", "小时"],
            "mental_health": ["心理", "情绪", "压力", "心态", "激励"]
        }

        section_keywords = keywords.get(section_key, [])
        if not section_keywords:
            return None

        # Look for sentences containing these keywords
        sentences = re.split(r'[。！？\n]', response)
        relevant_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence for keyword in section_keywords) and len(sentence) > 10:
                relevant_sentences.append(sentence)

        return '\n'.join(relevant_sentences[:3]) if relevant_sentences else None

    def _get_section_title(self, section_key: str) -> str:
        """Get Chinese title for section key"""
        titles = {
            "diet": "饮食建议",
            "exercise": "运动计划",
            "weight": "体重管理",
            "sleep": "睡眠优化",
            "mental_health": "心理健康",
        }
        return titles.get(section_key, section_key)

    def format_structured_response(
        self, sections: Dict[str, HealthAdviceSection], user_id: str
    ) -> HealthAdviceResponse:
        """
        Format parsed sections into structured response

        Args:
            sections: Parsed health advice sections
            user_id: User identifier

        Returns:
            Structured HealthAdviceResponse
        """
        return HealthAdviceResponse(
            diet=sections.get(
                "diet", HealthAdviceSection(title="饮食建议", content="暂无建议")
            ),
            exercise=sections.get(
                "exercise", HealthAdviceSection(title="运动计划", content="暂无建议")
            ),
            weight=sections.get(
                "weight", HealthAdviceSection(title="体重管理", content="暂无建议")
            ),
            sleep=sections.get(
                "sleep", HealthAdviceSection(title="睡眠优化", content="暂无建议")
            ),
            mental_health=sections.get(
                "mental_health",
                HealthAdviceSection(title="心理健康", content="暂无建议"),
            ),
            generated_at=datetime.now().isoformat(),
            user_id=user_id,
        )
