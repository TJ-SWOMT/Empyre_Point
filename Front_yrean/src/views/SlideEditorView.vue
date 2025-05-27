<script setup>
import { ref, onMounted, watch, computed, nextTick, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'
import { marked } from 'marked'

const route = useRoute()
const router = useRouter()
const presentationId = route.params.id
const slideId = ref(route.params.slide_id)
const error = ref('')
const isSubmitting = ref(false)
const isEditMode = computed(() => !!slideId.value)

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

const addImage = () => {
    console.log('addImage')
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
        
        const response = await presentationApi.updateElement(numericId, {
            element_type: 'text',
            ...updates
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
            x_position: x,
            y_position: y,
            width: 200,
            height: 100,
            font_family: defaultElementData.font_family,
            font_size: defaultElementData.font_size,
            font_color: defaultElementData.font_color,
            bold: defaultElementData.bold,
            italic: defaultElementData.italic,
            underline: defaultElementData.underline,
            text_align: defaultElementData.text_align,
            z_index: elements.value.length
        })

        if (response.error) throw new Error(response.error)
        
        // Ensure the element has a numeric ID
        const elementId = validateElementId(response.element.element_id)
        const newElement = {
            ...response.element,
            element_id: elementId,
            element_data: response.element.element_data || defaultElementData
        }
        
        console.log('Created new element:', newElement)
        elements.value.push(newElement)
        selectedElement.value = newElement
        
        // Use requestAnimationFrame for more reliable timing
        requestAnimationFrame(() => {
            startEditing(newElement)
        })
    } catch (err) {
        error.value = handleApiError(err)
        console.error('Error creating text element:', err)
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

    const rect = event.target.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    createTextElement(x, y);
    isAddingText.value = false; // Reset the mode after creating

    // Reset cursor
    const slideContainer = document.querySelector('.slide-container');
    if (slideContainer) {
        slideContainer.style.cursor = 'default';
    }
};

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
})

onUnmounted(() => {
    document.removeEventListener('mousedown', handleClickAway);
})
</script>

<template>
    <div>
        <div class="header-container">
            <h1>{{ isEditMode ? 'Edit Slide' : 'Create Slide' }}</h1>
            <div class="controls">
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

        <div 
            class="slide-container" 
            :style="{ backgroundColor: backgroundColor }"
            @click="handleSlideClick"
        >
            <!-- Text Elements -->
            <div 
                v-for="element in elements" 
                :key="`element-${element.element_id}-${element.element_data?.content}`"
                class="element text-element"
                :class="{ 
                    'selected': selectedElement?.element_id === element.element_id,
                    'editing': selectedElement?.element_id === element.element_id && isEditing
                }"
                :style="{
                    position: 'absolute',
                    left: `${element.x_position}px`,
                    top: `${element.y_position}px`,
                    width: element.width ? `${element.width}px` : 'auto',
                    height: element.height ? `${element.height}px` : 'auto',
                    zIndex: element.z_index
                }"
                @click.stop="selectElement(element)"
            >
                <div 
                    v-if="selectedElement?.element_id === element.element_id"
                    class="element-controls"
                >
                    <button @click.stop="deleteElement(element.element_id)" class="delete-btn">×</button>
                </div>
                
                <div 
                    class="text-editor"
                    :style="{
                        fontFamily: element.element_data?.font_family || 'Arial',
                        fontSize: `${element.element_data?.font_size || 18}px`,
                        color: element.element_data?.font_color || '#000000',
                        fontWeight: element.element_data?.bold ? 'bold' : 'normal',
                        fontStyle: element.element_data?.italic ? 'italic' : 'normal',
                        textDecoration: element.element_data?.underline ? 'underline' : 'none',
                        textAlign: element.element_data?.text_align || 'left'
                    }"
                    @dblclick.stop="startEditing(element)"
                >
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
                            border: 'none',
                            background: 'transparent',
                            resize: 'none',
                            outline: 'none',
                            padding: '5px',
                            backgroundColor: 'transparent',
                            boxShadow: 'none'
                        }"
                    ></textarea>
                    <div v-else v-html="marked(element.element_data?.content || '')"></div>
                </div>
            </div>
        </div>

        <!-- Element Styling Controls -->
        <div v-if="selectedElement" class="element-styling">
            <div class="styling-controls">
                <select 
                    v-model="selectedElement.element_data.font_family"
                    @change="updateElement(selectedElement.element_id, { 
                        font_family: selectedElement.element_data.font_family 
                    })"
                >
                    <option value="Arial">Arial</option>
                    <option value="Times New Roman">Times New Roman</option>
                    <option value="Courier New">Courier New</option>
                </select>
                <input 
                    type="number" 
                    v-model.number="selectedElement.element_data.font_size"
                    @change="updateElement(selectedElement.element_id, { 
                        font_size: selectedElement.element_data.font_size 
                    })"
                    min="8"
                    max="72"
                />
                <input 
                    type="color" 
                    v-model="selectedElement.element_data.font_color"
                    @change="updateElement(selectedElement.element_id, { 
                        font_color: selectedElement.element_data.font_color 
                    })"
                />
                <select 
                    v-model="selectedElement.element_data.text_align"
                    @change="updateElement(selectedElement.element_id, { 
                        text_align: selectedElement.element_data.text_align 
                    })"
                >
                    <option value="left">Left</option>
                    <option value="center">Center</option>
                    <option value="right">Right</option>
                </select>
                <!-- New manual controls for position and size -->
                <input type="number" v-model.number="selectedElement.x_position" @change="updateElement(selectedElement.element_id, { x_position: selectedElement.x_position })" min="0" placeholder="X" style="width:60px" />
                <input type="number" v-model.number="selectedElement.y_position" @change="updateElement(selectedElement.element_id, { y_position: selectedElement.y_position })" min="0" placeholder="Y" style="width:60px" />
                <input type="number" v-model.number="selectedElement.width" @change="updateElement(selectedElement.element_id, { width: selectedElement.width })" min="10" placeholder="Width" style="width:70px" />
                <input type="number" v-model.number="selectedElement.height" @change="updateElement(selectedElement.element_id, { height: selectedElement.height })" min="10" placeholder="Height" style="width:70px" />
                <input type="number" v-model.number="selectedElement.z_index" @change="updateElement(selectedElement.element_id, { z_index: selectedElement.z_index })" min="0" placeholder="Z" style="width:50px" />
            </div>
        </div>

        <div class="action-buttons">
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
.slide-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 1px solid #ccc;
    background-color: white;
    width: 960px;  /* Half of 1920px for better visibility */
    height: 540px; /* Half of 1080px to maintain 16:9 ratio */
    margin: 20px auto;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    position: relative;
    overflow: hidden;
    cursor: crosshair;
}

.header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    max-width: 960px;
    margin: 0 auto;
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
    margin-top: 20px;
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
}

.element.selected {
    outline: 2px solid #007bff;
}

.element-controls {
    position: absolute;
    top: -20px;
    right: 0;
    z-index: 1000;
}

.delete-btn {
    background: #dc3545;
    color: white;
    border: none;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    line-height: 20px;
    text-align: center;
    cursor: pointer;
    padding: 0;
    font-size: 14px;
}

.delete-btn:hover {
    background: #c82333;
}

.text-editor {
    width: 100%;
    height: 100%;
    min-height: 30px;
}

.element-styling {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: white;
    padding: 10px;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    z-index: 1000;
}

.styling-controls {
    display: flex;
    gap: 10px;
    align-items: center;
}

.styling-controls button {
    padding: 5px 10px;
    border: 1px solid #ddd;
    background: white;
    border-radius: 4px;
    cursor: pointer;
}

.styling-controls button.active {
    background-color: #0056b3;
    color: white;
}

.styling-controls select,
.styling-controls input[type="number"] {
    padding: 5px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.styling-controls input[type="color"] {
    width: 30px;
    height: 30px;
    padding: 0;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.text-element {
    min-width: 100px;
    min-height: 30px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 4px;
    padding: 5px;
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
</style> 