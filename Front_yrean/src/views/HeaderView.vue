<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import logo from '../../assets/Empyre_Point_Logo.png'

const router = useRouter()
const isMenuOpen = ref(false)
const isMobile = ref(window.innerWidth <= 900)

const toPresentations = () => {
  router.push('/presentations')
  closeMenu()
}

const toCreatePresentation = () => {
  router.push('/create-presentation')
  closeMenu()
}

const logOut = () => {
  sessionStorage.removeItem('user')
  router.push('/login')
  closeMenu()
}

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
  // Prevent body scroll when menu is open
  document.body.style.overflow = isMenuOpen.value ? 'hidden' : ''
}

const closeMenu = () => {
  isMenuOpen.value = false
  document.body.style.overflow = ''
}

// Handle window resize
const handleResize = () => {
  isMobile.value = window.innerWidth <= 900
  if (!isMobile.value) {
    closeMenu()
  }
}

// Close menu when clicking outside
const handleClickOutside = (event) => {
  const menu = document.querySelector('.mobile-menu')
  const hamburger = document.querySelector('.hamburger-button')
  if (menu && !menu.contains(event.target) && !hamburger?.contains(event.target)) {
    closeMenu()
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('click', handleClickOutside)
  // Ensure body scroll is restored
  document.body.style.overflow = ''
})
</script>

<template>
  <header class="header" :class="{ 'mobile-header': isMobile }">
    <div class="header-content">
      <img :src="logo" alt="Logo" class="logo_small">
      
      <!-- Desktop Navigation -->
      <div v-if="!isMobile" class="header_buttons">
        <button @click="toPresentations" class="header_button">My Presentations</button>
        <button @click="toCreatePresentation" class="header_button">Create New Presentation</button>
        <button @click="logOut" class="header_button">Log Out</button>
      </div>

      <!-- Mobile Hamburger Button -->
      <button 
        v-else 
        @click="toggleMenu" 
        class="hamburger-button"
        :class="{ 'is-active': isMenuOpen }"
        aria-label="Toggle menu"
      >
        <svg width="24" height="18" viewBox="0 0 24 18" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <rect y="2" width="24" height="2" rx="1" fill="currentColor" />
          <rect y="8" width="24" height="2" rx="1" fill="currentColor" />
          <rect y="14" width="24" height="2" rx="1" fill="currentColor" />
        </svg>
      </button>
    </div>

    <!-- Mobile Menu Overlay -->
    <div 
      v-if="isMobile" 
      class="menu-overlay" 
      :class="{ 'is-active': isMenuOpen }"
      @click="closeMenu"
    ></div>

    <!-- Mobile Menu -->
    <nav 
      v-if="isMobile" 
      class="mobile-menu" 
      :class="{ 'is-active': isMenuOpen }"
    >
      <div class="mobile-menu-content">
        <button @click="toPresentations" class="mobile-menu-button">My Presentations</button>
        <button @click="toCreatePresentation" class="mobile-menu-button">Create New Presentation</button>
        <button @click="logOut" class="mobile-menu-button">Log Out</button>
      </div>
    </nav>
  </header>
</template>
