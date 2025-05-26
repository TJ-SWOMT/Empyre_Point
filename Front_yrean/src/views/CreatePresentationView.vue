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
    const user_id = JSON.parse(sessionStorage.getItem('user')).user_id
    console.log('user22222', user_id)
    try {
        isSubmitting.value = true
        error.value = ''

        // const user = sessionStorage.getItem('user')
        console.log('user????', user_id)

        if (!user_id) {
            router.push('/login')
            return
        }

        const data = await presentationApi.createPresentation(
            user_id,
            title.value.trim(),
            description.value.trim() 
        )

        if (data.success && data.presentation?.presentation_id) {
            router.push(`/presentation/${data.presentation.presentation_id}`)
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