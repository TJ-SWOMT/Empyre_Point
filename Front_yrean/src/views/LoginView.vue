<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi, handleApiError } from '../services/api'
import logo from '../../assets/Empyre_Point_Logo.png'
import '../assets/styles/main.css'
const router = useRouter()
const loginError = ref('')
const isSubmitting = ref(false)

const username = ref('')
const password = ref('')

const onSubmit = async (e) => {
  console.log('onSubmit called')
  isSubmitting.value = true
  loginError.value = ''

  try {
    const data = await authApi.login(username.value, password.value)
    console.log('Login API response:', data)
    if (data.success) {
      console.log('Login successful')
      // router.push('/create-presentation')
      sessionStorage.setItem('user', JSON.stringify(data.user))
      
      router.push('/presentations')
    } else {
      loginError.value = data.error || 'Login failed'
    }
  } catch (err) {
    loginError.value = handleApiError(err)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <img :src="logo" alt="Logo" class="logo">
    <form @submit.prevent="onSubmit" class="login-form">
      <h1>Login</h1>
      <div class="form-group">
        <label for="username">Username</label>
        <input id="username" v-model="username" type="text" required />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input id="password" v-model="password" type="password" required />
      </div>
      <div v-if="loginError" class="error-message">{{ loginError }}</div>
      <button type="submit" :disabled="isSubmitting">{{ isSubmitting ? 'Logging in...' : 'Login' }}</button>
      <p class="register-link">
        Don't have an account? <router-link to="/register">Register here</router-link>
      </p>
    </form>
  </div>
</template>

<style scoped>
/* Only keep component-specific styles that aren't in main.css */
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: var(--spacing-md);
}

.login-form {
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

.register-link {
  margin-top: var(--spacing-md);
  text-align: center;
}
</style>