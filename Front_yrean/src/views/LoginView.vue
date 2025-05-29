<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi, handleApiError } from '../services/api'
import logo from '../../assets/Empyre_Point_Logo.png'
import '../assets/styles/empyre-point.css'
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