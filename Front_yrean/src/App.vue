<script setup>
import { useRouter } from 'vue-router'
import { ref } from 'vue'
import HeaderView from './views/HeaderView.vue'
import './styles/empyre-point.css'

const router = useRouter()
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
  <HeaderView v-if="isLoggedIn" />

    <router-view></router-view>

</template>




