<template>
	<v-card max-width="600" class="mx-auto">
		<v-toolbar color="light-blue" dark>
			<v-app-bar-nav-icon @click="nav2Set()"></v-app-bar-nav-icon>

			<v-toolbar-title>{{ $t('main_title') }}</v-toolbar-title>

			<v-spacer></v-spacer>

			<v-btn icon @click="nav2Edit(0,null)">
				<v-icon>mdi-plus-circle</v-icon>
			</v-btn>
		</v-toolbar>

		<v-list two-line subheader>
			<v-subheader inset>{{ $t('main_templates') }}</v-subheader>

			<v-list-item v-for="item in movie_list.templates" :key="item.uuid">
				<v-list-item-avatar>
					<v-icon :class="[item.iconClass]" v-text="item.icon"></v-icon>
				</v-list-item-avatar>

				<v-list-item-content @click="nav2Edit(item.uuid,item.query)">
					<v-list-item-title v-text="item.movie_info.title"></v-list-item-title>
				</v-list-item-content>

				<v-list-item-action>
					<v-btn icon @click="share(item.uuid)">
						<v-icon color="grey lighten-1">mdi-share-variant</v-icon>
					</v-btn>
				</v-list-item-action>
			</v-list-item>
			<v-subheader inset>{{ $t('main_streams') }}</v-subheader>
			<v-list-item v-for="item in movie_list.streams" :key="item.uuid">
				<v-list-item-avatar>
					<v-icon :class="[item.iconClass]" v-text="item.icon"></v-icon>
				</v-list-item-avatar>

				<v-list-item-content @click="nav2Play(item.movie_info.uri)">
					<v-list-item-title v-text="item.movie_info.title +' • '+ localMinutes(item.current_time)"></v-list-item-title>
					<v-list-item-subtitle
						v-text="item.movie_info.provider +' • '+ localDateTime
			(item.movie_info.timestamp,$t('locale_time_format')) +' • '+ item.movie_info.category"
					></v-list-item-subtitle>
					<v-expand-transition>
						<div v-show="item.movie_info.description_show">
							<v-divider></v-divider>
							<v-card-text>{{item.movie_info.description}}</v-card-text>
						</div>
					</v-expand-transition>
				</v-list-item-content>

				<v-list-item-action>
					<v-btn icon @click="nav2Edit(item.uuid,item.query,item)">
						<v-icon color="grey lighten-1">mdi-pencil</v-icon>
					</v-btn>
					<v-btn icon @click="share(item.uuid)">
						<v-icon color="grey lighten-1">mdi-share-variant</v-icon>
					</v-btn>
					<v-btn icon @click="item.movie_info.description_show = !item.movie_info.description_show">
						<v-icon>{{ item.movie_info.description_show ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
					</v-btn>
				</v-list-item-action>
			</v-list-item>

			<v-subheader inset>{{ $t('main_records') }}</v-subheader>
			<v-list-item v-for="item in movie_list.records" :key="item.uuid">
				<v-list-item-avatar>
					<v-icon :class="[item.iconClass]" v-text="item.icon"></v-icon>
				</v-list-item-avatar>

				<v-list-item-content @click="nav2Play(item.movie_info.uri)">
					<v-list-item-title v-text="item.movie_info.title +' • '+ item.movie_info.category"></v-list-item-title>
					<v-list-item-subtitle
						v-text="item.movie_info.provider +' • '+ localDateTime
			(item.movie_info.timestamp,$t('locale_date_format')) +' • ' + duration(item.movie_info.duration) +' • '+ duration(item.current_time)"
					></v-list-item-subtitle>
					<v-expand-transition>
						<div v-show="item.movie_info.description_show">
							<v-divider></v-divider>

							<v-card-text>{{item.movie_info.description}}</v-card-text>
						</div>
					</v-expand-transition>
				</v-list-item-content>

				<v-list-item-action>
					<v-btn icon @click="nav2Edit(item.uuid,item.query)">
						<v-icon color="grey lighten-1">mdi-pencil</v-icon>
					</v-btn>
					<v-btn icon @click="share(item.uuid)">
						<v-icon color="grey lighten-1">mdi-share-variant</v-icon>
					</v-btn>
					<v-btn icon @click="item.movie_info.description_show = !item.movie_info.description_show">
						<v-icon>{{ item.movie_info.description_show ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
					</v-btn>
				</v-list-item-action>
			</v-list-item>
			<v-subheader inset>{{ $t('main_timers') }}</v-subheader>
			<v-list-item v-for="item in movie_list.timers" :key="item.uuid">
				<v-list-item-avatar>
					<v-icon :class="[item.iconClass]" v-text="item.icon"></v-icon>
				</v-list-item-avatar>

				<v-list-item-content @click="nav2Play(item.movie_info.uri)">
					<v-list-item-title v-text="item.movie_info.title +' • '+ item.movie_info.category"></v-list-item-title>
					<v-list-item-subtitle
						v-text="item.movie_info.provider +' • '+ localDateTime
			(item.movie_info.timestamp,$t('locale_date_format')) +' • '+ duration(item.movie_info.duration) +' • '+ duration(item.current_time)"
					></v-list-item-subtitle>
					<v-expand-transition>
						<div v-show="item.movie_info.description_show">
							<v-divider></v-divider>

							<v-card-text>{{item.movie_info.description}}</v-card-text>
						</div>
					</v-expand-transition>
				</v-list-item-content>

				<v-list-item-action>
					<v-btn icon @click="nav2Edit(item.uuid,item.query)">
						<v-icon color="grey lighten-1">mdi-pencil</v-icon>
					</v-btn>
					<v-btn icon @click="share(item.uuid)">
						<v-icon color="grey lighten-1">mdi-share-variant</v-icon>
					</v-btn>
					<v-btn icon @click="item.movie_info.description_show = !item.movie_info.description_show">
						<v-icon>{{ item.movie_info.description_show ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
					</v-btn>
				</v-list-item-action>
			</v-list-item>
		</v-list>
	</v-card>
</template>


<script>
import router from "../router";
import messenger from "../messenger";
import moment from 'moment';
export default {
	name: "Schnipsl",
	title() {
		return `${this.name}`;
	},
	data() {
		return {
			movie_list: {
				templates: [
					{
						uuid: "1",
						icon: "mdi-magnify",
						iconClass: "red lighten-1 white--text",
						current_time: 0,
						movie_info: {
							title: "Titel",
							category: "Typ",
							provider: "Quelle",
							timestamp: "Datum",
							duration: "Dauer",
						}
					},
					{
						uuid: "2",
						icon: "mdi-magnify",
						iconClass: "red lighten-1 white--text",
						current_time: 10,
						movie_info: {
							title: "Titel-2",
							category: "Typ",
							provider: "Quelle",
							timestamp: "Datum",
							duration: "Dauer"
						}
					}
				],
				records: [
					{
						uuid: "3",
						icon: "mdi-play-pause",
						iconClass: "blue white--text",
						current_time: 20,
						movie_info: {
							title: "Titel-Stream",
							category: "Typ",
							provider: "Quelle",
							timestamp: "Datum",
							duration: "Dauer"
						}
					}
				],
				streams: [
					{
						uuid: "4",
						icon: "mdi-radio-tower",
						iconClass: "green lighten-1 white--text",
						current_time: "geschaut",
						movie_info: {
							title: "Titel-Stream",
							category: "Typ",
							provider: "Quelle",
							timestamp: "Datum",
							duration: "Dauer"
						}
					}
				],
				timers: [
					{
						uuid: "5",
						icon: "mdi-clock",
						iconClass: "amber white--text",
						current_time: "geschaut",
						movie_info: {
							title: "Titel-Timer",
							category: "Typ",
							provider: "Quelle",
							timestamp: "Datum",
							duration: "Dauer"
						}
					}
				]
			}
		};
	},
	created() {
		messenger.register("home", this.messenger_onMessage, null, null);
		
			if (localStorage.userName) {
				var username = localStorage.userName
				messenger.init(username, "bla", "register");
			} else {
				this.nav2Set();
			}
	},
	methods: {
		nav2Set() {
			router.push({ name: "Settings" });
		},
		nav2Edit(uuid,query,item) {
			console.log("click for edit", item, query);
			router.push({ name: "Edit", params: { uuid: uuid, query: query } });
		},
		nav2Play(uri) {
			console.log("click for Play uri", uri);
			messenger.emit("home_play_request", { uri: uri });
		},
		share(uuid) {
			console.log("click for share", uuid);
		},
		messenger_onMessage(type, data) {
			console.log("incoming message to home", type, data);
			if (type == "home_movie_info_list") {
				this.movie_list = data;
			}
			if (type == "home_movie_info_update") {
				var uuid = data.uuid;
				this.movie_list.records.forEach(function(movie_list_item) {
					if (movie_list_item.uuid == uuid) {
						//replace movie_info
						console.log("home_movie_info_update records");
						movie_list_item.current_time=data.current_time
						movie_list_item.movie_info = data.movie_info;
					}
				});
				this.movie_list.streams.forEach(function(movie_list_item) {
					if (movie_list_item.uuid == uuid) {
						//replace movie_list_item
						console.log("home_movie_info_update streams");
						movie_list_item.current_time=data.current_time
						movie_list_item.movie_info = data.movie_info;
					}
				});
				this.movie_list.templates.forEach(function(movie_list_item) {
					if (movie_list_item.uuid == uuid) {
						//replace movie_list_item
						console.log("home_movie_info_update templates");
						movie_list_item.current_time=data.current_time
						movie_list_item.movie_info = data.movie_info;
					}
				});
				this.movie_list.timers.forEach(function(movie_list_item) {
					if (movie_list_item.uuid == uuid) {
						//replace movie_list_item
						console.log("home_movie_info_update timers");
						movie_list_item.current_time=data.current_time
						movie_list_item.movie_info = data.movie_info;
					}
				});

				this.movie_list[data.uuid] = data;
			}
		},
		localDateTime(timestamp, locale){
			return moment.unix(timestamp).local(true).format(locale)
		},
		duration(secondsValue){
			var seconds=parseInt(secondsValue,10) 
			if (!Number.isInteger(seconds || seconds < 0)){
				return ''
			}
			if (seconds < 3600){
				return moment.unix(seconds).format("mm:ss")
			}else{
				return moment.unix(seconds).format("HH:mm:ss")
			}
		},
		localMinutes(secondsValue){
			var seconds=parseInt(secondsValue,10) 
			if (!Number.isInteger(seconds || seconds < 0)){
				return ''
			}
			if (seconds < 3600){
				return moment.unix(seconds).format("mm [min]")
			}else{
				return moment.unix(seconds).format("HH:mm")
			}
		},
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
