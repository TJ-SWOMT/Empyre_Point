<script setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'
import { marked } from 'marked'

const route = useRoute()
const router = useRouter()
const presentationId = route.params.id
const slideId = route.params.slide_id
const error = ref('')
const isSubmitting = ref(false)
const isEditMode = computed(() => !!slideId)

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
const isDragging = ref(false)
const dragStartPos = ref({ x: 0, y: 0 })
const elementStartPos = ref({ x: 0, y: 0 })

const isAddingText = ref(false)

const loadSlideData = async () => {
    if (!isEditMode.value) return

    try {
        const response = await presentationApi.getPresentation(presentationId)
        if (response.error) throw new Error(response.error)
        
        // Convert slideId to number for comparison since it comes from route params
        const slide = response.presentation.slides.find(s => Number(s.slide_id) === Number(slideId))
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
        const response = await presentationApi.getSlideElements(slideId)
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
                Number(slideId), // Ensure slideId is a number
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
        
        // Redirect back to the presentation view
        router.push(`/presentations/${presentationId}`)
    } catch (err) {
        error.value = handleApiError(err)
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

// Create a new text element
const createTextElement = async (x, y) => {
    try {
        const response = await presentationApi.createTextElement(slideId, {
            content: 'New Text',
            x_position: x,
            y_position: y,
            width: 200,
            height: 100,
            font_family: 'Arial',
            font_size: 18,
            font_color: '#000000',
            bold: false,
            italic: false,
            underline: false,
            text_align: 'left',
            z_index: elements.value.length
        })

        if (response.error) throw new Error(response.error)
        elements.value.push(response.element)
        selectedElement.value = response.element
    } catch (err) {
        error.value = handleApiError(err)
    }
}

// Update an element
const updateElement = async (elementId, updates) => {
    try {
        const response = await presentationApi.updateElement(elementId, {
            element_type: 'text',
            ...updates
        })

        if (response.error) throw new Error(response.error)
        
        // Update the element in our local state
        const index = elements.value.findIndex(e => e.element_id === elementId)
        if (index !== -1) {
            elements.value[index] = { ...elements.value[index], ...response.element }
        }
    } catch (err) {
        error.value = handleApiError(err)
    }
}

// Delete an element
const deleteElement = async (elementId) => {
    try {
        const response = await presentationApi.deleteElement(elementId)
        if (response.error) throw new Error(response.error)
        
        elements.value = elements.value.filter(e => e.element_id !== elementId)
        if (selectedElement.value?.element_id === elementId) {
            selectedElement.value = null
        }
    } catch (err) {
        error.value = handleApiError(err)
    }
}

// Handle element selection
const selectElement = (element) => {
    selectedElement.value = element
}

// Handle drag start
const handleDragStart = (event, element) => {
    if (event.target.closest('.text-editor')) return // Don't drag if clicking in editor
    
    isDragging.value = true
    selectedElement.value = element
    dragStartPos.value = {
        x: event.clientX,
        y: event.clientY
    }
    elementStartPos.value = {
        x: element.x_position,
        y: element.y_position
    }
    
    // Add event listeners for drag
    document.addEventListener('mousemove', handleDrag)
    document.addEventListener('mouseup', handleDragEnd)
}

// Handle drag
const handleDrag = (event) => {
    if (!isDragging.value || !selectedElement.value) return
    
    const dx = event.clientX - dragStartPos.value.x
    const dy = event.clientY - dragStartPos.value.y
    
    const newX = elementStartPos.value.x + dx
    const newY = elementStartPos.value.y + dy
    
    // Update element position
    updateElement(selectedElement.value.element_id, {
        x_position: newX,
        y_position: newY
    })
}

// Handle drag end
const handleDragEnd = () => {
    isDragging.value = false
    document.removeEventListener('mousemove', handleDrag)
    document.removeEventListener('mouseup', handleDragEnd)
}

// Handle slide click to create new text element
const handleSlideClick = (event) => {
    if (!isAddingText.value) return // Only create text if we're in add text mode
    if (event.target.closest('.element')) return // Don't create if clicking on existing element
    
    const rect = event.target.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    
    createTextElement(x, y)
    isAddingText.value = false // Reset the mode after creating
    
    // Reset cursor
    const slideContainer = document.querySelector('.slide-container')
    if (slideContainer) {
        slideContainer.style.cursor = 'default'
    }
}

const isEditing = ref(false)
const editingContent = ref('')
const textEditor = ref(null)

// Add these new functions for text editing
const startEditing = (element) => {
    selectedElement.value = element
    isEditing.value = true
    editingContent.value = element.element_data.content
    
    // Focus the textarea after it's rendered
    nextTick(() => {
        if (textEditor.value) {
            textEditor.value.focus()
        }
    })
}

const finishEditing = async () => {
    if (!selectedElement.value) return
    
    try {
        await updateElement(selectedElement.value.element_id, {
            content: editingContent.value
        })
        isEditing.value = false
    } catch (err) {
        error.value = handleApiError(err)
    }
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
                :key="element.element_id"
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
                @mousedown="(e) => handleDragStart(e, element)"
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
                        fontFamily: element.element_data.font_family,
                        fontSize: `${element.element_data.font_size}px`,
                        color: element.element_data.font_color,
                        fontWeight: element.element_data.bold ? 'bold' : 'normal',
                        fontStyle: element.element_data.italic ? 'italic' : 'normal',
                        textDecoration: element.element_data.underline ? 'underline' : 'none',
                        textAlign: element.element_data.text_align
                    }"
                    @dblclick.stop="startEditing(element)"
                >
                    <textarea
                        v-if="selectedElement?.element_id === element.element_id && isEditing"
                        v-model="editingContent"
                        @blur="finishEditing"
                        @keydown.enter.prevent="finishEditing"
                        :style="{
                            fontFamily: element.element_data.font_family,
                            fontSize: `${element.element_data.font_size}px`,
                            color: element.element_data.font_color,
                            fontWeight: element.element_data.bold ? 'bold' : 'normal',
                            fontStyle: element.element_data.italic ? 'italic' : 'normal',
                            textDecoration: element.element_data.underline ? 'underline' : 'none',
                            textAlign: element.element_data.text_align,
                            width: '100%',
                            height: '100%',
                            border: 'none',
                            background: 'transparent',
                            resize: 'none',
                            outline: 'none',
                            padding: '5px'
                        }"
                        ref="textEditor"
                    ></textarea>
                    <div v-else v-html="marked(element.element_data.content)"></div>
                </div>
            </div>
        </div>

        <!-- Element Styling Controls -->
        <div v-if="selectedElement" class="element-styling">
            <div class="styling-controls">
                <select 
                    v-model="selectedElement.element_data.font_family"
                    @change="updateElement(selectedElement.element_id, { font_family: selectedElement.element_data.font_family })"
                >
                    <option value="Arial">Arial</option>
                    <option value="Times New Roman">Times New Roman</option>
                    <option value="Courier New">Courier New</option>
                </select>
                
                <input 
                    type="number" 
                    v-model.number="selectedElement.element_data.font_size"
                    @change="updateElement(selectedElement.element_id, { font_size: selectedElement.element_data.font_size })"
                    min="8"
                    max="72"
                />
                
                <input 
                    type="color" 
                    v-model="selectedElement.element_data.font_color"
                    @change="updateElement(selectedElement.element_id, { font_color: selectedElement.element_data.font_color })"
                />
                
                <button 
                    @click="updateElement(selectedElement.element_id, { 
                        bold: !selectedElement.element_data.bold 
                    })"
                    :class="{ active: selectedElement.element_data.bold }"
                >
                    B
                </button>
                
                <button 
                    @click="updateElement(selectedElement.element_id, { 
                        italic: !selectedElement.element_data.italic 
                    })"
                    :class="{ active: selectedElement.element_data.italic }"
                >
                    I
                </button>
                
                <button 
                    @click="updateElement(selectedElement.element_id, { 
                        underline: !selectedElement.element_data.underline 
                    })"
                    :class="{ active: selectedElement.element_data.underline }"
                >
                    U
                </button>
                
                <select 
                    v-model="selectedElement.element_data.text_align"
                    @change="updateElement(selectedElement.element_id, { text_align: selectedElement.element_data.text_align })"
                >
                    <option value="left">Left</option>
                    <option value="center">Center</option>
                    <option value="right">Right</option>
                </select>
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
}
</style> 