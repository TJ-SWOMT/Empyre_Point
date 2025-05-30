import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('./views/LoginView.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('./views/RegisterView.vue')
  },
  {
    path: '/create-presentation',
    name: 'CreatePresentation',
    component: () => import('./views/CreatePresentationView.vue')
  },
  {
    path: '/presentations',
    name: 'UserPresentations',
    component: () => import('./views/UserPresentationsView.vue')
  },
  {
    path: '/presentations/:id/play',
    name: 'PlayPresentation',
    component: () => import('./views/PlayPresentationView.vue')
  },
  {
    path: '/presentations/:id/slides/new',
    name: 'CreateSlide',
    component: () => import('./views/SlideEditorView.vue')
  },
  {
    path: '/presentations/:id/slides/:slide_id',
    name: 'EditSlide',
    component: () => import('./views/SlideEditorView.vue')
  },
  {
    path: '/presentations/:id',
    name: 'Presentation',
    component: () => import('./views/PresentationView.vue')
  },
  {
    path: '/presentations/:id/edit',
    name: 'EditPresentation',
    component: () => import('./views/EditPresentationModalView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 