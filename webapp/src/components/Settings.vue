<template>
  <v-container>
    <h1>{{ $t('translation1') }}</h1>
    <v-form v-model="valid" ref="form">
      <v-text-field
      v-model="userName"
      label= '@:translation1'
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
    user (newUser) {
      localStorage.userName = newUser
    },
    pw (newPw) {
      localStorage.pw = newPw
    }
  }

}
</script>
