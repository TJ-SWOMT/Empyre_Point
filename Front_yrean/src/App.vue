<script setup>
import { useRouter } from 'vue-router'
import { ref } from 'vue'
import logo from '../assets/Empyre_Point_Logo.png'
import './assets/styles/empyre-point.css'
const router = useRouter()
const toPresentations = () => {
  router.push('/presentations')
}

const toCreatePresentation = () => {
  router.push('/create-presentation')
}

const logOut = () => {
  sessionStorage.removeItem('user')
  router.push('/login')
}

const isLoggedIn = ref(false)

// Watch for changes to sessionStorage and route changes
const checkLoginStatus = () => {
  isLoggedIn.value = !!sessionStorage.getItem('user')
}

// Watch route changes
router.beforeEach((to, from, next) => {
  checkLoginStatus()
  next()
})

// Check login status on component mount
checkLoginStatus()

</script>

<template>
  
  <div v-if="isLoggedIn" class="header">
    <img :src="logo" alt="Logo" class="logo_small">
    <div class="header_buttons">  
      <button @click="toPresentations" class="header_button">My Presentations</button>
      <button @click="toCreatePresentation" class="header_button">Create New Presentation</button>
      <button @click="logOut" class="header_button">Log Out</button>
    </div>
  </div>
  <div class="app-container">
    <router-view></router-view>
  </div>
</template>


