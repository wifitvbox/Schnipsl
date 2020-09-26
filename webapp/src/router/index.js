import Vue from 'vue'
import VueRouter from 'vue-router'
//import Home from '../views/Home.vue'
import Home from '@/components/Home'
import Settings from '@/components/Settings'
import Edit from '@/components/Edit'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/edit/:uuid',
    name: 'Edit',
    component: Edit
  },
  {
    path: '/set',
    name: 'Settings',
    component: Settings
  },
  {
    path: '*',
    redirect: '/Home'
  }
]

const router = new VueRouter({
  routes
})

export default router

