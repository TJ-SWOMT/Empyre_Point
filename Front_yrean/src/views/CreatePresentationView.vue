<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'
import '../assets/styles/main.css'

const router = useRouter()
const title = ref('')
const description = ref('')
const error = ref('')
const isSubmitting = ref(false)

const createPresentation = async () => {
    if (!title.value.trim()) {
        error.value = 'Please enter a title'
        return
    }

    // Get and validate user data from session storage
    const userData = sessionStorage.getItem('user')
    if (!userData) {
        error.value = 'Please log in to create a presentation'
        router.push('/login')
        return
    }

    let user_id
    try {
        const parsedUser = JSON.parse(userData)
        if (!parsedUser || !parsedUser.user_id) {
            throw new Error('Invalid user data')
        }
        user_id = parsedUser.user_id
    } catch (err) {
        console.error('Error parsing user data:', err)
        error.value = 'Session expired. Please log in again.'
        router.push('/login')
        return
    }

    try {
        isSubmitting.value = true
        error.value = ''

        const data = await presentationApi.createPresentation(
            user_id,
            title.value.trim(),
            description.value.trim() 
        )

        if (data.success && data.presentation?.presentation_id) {
            router.push(`/presentations/${data.presentation.presentation_id}`)
        } else {
            error.value = data.error || 'Failed to create presentation'
        }
    } catch (err) {
        error.value = handleApiError(err)
    } finally {
        isSubmitting.value = false
    }
}
</script>

<template>
    <div class="create-presentation-container">
        <div class="create-presentation-header">
            <div class="create-presentation-title">Create New Presentation</div>
        </div>
        <div class="presentation-form">
            <div class="form-group">
                <label for="title">Presentation Title</label>
                <input id="title" v-model="title" type="text" placeholder="Enter presentation title" required maxlength="32"/>
                <div class="char-count">{{ title.length }}/32 characters</div>
            </div>
            <div class="form-group">
                <label for="description">Description (Optional)</label>
                <textarea id="description" v-model="description" placeholder="Enter presentation description"
                    rows="3" maxlength="200"></textarea>
                <div class="char-count">{{ description.length }}/200 characters</div>
            </div>
            <button @click="createPresentation" :disabled="isSubmitting">
                {{ isSubmitting ? 'Creating...' : 'Create Presentation' }}
            </button>
            <div v-if="error" class="error-message">{{ error }}</div>
        </div>
    </div>
</template>

<style scoped>
/* Only keep component-specific styles that aren't in main.css */
.create-presentation-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: var(--spacing-md);
}

.presentation-form {
    /* width: 100%; */
    width: 55vw;
    padding: var(--spacing-lg);
    background-color: var(--white);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
}

textarea {
    resize: vertical;
    min-height: 20vh;
}

.create-presentation-header {
  /* margin-top: 100px; */
  right: 0;
  top: calc(var(--header-height) - 10px);
  position: fixed;
  color: white;
  background-color: var(--white);
  width: 100%;
  height: 100px;
  display: flex; /* Make the container a flex container */
  align-items: center; /* Vertically center content along the cross-axis */
  justify-content: center;
  box-shadow: inset 10px 10px 100px rgba(53, 89, 126, 1);

}

.create-presentation-title {
  background-color: var(--primary-color);
  color: var(--white);
  border: var(--button-border);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius);
  font-size: 2rem;
  font-weight: bold;
}

.char-count {
  font-size: 0.9rem;
  color: var(--text-light);
  text-align: right;
  margin-top: 2px;
}
</style>