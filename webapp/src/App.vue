<template>
<v-app>
  <div id="app">
    <router-view/>
		<v-footer  padless fixed>
			<v-card class="flex" flat tile>

				<v-card-title class="teal">
					<v-btn v-for="icon in icons" :key="icon" class="mx-4"  icon>
						<v-icon size="24px">{{ icon }}</v-icon>
					</v-btn>
				</v-card-title>

				<v-progress-linear value="15" color="red"></v-progress-linear>
			</v-card>
		</v-footer>
  </div>
  </v-app>
</template>

<script>
export default {
	data() {
		return {
			icons: ["mdi-skip-previous","mdi-rewind-10", "mdi-play","mdi-pause", "mdi-fast-forward-10","mdi-skip-next", "mdi-record"]
		};
	},
	methods: {
	}
};
</script>


<style lang="scss">
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  padding: 30px;

  a {
    font-weight: bold;
    color: #2c3e50;

    &.router-link-exact-active {
      color: #42b983;
    }
  }
}
</style>
