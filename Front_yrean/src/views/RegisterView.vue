<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import logo from '../../assets/Empyre_Point_Logo.png'
import '../assets/styles/main.css'
const router = useRouter()
const error = ref('')
const isSubmitting = ref(false)

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')

const onSubmit = async () => {
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  try {
    isSubmitting.value = true
    error.value = ''

    const response = await fetch('http://localhost:5001/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        email: email.value,
        password: password.value
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Registration failed')
    }

    // Store the user info if needed
    // authStore.setUser(data.user)

    // Redirect to create presentation page
    router.push('/create-presentation')
  } catch (err) {
    error.value = err.message
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="register-container">
    <img :src="logo" alt="Logo" class="logo">
    <form @submit.prevent="onSubmit" class="register-form">
      <h1>Register</h1>
      <div class="form-group">
        <label for="username">Username</label>
        <input id="username" v-model="username" type="text" required />
      </div>
      <div class="form-group">
        <label for="email">Email</label>
        <input id="email" v-model="email" type="email" required />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input id="password" v-model="password" type="password" required />
      </div>
      <div class="form-group">
        <label for="confirmPassword">Confirm Password</label>
        <input id="confirmPassword" v-model="confirmPassword" type="password" required />
      </div>
      <div v-if="error" class="error-message">{{ error }}</div>
      <button type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? 'Registering...' : 'Register' }}
      </button>
      <p class="login-link">
        Already have an account? <router-link to="/login">Login here</router-link>
      </p>
    </form>
  </div>
</template>

<style scoped>
/* Only keep component-specific styles that aren't in main.css */
.register-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: var(--spacing-md);
}

.register-form {
  width: 100%;
  max-width: 400px;
  padding: var(--spacing-lg);
  background-color: var(--white);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
}

.logo {
  display: block;
  margin: 0 auto var(--spacing-lg) auto;
  width: 30vw;
  max-width: 300px;
  height: auto;
}

.login-link {
  margin-top: var(--spacing-md);
  text-align: center;
}
</style>