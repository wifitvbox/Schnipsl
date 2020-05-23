<template>
	<v-app>
		<div id="app">
			<router-view />
			<v-footer padless fixed>
				<v-card class="flex" flat tile>
					<v-card-title class="teal">
						<v-btn icon class="mx-4"  @click="dialog = true">
							<v-icon size="24px">mdi-television-classic</v-icon>
						</v-btn>
						<v-btn icon class="mx-4">
							<v-icon size="24px">mdi-skip-previous</v-icon>
						</v-btn>
						<v-btn icon class="mx-4">
							<v-icon size="24px">mdi-rewind-10</v-icon>
						</v-btn>
						<v-btn icon @click="play = !play">
							<v-icon>{{ play ? 'mdi-pause' : 'mdi-play' }}</v-icon>
						</v-btn>
						<v-btn icon class="mx-4">
							<v-icon size="24px">mdi-fast-forward-10</v-icon>
						</v-btn>
						<v-btn icon class="mx-4">
							<v-icon size="24px">mdi-skip-next</v-icon>
						</v-btn>
					</v-card-title>

					<v-progress-linear value="15" color="red"></v-progress-linear>
				</v-card>
			</v-footer>
			<v-row justify="center">
				<v-dialog v-model="dialog" scrollable max-width="300px">
					<v-card>
						<v-card-title>Select Country</v-card-title>
						<v-divider></v-divider>
						<v-card-text style="height: 300px;">
							<v-radio-group v-model="dialogm1" column>
								<v-radio label="Bahamas, The" value="bahamas"></v-radio>
								<v-radio label="Bahrain" value="bahrain"></v-radio>
								<v-radio label="Bangladesh" value="bangladesh"></v-radio>
								<v-radio label="Barbados" value="barbados"></v-radio>
								<v-radio label="Belarus" value="belarus"></v-radio>
								<v-radio label="Belgium" value="belgium"></v-radio>
								<v-radio label="Belize" value="belize"></v-radio>
								<v-radio label="Benin" value="benin"></v-radio>
								<v-radio label="Bhutan" value="bhutan"></v-radio>
								<v-radio label="Bolivia" value="bolivia"></v-radio>
								<v-radio label="Bosnia and Herzegovina" value="bosnia"></v-radio>
								<v-radio label="Botswana" value="botswana"></v-radio>
								<v-radio label="Brazil" value="brazil"></v-radio>
								<v-radio label="Brunei" value="brunei"></v-radio>
								<v-radio label="Bulgaria" value="bulgaria"></v-radio>
								<v-radio label="Burkina Faso" value="burkina"></v-radio>
								<v-radio label="Burma" value="burma"></v-radio>
								<v-radio label="Burundi" value="burundi"></v-radio>
							</v-radio-group>
						</v-card-text>
						<v-divider></v-divider>
						<v-card-actions>
							<v-btn color="blue darken-1" text @click="dialog = false">Close</v-btn>
							<v-btn color="blue darken-1" text @click="dialog = false">Save</v-btn>
						</v-card-actions>
					</v-card>
				</v-dialog>
			</v-row>
		</div>
	</v-app>
</template>

<script>
export default {
	data() {
		return {
			play: false,
			dialogm1: "",
			dialog: false
		};
	},
	methods: {}
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
