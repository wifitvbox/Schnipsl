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
    path: '/about',
    name: 'About',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/About.vue')
  },
    {
      path: '/edit/:id',
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

