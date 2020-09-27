<template>
	<v-app toolbar footer>
		<!-- Provides the application the proper gutter -->
		<v-container fluid>
			<router-view />
		</v-container>
		<v-row justify="center">
			<v-dialog v-model="device_dialog_show" scrollable max-width="300px">
				<v-card>
					<v-card-title>{{
						$t("player_select_device_dialog_header")
					}}</v-card-title>
					<v-divider></v-divider>
					<v-card-text style="height: 300px">
						<v-radio-group v-model="device_info.actual_device" column>
							<v-radio
								v-for="item in device_info.devices"
								:value="item"
								:label="item"
								:key="item"
								:checked="(item = device_info.actual_device)"
							></v-radio>
						</v-radio-group>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn
							color="blue darken-1"
							text
							@click="device_dialog_show = false"
							>{{ $t("player_select_device_dialog_cancel") }}</v-btn
						>
						<v-btn color="blue darken-1" text @click="player_select_device()">{{
							$t("player_select_device_dialog_select")
						}}</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>
		</v-row>
		<v-row justify="center">
			<v-dialog v-model="offline_dialog_show" max-width="300px">
				<v-card>
					<v-card-title>{{
						$t("main_noconnect")
					}}</v-card-title>
					<v-divider></v-divider>
					<v-card-text style="height: 75px">
						<v-progress-circular
							indeterminate
							color="primary"
						></v-progress-circular>
					</v-card-text>
				</v-card>
			</v-dialog>
		</v-row>
		<v-footer padless>
			<v-card class="mx-auto" max-width="600">
				<v-card-title
					>{{ movie_info.title }} • {{ movie_info.category }}</v-card-title
				>
				<v-card-subtitle
					>{{ movie_info.provider }} •
					{{ localDate(movie_info.timestamp, $t("locale_date_format")) }} •
					{{ duration(movie_info.duration) }} •
					{{ duration(movie_info.current_time) }}</v-card-subtitle
				>
				<v-slider
					v-model="app_player_pos.volume"
					prepend-icon="mdi-volume-low"
					append-icon="mdi-volume-high"
					@click="player_volume()"
				></v-slider>
				<v-card-actions>
					<v-btn icon class="mx-4" @click="device_dialog_show = true">
						<v-icon size="24px">mdi-television-classic</v-icon>
					</v-btn>
					<v-btn icon class="mx-4" @click="player_key('prev')">
						<v-icon size="24px">mdi-skip-previous</v-icon>
					</v-btn>
					<v-btn icon class="mx-4" @click="player_key('minus10')">
						<v-icon size="24px">mdi-rewind-10</v-icon>
					</v-btn>
					<v-btn icon class="mx-4" @click="player_key('play')">
						<v-icon>{{
							app_player_pos.play ? "mdi-pause" : "mdi-play"
						}}</v-icon>
					</v-btn>
					<v-btn icon class="mx-4" @click="player_key('plus10')">
						<v-icon size="24px">mdi-fast-forward-10</v-icon>
					</v-btn>
					<v-btn icon class="mx-4" @click="player_key('next')">
						<v-icon size="24px">mdi-skip-next</v-icon>
					</v-btn>
					<v-btn icon @click="show = !show">
						<v-icon>{{ show ? "mdi-chevron-up" : "mdi-chevron-down" }}</v-icon>
					</v-btn>
				</v-card-actions>
				{{ duration(app_player_pos.current_time) }}
				<v-slider v-model="sliderPosition" append-icon="mdi-timer"></v-slider>
				{{ duration(movie_info.duration - app_player_pos.current_time) }}
				<v-expand-transition>
					<div v-show="show">
						<v-divider></v-divider>

						<v-card-text>{{ movie_info.description }}</v-card-text>
					</div>
				</v-expand-transition>
			</v-card>
		</v-footer>
	</v-app>
</template>

<script>
import messenger from "./messenger";
import moment from "moment";
export default {
	data() {
		return {
			app_player_pos: {
				play: false,
				current_time: 55,
				duration: 120,
				volume: 3,
			},
			movie_info: {
				title: "Titel",
				category: "Typ",
				provider: "provider",
				timestamp: 123456,
				duration: 120,
				current_time: 65,
				description: "Beschreibung",
			},
			movie_uri: null,
			device_info: {
				actual_device: "",
				devices: ["TV Wohnzimmer", "TV Küche", "Chromecast Büro"],
			},
			device_dialog_show: false,
			offline_dialog_show: false,
			show: false,
		};
	},
	created() {
		messenger.register(
			"app",
			this.messenger_onMessage,
			this.messenger_onWSConnect,
			this.messenger_onWSClose
		);
	},
	methods: {
		messenger_onMessage(type, data) {
			console.log("incoming message to app", type, data);
			if (type == "app_player_pos") {
				this.app_player_pos = data;
			}
			if (type == "app_movie_info") {
				this.movie_info = data;
			}
			if (type == "app_device_info") {
				this.movie_uri = data.movie_uri;
				this.device_info.devices = data.devices;
				// force the dialog for now
				// better would be: If actual device is not in devices...
				this.device_info.actual_device = null;
				if (!this.device_info.actual_device) {
					this.device_dialog_show = true;
				}
			}
		},
		messenger_onWSConnect() {
			this.showDisconnect(false);
		},
		showDisconnect(disconnected) {
			console.log("websocket disconnect?:", disconnected);
			this.offline_dialog_show = disconnected;
		},
		messenger_onWSClose() {
			this.showDisconnect(true);
		},
		player_key(id) {
			console.log("Send key");
			messenger.emit("player_key", { keyid: id });
		},
		player_volume() {
			console.log("Send volume");
			messenger.emit("player_volume", {
				timer_vol: this.app_player_pos.volume,
			});
		},
		player_select_device() {
			console.log("Send device");
			this.device_dialog_show = false;
			if (this.device_info.actual_device != "") {
				messenger.emit("select_player_device", {
					timer_dev: this.device_info.actual_device,
					movie_uri: this.movie_uri,
				});
			}
		},
		localDate(timestamp, locale) {
			return moment.unix(timestamp).local().format(locale);
		},
		duration(secondsValue) {
			var seconds = parseInt(secondsValue, 10);
			if (!Number.isInteger(seconds || seconds < 0)) {
				return "";
			}
			if (seconds < 3600) {
				return moment.unix(seconds).format("mm:ss");
			} else {
				return moment.unix(seconds).format("HH:mm:ss");
			}
		},
	},
	computed: {
		sliderPosition: {
			// getter
			get: function () {
				if (
					this.app_player_pos.current_time >= 0 &&
					this.app_player_pos.duration > 0
				) {
					return parseInt(
						(this.app_player_pos.current_time * 100) /
							this.app_player_pos.duration
					);
				} else {
					return "-";
				}
			},
			// setter
			set: function (newValue) {
				console.log("Send timer by setter");
				this.app_player_pos.current_time = newValue;
				messenger.emit("player_time", {
					timer_pos: this.app_player_pos.current_time,
				});
			},
		},
	},
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
