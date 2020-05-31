<template>
	<v-card max-width="600" class="mx-auto">
		<v-toolbar color="light-blue" dark>
			<v-app-bar-nav-icon @click="nav2Set()"></v-app-bar-nav-icon>

			<v-toolbar-title>{{ $t('main_title') }}</v-toolbar-title>

			<v-spacer></v-spacer>

			<v-btn icon>
				<v-icon>mdi-magnify</v-icon>
			</v-btn>

			<v-btn icon>
				<v-icon>mdi-plus-circle</v-icon>
			</v-btn>
		</v-toolbar>

		<v-list two-line subheader>
			<v-subheader inset>{{ $t('main_templates') }}</v-subheader>

			<v-list-item v-for="item in items.templates" :key="item.title" @click="nav2Play(item.title)">
				<v-list-item-avatar>
					<v-icon :class="[item.iconClass]" v-text="item.icon"></v-icon>
				</v-list-item-avatar>

				<v-list-item-content>
					<v-list-item-title v-text="item.title"></v-list-item-title>
					<v-list-item-subtitle v-text="item.subtitle"></v-list-item-subtitle>
				</v-list-item-content>

				<v-list-item-action>
					<v-btn icon @click="nav2Edit(item.title)">
						<v-icon color="grey lighten-1">mdi-pencil</v-icon>
					</v-btn>
				</v-list-item-action>
			</v-list-item>

			<v-subheader inset>{{ $t('main_streams') }}</v-subheader>
			<v-list-item v-for="item in items.streams" :key="item.title" @click="nav2Play(item.title)">
				<v-list-item-avatar>
					<v-icon :class="[item.iconClass]" v-text="item.icon"></v-icon>
				</v-list-item-avatar>

				<v-list-item-content>
					<v-list-item-title v-text="item.title"></v-list-item-title>
					<v-list-item-subtitle v-text="item.subtitle"></v-list-item-subtitle>
				</v-list-item-content>

				<v-list-item-action>
					<v-btn icon @click="nav2Edit(item.title)">
						<v-icon color="grey lighten-1">mdi-pencil</v-icon>
					</v-btn>
				</v-list-item-action>
			</v-list-item>

			<v-subheader inset>{{ $t('main_records') }}</v-subheader>
			<v-list-item v-for="item in items.records" :key="item.title" @click="nav2Play(item.title)">
				<v-list-item-avatar>
					<v-icon :class="[item.iconClass]" v-text="item.icon"></v-icon>
				</v-list-item-avatar>

				<v-list-item-content>
					<v-list-item-title v-text="item.title"></v-list-item-title>
					<v-list-item-subtitle v-text="item.subtitle"></v-list-item-subtitle>
				</v-list-item-content>

				<v-list-item-action>
					<v-btn icon @click="nav2Edit(item.title)">
						<v-icon color="grey lighten-1">mdi-pencil</v-icon>
					</v-btn>
				</v-list-item-action>
			</v-list-item>
		</v-list>
			<v-subheader inset>{{ $t('main_timers') }}</v-subheader>
			<v-list-item v-for="item in items.timers" :key="item.title" @click="nav2Play(item.title)">
				<v-list-item-avatar>
					<v-icon :class="[item.iconClass]" v-text="item.icon"></v-icon>
				</v-list-item-avatar>

				<v-list-item-content>
					<v-list-item-title v-text="item.title"></v-list-item-title>
					<v-list-item-subtitle v-text="item.subtitle"></v-list-item-subtitle>
				</v-list-item-content>

				<v-list-item-action>
					<v-btn icon @click="nav2Edit(item.title)">
						<v-icon color="grey lighten-1">mdi-pencil</v-icon>
					</v-btn>
				</v-list-item-action>
			</v-list-item>
	</v-card>
</template>


<script>
import router from "../router";
import messenger from "../messenger";
export default {
	name: "Schnipsl",
	title () {
	return `${this.name}`
  },
	data() {
		return {
			msg: "Welcome to Your Vue.js App",
			items: {
				templates:[
				{
					icon: "mdi-magnify",
					iconClass: "red lighten-1 white--text",
					title: "Photos1",
					subtitle: "Jan 9, 2014"
				},
				{
					icon: "mdi-radio-tower",
					iconClass: "green lighten-1 white--text",
					title: "Recipes1",
					subtitle: "Jan 17, 2014"
				},
				{
					icon: "mdi-play-pause",
					iconClass: "orange white--text",
					title: "Photos2",
					subtitle: "Jan 9, 2014"
				}
			],
			records: [
				{
					icon: "mdi-play-pause",
					iconClass: "blue white--text",
					title: "Vacation itinerary",
					subtitle: "Jan 20, 2014"
				},
				{
					icon: "mdi-clock",
					iconClass: "amber white--text",
					title: "Kitchen remodel",
					subtitle: "Jan 10, 2014"
				}
			],
			streams:[],
			timers:[]
			}
		};
	},
	created() {
		messenger.register("home", this.messenger_onMessage, null, null);
		messenger.init("steffen", "bla", "register");
	},
	methods: {
		nav2Set() {
			router.push({ name: "Settings" });
		},
		nav2Edit(item) {
			console.log("click for edit", item);
			router.push({ name: "Edit", params: { id: item } });
		},
		nav2Play(item) {
			console.log("click for Play", item);
		},
		messenger_onMessage(type, data) {
			console.log("incoming message to home", type, data);
			if (type == "home_data") {
				this.items.streams = data;
			}
		},
		sendToServer() {
			// eslint-disable-next-line
			if (false) {
				// demo mode
				// delete local stored data
				// window.klobsdata = []
				window.klobsdata["sessiondata"]["trainings"] = [];
				localStorage.removeItem("sessiondata");
				this.sessiondata = { trainings: [] };
			} else {
				this.syncData(self, this.serializeSessiondata(this.sessiondata));
			}
		},
		// eslint-disable-next-line
		syncData: function(self, sessionData) {
			// das mit dem Passwort steht hier: https://stackoverflow.com/questions/43842793/basic-authentication-with-fetch
			// var username = ''
			if (localStorage.user) {
				// username = localStorage.user
			} else {
				this.nav2Set();
			}
		},
		updateOnlineStatus(e) {
			const { type } = e;
			this.onLine = type === "online";
		}
	}
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
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
