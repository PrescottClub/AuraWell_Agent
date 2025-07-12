// src/plugins/motion.js
import { MotionPlugin } from '@vueuse/motion'

export default {
  install(app) {
    app.use(MotionPlugin, {
      directives: {
        // 定义一个名为 'pop' 的全局预设
        'pop': {
          initial: { scale: 1, opacity: 1 },
          hovered: { scale: 1.05 },
          tapped: { scale: 0.98 },
          visible: { // 当元素进入视口时
            scale: 1,
            opacity: 1,
            transition: {
              type: 'spring',
              stiffness: 350,
              damping: 20,
              delay: 100,
            }
          },
          hidden: { // 当元素离开视口时
            scale: 0.8,
            opacity: 0,
          }
        },
        // 添加一个卡片入场动画预设
        'card-slide': {
          initial: { y: 50, opacity: 0 },
          visible: {
            y: 0,
            opacity: 1,
            transition: {
              type: 'spring',
              stiffness: 300,
              damping: 25,
              delay: 200,
            }
          },
          hidden: { y: 50, opacity: 0 }
        },
        // 添加一个按钮弹跳动画预设
        'bounce': {
          initial: { scale: 1 },
          hovered: { 
            scale: 1.05,
            transition: {
              type: 'spring',
              stiffness: 400,
              damping: 20
            }
          },
          tapped: { 
            scale: 0.95,
            transition: {
              type: 'spring',
              stiffness: 600,
              damping: 15
            }
          }
        }
      }
    })
  }
}