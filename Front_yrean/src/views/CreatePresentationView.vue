<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { presentationApi, handleApiError } from '../services/api'

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
        <h1>Create New Presentation</h1>
        <div class="presentation-form">
            <div class="form-group">
                <label for="title">Presentation Title</label>
                <input id="title" v-model="title" type="text" placeholder="Enter presentation title" required />
            </div>
            <div class="form-group">
                <label for="description">Description (Optional)</label>
                <textarea id="description" v-model="description" placeholder="Enter presentation description"
                    rows="3"></textarea>
            </div>
            <button @click="createPresentation" :disabled="isSubmitting">
                {{ isSubmitting ? 'Creating...' : 'Create Presentation' }}
            </button>
            <div v-if="error" class="error-message">{{ error }}</div>
        </div>
    </div>
</template>