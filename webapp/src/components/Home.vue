<template>
	<v-card max-width="600" class="mx-auto">
		<v-toolbar color="light-blue" dark>
			<v-app-bar-nav-icon @click="nav2Set()"></v-app-bar-nav-icon>

			<v-toolbar-title>{{ $t('main_title') }}</v-toolbar-title>

			<v-spacer></v-spacer>

			<v-btn icon>
				<v-icon>mdi-plus-circle</v-icon>
			</v-btn>
		</v-toolbar>

		<v-list two-line subheader>
			<v-subheader inset>{{ $t('main_templates') }}</v-subheader>

			<v-list-item v-for="item in movie_info_list.templates" :key="item.id" @click="nav2Play(item.id)">
				<v-list-item-avatar>
					<v-icon :class="[item.iconClass]" v-text="item.icon"></v-icon>
				</v-list-item-avatar>

				<v-list-item-content>
					<v-list-item-title v-text="item.movie_info.title +' • '+ item.movie_info.category"></v-list-item-title>
					<v-list-item-subtitle
						v-text="item.movie_info.source +' • '+ item.movie_info.date +' • '+ item.movie_info.duration +' • '+ item.movie_info.viewed"
					></v-list-item-subtitle>
				</v-list-item-content>

				<v-list-item-action>
					<v-btn icon @click="nav2Edit(item.id)">
						<v-icon color="grey lighten-1">mdi-pencil</v-icon>
					</v-btn>
				</v-list-item-action>
			</v-list-item>

			<v-subheader inset>{{ $t('main_streams') }}</v-subheader>
			<v-list-item v-for="item in movie_info_list.streams" :key="item.id" @click="nav2Play(item.id)">
				<v-list-item-avatar>
					<v-icon :class="[item.iconClass]" v-text="item.icon"></v-icon>
				</v-list-item-avatar>

				<v-list-item-content>
					<v-list-item-title v-text="item.movie_info.title +' • '+ item.movie_info.category"></v-list-item-title>
					<v-list-item-subtitle
						v-text="item.movie_info.source +' • '+ item.movie_info.date +' • '+ item.movie_info.duration +' • '+ item.movie_info.viewed"
					></v-list-item-subtitle>
				</v-list-item-content>

				<v-list-item-action>
					<v-btn icon @click="nav2Edit(item.id)">
						<v-icon color="grey lighten-1">mdi-pencil</v-icon>
					</v-btn>
				</v-list-item-action>
			</v-list-item>

			<v-subheader inset>{{ $t('main_records') }}</v-subheader>
			<v-list-item v-for="item in movie_info_list.records" :key="item.id" @click="nav2Play(item.id)">
				<v-list-item-avatar>
					<v-icon :class="[item.iconClass]" v-text="item.icon"></v-icon>
				</v-list-item-avatar>

				<v-list-item-content>
					<v-list-item-title v-text="item.movie_info.title +' • '+ item.movie_info.category"></v-list-item-title>
					<v-list-item-subtitle
						v-text="item.movie_info.source +' • '+ item.movie_info.date +' • '+ item.movie_info.duration +' • '+ item.movie_info.viewed"
					></v-list-item-subtitle>
				</v-list-item-content>

				<v-list-item-action>
					<v-btn icon @click="nav2Edit(item.id)">
						<v-icon color="grey lighten-1">mdi-pencil</v-icon>
					</v-btn>
				</v-list-item-action>
			</v-list-item>
			<v-subheader inset>{{ $t('main_timers') }}</v-subheader>
			<v-list-item v-for="item in movie_info_list.timers" :key="item.id" @click="nav2Play(item.id)">
				<v-list-item-avatar>
					<v-icon :class="[item.iconClass]" v-text="item.icon"></v-icon>
				</v-list-item-avatar>

				<v-list-item-content>
					<v-list-item-title v-text="item.movie_info.title +' • '+ item.movie_info.category"></v-list-item-title>
					<v-list-item-subtitle
						v-text="item.movie_info.source +' • '+ item.movie_info.date +' • '+ item.movie_info.duration +' • '+ item.movie_info.viewed"
					></v-list-item-subtitle>
				</v-list-item-content>

				<v-list-item-action>
					<v-btn icon @click="nav2Edit(item.id)">
						<v-icon color="grey lighten-1">mdi-pencil</v-icon>
					</v-btn>
					<v-btn icon @click="share(item.id)">
						<v-icon color="grey lighten-1">mdi-share-variant</v-icon>
					</v-btn>
				</v-list-item-action>
			</v-list-item>
		</v-list>
	</v-card>
</template>


<script>
import router from "../router";
import messenger from "../messenger";
export default {
	name: "Schnipsl",
	title() {
		return `${this.name}`;
	},
	data() {
		return {
			movie_info_list: {
				templates: [
					{
						id: "1",
						icon: "mdi-magnify",
						iconClass: "red lighten-1 white--text",
						movie_info: {
							title: "Titel",
							category: "Typ",
							source: "Quelle",
							date: "Datum",
							duration: "Dauer",
							viewed: "geschaut"
						}
					},
					{
						id: "2",
						icon: "mdi-magnify",
						iconClass: "red lighten-1 white--text",
						movie_info: {
							title: "Titel-2",
							category: "Typ",
							source: "Quelle",
							date: "Datum",
							duration: "Dauer",
							viewed: "geschaut"
						}
					}
				],
				records: [
					{
						id: "3",
						icon: "mdi-play-pause",
						iconClass: "blue white--text",
						movie_info: {
							title: "Titel-Stream",
							category: "Typ",
							source: "Quelle",
							date: "Datum",
							duration: "Dauer",
							viewed: "geschaut"
						}
					}
				],
				streams: [
					{
						id: "4",
						icon: "mdi-radio-tower",
						iconClass: "green lighten-1 white--text",
						movie_info: {
							title: "Titel-Stream",
							category: "Typ",
							source: "Quelle",
							date: "Datum",
							duration: "Dauer",
							viewed: "geschaut"
						}
					}
				],
				timers: [
					{
						id: "5",
						icon: "mdi-clock",
						iconClass: "amber white--text",
						movie_info: {
							title: "Titel-Timer",
							category: "Typ",
							source: "Quelle",
							date: "Datum",
							duration: "Dauer",
							viewed: "geschaut"
						}
					}
				]
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
		nav2Play(itemId) {
			console.log("click for Play", itemId);
			messenger.emit("home_play_request", { itemId: itemId });
		},
		share(itemId) {
			console.log("click for share", itemId);
		},
		messenger_onMessage(type, data) {
			console.log("incoming message to home", type, data);
			if (type == "home_movie_info_list") {
				this.movie_info_list = data;
			}
			if (type == "home_movie_info_update") {
				var id = data.id;
				this.movie_info_list.records.forEach(function(movie_info) {
					if (movie_info.id == id) {
						//replace movie_info
						console.log("home_movie_info_update records");
						movie_info.movie_info = data.movie_info.movie_info;
					}
				});
				this.movie_info_list.streams.forEach(function(movie_info) {
					if (movie_info.id == id) {
						//replace movie_info
						console.log("home_movie_info_update streams");
						movie_info.movie_info = data.movie_info.movie_info;
					}
				});
				this.movie_info_list.templates.forEach(function(movie_info) {
					if (movie_info.id == id) {
						//replace movie_info
						console.log("home_movie_info_update templates");
						movie_info.movie_info = data.movie_info.movie_info;
					}
				});
				this.movie_info_list.timers.forEach(function(movie_info) {
					if (movie_info.id == id) {
						//replace movie_info
						console.log("home_movie_info_update timers");
						movie_info.movie_info = data.movie_info.movie_info;
					}
				});

				this.movie_info_list[data.id] = data;
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
