<template>
	<!-- Grid card layout für die gefundenen Einträge? Kuckst Du hier https://codepen.io/munieru_jp/pen/jpdJNV-->

	<v-card max-width="600" class="mx-auto">
		<v-toolbar color="yellow">
			<v-toolbar-items>
				<v-btn icon @click="edit_delete_dialog_show = true">
					<v-icon>mdi-delete</v-icon>
				</v-btn>
				<v-divider vertical></v-divider>
				<v-spacer></v-spacer>
			</v-toolbar-items>
		</v-toolbar>
		{{ $t("edit_select_header") }}
		<v-col cols="12">
			<v-form ref="edit_select">
				<v-text-field
					v-model="query.name"
					:label="$t('edit_select_name')"
				></v-text-field>
				<v-autocomplete
					v-model="query.source_values"
					:items="query.source_items"
					outlined
					chips
					small-chips
					:label="$t('edit_select_source')"
					multiple
					@input="edit_query_available_providers()"
				></v-autocomplete>
				<v-autocomplete
					v-model="query.provider_values"
					:items="query.provider_items"
					outlined
					chips
					small-chips
					:label="$t('edit_select_provider')"
					multiple
					@input="edit_query_available_categories()"
				></v-autocomplete>
				<v-autocomplete
					v-model="query.category_values"
					:items="query.category_items"
					outlined
					chips
					small-chips
					:label="$t('edit_select_category')"
					multiple
				></v-autocomplete>
				<v-text-field
					v-model="query.title"
					:label="$t('edit_select_title')"
				></v-text-field>
				<v-text-field
					v-model="query.description"
					:label="$t('edit_select_description')"
				></v-text-field>
			</v-form>
			<v-row>
			<v-btn icon @click="edit_query_available_movies(prev_page)" :disabled="this.prev_page<0">
				<v-icon>mdi-chevron-left</v-icon>
			</v-btn>
			<v-spacer></v-spacer>
			<v-btn icon @click="edit_query_available_movies(0)">
				<v-icon>mdi-magnify</v-icon>
			</v-btn>
			<v-spacer></v-spacer>
			<v-btn icon @click="edit_query_available_movies(next_page)" :disabled="this.next_page<0">
				<v-icon>mdi-chevron-right</v-icon>
			</v-btn>
			</v-row>
		</v-col>
		<v-divider></v-divider>
		<v-list>
			<v-list-item v-for="movie_info in movie_info_list" :key="movie_info.uri">
				<!-- 			
				<v-card class="mx-auto" max-width="344">
					<v-card-title @click="requestPlay(movie_info.uri)">{{movie_info.title +' • '+ movie_info.category}}</v-card-title>

					<v-card-subtitle>{{movie_info.provider +' • '+ movie_info.timestamp +' • '+ movie_info.duration +' • '+ movie_info.current_time}}</v-card-subtitle>

					<v-card-actions>
						<v-btn icon class="mx-4">
							<v-icon size="24px">mdi-record</v-icon>
						</v-btn>

						<v-spacer></v-spacer>

						<v-btn icon @click="movie_info.description_show = !movie_info.description_show">
							<v-icon>{{ movie_info.description_show ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
						</v-btn>
					</v-card-actions>

					<v-expand-transition>
						<div v-show="movie_info.description_show">
							<v-divider></v-divider>

							<v-card-text>{{movie_info.description}}</v-card-text>
						</div>
					</v-expand-transition>
				</v-card>
 -->

				<!-- 				<v-list-item-avatar>
					<v-icon :class="[item.iconClass]" v-text="item.icon"></v-icon>
				</v-list-item-avatar>
 -->
				<v-list-item-content @click="requestPlay(movie_info.uri)">
					<v-list-item-title
						v-text="movie_info.title + ' • ' + movie_info.category"
					></v-list-item-title>
					<v-list-item-subtitle
						v-text="
							movie_info.provider +
							' • ' +
							localDate(movie_info.timestamp, $t('locale_date_format')) +
							' • ' +
							duration(movie_info.duration)
						"
					></v-list-item-subtitle>
					<v-expand-transition>
						<div v-show="movie_info.description_show">
							<v-divider></v-divider>

							<v-card-text>{{ movie_info.description }}</v-card-text>
						</div>
					</v-expand-transition>
				</v-list-item-content>

				<v-list-item-action>
					<v-btn icon class="mx-4" @click="requestPlayAdd(movie_info.uri)">
						<v-icon size="24px">mdi-video-plus</v-icon>
					</v-btn>
					<v-btn icon class="mx-4">
						<v-icon size="24px">mdi-record</v-icon>
					</v-btn>
					<v-btn
						icon
						@click="movie_info.description_show = !movie_info.description_show"
					>
						<v-icon>{{
							movie_info.description_show
								? "mdi-chevron-up"
								: "mdi-chevron-down"
						}}</v-icon>
					</v-btn>
				</v-list-item-action>
			</v-list-item>
		</v-list>
		<v-row justify="center">
			<v-dialog v-model="edit_delete_dialog_show" scrollable max-width="300px">
				<v-card>
					<v-card-title>{{ $t("edit_delete_dialog_header") }}</v-card-title>
					<v-divider></v-divider>
					<!-- 						<v-card-text style="height: 300px;">

						</v-card-text>
						<v-divider></v-divider>
 -->
					<v-card-actions>
						<v-btn
							color="blue darken-1"
							text
							@click="edit_delete_dialog_show = false"
							>{{ $t("edit_delete_dialog_cancel") }}</v-btn
						>
						<v-btn color="blue darken-1" text @click="edit_delete()">{{
							$t("edit_delete_dialog_select")
						}}</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>
		</v-row>
	</v-card>
</template>

<script>
import router from "../router";
import messenger from "../messenger";
import moment from "moment";

export default {
	name: "Edit",
	data: () => ({
		edit_delete_dialog_show: false,
		uuid: 0,
		query: {},
		movie_info_list: [],
		prev_page: -1,
		query_start_page: 0,
		next_page: -1,
	}),
	computed: {
		onsides: function () {
			return "43 ?!";
		},
	},
	created() {
		try {
			messenger.register("edit", this.messenger_onMessage, null, null);
			this.uuid = this.$route.params.uuid;
			if (this.$route.params.query) {
				this.query = this.$route.params.query;
				if (this.query.name !== "") {
					this.edit_query_available_movies(this.query_start_page);
				}
			} else {
				this.query = {
					name: "",
					source_items: [],
					source_values: [],
					provider_items: [],
					provider_values: [],
					category_items: [],
					category_values: [],
					title: "",
					description: "",
				};
			}
			this.edit_query_available_sources();
			// if we edit a quick search, identified by a name given, we instandly do a search

			console.log("Edit loaded");
		} catch (error) {
			console.log("Edit exception", error);
			this.nav2Main();
		}
	},
	methods: {
		nav2Main() {
			router.push({ name: "Home" }); // always goes 'back enough' to Main
		},
		requestPlay(movie_uri) {
			console.log("requestPlay", movie_uri);
			messenger.emit("edit_play_request", {
				uuid: this.uuid,
				query: this.query,
				movie_uri: movie_uri,
			});
			this.nav2Main();
		},
		requestPlayAdd(movie_uri) {
			console.log("requestPlayAdd", movie_uri);
			messenger.emit("edit_play_add_request", {
				uuid: this.uuid,
				query: this.query,
				movie_uri: movie_uri,
			});
		},
		edit_delete() {
			console.log("requestDelete", this.uuid);
			this.edit_delete_dialog_show = false;
			messenger.emit("edit_delete_request", {
				uuid: this.uuid,
			});
			this.nav2Main();
		},
		messenger_onMessage(type, data) {
			console.log("incoming message to edit", type, data);
			if (type == "edit_query_available_sources_answer") {
				this.query.source_items = data.select_items;
				this.query.source_values = data.select_values;
				this.edit_query_available_providers();
				this.edit_query_available_categories();
			}
			if (type == "edit_query_available_providers_answer") {
				this.query.provider_items = data.select_items;
				this.query.provider_values = data.select_values;
				this.edit_query_available_categories();
			}
			if (type == "edit_query_available_categories_answer") {
				this.query.category_items = data.select_items;
				this.query.category_values = data.select_values;
			}
			if (type == "edit_query_available_movies_answer") {
				this.movie_info_list = data.movie_info_list;
				this.prev_page = data.prev_page;
				this.query_start_page = data.query_start_page;
				this.next_page = data.next_page;
			}
		},
		edit_query_available_sources() {
			console.log("edit_query_available_sources");
			messenger.emit("edit_query_available_sources", {
				select_source_values: this.query.source_values,
			});
		},
		edit_query_available_providers() {
			console.log("edit_query_available_providers");
			messenger.emit("edit_query_available_providers", {
				select_source_values: this.query.source_values,
				select_provider_values: this.query.provider_values,
			});
		},
		edit_query_available_categories() {
			console.log("edit_query_available_categories");
			messenger.emit("edit_query_available_categories", {
				select_source_values: this.query.source_values,
				select_provider_values: this.query.provider_values,
				select_category_values: this.query.category_values,
			});
		},
		edit_query_available_movies(query_start_page) {
			console.log("edit_query_available_movies");
			messenger.emit("edit_query_available_movies", {
				select_source_values: this.query.source_values,
				select_provider_values: this.query.provider_values,
				select_category_values: this.query.category_values,
				select_title: this.query.title,
				select_description: this.query.description,
				query_start_page: query_start_page
			});
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
};
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
