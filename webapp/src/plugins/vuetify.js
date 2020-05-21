import Vue from 'vue';
import Vuetify , {
    VApp, // required
    VNavigationDrawer,
    VFooter,
    VToolbar,
    VToolbarTitle,
    VSpacer,
    VBtn,
    VContent,
    VContainer,
    VLayout,
    VFlex,
    VImg,
    VFadeTransition,
    VCard,
    VIcon,
    VList,
    VSubheader,
    VDivider,
    VDialog,
    VCardText,
    VTextField,
    VCardActions,
    VDatePicker,
    VTimePicker,
    VMenu,
    VSelect,
    VForm,
    VCheckbox
  
  } from 'vuetify/lib'
  

Vue.use(Vuetify, {
    iconfont: 'md',
    components: {
      VApp,
      VNavigationDrawer,
      VFooter,
      VToolbar,
      VToolbarTitle,
      VSpacer,
      VBtn,
      VContent,
      VContainer,
      VLayout,
      VFlex,
      VImg,
      VFadeTransition,
      VCard,
      VIcon,
      VList,
      VDivider,
      VSubheader,
      VDialog,
      VCardText,
      VTextField,
      VCardActions,
      VDatePicker,
      VTimePicker,
      VMenu,
      VSelect,
      VForm,
      VCheckbox
    }
  })

export default new Vuetify({
});
