<script setup>
import { ref, onMounted, watch, computed, nextTick, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'
import { marked } from 'marked'
import { useSlideScale } from '../composables/useSlideScale'
import BackgroundImageModal from './BackgroundImageModal.vue'
import '../styles/empyre-point.css'

const route = useRoute()
const router = useRouter()
const presentationId = route.params.id
const slideId = ref(route.params.slide_id)
const error = ref('')
const isSubmitting = ref(false)
const isEditMode = computed(() => !!slideId.value)
const slideTitle = ref('')
const slideSureness = ref(false)

const headerRef = ref(null)
const controlsRef = ref(null)
const actionButtonsRef = ref(null)
const availableHeight = ref(600) // fallback default

// Set up availableWidth ref
const centerFlexRef = ref(null)
const availableWidth = ref(window.innerWidth)

function updateAvailableWidth () {
  nextTick(() => {
    if (centerFlexRef.value) {
      availableWidth.value = centerFlexRef.value.offsetWidth
    } else {
      availableWidth.value = window.innerWidth
    }
  })
}

const { scale, DESIGN_WIDTH, DESIGN_HEIGHT, calculateScale } = useSlideScale(
  availableHeight,
  computed(() => window.innerWidth)
)

// Initialize background color from session storage, but use presentation-specific key
const getStoredBackgroundColor = () => {
  const storedColor = sessionStorage.getItem(
    `slideBackgroundColor_${presentationId}`
  )
  return storedColor || '#FFFFFF'
}

const backgroundColor = ref(getStoredBackgroundColor())
const slideData = ref(null)

// Watch for changes to backgroundColor and save to session storage with presentation-specific key
watch(backgroundColor, newColor => {
  sessionStorage.setItem(`slideBackgroundColor_${presentationId}`, newColor)
})

const texts = ref([])

const elements = ref([])
const selectedElement = ref(null)

const isAddingText = ref(false)

// Add computed properties for integer display
const integerFontSize = computed({
  get: () => Math.round(selectedElement.value?.element_data?.font_size || 0),
  set: value => {
    if (selectedElement.value) {
      selectedElement.value.element_data.font_size = Math.round(value)
    }
  }
})

const integerX = computed({
  get: () => Math.round(selectedElement.value?.x_position || 0),
  set: value => {
    if (selectedElement.value) {
      selectedElement.value.x_position = Math.round(value)
    }
  }
})

const integerY = computed({
  get: () => Math.round(selectedElement.value?.y_position || 0),
  set: value => {
    if (selectedElement.value) {
      selectedElement.value.y_position = Math.round(value)
    }
  }
})

const integerWidth = computed({
  get: () => Math.round(selectedElement.value?.width || 0),
  set: value => {
    if (selectedElement.value) {
      selectedElement.value.width = Math.round(value)
    }
  }
})

const integerHeight = computed({
  get: () => Math.round(selectedElement.value?.height || 0),
  set: value => {
    if (selectedElement.value) {
      selectedElement.value.height = Math.round(value)
    }
  }
})

const integerZIndex = computed({
  get: () => Math.round(selectedElement.value?.z_index || 0),
  set: value => {
    if (selectedElement.value) {
      selectedElement.value.z_index = Math.round(value)
    }
  }
})

// Add computed property for action buttons key
const actionButtonsKey = computed(() => {
  return `${isEditMode.value}-${slideId.value}-${totalSlides.value}-${newSlideNumber.value}-${isSubmitting.value}`
})

// Add new refs for background image settings
const showBackgroundImageModal = ref(false)
const backgroundImage = ref(null)
const backgroundImageOpacity = ref(1)
const backgroundImageFit = ref('cover')

// Add new refs for temporary background image settings
const tempBackgroundImage = ref(null)
const tempBackgroundImageOpacity = ref(1)
const tempBackgroundImageFit = ref('cover')

// Add new refs for slide number
const totalSlides = ref(0)
const newSlideNumber = ref(null)

// Add new refs for action bar state
const isActionBarExpanded = ref(true)
const actionBarHeight = ref(0)

// Add new ref for styling controls state
const isStylingExpanded = ref(true)

// Add new ref for loading state
const isLoading = ref(true)

// Add isMobile ref for responsive logic
const isMobile = ref(window.innerWidth <= 600)
function handleResize() {
  isMobile.value = window.innerWidth <= 600
}

const loadSlideData = async () => {
  try {
    isLoading.value = true
    const response = await presentationApi.getPresentation(presentationId)
    if (response.error) throw new Error(response.error)
    
    totalSlides.value = response.presentation.slides.length

    if (!isEditMode.value) {
      newSlideNumber.value = totalSlides.value + 1
      isLoading.value = false
      return
    }

    // For edit mode, continue with existing logic
    const slide = response.presentation.slides.find(
      s => Number(s.slide_id) === Number(slideId.value)
    )
    if (slide) {
      slideData.value = {
        ...slide,
        slide_id: Number(slide.slide_id) // Ensure consistent type
      }
      newSlideNumber.value = slide.slide_number // Set the current slide number for edit mode
      backgroundColor.value = slide.background_color || '#FFFFFF'
      slideTitle.value = slide.title || ''
      
      // Initialize both actual and temporary values
      backgroundImage.value = slide.background_image_url || null
      backgroundImageOpacity.value = slide.background_image_opacity || 1
      backgroundImageFit.value = slide.background_image_fit || 'cover'
      
      tempBackgroundImage.value = slide.background_image_url || null
      tempBackgroundImageOpacity.value = slide.background_image_opacity || 1
      tempBackgroundImageFit.value = slide.background_image_fit || 'cover'
    } else {
      throw new Error('Slide not found')
    }
  } catch (err) {
    error.value = handleApiError(err)
  } finally {
    isLoading.value = false
  }
}

const loadSlideElements = async () => {
  
  if (!isEditMode.value) {
    isLoading.value = false
    return
  }

  try {
    isLoading.value = true
    const response = await presentationApi.getSlideElements(slideId.value)
    if (response.error) throw new Error(response.error)
    elements.value = response.elements || []
  } catch (err) {
    error.value = handleApiError(err)
  } finally {
    isLoading.value = false
  }
}

// Helper to reorder slides after save
async function reorderSlides(presentationId, movedSlideId, newNumber) {
  // 1. Fetch all slides
  const response = await presentationApi.getPresentation(presentationId)
  if (!response.success) return

  let slides = response.presentation.slides.sort((a, b) => a.slide_number - b.slide_number)

  // 2. Remove the moved slide from the array (if it exists)
  const movedSlideIndex = slides.findIndex(s => String(s.slide_id) === String(movedSlideId))
  let movedSlide
  if (movedSlideIndex !== -1) {
    [movedSlide] = slides.splice(movedSlideIndex, 1)
  } else {
    // For new slides, fetch the slide data
    const newSlideResp = await presentationApi.getPresentation(presentationId)
    movedSlide = newSlideResp.presentation.slides.find(s => String(s.slide_id) === String(movedSlideId))
  }
  if (!movedSlide) return

  // 3. Insert the moved slide at the new position (newNumber - 1)
  slides.splice(newNumber - 1, 0, movedSlide)

  // 4. Update slide_number for all slides
  for (let i = 0; i < slides.length; i++) {
    const slide = slides[i]
    const correctNumber = i + 1
    if (slide.slide_number !== correctNumber) {
      await presentationApi.updateSlide(
        slide.slide_id,
        correctNumber,
        slide.background_color,
        slide.background_image_url,
        slide.title,
        slide.background_image_opacity,
        slide.background_image_fit
      )
    }
  }
}

const saveSlide = async (shouldRedirect = false) => {
  try {
    isSubmitting.value = true
    error.value = ''

    // Update the actual background image values from temporary ones
    backgroundImage.value = tempBackgroundImage.value
    backgroundImageOpacity.value = tempBackgroundImageOpacity.value
    backgroundImageFit.value = tempBackgroundImageFit.value

    let response
    let wasNewSlide = false
    let oldSlideNumber = slideData.value?.slide_number
    if (isEditMode.value && !slideId.value.toString().startsWith('temp-')) {
      // Update existing slide
      response = await presentationApi.updateSlide(
        Number(slideId.value),
        newSlideNumber.value !== slideData.value?.slide_number ? newSlideNumber.value : undefined,
        backgroundColor.value,
        backgroundImage.value,
        slideTitle.value,
        backgroundImageOpacity.value,
        backgroundImageFit.value
      )
    } else {
      // For new slides, get the total number of slides first
      const presentationResponse = await presentationApi.getPresentation(presentationId)
      if (presentationResponse.error) throw new Error(presentationResponse.error)
      
      // Calculate the new slide number (last slide number + 1)
      const lastSlideNumber = presentationResponse.presentation.slides.length > 0 
        ? Math.max(...presentationResponse.presentation.slides.map(s => s.slide_number))
        : 0
      const newSlideNumberToUse = newSlideNumber.value

      // Create new slide with the chosen slide number
      response = await presentationApi.createSlide(
        presentationId,
        newSlideNumberToUse,
        backgroundColor.value,
        backgroundImage.value,
        slideTitle.value,
        backgroundImageOpacity.value,
        backgroundImageFit.value
      )
      wasNewSlide = true
    }

    if (response.error) {
      throw new Error(response.error)
    }

    // If this was a new slide, update the slideId
    if (!isEditMode.value || slideId.value.toString().startsWith('temp-')) {
      slideId.value = response.slide.slide_id
    }

    // Save all element positions, sizes, and styles
    const updatePromises = elements.value.map(async element => {
      // Skip temporary elements that haven't been saved yet
      if (element.element_id.toString().startsWith('temp-')) {
        // Create new element
        if (element.element_type === 'text') {
          const response = await presentationApi.createTextElement(slideId.value, {
            content: element.element_data.content,
            x_position: element.x_position,
            y_position: element.y_position,
            width: element.width,
            height: element.height,
            z_index: element.z_index,
            font_family: element.element_data.font_family,
            font_size: element.element_data.font_size,
            font_color: element.element_data.font_color,
            bold: element.element_data.bold,
            italic: element.element_data.italic,
            underline: element.element_data.underline,
            text_align: element.element_data.text_align
          })
          if (response.error) throw new Error(response.error)
          return response.element
        } else if (element.element_type === 'image') {
          const response = await presentationApi.createImageElement(slideId.value, {
            image_url: element.element_data.image_url,
            x_position: element.x_position,
            y_position: element.y_position,
            width: element.width,
            height: element.height,
            z_index: element.z_index
          })
          if (response.error) throw new Error(response.error)
          return response.element
        }
      } else {
        // Update existing element
        return updateElement(element.element_id, {
          x_position: element.x_position,
          y_position: element.y_position,
          width: element.width,
          height: element.height,
          z_index: element.z_index,
          font_family: element.element_data?.font_family,
          font_size: element.element_data?.font_size,
          font_color: element.element_data?.font_color,
          bold: element.element_data?.bold,
          italic: element.element_data?.italic,
          underline: element.element_data?.underline,
          text_align: element.element_data?.text_align,
          content: element.element_data?.content
        })
      }
    })
    await Promise.all(updatePromises)

    // Reorder slides if needed (for both new and edit)
    await reorderSlides(presentationId, slideId.value, newSlideNumber.value)

    // Only redirect if explicitly requested
    if (shouldRedirect) {
      router.push(`/presentations/${presentationId}`)
    } else if (!isEditMode.value && response.slide) {
      // For new slides, just update the URL without redirecting
      router.replace(`/presentations/${presentationId}/slides/${response.slide.slide_id}`)
      return response
    }
  } catch (err) {
    error.value = handleApiError(err)
    return null
  } finally {
    isSubmitting.value = false
  }
}

const addText = () => {
  isAddingText.value = true
  // Change cursor to indicate we're in text adding mode
  const slideContainer = document.querySelector('.slide-container')
  if (slideContainer) {
    slideContainer.style.cursor = 'text'
  }
}

const deleteText = id => {
  texts.value = texts.value.filter(text => text.id !== id)
}

const deleteSlide = async event => {
  if (event) {
    event.preventDefault()
    event.stopPropagation()
  }

  if (!slideSureness.value) {
    slideSureness.value = true
    return
  }

  try {
    await presentationApi.deleteSlide(slideId.value)
    router.push(`/presentations/${presentationId}`)
  } catch (err) {
    error.value = handleApiError(err)
    slideSureness.value = false // Reset on error
  }
}

const resetSlideSureness = () => {
  slideSureness.value = false
}

// Add click outside handler for slide deletion
const handleClickOutside = event => {
  // If click is outside both .text-element and .element-styling and delete button, reset slideSureness
  if (
    !event.target.closest('.text-element') &&
    !event.target.closest('.element-styling') &&
    !event.target.closest('.delete-slide-button')
  ) {
    resetSlideSureness()
  }
}

const addImage = async () => {
  try {
    // Create a file input element
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*'

    // Handle file selection
    input.onchange = async event => {
      const file = event.target.files[0]
      if (!file) return

      let imgUrl = null
      try {
        // Create a temporary image to get dimensions
        const img = new Image()
        imgUrl = URL.createObjectURL(file)

        // Wait for image to load to get dimensions
        await new Promise((resolve, reject) => {
          img.onload = resolve
          img.onerror = reject
          img.src = imgUrl
        })

        // Calculate dimensions to fit within slide while maintaining aspect ratio
        const slideAspectRatio = DESIGN_WIDTH / DESIGN_HEIGHT
        const imageAspectRatio = img.width / img.height

        let finalWidth, finalHeight

        if (imageAspectRatio > slideAspectRatio) {
          // Image is wider than slide aspect ratio, fit to width
          finalWidth = DESIGN_WIDTH * 0.9 // 90% of slide width
          finalHeight = finalWidth / imageAspectRatio
        } else {
          // Image is taller than slide aspect ratio, fit to height
          finalHeight = DESIGN_HEIGHT * 0.9 // 90% of slide height
          finalWidth = finalHeight * imageAspectRatio
        }

        // Round dimensions to integers
        finalWidth = Math.round(finalWidth)
        finalHeight = Math.round(finalHeight)

        // Upload the image
        const uploadResponse = await presentationApi.uploadImage(file)
        if (uploadResponse.error) {
          throw new Error(uploadResponse.error)
        }

        // For new slides, create a temporary slide ID if we don't have one
        if (!isEditMode.value && !slideId.value) {
          slideId.value = 'temp-' + Date.now()
        }

        // Calculate position to center the image
        const xPos = Math.round((DESIGN_WIDTH - finalWidth) / 2)
        const yPos = Math.round((DESIGN_HEIGHT - finalHeight) / 2)

        const elementData = {
          image_url: uploadResponse.image_url,
          x_position: xPos,
          y_position: yPos,
          width: finalWidth,
          height: finalHeight,
          z_index: elements.value.length || 0
        }

        // Only make API call if we're in edit mode
        if (isEditMode.value && !slideId.value.toString().startsWith('temp-')) {
          const response = await presentationApi.createImageElement(
            slideId.value,
            elementData
          )
          if (response.error) {
            throw new Error(response.error)
          }

          // Add the new element to the elements array
          elements.value.push({
            element_id: response.element.element_id,
            element_type: 'image',
            x_position: xPos,
            y_position: yPos,
            width: finalWidth,
            height: finalHeight,
            z_index: elements.value.length || 0,
            element_data: {
              image_url: uploadResponse.image_url,
              alt_text: '',
              natural_width: img.width,
              natural_height: img.height
            }
          })
        } else {
          // For new slides or temporary slides, create element locally
          const tempElementId = 'temp-' + Date.now()
          elements.value.push({
            element_id: tempElementId,
            element_type: 'image',
            x_position: xPos,
            y_position: yPos,
            width: finalWidth,
            height: finalHeight,
            z_index: elements.value.length || 0,
            element_data: {
              image_url: uploadResponse.image_url,
              alt_text: '',
              natural_width: img.width,
              natural_height: img.height
            }
          })
        }

        // Select the new element
        selectedElement.value = elements.value[elements.value.length - 1]
      } catch (err) {
        error.value = handleApiError(err)
        console.error('Error in image upload handler:', err)
      } finally {
        // Clean up
        if (imgUrl) {
          URL.revokeObjectURL(imgUrl)
        }
      }
    }

    // Trigger file selection
    input.click()
  } catch (err) {
    error.value = handleApiError(err)
    console.error('Error adding image:', err)
  }
}

// Add a computed property for maintaining aspect ratio
const aspectRatio = computed(() => {
  if (!selectedElement.value || selectedElement.value.element_type !== 'image')
    return null
  const { natural_width, natural_height } = selectedElement.value.element_data
  return natural_width / natural_height
})

// Modify the width/height update handlers to maintain aspect ratio
const updateElementDimensions = async (width, height) => {
  if (!selectedElement.value || selectedElement.value.element_type !== 'image')
    return

  const updates = {}
  if (width !== undefined) {
    updates.width = width
    if (aspectRatio.value) {
      updates.height = Math.round(width / aspectRatio.value)
    }
  } else if (height !== undefined) {
    updates.height = height
    if (aspectRatio.value) {
      updates.width = Math.round(height * aspectRatio.value)
    }
  }

  await updateElement(selectedElement.value.element_id, updates)
}

const box = ref(null)
const pageX = ref(null)
const pageY = ref(null)

// Update the helper function to validate integer IDs
const validateElementId = id => {
  if (!id) {
    console.error('Missing element ID')
    throw new Error('Missing element ID')
  }
  const numId = typeof id === 'string' ? parseInt(id, 10) : id
  if (isNaN(numId)) {
    console.error('Invalid element ID:', id)
    throw new Error('Invalid element ID')
  }
  return numId
}

// Add a new ref to track the current editing state
const currentEditState = ref(null)

const updateElement = async (elementId, updates) => {
  try {
    const numericId = validateElementId(elementId)
    console.log('Updating element with ID:', numericId, 'Updates:', updates)

    // Find the current element to get its type
    const currentElement = elements.value.find(e => validateElementId(e.element_id) === numericId)
    if (!currentElement) {
      throw new Error('Element not found')
    }

    // Ensure numeric values are integers
    const integerUpdates = Object.entries(updates).reduce(
      (acc, [key, value]) => {
        // Convert numeric values to integers
        if (typeof value === 'number') {
          acc[key] = Math.round(value)
        } else {
          acc[key] = value
        }
        return acc
      },
      {}
    )

    const response = await presentationApi.updateElement(numericId, {
      element_type: currentElement.element_type, // Use the actual element type
      ...integerUpdates
    })

    console.log('Server response:', JSON.stringify(response, null, 2))

    if (response.error) throw new Error(response.error)

    if (!response.success || !response.element) {
      console.error('Invalid server response:', response)
      throw new Error('Invalid server response')
    }

    // Create a new array to trigger reactivity
    const updatedElements = elements.value.map(e => {
      if (validateElementId(e.element_id) === numericId) {
        // Create the updated element with the correct structure based on type
        const updatedElement = {
          element_id: numericId,
          element_type: currentElement.element_type,
          x_position: response.element.x_position,
          y_position: response.element.y_position,
          width: response.element.width,
          height: response.element.height,
          z_index: response.element.z_index,
          element_data: currentElement.element_type === 'text' 
            ? {
                content: response.element.content,
                font_family: response.element.font_family,
                font_size: response.element.font_size,
                font_color: response.element.font_color,
                bold: response.element.bold,
                italic: response.element.italic,
                underline: response.element.underline,
                text_align: response.element.text_align
              }
            : {
                image_url: response.element.image_url,
                alt_text: response.element.alt_text,
                natural_width: e.element_data?.natural_width,
                natural_height: e.element_data?.natural_height
              }
        }

        console.log('Updated element:', JSON.stringify(updatedElement, null, 2))
        return updatedElement
      }
      return e
    })

    // Force a reactive update by creating a new array
    elements.value = [...updatedElements]

    // Update selectedElement if it's the one being edited
    if (selectedElement.value?.element_id === numericId) {
      const newSelected = updatedElements.find(
        e => validateElementId(e.element_id) === numericId
      )
      console.log(
        'Setting new selected element:',
        JSON.stringify(newSelected, null, 2)
      )
      selectedElement.value = { ...newSelected }
    }

    // Force a re-render of the elements
    nextTick(() => {
      console.log(
        'Elements after nextTick:',
        JSON.stringify(elements.value, null, 2)
      )
    })

    return true
  } catch (err) {
    error.value = handleApiError(err)
    console.error('Error updating element:', err)
    return false
  }
}

// Update createTextElement to pass false for shouldRedirect
const createTextElement = async (x, y) => {
  try {
    // For new slides, create a temporary element first
    if (!isEditMode.value || slideId.value.toString().startsWith('temp-')) {
      const tempElementId = 'temp-' + Date.now()
      const xPos = Math.round(Number(x) || 0)
      const yPos = Math.round(Number(y) || 0)

      const defaultElementData = {
        content: 'New Text',
        font_family: 'Arial',
        font_size: 18,
        font_color: '#000000',
        bold: false,
        italic: false,
        underline: false,
        text_align: 'left'
      }

      // Create temporary element
      const tempElement = {
        element_id: tempElementId,
        element_type: 'text',
        x_position: xPos,
        y_position: yPos,
        width: 200,
        height: 100,
        z_index: elements.value.length || 0,
        element_data: defaultElementData
      }

      // Add to elements array
      elements.value.push(tempElement)
      selectedElement.value = tempElement

      // Start editing immediately
      nextTick(() => {
        isEditing.value = true
        editingContent.value = defaultElementData.content

        // Use a small delay to ensure the textarea is fully rendered
        setTimeout(() => {
          const textarea = document.querySelector('.text-element.editing textarea')
          if (textarea) {
            textarea.focus()
            textarea.setSelectionRange(0, textarea.value.length)
            textarea.style.opacity = '1'
            textarea.style.background = 'rgba(255,255,255,0.95)'
          }
        }, 50)
      })

      // Save the slide first if we haven't already
      if (!slideId.value || slideId.value.toString().startsWith('temp-')) {
        const saveResponse = await saveSlide(false)
        if (!saveResponse) {
          // If save fails, remove the temporary element
          elements.value = elements.value.filter(e => e.element_id !== tempElementId)
          selectedElement.value = null
          throw new Error('Failed to save slide before adding element')
        }
        // Update slideId with the new ID from the save response
        slideId.value = saveResponse.slide.slide_id

        // Now create the actual element
        const response = await presentationApi.createTextElement(slideId.value, {
          content: defaultElementData.content,
          x_position: xPos,
          y_position: yPos,
          width: 200,
          height: 100,
          z_index: elements.value.length || 0,
          font_family: defaultElementData.font_family,
          font_size: defaultElementData.font_size,
          font_color: defaultElementData.font_color,
          bold: defaultElementData.bold,
          italic: defaultElementData.italic,
          underline: defaultElementData.underline,
          text_align: defaultElementData.text_align
        })

        if (response.error) {
          throw new Error(response.error)
        }

        // Replace temporary element with real one
        const elementId = validateElementId(response.element.element_id)
        const newElement = {
          element_id: elementId,
          element_type: 'text',
          x_position: Math.round(Number(response.element.x_position ?? xPos)),
          y_position: Math.round(Number(response.element.y_position ?? yPos)),
          width: Math.round(Number(response.element.width ?? 200)),
          height: Math.round(Number(response.element.height ?? 100)),
          z_index: Math.round(Number(response.element.z_index ?? elements.value.length)),
          element_data: {
            content: defaultElementData.content,
            font_family: defaultElementData.font_family,
            font_size: Math.round(Number(defaultElementData.font_size)),
            font_color: defaultElementData.font_color,
            bold: defaultElementData.bold,
            italic: defaultElementData.italic,
            underline: defaultElementData.underline,
            text_align: defaultElementData.text_align
          }
        }

        // Replace the temporary element with the real one
        elements.value = elements.value.map(e => 
          e.element_id === tempElementId ? newElement : e
        )
        selectedElement.value = newElement
      }
    } else {
      // For existing slides, create element directly
      const xPos = Math.round(Number(x) || 0)
      const yPos = Math.round(Number(y) || 0)

      const defaultElementData = {
        content: 'New Text',
        font_family: 'Arial',
        font_size: 18,
        font_color: '#000000',
        bold: false,
        italic: false,
        underline: false,
        text_align: 'left'
      }

      const response = await presentationApi.createTextElement(slideId.value, {
        content: defaultElementData.content,
        x_position: xPos,
        y_position: yPos,
        width: 200,
        height: 100,
        z_index: elements.value.length || 0,
        font_family: defaultElementData.font_family,
        font_size: defaultElementData.font_size,
        font_color: defaultElementData.font_color,
        bold: defaultElementData.bold,
        italic: defaultElementData.italic,
        underline: defaultElementData.underline,
        text_align: defaultElementData.text_align
      })

      if (response.error) {
        throw new Error(response.error)
      }

      const elementId = validateElementId(response.element.element_id)
      const newElement = {
        element_id: elementId,
        element_type: 'text',
        x_position: Math.round(Number(response.element.x_position ?? xPos)),
        y_position: Math.round(Number(response.element.y_position ?? yPos)),
        width: Math.round(Number(response.element.width ?? 200)),
        height: Math.round(Number(response.element.height ?? 100)),
        z_index: Math.round(Number(response.element.z_index ?? elements.value.length)),
        element_data: {
          content: defaultElementData.content,
          font_family: defaultElementData.font_family,
          font_size: Math.round(Number(defaultElementData.font_size)),
          font_color: defaultElementData.font_color,
          bold: defaultElementData.bold,
          italic: defaultElementData.italic,
          underline: defaultElementData.underline,
          text_align: defaultElementData.text_align
        }
      }

      elements.value.push(newElement)
      selectedElement.value = newElement

      // Start editing
      nextTick(() => {
        isEditing.value = true
        editingContent.value = defaultElementData.content

        setTimeout(() => {
          const textarea = document.querySelector('.text-element.editing textarea')
          if (textarea) {
            textarea.focus()
            textarea.setSelectionRange(0, textarea.value.length)
            textarea.style.opacity = '1'
            textarea.style.background = 'rgba(255,255,255,0.95)'
          }
        }, 50)
      })
    }
  } catch (err) {
    error.value = handleApiError(err)
    console.error('Error creating text element:', err)
  }
}

// Update deleteElement to handle integer IDs
const deleteElement = async elementId => {
  try {
    const numericId = validateElementId(elementId)
    const response = await presentationApi.deleteElement(numericId)
    if (response.error) throw new Error(response.error)

    elements.value = elements.value.filter(
      e => validateElementId(e.element_id) !== numericId
    )
    if (selectedElement.value?.element_id === numericId) {
      selectedElement.value = null
      isEditing.value = false
    }
  } catch (err) {
    error.value = handleApiError(err)
    console.error('Error deleting element:', err)
  }
}

// Handle element selection
const selectElement = element => {
  selectedElement.value = element
}

const isEditing = ref(false)
const editingContent = ref('')
const textEditor = ref(null)

// Update the text editing functions to use a more reliable focus method
const startEditing = element => {
  selectedElement.value = element
  isEditing.value = true
  // Store the initial state
  currentEditState.value = {
    content: element.element_data?.content || '',
    element_id: element.element_id
  }
  // Set the editing content
  editingContent.value = element.element_data?.content || ''

  // Use nextTick to ensure the DOM is updated
  nextTick(() => {
    const textarea = document.querySelector('.text-element.editing textarea')
    if (textarea) {
      textarea.focus()
      // Place cursor at the end of the text
      const length = textarea.value.length
      textarea.setSelectionRange(length, length)
    }
  })
}

const finishEditing = async () => {
  if (!selectedElement.value) return

  try {
    // Don't update if content hasn't changed
    if (editingContent.value === selectedElement.value.element_data?.content) {
      isEditing.value = false
      return
    }

    // Only update if we have content
    if (editingContent.value.trim()) {
      const success = await updateElement(selectedElement.value.element_id, {
        content: editingContent.value
      })

      if (success) {
        // Update was successful, clear editing state
        isEditing.value = false
        editingContent.value = ''
      } else {
        // If update failed, revert to original content
        editingContent.value = selectedElement.value.element_data?.content || ''
      }
    } else {
      // If content is empty, revert to original content
      editingContent.value = selectedElement.value.element_data?.content || ''
      isEditing.value = false
    }
  } catch (err) {
    error.value = handleApiError(err)
    console.error('Error finishing edit:', err)
    // Revert to original content on error
    editingContent.value = selectedElement.value.element_data?.content || ''
  }
}

const handleKeyDown = event => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    finishEditing()
  } else if (event.key === 'Escape') {
    event.preventDefault()
    // Revert to original content
    if (currentEditState.value) {
      editingContent.value = currentEditState.value.content
    }
    isEditing.value = false
    currentEditState.value = null
  }
}

const handleClickAway = event => {
  // If click is outside both .text-element and .element-styling, deselect
  if (
    !event.target.closest('.text-element') &&
    !event.target.closest('.element-styling')
  ) {
    selectedElement.value = null
    isEditing.value = false
  }
}

const handleSlideClick = event => {
  if (!isAddingText.value) return // Only create text if we're in add text mode
  if (event.target.closest('.element')) return // Don't create if clicking on existing element

  // Get the slide container element
  const slideContainer = event.currentTarget
  if (!slideContainer) {
    console.error('Slide container not found')
    return
  }

  // Validate scale value
  if (!scale.value || isNaN(scale.value) || scale.value <= 0) {
    console.error('Invalid scale value:', scale.value)
    // Force a scale recalculation
    calculateScale()
    // If still invalid, use a fallback scale
    if (!scale.value || isNaN(scale.value) || scale.value <= 0) {
      scale.value = 1
    }
  }

  // Get the container's position relative to the viewport
  const rect = slideContainer.getBoundingClientRect()

  // Calculate the click position relative to the container
  const clickX = event.clientX - rect.left
  const clickY = event.clientY - rect.top

  // Calculate the scaled position
  // The container is centered, so we need to account for the transform
  const containerCenterX = rect.width / 2
  const containerCenterY = rect.height / 2

  // Calculate the position relative to the center
  const relativeX = clickX - containerCenterX
  const relativeY = clickY - containerCenterY

  // Apply the inverse of the scale to get the actual position
  const currentScale = scale.value || 1 // Fallback to 1 if scale is invalid
  const scaledX = relativeX / currentScale
  const scaledY = relativeY / currentScale

  // Add the center offset back to get the final position
  const finalX = scaledX + DESIGN_WIDTH / 2
  const finalY = scaledY + DESIGN_HEIGHT / 2

  // Validate the final coordinates
  if (isNaN(finalX) || isNaN(finalY)) {
    console.error('Invalid coordinates after calculation:', {
      clickX,
      clickY,
      relativeX,
      relativeY,
      scaledX,
      scaledY,
      finalX,
      finalY,
      scale: currentScale,
      rect,
      DESIGN_WIDTH,
      DESIGN_HEIGHT
    })
    return
  }

  // Ensure coordinates are within bounds
  const boundedX = Math.max(0, Math.min(finalX, DESIGN_WIDTH))
  const boundedY = Math.max(0, Math.min(finalY, DESIGN_HEIGHT))

  console.log('Creating text element at position:', {
    click: { x: clickX, y: clickY },
    relative: { x: relativeX, y: relativeY },
    scaled: { x: scaledX, y: scaledY },
    final: { x: finalX, y: finalY },
    bounded: { x: boundedX, y: boundedY },
    scale: currentScale,
    design: { width: DESIGN_WIDTH, height: DESIGN_HEIGHT }
  })

  createTextElement(boundedX, boundedY)
  isAddingText.value = false // Reset the mode after creating

  // Reset cursor
  if (slideContainer) {
    slideContainer.style.cursor = 'default'
  }
}

// Add function to toggle action bar
const toggleActionBar = () => {
  isActionBarExpanded.value = !isActionBarExpanded.value
  // Update available height after toggle
  nextTick(() => {
    updateAvailableHeight()
  })
}

// Modify updateAvailableHeight to account for action bar state
function updateAvailableHeight() {
  nextTick(() => {
    const headerH = headerRef.value?.getBoundingClientRect().height || 0
    const controlsH = isActionBarExpanded.value ? 
      (headerRef.value?.querySelector('.action-bar-content')?.getBoundingClientRect().height || 0) : 
      (headerRef.value?.querySelector('.action-bar-toggle')?.getBoundingClientRect().height || 0)
    const actionsH = actionButtonsRef.value?.getBoundingClientRect().height || 0
    const margin = 16
    const newHeight = window.innerHeight - (headerH + controlsH + actionsH + margin)

    if (newHeight > 0) {
      availableHeight.value = newHeight
      calculateScale()
    } else {
      console.warn('Invalid height calculated:', newHeight)
      availableHeight.value = 600
      calculateScale()
    }
    updateAvailableWidth()
  })
}

// Move cleanup functions outside of onMounted
const cleanup = () => {
  document.removeEventListener('mousedown', handleClickAway)
  document.removeEventListener('mousedown', handleClickOutside)
  window.removeEventListener('resize', updateAvailableHeight)
  if (actionBarObserver.value) {
    actionBarObserver.value.disconnect()
  }
}

// Add ref for the observer
const actionBarObserver = ref(null)

onMounted(() => {
  // Set up initial state
  box.value = document.querySelector('.slide-container')
  pageX.value = document.getElementById('x')
  pageY.value = document.getElementById('y')

  if (box.value) {
    const updateDisplay = event => {
      if (pageX.value && pageY.value) {
        pageX.value.innerText = event.pageX
        pageY.value.innerText = event.pageY
      }
    }

    box.value.addEventListener('mousemove', updateDisplay)
    box.value.addEventListener('mouseenter', updateDisplay)
    box.value.addEventListener('mouseleave', updateDisplay)
  }

  document.addEventListener('mousedown', handleClickAway)
  document.addEventListener('mousedown', handleClickOutside)

  // Initial height calculation
  updateAvailableHeight()

  // Add resize listener
  window.addEventListener('resize', updateAvailableHeight)

  // Add resize observer for action bar
  actionBarObserver.value = new ResizeObserver(() => {
    updateAvailableHeight()
  })
  
  if (headerRef.value) {
    actionBarObserver.value.observe(headerRef.value)
  }

  // Remove optimistic set for new slides
  loadSlideData()
  if (isEditMode.value) {
    loadSlideElements()
  }

  // Add resize listener for isMobile
  window.addEventListener('resize', handleResize)
})

// Register cleanup
onUnmounted(cleanup)

// Add a watch to ensure scale is always valid
watch(
  scale,
  newScale => {
    if (!newScale || isNaN(newScale) || newScale <= 0) {
      console.warn('Invalid scale detected, recalculating...')
      calculateScale()
    }
  },
  { immediate: true }
)

// Add a new function to handle double clicks
const handleDoubleClick = (element, event) => {
  if (element.element_type === 'text') {
    event.stopPropagation() // Prevent slide click handler from firing
    startEditing(element)
  }
}

// Add handlers for background image modal
const handleBackgroundImageUpdate = (settings) => {
  // Only update temporary values
  tempBackgroundImage.value = settings.image_url
  tempBackgroundImageOpacity.value = settings.opacity
  tempBackgroundImageFit.value = settings.fit
}

const handleBackgroundImageRemove = () => {
  // Only update temporary values
  tempBackgroundImage.value = null
  tempBackgroundImageOpacity.value = 1
  tempBackgroundImageFit.value = 'cover'
}

// Add function to toggle styling controls
const toggleStyling = () => {
  isStylingExpanded.value = !isStylingExpanded.value
}
</script>

<template>
  <div class="page-content-wrapper">
    <div class="page-header">
      <div class="page-header-text">
        {{ isEditMode ? 'Edit Slide' : 'Create Slide' }}
      </div>
    </div>

    <div class="page-actions" ref="headerRef">
      <div class="slide-controls-container">
        <button
          @click="addText"
          :class="{ active: isAddingText }"
          title="Click to add text, then click on the slide where you want the text to appear"
        >
          Add Text
        </button>
        <button @click="addImage">Add Image</button>
        <button
          @click.stop="deleteSlide($event)"
          class="btn btn-danger delete-slide-button"
        >
          {{ !slideSureness ? 'Delete Slide' : 'Click again to delete' }}
        </button>
      </div>
      <div class="slide-background-edit-actions">
        <div class="color-picker">
          <label for="backgroundColor">Background Color:</label>
          <input
            type="color"
            id="backgroundColor"
            v-model="backgroundColor"
            title="Choose slide background color"
          />
        </div>
        <button @click="showBackgroundImageModal = true">Set Background Image</button>
      </div>
      <div class="slide-title-container">
        <label for="slideTitle">Slide Title:</label>
        <input type="text" v-model="slideTitle" placeholder="Slide Title" />
      </div>
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>

    <div class="slide-editor-content">
      <div v-if="isLoading" class="loading-container">
        <div class="loading-spinner"></div>
        <div class="loading-text">Loading slide...</div>
      </div>
      <div
        v-else
        class="slide-scale-wrapper"
        :style="{
          width: '100%',
          height: availableHeight + 'px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'visible'
        }"
      >
        <div
          class="slide-container"
          :style="{
            backgroundColor: backgroundColor,
            width: isMobile ? '100vw' : DESIGN_WIDTH + 'px',
            maxWidth: '100vw',
            height: DESIGN_HEIGHT + 'px',
            transform: `scale(${scale})`,
            transformOrigin: 'center center',
            position: 'relative'
          }"
          @click="handleSlideClick"
        >
          <!-- Add background image layer -->
          <div
            v-if="tempBackgroundImage"
            class="background-image-layer"
            :style="{
              backgroundImage: `url(${tempBackgroundImage})`,
              backgroundSize: tempBackgroundImageFit === 'stretch' ? '100% 100%' : tempBackgroundImageFit,
              backgroundPosition: 'center',
              backgroundRepeat: 'no-repeat',
              opacity: tempBackgroundImageOpacity,
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              zIndex: 0
            }"
          ></div>

          <!-- Text Elements -->
          <div
            v-for="element in elements"
            :key="`element-${element.element_id}-${
              element.element_data?.image_url || element.element_data?.content
            }`"
            class="element"
            :class="{
              selected: selectedElement?.element_id === element.element_id,
              'text-element': element.element_type === 'text',
              'image-element': element.element_type === 'image',
              editing:
                selectedElement?.element_id === element.element_id &&
                isEditing &&
                element.element_type === 'text'
            }"
            :style="{
              position: 'absolute',
              left: `${element.x_position}px`,
              top: `${element.y_position}px`,
              width: `${element.width}px`,
              height: `${element.height}px`,
              zIndex: element.z_index + 1, // Ensure elements are above background
              ...(element.element_type === 'text'
                ? {
                    fontFamily: element.element_data?.font_family || 'Arial',
                    fontSize: `${element.element_data?.font_size || 18}px`,
                    color: element.element_data?.font_color || '#000000',
                    fontWeight: element.element_data?.bold ? 'bold' : 'normal',
                    fontStyle: element.element_data?.italic
                      ? 'italic'
                      : 'normal',
                    textDecoration: element.element_data?.underline
                      ? 'underline'
                      : 'none',
                    textAlign: element.element_data?.text_align || 'left',
                    background: 'rgba(255,255,255,0.1)',
                    border: '2px solid rgba(0,0,0,0.5)',
                    boxSizing: 'border-box',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: 0,
                    cursor: element.element_type === 'text' ? 'text' : 'move'
                  }
                : {
                    background: 'transparent',
                    border: '2px solid rgba(0,0,0,0.5)',
                    boxSizing: 'border-box',
                    overflow: 'visible'
                  })
            }"
            @click.stop="selectElement(element)"
            @dblclick="handleDoubleClick(element, $event)"
          >
            <div
              v-if="selectedElement?.element_id === element.element_id"
              class="element-controls"
            >
              <button
                @click.stop="deleteElement(element.element_id)"
                class="delete-btn"
              >
                ×
              </button>
            </div>

            <!-- Text element content -->
            <div
              v-if="element.element_type === 'text'"
              class="text-editor"
              :class="{
                editing:
                  selectedElement?.element_id === element.element_id &&
                  isEditing,
                'new-element':
                  !element.element_data?.content ||
                  element.element_data?.content === 'New Text'
              }"
            >
              <textarea
                v-if="
                  selectedElement?.element_id === element.element_id &&
                  isEditing
                "
                v-model="editingContent"
                @blur="finishEditing"
                @keydown="handleKeyDown"
                :style="{
                  fontFamily: element.element_data?.font_family || 'Arial',
                  fontSize: `${element.element_data?.font_size || 18}px`,
                  color: element.element_data?.font_color || '#000000',
                  fontWeight: element.element_data?.bold ? 'bold' : 'normal',
                  fontStyle: element.element_data?.italic ? 'italic' : 'normal',
                  textDecoration: element.element_data?.underline
                    ? 'underline'
                    : 'none',
                  textAlign: element.element_data?.text_align || 'left',
                  width: `${selectedElement?.width || 200}px`,
                  height: `${selectedElement?.height || 100}px`,
                  border: '2px solid #28a745',
                  background: 'rgba(255,255,255,0.95)',
                  resize: 'none',
                  outline: 'none',
                  padding: '5px',
                  boxShadow: 'none',
                  boxSizing: 'border-box',
                  overflow: 'visible',
                  whiteSpace: 'pre-wrap',
                  wordWrap: 'break-word',
                  display: 'block',
                  opacity: '1',
                  transition: 'opacity 0.1s ease-in-out',
                  cursor: 'text'
                }"
              ></textarea>
              <div
                v-else
                v-html="marked(element.element_data?.content || '')"
                style="
                  width: 100%;
                  height: 100%;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 5px;
                  box-sizing: border-box;
                  background: rgba(255, 255, 255, 0.1);
                  cursor: text;
                "
              ></div>
            </div>

            <!-- Image element content -->
            <div
              v-else-if="element.element_type === 'image'"
              class="image-container"
              style="
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: visible;
              "
            >
              <img
                :src="element.element_data?.image_url"
                :alt="element.element_data?.alt_text || ''"
                style="max-width: 100%; max-height: 100%; object-fit: contain"
              />
            </div>
          </div>
        </div>
        <div class="action-buttons centered-under-slide" :key="actionButtonsKey">
          <div class="slide-number-input">
            <label for="slideNumber">Slide Number:</label>
            <div class="slide-number-wrapper">
              <template v-if="!isLoading && newSlideNumber !== null">
                <input
                  id="slideNumber"
                  type="number"
                  v-model.number="newSlideNumber"
                  :min="1"
                  :max="isEditMode ? totalSlides : totalSlides + 1"
                  step="1"
                />
                <span class="slide-number-total">of {{ isEditMode ? totalSlides : totalSlides + 1 }}</span>
              </template>
              <template v-else>
                <div style="width: 100px; height: 44px; background: #eee; border-radius: 8px; display: inline-block; animation: pulse 1.2s infinite; margin-right: 8px;"></div>
                <span class="slide-number-total">of ...</span>
              </template>
            </div>
          </div>
          <button
            @click="router.push(`/presentations/${presentationId}`)"
            class="cancel-button"
          >
            Cancel
          </button>
          <button
       
            @click="saveSlide(false)"
            :disabled="isSubmitting"
            class="save-button"
          >
            {{
              isSubmitting
                ? 'Saving...'
                : isEditMode
                ? 'Save Changes'
                : 'Create Slide'
            }}
          </button>
          <button
            @click="saveSlide(true)"
            :disabled="isSubmitting"
            class="save-and-return-button"
          >
            {{ isSubmitting ? 'Saving...' : 'Save & Return' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Element Styling Controls -->
    <div 
      v-if="selectedElement" 
      class="element-styling"
      :class="{ 'is-expanded': isStylingExpanded }"
    >
      <button 
        class="styling-toggle"
        @click="toggleStyling"
        :class="{ 'is-active': isStylingExpanded }"
        aria-label="Toggle styling controls"
      >
        <span>Style</span>
        <span class="toggle-icon"></span>
      </button>
      <div class="styling-controls">
        <div v-if="selectedElement.element_type === 'text'" class="control-group">
          <label for="font-family">Font:</label>
          <select
            id="font-family"
            v-model="selectedElement.element_data.font_family"
            @change="
              updateElement(selectedElement.element_id, {
                font_family: selectedElement.element_data.font_family
              })
            "
          >
            <option value="Arial">Arial</option>
            <option value="Times New Roman">Times New Roman</option>
            <option value="Courier New">Courier New</option>
          </select>
        </div>
        <div v-if="selectedElement.element_type === 'text'" class="control-group">
          <label for="font-size">Size:</label>
          <input
            id="font-size"
            type="number"
            v-model.number="integerFontSize"
            @change="
              updateElement(selectedElement.element_id, {
                font_size: integerFontSize
              })
            "
            min="8"
            max="72"
            step="1"
          />
        </div>
        <div v-if="selectedElement.element_type === 'text'" class="control-group">
          <label for="font-color">Color:</label>
          <input
            id="font-color"
            type="color"
            v-model="selectedElement.element_data.font_color"
            @change="
              updateElement(selectedElement.element_id, {
                font_color: selectedElement.element_data.font_color
              })
            "
          />
        </div>
        <!-- <div class="control-group">
          <label for="text-align">Align:</label>
          <select
            id="text-align"
            v-model="selectedElement.element_data.text_align"
            @change="
              updateElement(selectedElement.element_id, {
                text_align: selectedElement.element_data.text_align
              })
            "
          >
            <option value="left">Left</option>
            <option value="center">Center</option>
            <option value="right">Right</option>
          </select>
        </div> -->
        <div class="control-group">
          <label for="x-position">X:</label>
          <input
            id="x-position"
            type="number"
            v-model.number="integerX"
            @change="
              updateElement(selectedElement.element_id, {
                x_position: integerX
              })
            "
            min="0"
            step="1"
            placeholder="X"
          />
        </div>
        <div class="control-group">
          <label for="y-position">Y:</label>
          <input
            id="y-position"
            type="number"
            v-model.number="integerY"
            @change="
              updateElement(selectedElement.element_id, {
                y_position: integerY
              })
            "
            min="0"
            step="1"
            placeholder="Y"
          />
        </div>
        <div class="control-group">
          <label for="width">Width:</label>
          <input
            id="width"
            type="number"
            v-model.number="integerWidth"
            @change="updateElementDimensions(integerWidth, undefined)"
            min="10"
            step="1"
            placeholder="Width"
          />
        </div>
        <div class="control-group">
          <label for="height">Height:</label>
          <input
            id="height"
            type="number"
            v-model.number="integerHeight"
            @change="updateElementDimensions(undefined, integerHeight)"
            min="10"
            step="1"
            placeholder="Height"
          />
        </div>
        <div class="control-group">
          <label for="z-index">Z:</label>
          <input
            id="z-index"
            type="number"
            v-model.number="integerZIndex"
            @change="
              updateElement(selectedElement.element_id, {
                z_index: integerZIndex
              })
            "
            min="0"
            step="1"
            placeholder="Z"
          />
        </div>
      </div>
    </div>

    <!-- Add the background image modal -->
    <BackgroundImageModal
      :show="showBackgroundImageModal"
      :current-image="backgroundImage"
      :current-opacity="backgroundImageOpacity"
      :current-fit="backgroundImageFit"
      @close="showBackgroundImageModal = false"
      @update="handleBackgroundImageUpdate"
      @remove="handleBackgroundImageRemove"
    />
  </div>
</template>

