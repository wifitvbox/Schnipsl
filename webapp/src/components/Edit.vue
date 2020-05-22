<template>
  <v-expansion-panels>
    <v-expansion-panel
      v-for="(item,i) in 5"
      :key="i"
    >
      <v-expansion-panel-header>Item</v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-col cols="12">
          <v-autocomplete
            v-model="values"
            :items="items"
            outlined
            chips
            small-chips
            label="Outlined"
            multiple
          ></v-autocomplete>
        </v-col>
      </v-expansion-panel-content>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script>
import router from '../router'
export default {
  name: 'Edit',
  data () {
    return {
      id: 0,
      msg: 'Edit page',
      selected: [],
      users: [],
      colors: [
        { hex: '#f00', label: 'Red' },
        { hex: '#0f0', label: 'Green' },
        { hex: '#00f', label: 'Blue' }
      ],
      items: ['foo', 'bar', 'fizz', 'buzz'],
      values: ['foo', 'bar'],
      value: null,

    }
  },
  computed: {
    onsides: function () {
      return '43 ?!'
    }
  },
  created () {
    this.id = this.$route.params.id
    // first we fill a lookup to see which users are actual already selected
    try {
      console.log("Edit loaded")
    } catch (error) {
      this.nav2Main()
    }
  },
  methods: {
    nav2Main () {
      router.push({ name: 'Home' }) // always goes 'back enough' to Main
    }
  }
}
</script>

<style scoped>
h1,
h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}
</style>
