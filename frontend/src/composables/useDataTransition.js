import { ref } from 'vue';
import { gsap } from 'gsap';

export function useDataTransition() {
  const isAnimating = ref(false);

  // 数值变化动画
  const animateValueChange = (element, fromValue, toValue, options = {}) => {
    const {
      duration = 1.2,
      delay = 0,
      easing = 'power2.out',
      onComplete = () => {},
      precision = 0,
    } = options;

    if (!element || isAnimating.value) return Promise.resolve();

    isAnimating.value = true;

    return new Promise(resolve => {
      const obj = { value: fromValue };

      gsap.to(obj, {
        value: toValue,
        duration,
        delay,
        ease: easing,
        onUpdate: () => {
          element.textContent = obj.value.toFixed(precision);
        },
        onComplete: () => {
          isAnimating.value = false;
          onComplete();
          resolve();
        },
      });
    });
  };

  // 数据更新脉冲效果
  const pulseOnUpdate = (element, options = {}) => {
    const { scale = 1.05, duration = 0.3, color = '#10B981' } = options;

    if (!element) return;

    // 轻微缩放 + 颜色变化
    gsap
      .timeline()
      .to(element, {
        scale,
        color,
        duration: duration / 2,
        ease: 'power2.out',
      })
      .to(element, {
        scale: 1,
        color: 'inherit',
        duration: duration / 2,
        ease: 'power2.out',
      });
  };

  // 趋势指示器动画
  const animateTrend = (element, trendValue, options = {}) => {
    const { duration = 0.6, bounceScale = 1.1 } = options;

    if (!element) return;

    const isPositive = trendValue > 0;
    const color = isPositive ? '#10B981' : '#EF4444';

    gsap
      .timeline()
      .fromTo(
        element,
        { opacity: 0, y: isPositive ? 10 : -10 },
        { opacity: 1, y: 0, duration: duration / 2, ease: 'power2.out' }
      )
      .to(element, {
        scale: bounceScale,
        color,
        duration: 0.2,
        ease: 'back.out(1.7)',
        yoyo: true,
        repeat: 1,
      });
  };

  // 进度条平滑增长
  const animateProgress = (element, percentage, options = {}) => {
    const { duration = 1.5, delay = 0, easing = 'power2.out' } = options;

    if (!element) return;

    gsap.fromTo(
      element,
      { width: '0%' },
      {
        width: `${percentage}%`,
        duration,
        delay,
        ease: easing,
      }
    );
  };

  // 卡片数据刷新动画
  const refreshCardData = (cardElement, options = {}) => {
    const { duration = 0.4, stagger = 0.1 } = options;

    if (!cardElement) return;

    const dataElements = cardElement.querySelectorAll('[data-animate="value"]');

    gsap
      .timeline()
      .to(dataElements, {
        opacity: 0.3,
        scale: 0.95,
        duration: duration / 2,
        stagger,
        ease: 'power2.out',
      })
      .to(dataElements, {
        opacity: 1,
        scale: 1,
        duration: duration / 2,
        stagger,
        ease: 'back.out(1.7)',
      });
  };

  // 数据加载骨架屏过渡
  const transitionFromSkeleton = (
    skeletonElement,
    contentElement,
    options = {}
  ) => {
    const { duration = 0.6 } = options;

    if (!skeletonElement || !contentElement) return;

    return gsap
      .timeline()
      .to(skeletonElement, {
        opacity: 0,
        scale: 0.98,
        duration: duration / 2,
        ease: 'power2.out',
      })
      .fromTo(
        contentElement,
        { opacity: 0, y: 20 },
        {
          opacity: 1,
          y: 0,
          duration: duration / 2,
          ease: 'power2.out',
        },
        `-=${duration / 4}`
      );
  };

  return {
    isAnimating,
    animateValueChange,
    pulseOnUpdate,
    animateTrend,
    animateProgress,
    refreshCardData,
    transitionFromSkeleton,
  };
}
