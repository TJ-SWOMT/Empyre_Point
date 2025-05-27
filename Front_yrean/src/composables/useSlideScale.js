import { ref, onMounted, onUnmounted, nextTick } from 'vue'

// Constants for the design canvas size
const DESIGN_WIDTH = 960
const DESIGN_HEIGHT = 540

export function useSlideScale(extraVerticalSpace = 240) { // default: header+controls+buttons
  const scale = ref(1)

  function calculateScale() {
    const margin = 40
    const maxW = window.innerWidth - margin * 2
    const maxH = window.innerHeight - extraVerticalSpace
    const scaleW = maxW / DESIGN_WIDTH
    const scaleH = maxH / DESIGN_HEIGHT
    scale.value = Math.min(scaleW, scaleH, 1) // never upscale above 1
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