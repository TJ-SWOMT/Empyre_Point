<script setup>
import { useRouter } from 'vue-router'
import { ref } from 'vue'

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
    <button @click="toPresentations">My Presentations</button>
    <button @click="toCreatePresentation">Create New Presentation</button>
    <button @click="logOut">Log Out</button>
  </div>
  <router-view></router-view>
</template>

