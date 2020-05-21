import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify';
import router from './router'


import VueI18n from 'vue-i18n'
import messages from './lang'


Vue.config.productionTip = false

Vue.use(VueI18n)
Vue.use(vuetify)
export const i18n = new VueI18n({
  locale: 'de',
  fallbackLocale: 'de',
  messages
})


new Vue({
  vuetify,
  router,
  i18n,
  render: h => h(App)
}).$mount('#app')

