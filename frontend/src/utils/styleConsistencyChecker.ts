/**
 * AuraWell 全局样式统一性检查工具
 * 
 * 检查所有页面和组件的设计风格一致性，确保统一的视觉语言
 */

export interface StyleConsistencyReport {
  score: number
  issues: StyleIssue[]
  recommendations: string[]
  summary: {
    totalElements: number
    consistentElements: number
    inconsistentElements: number
    coverage: number
  }
}

export interface StyleIssue {
  type: 'color' | 'typography' | 'spacing' | 'border' | 'shadow' | 'component'
  severity: 'low' | 'medium' | 'high' | 'critical'
  element: string
  description: string
  expected: string
  actual: string
  solution: string
}

export interface DesignTokenUsage {
  colors: Map<string, number>
  fonts: Map<string, number>
  spacing: Map<string, number>
  borderRadius: Map<string, number>
  shadows: Map<string, number>
}

/**
 * 样式一致性检查器
 */
export class StyleConsistencyChecker {
  private designTokens = {
    colors: {
      primary: '#1a365d',
      health: '#2d7d32',
      accent: '#d84315',
      background: '#ffffff',
      'background-alt': '#f8fafc',
      'background-surface': '#f1f5f9',
      'background-elevated': '#ffffff',
      'text-primary': '#212529',
      'text-secondary': '#6c757d',
      'text-muted': '#adb5bd',
      'border-light': '#e9ecef',
      'border': '#dee2e6',
      'border-strong': '#adb5bd'
    },
    
    fonts: {
      'font-family-sans': 'Inter, system-ui, -apple-system, sans-serif',
      'font-family-mono': 'JetBrains Mono, Consolas, monospace'
    },
    
    spacing: {
      '1': '0.25rem',
      '2': '0.5rem',
      '3': '0.75rem',
      '4': '1rem',
      '5': '1.25rem',
      '6': '1.5rem',
      '8': '2rem',
      '10': '2.5rem',
      '12': '3rem',
      '16': '4rem',
      '20': '5rem',
      '24': '6rem'
    },
    
    borderRadius: {
      'sm': '0.375rem',
      'base': '0.5rem',
      'md': '0.75rem',
      'lg': '1rem',
      'xl': '1.5rem',
      '2xl': '2rem'
    },
    
    shadows: {
      'sm': '0 1px 2px rgba(0, 0, 0, 0.05)',
      'base': '0 1px 3px rgba(0, 0, 0, 0.1)',
      'md': '0 4px 6px rgba(0, 0, 0, 0.1)',
      'lg': '0 10px 15px rgba(0, 0, 0, 0.1)'
    }
  }

  /**
   * 执行完整的样式一致性检查
   */
  checkConsistency(): StyleConsistencyReport {
    const issues: StyleIssue[] = []
    let totalElements = 0
    let consistentElements = 0

    // 检查颜色使用
    const colorIssues = this.checkColorConsistency()
    issues.push(...colorIssues)

    // 检查字体使用
    const fontIssues = this.checkTypographyConsistency()
    issues.push(...fontIssues)

    // 检查间距使用
    const spacingIssues = this.checkSpacingConsistency()
    issues.push(...spacingIssues)

    // 检查组件一致性
    const componentIssues = this.checkComponentConsistency()
    issues.push(...componentIssues)

    // 检查边框和阴影
    const borderIssues = this.checkBorderConsistency()
    issues.push(...borderIssues)

    // 计算统计信息
    const allElements = document.querySelectorAll('*')
    totalElements = allElements.length
    consistentElements = totalElements - issues.length
    
    const score = Math.round((consistentElements / totalElements) * 100)
    const coverage = Math.round((consistentElements / totalElements) * 100)

    // 生成建议
    const recommendations = this.generateRecommendations(issues)

    return {
      score,
      issues,
      recommendations,
      summary: {
        totalElements,
        consistentElements,
        inconsistentElements: issues.length,
        coverage
      }
    }
  }

  /**
   * 检查颜色使用一致性
   */
  private checkColorConsistency(): StyleIssue[] {
    const issues: StyleIssue[] = []
    const elements = document.querySelectorAll('*')

    elements.forEach((element, index) => {
      const computedStyle = window.getComputedStyle(element)
      const color = computedStyle.color
      const backgroundColor = computedStyle.backgroundColor
      
      // 检查是否使用了非设计令牌的颜色
      if (this.isCustomColor(color) && !this.isDesignTokenColor(color)) {
        issues.push({
          type: 'color',
          severity: 'medium',
          element: `${element.tagName.toLowerCase()}[${index}]`,
          description: '使用了非设计令牌的文字颜色',
          expected: '使用设计令牌中定义的颜色',
          actual: color,
          solution: '替换为 var(--color-text-primary) 或其他设计令牌颜色'
        })
      }

      if (this.isCustomColor(backgroundColor) && !this.isDesignTokenColor(backgroundColor)) {
        issues.push({
          type: 'color',
          severity: 'medium',
          element: `${element.tagName.toLowerCase()}[${index}]`,
          description: '使用了非设计令牌的背景颜色',
          expected: '使用设计令牌中定义的颜色',
          actual: backgroundColor,
          solution: '替换为 var(--color-background) 或其他设计令牌颜色'
        })
      }
    })

    return issues
  }

  /**
   * 检查字体使用一致性
   */
  private checkTypographyConsistency(): StyleIssue[] {
    const issues: StyleIssue[] = []
    const elements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, div')

    elements.forEach((element, index) => {
      const computedStyle = window.getComputedStyle(element)
      const fontFamily = computedStyle.fontFamily

      // 检查字体族
      if (!this.isDesignTokenFont(fontFamily)) {
        issues.push({
          type: 'typography',
          severity: 'high',
          element: `${element.tagName.toLowerCase()}[${index}]`,
          description: '使用了非标准字体',
          expected: 'Inter, system-ui, -apple-system, sans-serif',
          actual: fontFamily,
          solution: '使用 var(--font-family-sans) 或标准字体栈'
        })
      }

      // 检查是否使用了标准的文字类名
      const classList = Array.from(element.classList)
      const hasTextClass = classList.some(cls => 
        cls.startsWith('text-heading-') || 
        cls.startsWith('text-body') || 
        cls.startsWith('text-caption') ||
        cls.startsWith('text-metric')
      )

      if (!hasTextClass && element.textContent?.trim()) {
        issues.push({
          type: 'typography',
          severity: 'low',
          element: `${element.tagName.toLowerCase()}[${index}]`,
          description: '未使用标准文字样式类',
          expected: 'text-heading-*, text-body, text-caption 等',
          actual: classList.join(' '),
          solution: '添加适当的文字样式类名'
        })
      }
    })

    return issues
  }

  /**
   * 检查间距使用一致性
   */
  private checkSpacingConsistency(): StyleIssue[] {
    const issues: StyleIssue[] = []
    const elements = document.querySelectorAll('*')

    elements.forEach((element, index) => {
      const computedStyle = window.getComputedStyle(element)
      const margin = computedStyle.margin
      const padding = computedStyle.padding

      // 检查是否使用了非标准间距值
      if (this.hasCustomSpacing(margin) || this.hasCustomSpacing(padding)) {
        const classList = Array.from(element.classList)
        const hasSpacingClass = classList.some(cls => 
          cls.match(/^(m|p)[trblxy]?-\d+$/) || 
          cls.match(/^gap-\d+$/) ||
          cls.match(/^space-[xy]-\d+$/)
        )

        if (!hasSpacingClass) {
          issues.push({
            type: 'spacing',
            severity: 'low',
            element: `${element.tagName.toLowerCase()}[${index}]`,
            description: '使用了自定义间距值',
            expected: '使用 Tailwind 间距类或设计令牌',
            actual: `margin: ${margin}, padding: ${padding}`,
            solution: '使用 m-*, p-*, gap-* 等标准间距类'
          })
        }
      }
    })

    return issues
  }

  /**
   * 检查组件使用一致性
   */
  private checkComponentConsistency(): StyleIssue[] {
    const issues: StyleIssue[] = []

    // 检查卡片组件
    const cards = document.querySelectorAll('.card, [class*="card"]')
    cards.forEach((card, index) => {
      const classList = Array.from(card.classList)
      const hasAuraCard = classList.includes('aura-card')

      if (!hasAuraCard) {
        issues.push({
          type: 'component',
          severity: 'high',
          element: `card[${index}]`,
          description: '未使用标准卡片组件',
          expected: 'aura-card',
          actual: classList.join(' '),
          solution: '替换为 aura-card 组件'
        })
      }
    })

    // 检查按钮组件
    const buttons = document.querySelectorAll('button, .btn, [class*="btn"]')
    buttons.forEach((button, index) => {
      const classList = Array.from(button.classList)
      const hasAuraBtn = classList.some(cls => cls.startsWith('aura-btn'))

      if (!hasAuraBtn && button.tagName === 'BUTTON') {
        issues.push({
          type: 'component',
          severity: 'high',
          element: `button[${index}]`,
          description: '未使用标准按钮组件',
          expected: 'aura-btn aura-btn--primary',
          actual: classList.join(' '),
          solution: '添加 aura-btn 和相应的变体类'
        })
      }
    })

    return issues
  }

  /**
   * 检查边框和阴影一致性
   */
  private checkBorderConsistency(): StyleIssue[] {
    const issues: StyleIssue[] = []
    const elements = document.querySelectorAll('*')

    elements.forEach((element, index) => {
      const computedStyle = window.getComputedStyle(element)
      const borderRadius = computedStyle.borderRadius
      const boxShadow = computedStyle.boxShadow

      // 检查边框圆角
      if (borderRadius && borderRadius !== '0px' && !this.isStandardBorderRadius(borderRadius)) {
        issues.push({
          type: 'border',
          severity: 'low',
          element: `${element.tagName.toLowerCase()}[${index}]`,
          description: '使用了非标准圆角值',
          expected: '使用设计令牌中的圆角值',
          actual: borderRadius,
          solution: '使用 rounded-sm, rounded-md, rounded-lg 等标准类'
        })
      }

      // 检查阴影
      if (boxShadow && boxShadow !== 'none' && !this.isStandardShadow(boxShadow)) {
        issues.push({
          type: 'shadow',
          severity: 'low',
          element: `${element.tagName.toLowerCase()}[${index}]`,
          description: '使用了非标准阴影值',
          expected: '使用设计令牌中的阴影值',
          actual: boxShadow,
          solution: '使用 shadow-sm, shadow-md, shadow-lg 等标准类'
        })
      }
    })

    return issues
  }

  /**
   * 生成修复建议
   */
  private generateRecommendations(issues: StyleIssue[]): string[] {
    const recommendations: string[] = []
    const issueTypes = new Set(issues.map(issue => issue.type))

    if (issueTypes.has('color')) {
      recommendations.push('统一使用设计令牌中定义的颜色变量')
    }

    if (issueTypes.has('typography')) {
      recommendations.push('使用标准的文字样式类名（text-heading-*, text-body, text-caption）')
    }

    if (issueTypes.has('spacing')) {
      recommendations.push('使用 Tailwind 的标准间距类（m-*, p-*, gap-*）')
    }

    if (issueTypes.has('component')) {
      recommendations.push('统一使用 aura 组件系统（aura-card, aura-btn）')
    }

    if (issueTypes.has('border') || issueTypes.has('shadow')) {
      recommendations.push('使用标准的边框圆角和阴影类名')
    }

    if (recommendations.length === 0) {
      recommendations.push('样式一致性良好，继续保持统一的设计语言！')
    }

    return recommendations
  }

  /**
   * 工具方法
   */
  private isCustomColor(color: string): boolean {
    return color !== 'rgba(0, 0, 0, 0)' && 
           color !== 'transparent' && 
           color !== 'inherit' && 
           color !== 'initial'
  }

  private isDesignTokenColor(color: string): boolean {
    // 简化检查，实际应该解析CSS变量
    return color.includes('var(--color-') || 
           Object.values(this.designTokens.colors).includes(color)
  }

  private isDesignTokenFont(fontFamily: string): boolean {
    return fontFamily.includes('Inter') || 
           fontFamily.includes('system-ui') ||
           fontFamily.includes('JetBrains Mono')
  }

  private hasCustomSpacing(spacing: string): boolean {
    // 检查是否使用了非标准间距值
    const standardValues = ['0px', 'auto', 'inherit', 'initial']
    return !standardValues.includes(spacing) && 
           !spacing.match(/^\d+(\.\d+)?(rem|px)$/)
  }

  private isStandardBorderRadius(borderRadius: string): boolean {
    const standardValues = Object.values(this.designTokens.borderRadius)
    return standardValues.some(value => borderRadius.includes(value))
  }

  private isStandardShadow(boxShadow: string): boolean {
    const standardValues = Object.values(this.designTokens.shadows)
    return standardValues.some(value => {
      const parts = value.split(' ')
      return parts.length > 1 && parts[1] && boxShadow.includes(parts[1])
    })
  }

  /**
   * 获取设计令牌使用统计
   */
  getDesignTokenUsage(): DesignTokenUsage {
    const usage: DesignTokenUsage = {
      colors: new Map(),
      fonts: new Map(),
      spacing: new Map(),
      borderRadius: new Map(),
      shadows: new Map()
    }

    const elements = document.querySelectorAll('*')
    
    elements.forEach(element => {
      const computedStyle = window.getComputedStyle(element)
      
      // 统计颜色使用
      const color = computedStyle.color
      const backgroundColor = computedStyle.backgroundColor
      
      if (this.isDesignTokenColor(color)) {
        usage.colors.set(color, (usage.colors.get(color) || 0) + 1)
      }
      
      if (this.isDesignTokenColor(backgroundColor)) {
        usage.colors.set(backgroundColor, (usage.colors.get(backgroundColor) || 0) + 1)
      }

      // 统计字体使用
      const fontFamily = computedStyle.fontFamily
      if (this.isDesignTokenFont(fontFamily)) {
        usage.fonts.set(fontFamily, (usage.fonts.get(fontFamily) || 0) + 1)
      }
    })

    return usage
  }

  /**
   * 生成样式一致性报告
   */
  generateReport(): string {
    const report = this.checkConsistency()

    let reportText = `# AuraWell 样式一致性报告\n\n`
    reportText += `## 总体评分: ${report.score}/100\n\n`
    reportText += `## 统计信息\n`
    reportText += `- 总元素数: ${report.summary.totalElements}\n`
    reportText += `- 一致元素数: ${report.summary.consistentElements}\n`
    reportText += `- 不一致元素数: ${report.summary.inconsistentElements}\n`
    reportText += `- 覆盖率: ${report.summary.coverage}%\n\n`

    if (report.issues.length > 0) {
      reportText += `## 发现的问题 (${report.issues.length})\n\n`
      
      const groupedIssues = report.issues.reduce((groups, issue) => {
        if (!groups[issue.type]) {
          groups[issue.type] = []
        }
        groups[issue.type]?.push(issue)
        return groups
      }, {} as Record<string, StyleIssue[]>)

      Object.entries(groupedIssues).forEach(([type, issues]) => {
        reportText += `### ${type.toUpperCase()} 问题 (${issues.length})\n\n`
        issues.forEach((issue, index) => {
          reportText += `${index + 1}. **${issue.severity.toUpperCase()}**: ${issue.description}\n`
          reportText += `   - 元素: ${issue.element}\n`
          reportText += `   - 期望: ${issue.expected}\n`
          reportText += `   - 实际: ${issue.actual}\n`
          reportText += `   - 解决方案: ${issue.solution}\n\n`
        })
      })
    }

    reportText += `## 建议\n\n`
    report.recommendations.forEach((rec, index) => {
      reportText += `${index + 1}. ${rec}\n`
    })

    return reportText
  }
}

/**
 * 创建样式一致性检查器实例
 */
export function createStyleConsistencyChecker(): StyleConsistencyChecker {
  return new StyleConsistencyChecker()
}
