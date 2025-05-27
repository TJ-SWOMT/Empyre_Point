<script setup>
import { ref, onMounted, watch, computed, nextTick, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'
import { marked } from 'marked'
import { useSlideScale } from '../composables/useSlideScale'

const route = useRoute()
const router = useRouter()
const presentationId = route.params.id
const slideId = ref(route.params.slide_id)
const error = ref('')
const isSubmitting = ref(false)
const isEditMode = computed(() => !!slideId.value)

const headerRef = ref(null)
const controlsRef = ref(null)
const actionButtonsRef = ref(null)
const availableHeight = ref(600) // fallback default

const { scale, DESIGN_WIDTH, DESIGN_HEIGHT, calculateScale } = useSlideScale(availableHeight)

// Initialize background color from session storage, but use presentation-specific key
const getStoredBackgroundColor = () => {
    const storedColor = sessionStorage.getItem(`slideBackgroundColor_${presentationId}`)
    return storedColor || '#FFFFFF'
}

const backgroundColor = ref(getStoredBackgroundColor())
const slideData = ref(null)

// Watch for changes to backgroundColor and save to session storage with presentation-specific key
watch(backgroundColor, (newColor) => {
    sessionStorage.setItem(`slideBackgroundColor_${presentationId}`, newColor)
})

const texts = ref([])

const elements = ref([])
const selectedElement = ref(null)

const isAddingText = ref(false)

// Add computed properties for integer display
const integerFontSize = computed({
    get: () => Math.round(selectedElement.value?.element_data?.font_size || 0),
    set: (value) => {
        if (selectedElement.value) {
            selectedElement.value.element_data.font_size = Math.round(value)
        }
    }
})

const integerX = computed({
    get: () => Math.round(selectedElement.value?.x_position || 0),
    set: (value) => {
        if (selectedElement.value) {
            selectedElement.value.x_position = Math.round(value)
        }
    }
})

const integerY = computed({
    get: () => Math.round(selectedElement.value?.y_position || 0),
    set: (value) => {
        if (selectedElement.value) {
            selectedElement.value.y_position = Math.round(value)
        }
    }
})

const integerWidth = computed({
    get: () => Math.round(selectedElement.value?.width || 0),
    set: (value) => {
        if (selectedElement.value) {
            selectedElement.value.width = Math.round(value)
        }
    }
})

const integerHeight = computed({
    get: () => Math.round(selectedElement.value?.height || 0),
    set: (value) => {
        if (selectedElement.value) {
            selectedElement.value.height = Math.round(value)
        }
    }
})

const integerZIndex = computed({
    get: () => Math.round(selectedElement.value?.z_index || 0),
    set: (value) => {
        if (selectedElement.value) {
            selectedElement.value.z_index = Math.round(value)
        }
    }
})

const loadSlideData = async () => {
    if (!isEditMode.value) return

    try {
        const response = await presentationApi.getPresentation(presentationId)
        if (response.error) throw new Error(response.error)
        
        // Convert slideId to number for comparison since it comes from route params
        const slide = response.presentation.slides.find(s => Number(s.slide_id) === Number(slideId.value))
        if (slide) {
            slideData.value = {
                ...slide,
                slide_id: Number(slide.slide_id) // Ensure consistent type
            }
            backgroundColor.value = slide.background_color || '#FFFFFF'
        } else {
            throw new Error('Slide not found')
        }
    } catch (err) {
        error.value = handleApiError(err)
    }
}

const loadSlideElements = async () => {
    if (!isEditMode.value) return

    try {
        const response = await presentationApi.getSlideElements(slideId.value)
        if (response.error) throw new Error(response.error)
        elements.value = response.elements || []
    } catch (err) {
        error.value = handleApiError(err)
    }
}

const saveSlide = async () => {
    try {
        isSubmitting.value = true
        error.value = ''
        
        let response
        if (isEditMode.value) {
            if (!slideData.value) {
                throw new Error('Slide data not loaded')
            }
            // Update existing slide
            response = await presentationApi.updateSlide(
                Number(slideId.value), // Ensure slideId is a number
                slideData.value.slide_number,
                backgroundColor.value,
                slideData.value.background_image_url
            )
        } else {
            // Create new slide
            response = await presentationApi.createSlide(
                presentationId,
                1,  // The backend will handle the slide number
                backgroundColor.value
            )
        }
        
        if (response.error) {
            throw new Error(response.error)
        }

        // Save all element positions, sizes, and styles
        const updatePromises = elements.value.map(element => {
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
        })
        await Promise.all(updatePromises)
        
        // For new slides, update the URL with the new slide ID
        if (!isEditMode.value && response.slide) {
            router.replace(`/presentations/${presentationId}/slides/${response.slide.slide_id}`)
        } else {
            // Redirect back to the presentation view
            router.push(`/presentations/${presentationId}`)
        }

        return response
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

const deleteText = (id) => {
    texts.value = texts.value.filter(text => text.id !== id)
}

const addImage = async () => {
    try {
        // Create a file input element
        const input = document.createElement('input')
        input.type = 'file'
        input.accept = 'image/*'
        
        // Handle file selection
        input.onchange = async (event) => {
            const file = event.target.files[0]
            if (!file) return
            
            // Create a temporary image to get dimensions
            const img = new Image()
            const imgUrl = URL.createObjectURL(file)
            
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
                error.value = uploadResponse.error
                URL.revokeObjectURL(imgUrl)
                return
            }
            
            // For new slides, we need to save the slide first
            if (!isEditMode.value) {
                const response = await saveSlide()
                if (!response) {
                    throw new Error('Failed to create slide')
                }
                // Update the slideId from the response
                slideId.value = response.slide.slide_id
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
            
            const response = await presentationApi.createImageElement(slideId.value, elementData)
            if (response.error) {
                error.value = response.error
                URL.revokeObjectURL(imgUrl)
                return
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
            
            // Clean up
            URL.revokeObjectURL(imgUrl)
            
            // Select the new element
            selectedElement.value = elements.value[elements.value.length - 1]
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
    if (!selectedElement.value || selectedElement.value.element_type !== 'image') return null
    const { natural_width, natural_height } = selectedElement.value.element_data
    return natural_width / natural_height
})

// Modify the width/height update handlers to maintain aspect ratio
const updateElementDimensions = async (width, height) => {
    if (!selectedElement.value || selectedElement.value.element_type !== 'image') return
    
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
const validateElementId = (id) => {
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
        
        // Ensure numeric values are integers
        const integerUpdates = Object.entries(updates).reduce((acc, [key, value]) => {
            // Convert numeric values to integers
            if (typeof value === 'number') {
                acc[key] = Math.round(value)
            } else {
                acc[key] = value
            }
            return acc
        }, {})
        
        const response = await presentationApi.updateElement(numericId, {
            element_type: 'text',
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
                // Extract element_data properties from the server response
                const elementData = {
                    content: response.element.content,
                    font_family: response.element.font_family,
                    font_size: response.element.font_size,
                    font_color: response.element.font_color,
                    bold: response.element.bold,
                    italic: response.element.italic,
                    underline: response.element.underline,
                    text_align: response.element.text_align
                }

                // Create the updated element with the correct structure
                const updatedElement = {
                    element_id: numericId,
                    element_type: 'text',
                    x_position: response.element.x_position,
                    y_position: response.element.y_position,
                    width: response.element.width,
                    height: response.element.height,
                    z_index: response.element.z_index,
                    element_data: elementData
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
            const newSelected = updatedElements.find(e => validateElementId(e.element_id) === numericId)
            console.log('Setting new selected element:', JSON.stringify(newSelected, null, 2))
            selectedElement.value = { ...newSelected }
        }

        // Force a re-render of the elements
        nextTick(() => {
            console.log('Elements after nextTick:', JSON.stringify(elements.value, null, 2))
        })

        return true
    } catch (err) {
        error.value = handleApiError(err)
        console.error('Error updating element:', err)
        return false
    }
}

// Update createTextElement to handle integer IDs
const createTextElement = async (x, y) => {
    try {
        // For new slides, we need to save the slide first
        if (!isEditMode.value) {
            const response = await saveSlide()
            if (!response) {
                throw new Error('Failed to create slide')
            }
            // Update the slideId from the response
            slideId.value = response.slide.slide_id
        }

        // Ensure x and y are integers and not null
        const xPos = Math.round(Number(x) || 0)
        const yPos = Math.round(Number(y) || 0)

        // Log the initial values
        console.log('Creating text element with position:', { x: xPos, y: yPos })

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

        // Prepare the element data with explicit numeric values
        const elementData = {
            content: defaultElementData.content,
            x_position: xPos,
            y_position: yPos,
            width: 200,
            height: 100,
            font_family: defaultElementData.font_family,
            font_size: defaultElementData.font_size,
            font_color: defaultElementData.font_color,
            bold: defaultElementData.bold,
            italic: defaultElementData.italic,
            underline: defaultElementData.underline,
            text_align: defaultElementData.text_align,
            z_index: elements.value.length || 0
        }

        // Log the data being sent to the API
        console.log('Sending element data to API:', elementData)

        const response = await presentationApi.createTextElement(slideId.value, elementData)

        if (response.error) {
            console.error('API returned error:', response.error)
            throw new Error(response.error)
        }

        if (!response.element) {
            console.error('API response missing element data:', response)
            throw new Error('Invalid API response: missing element data')
        }
        
        // Log the API response
        console.log('API response:', response)

        // Ensure the element has a numeric ID and all numeric values are integers
        const elementId = validateElementId(response.element.element_id)
        
        // Create a new element with explicit numeric values and null checks
        const newElement = {
            element_id: elementId,
            element_type: 'text',
            x_position: Math.round(Number(response.element.x_position ?? xPos)),
            y_position: Math.round(Number(response.element.y_position ?? yPos)),
            width: Math.round(Number(response.element.width ?? 200)),
            height: Math.round(Number(response.element.height ?? 100)),
            z_index: Math.round(Number(response.element.z_index ?? elements.value.length)),
            element_data: {
                content: response.element.element_data?.content ?? defaultElementData.content,
                font_family: response.element.element_data?.font_family ?? defaultElementData.font_family,
                font_size: Math.round(Number(response.element.element_data?.font_size ?? defaultElementData.font_size)),
                font_color: response.element.element_data?.font_color ?? defaultElementData.font_color,
                bold: response.element.element_data?.bold ?? defaultElementData.bold,
                italic: response.element.element_data?.italic ?? defaultElementData.italic,
                underline: response.element.element_data?.underline ?? defaultElementData.underline,
                text_align: response.element.element_data?.text_align ?? defaultElementData.text_align
            }
        }
        
        // Log the final element object
        console.log('Created new element:', newElement)

        // Validate all numeric fields before adding to elements array
        const requiredNumericFields = ['x_position', 'y_position', 'width', 'height', 'z_index', 'element_data.font_size']
        for (const field of requiredNumericFields) {
            const value = field.includes('.') 
                ? newElement.element_data[field.split('.')[1]]
                : newElement[field]
            if (typeof value !== 'number' || isNaN(value)) {
                console.error(`Invalid numeric value for ${field}:`, value)
                throw new Error(`Invalid numeric value for ${field}`)
            }
        }

        elements.value.push(newElement)
        selectedElement.value = newElement
        
        // Use requestAnimationFrame for more reliable timing
        requestAnimationFrame(() => {
            startEditing(newElement)
        })
    } catch (err) {
        error.value = handleApiError(err)
        console.error('Error creating text element:', err)
        // Log the full error stack for debugging
        console.error('Error stack:', err.stack)
    }
}

// Update deleteElement to handle integer IDs
const deleteElement = async (elementId) => {
    try {
        const numericId = validateElementId(elementId)
        const response = await presentationApi.deleteElement(numericId)
        if (response.error) throw new Error(response.error)
        
        elements.value = elements.value.filter(e => validateElementId(e.element_id) !== numericId)
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
const selectElement = (element) => {
    selectedElement.value = element
}

const isEditing = ref(false)
const editingContent = ref('')
const textEditor = ref(null)

// Update the text editing functions to use a more reliable focus method
const startEditing = (element) => {
    selectedElement.value = element
    isEditing.value = true
    // Store the initial state
    currentEditState.value = {
        content: element.element_data?.content || '',
        element_id: element.element_id
    }
    editingContent.value = currentEditState.value.content
    
    // Use requestAnimationFrame to ensure the DOM is updated
    requestAnimationFrame(() => {
        const textarea = document.querySelector('.text-element.editing textarea')
        if (textarea) {
            textarea.focus()
            // Move cursor to end of text
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

const handleKeyDown = (event) => {
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

const handleClickAway = (event) => {
    // If click is outside both .text-element and .element-styling, deselect
    if (
        !event.target.closest('.text-element') &&
        !event.target.closest('.element-styling')
    ) {
        selectedElement.value = null;
        isEditing.value = false;
    }
}

const handleSlideClick = (event) => {
    if (!isAddingText.value) return; // Only create text if we're in add text mode
    if (event.target.closest('.element')) return; // Don't create if clicking on existing element

    // Get the slide container element
    const slideContainer = event.currentTarget;
    if (!slideContainer) {
        console.error('Slide container not found')
        return;
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
    const rect = slideContainer.getBoundingClientRect();
    
    // Calculate the click position relative to the container
    const clickX = event.clientX - rect.left;
    const clickY = event.clientY - rect.top;

    // Calculate the scaled position
    // The container is centered, so we need to account for the transform
    const containerCenterX = rect.width / 2;
    const containerCenterY = rect.height / 2;
    
    // Calculate the position relative to the center
    const relativeX = clickX - containerCenterX;
    const relativeY = clickY - containerCenterY;
    
    // Apply the inverse of the scale to get the actual position
    const currentScale = scale.value || 1; // Fallback to 1 if scale is invalid
    const scaledX = relativeX / currentScale;
    const scaledY = relativeY / currentScale;
    
    // Add the center offset back to get the final position
    const finalX = scaledX + (DESIGN_WIDTH / 2);
    const finalY = scaledY + (DESIGN_HEIGHT / 2);

    // Validate the final coordinates
    if (isNaN(finalX) || isNaN(finalY)) {
        console.error('Invalid coordinates after calculation:', { 
            clickX, clickY, 
            relativeX, relativeY, 
            scaledX, scaledY, 
            finalX, finalY,
            scale: currentScale,
            rect,
            DESIGN_WIDTH,
            DESIGN_HEIGHT
        });
        return;
    }

    // Ensure coordinates are within bounds
    const boundedX = Math.max(0, Math.min(finalX, DESIGN_WIDTH));
    const boundedY = Math.max(0, Math.min(finalY, DESIGN_HEIGHT));

    console.log('Creating text element at position:', {
        click: { x: clickX, y: clickY },
        relative: { x: relativeX, y: relativeY },
        scaled: { x: scaledX, y: scaledY },
        final: { x: finalX, y: finalY },
        bounded: { x: boundedX, y: boundedY },
        scale: currentScale,
        design: { width: DESIGN_WIDTH, height: DESIGN_HEIGHT }
    });

    createTextElement(boundedX, boundedY);
    isAddingText.value = false; // Reset the mode after creating

    // Reset cursor
    if (slideContainer) {
        slideContainer.style.cursor = 'default';
    }
};

function updateAvailableHeight() {
    nextTick(() => {
        const headerH = headerRef.value?.getBoundingClientRect().height || 0
        const controlsH = controlsRef.value?.getBoundingClientRect().height || 0
        const actionsH = actionButtonsRef.value?.getBoundingClientRect().height || 0
        const margin = 40
        availableHeight.value = window.innerHeight - (headerH + controlsH + actionsH + margin)
        calculateScale()
    })
}

onMounted(async () => {
    if (isEditMode.value) {
        await loadSlideData()
        await loadSlideElements()
    }

    box.value = document.querySelector(".slide-container")
    pageX.value = document.getElementById("x")
    pageY.value = document.getElementById("y")

    if (box.value) {
        const updateDisplay = (event) => {
            if (pageX.value && pageY.value) {
                pageX.value.innerText = event.pageX
                pageY.value.innerText = event.pageY
            }
        }

        box.value.addEventListener("mousemove", updateDisplay)
        box.value.addEventListener("mouseenter", updateDisplay)
        box.value.addEventListener("mouseleave", updateDisplay)
    }

    document.addEventListener('mousedown', handleClickAway);
    updateAvailableHeight()
    window.addEventListener('resize', updateAvailableHeight)
})

onUnmounted(() => {
    document.removeEventListener('mousedown', handleClickAway);
    window.removeEventListener('resize', updateAvailableHeight)
})

// Add a watch to ensure scale is always valid
watch(scale, (newScale) => {
    if (!newScale || isNaN(newScale) || newScale <= 0) {
        console.warn('Invalid scale detected, recalculating...')
        calculateScale()
    }
}, { immediate: true })
</script>

<template>
    <div class="editor-root">
        <div class="header-container" ref="headerRef">
            <h1>{{ isEditMode ? 'Edit Slide' : 'Create Slide' }}</h1>
            <div class="controls" ref="controlsRef">
                <div class="color-picker">
                    <label for="backgroundColor">Background Color:</label>
                    <input 
                        type="color" 
                        id="backgroundColor" 
                        v-model="backgroundColor"
                        title="Choose slide background color"
                    />
                </div>
                <button 
                    @click="addText" 
                    :class="{ active: isAddingText }"
                    title="Click to add text, then click on the slide where you want the text to appear"
                >
                    Add Text
                </button>
                <button @click="addImage">Add Image</button>
            </div>
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>

        <div class="center-flex">
            <div class="slide-scale-wrapper" :style="{ height: availableHeight + 'px' }">
                <div 
                    class="slide-container" 
                    :style="{ 
                        backgroundColor: backgroundColor, 
                        width: DESIGN_WIDTH + 'px', 
                        height: DESIGN_HEIGHT + 'px', 
                        position: 'absolute',
                        left: '50%',
                        top: '50%',
                        transform: `translate(-50%, -50%) scale(${scale})`,
                        transformOrigin: 'top left'
                    }"
                    @click="handleSlideClick"
                >
                    <!-- Text Elements -->
                    <div 
                        v-for="element in elements" 
                        :key="`element-${element.element_id}-${element.element_data?.image_url || element.element_data?.content}`"
                        class="element"
                        :class="{ 
                            'selected': selectedElement?.element_id === element.element_id,
                            'text-element': element.element_type === 'text',
                            'image-element': element.element_type === 'image',
                            'editing': selectedElement?.element_id === element.element_id && isEditing && element.element_type === 'text'
                        }"
                        :style="{
                            position: 'absolute',
                            left: `${element.x_position}px`,
                            top: `${element.y_position}px`,
                            width: `${element.width}px`,
                            height: `${element.height}px`,
                            zIndex: element.z_index,
                            ...(element.element_type === 'text' ? {
                                fontFamily: element.element_data?.font_family || 'Arial',
                                fontSize: `${element.element_data?.font_size || 18}px`,
                                color: element.element_data?.font_color || '#000000',
                                fontWeight: element.element_data?.bold ? 'bold' : 'normal',
                                fontStyle: element.element_data?.italic ? 'italic' : 'normal',
                                textDecoration: element.element_data?.underline ? 'underline' : 'none',
                                textAlign: element.element_data?.text_align || 'left',
                                background: 'rgba(255,255,255,0.1)',
                                border: '2px solid rgba(0,0,0,0.5)',
                                boxSizing: 'border-box',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                padding: 0
                            } : {
                                background: 'transparent',
                                border: '2px solid rgba(0,0,0,0.5)',
                                boxSizing: 'border-box',
                                overflow: 'hidden'
                            })
                        }"
                        @click.stop="selectElement(element)"
                    >
                        <div 
                            v-if="selectedElement?.element_id === element.element_id"
                            class="element-controls"
                        >
                            <button @click.stop="deleteElement(element.element_id)" class="delete-btn">×</button>
                        </div>
                        
                        <!-- Text element content -->
                        <div v-if="element.element_type === 'text'" class="text-editor" style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;text-align:center;overflow:hidden;word-break:break-word;line-height:1.2;padding:2px;">
                            <textarea
                                v-if="selectedElement?.element_id === element.element_id && isEditing"
                                v-model="editingContent"
                                @blur="finishEditing"
                                @keydown="handleKeyDown"
                                :style="{
                                    fontFamily: element.element_data?.font_family || 'Arial',
                                    fontSize: `${element.element_data?.font_size || 18}px`,
                                    color: element.element_data?.font_color || '#000000',
                                    fontWeight: element.element_data?.bold ? 'bold' : 'normal',
                                    fontStyle: element.element_data?.italic ? 'italic' : 'normal',
                                    textDecoration: element.element_data?.underline ? 'underline' : 'none',
                                    textAlign: element.element_data?.text_align || 'left',
                                    width: '100%',
                                    height: '100%',
                                    border: '2px solid #28a745',
                                    background: 'rgba(255,255,255,0.7)',
                                    resize: 'none',
                                    outline: 'none',
                                    padding: '5px',
                                    boxShadow: 'none',
                                    boxSizing: 'border-box',
                                    overflow: 'hidden'
                                }"
                            ></textarea>
                            <div v-else v-html="marked(element.element_data?.content || '')" style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;"></div>
                        </div>
                        
                        <!-- Image element content -->
                        <div v-else-if="element.element_type === 'image'" class="image-container" style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;overflow:hidden;">
                            <img 
                                :src="element.element_data?.image_url" 
                                :alt="element.element_data?.alt_text || ''"
                                style="max-width:100%;max-height:100%;object-fit:contain;"
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Element Styling Controls -->
        <div v-if="selectedElement" class="element-styling">
            <div class="styling-controls">
                <div class="control-group">
                    <label for="font-family">Font:</label>
                    <select 
                        id="font-family"
                        v-model="selectedElement.element_data.font_family"
                        @change="updateElement(selectedElement.element_id, { 
                            font_family: selectedElement.element_data.font_family 
                        })"
                    >
                        <option value="Arial">Arial</option>
                        <option value="Times New Roman">Times New Roman</option>
                        <option value="Courier New">Courier New</option>
                    </select>
                </div>
                <div class="control-group">
                    <label for="font-size">Size:</label>
                    <input 
                        id="font-size"
                        type="number" 
                        v-model.number="integerFontSize"
                        @change="updateElement(selectedElement.element_id, { 
                            font_size: integerFontSize
                        })"
                        min="8"
                        max="72"
                        step="1"
                    />
                </div>
                <div class="control-group">
                    <label for="font-color">Color:</label>
                    <input 
                        id="font-color"
                        type="color" 
                        v-model="selectedElement.element_data.font_color"
                        @change="updateElement(selectedElement.element_id, { 
                            font_color: selectedElement.element_data.font_color 
                        })"
                    />
                </div>
                <div class="control-group">
                    <label for="text-align">Align:</label>
                    <select 
                        id="text-align"
                        v-model="selectedElement.element_data.text_align"
                        @change="updateElement(selectedElement.element_id, { 
                            text_align: selectedElement.element_data.text_align 
                        })"
                    >
                        <option value="left">Left</option>
                        <option value="center">Center</option>
                        <option value="right">Right</option>
                    </select>
                </div>
                <div class="control-group">
                    <label for="x-position">X:</label>
                    <input 
                        id="x-position"
                        type="number" 
                        v-model.number="integerX"
                        @change="updateElement(selectedElement.element_id, { 
                            x_position: integerX
                        })" 
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
                        @change="updateElement(selectedElement.element_id, { 
                            y_position: integerY
                        })" 
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
                        @change="updateElement(selectedElement.element_id, { 
                            z_index: integerZIndex
                        })" 
                        min="0" 
                        step="1"
                        placeholder="Z" 
                    />
                </div>
            </div>
        </div>

        <div class="action-buttons" ref="actionButtonsRef">
            <button @click="router.push(`/presentations/${presentationId}`)" class="cancel-button">
                Cancel
            </button>
            <button @click="saveSlide" :disabled="isSubmitting" class="save-button">
                {{ isSubmitting ? 'Saving...' : (isEditMode ? 'Save Changes' : 'Create Slide') }}
            </button>
        </div>
    </div>
</template>

<style scoped>
.editor-root {
    /* min-height: 100vh; */
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    background: #222;
}

.center-flex {
    flex: 1;
    width: 100vw;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 0;
    min-width: 0;
}

.slide-scale-wrapper {
    display: block;
    position: relative;
    width: 100vw;
    /* height is set dynamically via style binding */
    /* overflow: hidden; */
    margin: 0 auto;
    min-height: 0;
    min-width: 0;
}

.slide-container {
    background-color: white;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
    position: absolute;
    /* overflow: hidden; */
    border: 1px solid #ccc;
    cursor: crosshair;
    transform-origin: top left;
    box-sizing: border-box;
    /* left/top/translate handled inline */
}

.header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    max-width: 960px;
    margin: 0;
}

.controls {
    display: flex;
    gap: 10px;
    align-items: center;
}

.color-picker {
    display: flex;
    align-items: center;
    gap: 8px;
}

.color-picker label {
    font-size: 14px;
    color: #666;
}

.color-picker input[type="color"] {
    width: 40px;
    height: 40px;
    padding: 0;
    border: 2px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
}

.color-picker input[type="color"]::-webkit-color-swatch-wrapper {
    padding: 0;
}

.color-picker input[type="color"]::-webkit-color-swatch {
    border: none;
    border-radius: 2px;
}

.error-message {
    color: #dc3545;
    margin: 10px 0;
    text-align: center;
}

.action-buttons {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin: 24px 0 32px 0;
    width: 100vw;
    position: relative;
    z-index: 10;
}

.cancel-button, .save-button {
    padding: 10px 20px;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.cancel-button {
    background-color: #f8f9fa;
    border: 1px solid #ddd;
    color: #666;
}

.cancel-button:hover {
    background-color: #e9ecef;
}

.save-button {
    background-color: #007bff;
    border: 1px solid #0056b3;
    color: white;
}

.save-button:hover {
    background-color: #0056b3;
}

.save-button:disabled {
    background-color: #ccc;
    border-color: #999;
    cursor: not-allowed;
}

.slide-container {
    position: relative;
    cursor: crosshair;
}

.element {
    position: absolute;
    cursor: move;
    user-select: none;
    overflow: visible !important;
}

.element.selected {
    outline: 2px solid #007bff;
}

.element-controls {
    position: absolute;
    top: -30px;
    right: -10px;
    z-index: 9999;
    pointer-events: auto;
}

.delete-btn {
    background: #dc3545;
    color: white;
    border: none;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    line-height: 24px;
    text-align: center;
    cursor: pointer;
    padding: 0;
    font-size: 16px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    position: relative;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
}

.delete-btn:hover {
    background: #c82333;
    transform: scale(1.1);
    box-shadow: 0 3px 6px rgba(0,0,0,0.3);
}

.text-editor {
    width: 100%;
    height: 100%;
    min-height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    overflow: hidden;
    word-break: break-word;
    line-height: 1.2;
    padding: 2px;
}

.element-styling {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: white;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    z-index: 1000;
}

.styling-controls {
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
}

.control-group {
    display: flex;
    flex-direction: column;
    gap: 4px;
    align-items: flex-start;
}

.control-group label {
    font-size: 12px;
    color: #666;
    font-weight: 500;
}

.control-group select,
.control-group input[type="number"] {
    padding: 4px 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 13px;
    min-width: 60px;
}

.control-group input[type="color"] {
    width: 30px;
    height: 30px;
    padding: 0;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
}

.text-element {
    position: absolute;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255,255,255,0.9);
    border: 2px solid rgba(0,0,0,0.5);
    white-space: pre-wrap;
    word-wrap: break-word;
    overflow-wrap: break-word;
    overflow: hidden;
    min-width: 0;
    min-height: 0;
    padding: 0;
}

.text-element.selected {
    outline: 2px solid #007bff;
    background: white;
}

.text-element.editing {
    outline: 2px solid #28a745;
    background: transparent;
    box-shadow: none;
}

.text-element.editing textarea {
    cursor: text;
    background: transparent;
    border: none;
    box-shadow: none;
}

.image-element {
    position: absolute;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: 2px solid rgba(0,0,0,0.5);
    overflow: hidden;
}

.image-element.selected {
    outline: 2px solid #007bff;
}

.image-container {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

.image-container img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

@media (max-width: 900px) {
  .header-container {
    flex-direction: column;
    align-items: flex-start;
    padding: 8px 4vw;
    max-width: 100vw;
    gap: 8px;
  }
  .controls {
    flex-wrap: wrap;
    gap: 8px;
    width: 100%;
    justify-content: flex-start;
  }
  .color-picker label {
    font-size: 13px;
  }
  .slide-scale-wrapper {
    width: 100vw;
    min-width: 0;
    margin: 0;
  }
  .action-buttons {
    flex-direction: column;
    gap: 12px;
    width: 100vw;
    margin: 16px 0 20px 0;
  }
  .cancel-button, .save-button {
    width: 90vw;
    max-width: 320px;
    font-size: 15px;
    padding: 10px 0;
  }
  .element-styling {
    width: 95vw;
    padding: 12px;
  }
  .styling-controls {
    gap: 8px;
  }
  .control-group {
    min-width: 80px;
  }
}

@media (max-width: 600px) {
  .header-container {
    padding: 4px 2vw;
    font-size: 18px;
    gap: 4px;
  }
  .controls {
    flex-direction: column;
    align-items: stretch;
    gap: 6px;
  }
  .slide-scale-wrapper {
    width: 100vw;
    min-width: 0;
    margin: 0;
  }
  .action-buttons {
    flex-direction: column;
    gap: 8px;
    width: 100vw;
    margin: 10px 0 14px 0;
  }
  .cancel-button, .save-button {
    width: 96vw;
    max-width: 240px;
    font-size: 14px;
    padding: 9px 0;
  }
  .element-styling {
    width: 98vw;
    padding: 8px;
  }
  .styling-controls {
    gap: 6px;
  }
  .control-group {
    min-width: 70px;
  }
  .control-group label {
    font-size: 11px;
  }
  .control-group select,
  .control-group input[type="number"] {
    font-size: 12px;
    padding: 3px 6px;
  }
}
</style> 