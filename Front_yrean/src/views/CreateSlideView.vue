<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'

const route = useRoute()
const router = useRouter()
const presentationId = route.params.id
const error = ref('')
const isSubmitting = ref(false)
const backgroundColor = ref(sessionStorage.getItem('slideBackgroundColor') || '#FFFFFF')  // Initialize from session storage

// Watch for changes to backgroundColor and save to session storage
watch(backgroundColor, (newColor) => {
    sessionStorage.setItem('slideBackgroundColor', newColor)
})

const texts = ref([])

const createSlide = async () => {
    try {
        isSubmitting.value = true
        error.value = ''
        
        // Create the slide - backend will handle the slide number
        const response = await presentationApi.createSlide(
            presentationId,
            1,  // The backend will ignore this and use the next available number
            backgroundColor.value  // Add the background color
        )
        
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
    texts.value.push({
        id: texts.value.length + 1,
        text: ''
    })
}

const deleteText = (id, event) => {
    texts.value = texts.value.filter(text => text.id !== id)
}

const addImage = () => {
    console.log('addImage')
}

const box = ref(null)
const pageX = ref(null) 
const pageY = ref(null)

onMounted(() => {
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
        <h1>Create Slide</h1>
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
            <button @click="addText">Add Text</button>
            <button @click="addImage">Add Image</button>
        </div>
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>

    <div class="slide-container" :style="{ backgroundColor: backgroundColor }">
        <form v-for="text in texts" :key="text.id">
            <input type="text" placeholder="Text" />
            <button @click="deleteText(text.id)">x</button>
        </form>
        <p><code>pageX</code>: <span id="x">n/a</span></p>
        <p><code>pageY</code>: <span id="y">n/a</span></p>
        

      
    </div>
    <button @click="createSlide" :disabled="isSubmitting">
        {{ isSubmitting ? 'Creating...' : 'Create Slide' }}
    </button>
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
}

/* Add a container to center the slide */
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
</style>