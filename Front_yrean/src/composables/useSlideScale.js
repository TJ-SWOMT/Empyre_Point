import { ref, onMounted, onUnmounted, nextTick } from 'vue'

// Constants for the design canvas size
const DESIGN_WIDTH = 960
const DESIGN_HEIGHT = 540

export function useSlideScale() {
  const scale = ref(1)

  function calculateScale() {
    const scaleW = window.innerWidth / DESIGN_WIDTH
    const scaleH = window.innerHeight / DESIGN_HEIGHT
    scale.value = Math.min(scaleW, scaleH)
  }

  onMounted(() => {
    calculateScale()
    window.addEventListener('resize', calculateScale)
    nextTick(() => calculateScale())
  })

  onUnmounted(() => {
    window.removeEventListener('resize', calculateScale)
  })

  return {
    scale,
    calculateScale,
    DESIGN_WIDTH,
    DESIGN_HEIGHT
  }
} 