import { ref, onMounted, onUnmounted, nextTick } from 'vue'

// Constants for the design canvas size
const DESIGN_WIDTH = 960
const DESIGN_HEIGHT = 540

export function useSlideScale(availableHeightRef, availableWidthRef) {
  const scale = ref(1)

  function calculateScale() {
    const width = availableWidthRef?.value || window.innerWidth
    const height = availableHeightRef?.value || window.innerHeight
    const scaleW = width / DESIGN_WIDTH
    const scaleH = height / DESIGN_HEIGHT
    scale.value = Math.min(scaleW, scaleH, 1) // Never scale up beyond 1
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