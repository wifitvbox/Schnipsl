<template>
	<!-- Grid card layout für die gefundenen Einträge? Kuckst Du hier https://codepen.io/munieru_jp/pen/jpdJNV-->

	<v-card max-width="600" class="mx-auto">
		<v-toolbar color="yellow">
			<v-toolbar-items class="hidden-sm-and-down">
				<v-btn icon @click="edit_delete_dialog_show = true">
					<v-icon>mdi-delete</v-icon>
				</v-btn>

				<v-divider vertical></v-divider>
				<v-spacer></v-spacer>
			</v-toolbar-items>
		</v-toolbar>
		{{$t('edit_select_header')}}
		<v-col cols="12">
			<v-form ref="edit_select">
				<v-text-field v-model="query.name" :label="$t('edit_select_name')"></v-text-field>
				<v-autocomplete
					v-model="query.source_values"
					:items="query.source_items"
					outlined
					chips
					small-chips
					:label="$t('edit_select_source')"
					multiple
					@input="edit_query_available_sources()"
				></v-autocomplete>
				<v-autocomplete
					v-model="query.provider_values"
					:items="query.provider_items"
					outlined
					chips
					small-chips
					:label="$t('edit_select_provider')"
					multiple
					@input="edit_query_available_providers()"
				></v-autocomplete>
				<v-autocomplete
					v-model="query.category_values"
					:items="query.category_items"
					outlined
					chips
					small-chips
					:label="$t('edit_select_category')"
					multiple
					@input="edit_query_available_categories()"
				></v-autocomplete>
				<v-text-field v-model="query.title" :label="$t('edit_select_title')"></v-text-field>
				<v-text-field v-model="query.description" :label="$t('edit_select_description')"></v-text-field>
			</v-form>
			<v-btn icon @click="edit_query_available_movies()">
				<v-icon>mdi-magnify</v-icon>
			</v-btn>
		</v-col>
		<v-divider></v-divider>
		<v-list>
			<v-list-item v-for="movie_info in movie_info_list" :key="movie_info.id">
				<!--v-card class="mx-auto" max-width="344"-->
				<v-card class="mx-auto" max-width="344">
					<v-card-title @click="requestPlay(movie_info.id)">{{movie_info.title +' • '+ movie_info.category}}</v-card-title>

					<v-card-subtitle>{{movie_info.source +' • '+ movie_info.date +' • '+ movie_info.duration +' • '+ movie_info.viewed}}</v-card-subtitle>

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
			</v-list-item>
		</v-list>
			<v-row justify="center">
				<v-dialog v-model="edit_delete_dialog_show" scrollable max-width="300px">
					<v-card>
						<v-card-title>{{ $t('edit_delete_dialog_header') }}</v-card-title>
						<v-divider></v-divider>
						<v-card-text style="height: 300px;">

						</v-card-text>
						<v-divider></v-divider>
						<v-card-actions>
							<v-btn color="blue darken-1" text @click="edit_delete_dialog_show = false">{{ $t('edit_delete_dialog_cancel') }}</v-btn>
							<v-btn color="blue darken-1" text @click="edit_delete()">{{ $t('edit_delete_dialog_select') }}</v-btn>
						</v-card-actions>
					</v-card>
				</v-dialog>
			</v-row>
	</v-card>
</template>

<script>
import router from "../router";
import messenger from "../messenger";
export default {
	name: "Edit",
	data: () => ({
		edit_delete_dialog_show : false,
		id: 0,
		query : {
		/*
		name: "Dokumentationen",
		source_items: ["TV", "Mediathek", "Podcasts", "YouTube"],
		source_values: ["Mediathek", "TV"],
		provider_items: ["ARD", "ZDF", "ARTE", "3SAT"],
		provider_values: ["ARD", "3SAT"],
		category_items: ["Krimi", "Fantasie", "Action", "Doku"],
		category_values: ["Doku"],
		title: "37",
		description: ""
		*/
		},
		movie_info_list: [
			/*
			{
				id: "1",
				title: "Titel-A",
				category: "Typ",
				source: "Quelle",
				date: "Datum",
				duration: "Dauer",
				viewed: "geschaut"
			}
			*/
		]
	}),
	computed: {
		onsides: function() {
			return "43 ?!";
		}
	},
	created() {
		messenger.register("edit", this.messenger_onMessage, null, null);
		this.id = this.$route.params.id;
		if (this.$route.params.query){
			this.query=this.$route.params.query
		}else{
			this.query={
				name: "",
				source_items: [],
				source_values: [],
				provider_items: [],
				provider_values: [],
				category_items: [],
				category_values: [],
				title: "",
				description: ""
			}
		}
		this.edit_query_available_sources()
		this.edit_query_available_providers()
		this.edit_query_available_categories()
		
		try {
			console.log("Edit loaded");
		} catch (error) {
			this.nav2Main();
		}
	},
	methods: {
		nav2Main() {
			router.push({ name: "Home" }); // always goes 'back enough' to Main
		},
		requestPlay(movie_info_id) {
			console.log("requestPlay",movie_info_id)
			messenger.emit("edit_play_request", {
				edit_id: this.id,
				query: this.query,
				movie_info_id: movie_info_id
			})
			this.nav2Main();
		},
		edit_delete() {
			console.log("requestDelete", this.id)
			this.edit_delete_dialog_show=false
			messenger.emit("edit_delete_request", {
				edit_id: this.id,
			})
			this.nav2Main();
		},
		messenger_onMessage(type, data) {
			console.log("incoming message to edit", type, data);
			if (type == "edit_query_available_sources_answer") {
				this.query.source_items = data.select_items;
				this.query.source_values = data.select_values;
				this.edit_query_available_providers()
				this.edit_query_available_categories()
			}
			if (type == "edit_query_available_providers_answer") {
				this.query.provider_items = data.select_items;
				this.query.provider_values = data.select_values;
				this.edit_query_available_categories()
			}
			if (type == "edit_query_available_categories_answer") {
				this.query.category_items = data.select_items;
				this.query.category_values = data.select_values;
			}
			if (type == "edit_query_available_movies_answer") {
				this.movie_info_list = data;
			}
		},
		edit_query_available_sources() {
			console.log("edit_query_available_sources");
			messenger.emit("edit_query_available_sources", {
				select_source_values: this.query.source_values
			});
		},
		edit_query_available_providers() {
			console.log("edit_query_available_providers");
			messenger.emit("edit_query_available_providers", {
				select_source_values: this.query.source_values,
				select_provider_values: this.query.provider_values
			});
		},
		edit_query_available_categories() {
			console.log("edit_query_available_categories");
			messenger.emit("edit_query_available_categories", {
				select_source_values: this.query.source_values,
				select_provider_values: this.query.provider_values,
				select_category_values: this.query.category_values
			});
		},
		edit_query_available_movies() {
			console.log("edit_query_available_movies");
			messenger.emit("edit_query_available_movies", {
				select_source_values: this.query.source_values,
				select_provider_values: this.query.provider_values,
				select_category_values: this.query.category_values,
				select_title: this.query.title,
				select_description: this.query.description
			});
		}
	}
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
