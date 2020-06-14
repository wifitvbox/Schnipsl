<template>
	<!-- Grid card layout für die gefundenen Einträge? Kuckst Du hier https://codepen.io/munieru_jp/pen/jpdJNV-->

	<v-card max-width="600" class="mx-auto">
		<v-toolbar color="yellow">
			<v-toolbar-items class="hidden-sm-and-down">
				<v-btn icon>
					<v-icon>mdi-delete</v-icon>
				</v-btn>

				<v-divider vertical></v-divider>
				<v-spacer></v-spacer>
			</v-toolbar-items>
		</v-toolbar>
		{{$t('edit_select_header')}}
		<v-col cols="12">
			<v-form ref="edit_select">
				<v-text-field v-model="select_name" :label="$t('edit_select_name')"></v-text-field>
				<v-autocomplete
					v-model="select_source_values"
					:items="select_source_items"
					outlined
					chips
					small-chips
					:label="$t('edit_select_source')"
					multiple
					@input="edit_query_available_sources()"
				></v-autocomplete>
				<v-autocomplete
					v-model="select_provider_values"
					:items="select_provider_items"
					outlined
					chips
					small-chips
					:label="$t('edit_select_provider')"
					multiple
					@input="edit_query_available_providers()"
				></v-autocomplete>
				<v-autocomplete
					v-model="select_category_values"
					:items="select_category_items"
					outlined
					chips
					small-chips
					:label="$t('edit_select_category')"
					multiple
					@input="edit_query_available_categories()"
				></v-autocomplete>
				<v-text-field v-model="select_title" :label="$t('edit_select_title')"></v-text-field>
				<v-text-field v-model="select_description" :label="$t('edit_select_description')"></v-text-field>
			</v-form>
			<v-btn icon @click="edit_query_available_movies()">
				<v-icon>mdi-magnify</v-icon>
			</v-btn>
		</v-col>
		<v-divider></v-divider>
		<v-list>
			<v-list-item v-for="movie_info in movie_info_list" :key="movie_info.id" @click="nav2Play(movie_info.id)">
				<!--v-card class="mx-auto" max-width="344"-->
				<v-card class="mx-auto" max-width="344">
					<v-card-title>{{movie_info.title +' • '+ movie_info.category}}</v-card-title>

					<v-card-subtitle>{{movie_info.source +' • '+ movie_info.date +' • '+ movie_info.duration +' • '+ movie_info.viewed}}</v-card-subtitle>

					<v-card-actions>
						<v-btn icon class="mx-4">
							<v-icon size="24px">mdi-record</v-icon>
						</v-btn>

						<v-spacer></v-spacer>

						<v-btn icon @click="movie_info.description_show = !movie_info.description_show">
							<v-icon>{{ show ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
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
	</v-card>
</template>

<script>
import router from "../router";
import messenger from "../messenger";
export default {
	name: "Edit",
	data: () => ({
		id: 0,
		select_name: "Dokumentationen",
		select_source_items: ["TV", "Mediathek", "Podcasts", "YouTube"],
		select_source_values: ["Mediathek", "TV"],
		select_provider_items: ["ARD", "ZDF", "ARTE", "3SAT"],
		select_provider_values: ["ARD", "3SAT"],
		select_category_items: ["Krimi", "Fantasie", "Action", "Doku"],
		select_category_values: ["Doku"],
		value: null,
		select_title: "37",
		select_description: "",
		show: false,
		movie_info_list: [
			{
				id: "1",
				title: "Titel-A",
				category: "Typ",
				source: "Quelle",
				date: "Datum",
				duration: "Dauer",
				viewed: "geschaut"
			},
			{
				id: "2",

				title: "Titel-2",
				category: "Typ",
				source: "Quelle",
				date: "Datum",
				duration: "Dauer",
				viewed: "geschaut"
			}
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
		// first we fill a lookup to see which users are actual already selected
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
		nav2Play() {
			console.log("nav2Play");
		},
		messenger_onMessage(type, data) {
			console.log("incoming message to edit", type, data);
			if (type == "edit_query_available_sources_answer") {
				this.select_source_items = data.select_items;
				this.select_source_values = data.select_values;
			}
			if (type == "edit_query_available_providers_answer") {
				this.select_provider_items = data.select_items;
				this.select_provider_values = data.select_values;
			}
			if (type == "edit_query_available_categories_answer") {
				this.select_category_items = data.select_items;
				this.select_category_values = data.select_values;
			}
			if (type == "edit_query_available_movies_answer") {
				this.movie_info_list = data;
			}
		},
		edit_query_available_sources() {
			console.log("edit_query_available_sources");
			messenger.emit("edit_query_available_sources", {
				select_source_values: this.select_source_values
			});
		},
		edit_query_available_providers() {
			console.log("edit_query_available_providers");
			messenger.emit("edit_query_available_providers", {
				select_source_values: this.select_source_values,
				select_provider_values: this.select_provider_values
			});
		},
		edit_query_available_categories() {
			console.log("edit_query_available_categories");
			messenger.emit("edit_query_available_categories", {
				select_source_values: this.select_source_values,
				select_provider_values: this.select_provider_values,
				select_category_values: this.select_category_values
			});
		},
		edit_query_available_movies() {
			console.log("edit_query_available_movies");
			messenger.emit("edit_query_available_movies", {
				select_source_values: this.select_source_values,
				select_provider_values: this.select_provider_values,
				select_category_values: this.select_category_values,
				select_title: this.select_title,
				select_description: this.select_description
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
