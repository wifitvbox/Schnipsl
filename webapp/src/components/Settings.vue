<template>
  <v-container>
    <h1>{{ $t('settings') }}</h1>
    {{ $t('settings_name_intro') }}
    <v-form ref="form">
      <v-text-field
      v-model="userName"
      :label= "$t('settings_name_help')"
      required
      ></v-text-field>
    </v-form>
  </v-container>
</template>

<script>
export default {
  name: 'Settings',
  data () {
    return {
      userName: '',
      pw: ''
    }
  },
  methods: {
  },
  mounted () {
    if (localStorage.userName) {
      this.userName = localStorage.userName
    }
    if (localStorage.pw) {
      this.pw = localStorage.pw
    }
  },
  watch: {
    userName (newUser) {
      localStorage.userName = newUser
    },
    pw (newPw) {
      localStorage.pw = newPw
    }
  }
}
</script>
