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
				></v-autocomplete>
				<v-autocomplete
					v-model="select_categorie_values"
					:items="select_categorie_items"
					outlined
					chips
					small-chips
					:label="$t('edit_select_categorie')"
					multiple
				></v-autocomplete>
				<v-text-field v-model="select_title" :label="$t('edit_select_title')"></v-text-field>
				<v-text-field v-model="select_content" :label="$t('edit_select_content')"></v-text-field>
			</v-form>
			<v-btn icon>
				<v-icon>mdi-magnify</v-icon>
			</v-btn>
		</v-col>
		<v-divider></v-divider>
		<v-list>
			<v-list-item v-for="item in items" :key="item.title" @click="nav2Play(item.title)">
				<v-card class="mx-auto" max-width="344">

					<v-card-title>{{"item.title"}}</v-card-title>

					<v-card-subtitle>1,000 miles of wonder</v-card-subtitle>

					<v-card-actions>
						<v-btn icon class="mx-4">
							<v-icon size="24px">mdi-record</v-icon>
						</v-btn>

						<v-spacer></v-spacer>

						<v-btn icon @click="show = !show">
							<v-icon>{{ show ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
						</v-btn>
					</v-card-actions>

					<v-expand-transition>
						<div v-show="show">
							<v-divider></v-divider>

							<v-card-text>I'm a thing. But, like most politicians, he promised more than he could deliver. You won't have time for sleeping, soldier, not with all the bed making you'll be doing. Then we'll go with that data file! Hey, you add a one and two zeros to that or we walk! You're going to do his laundry? I've got to find a way to escape.</v-card-text>
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
		select_categorie_items: ["Krimi", "Fantasie", "Action", "Doku"],
		select_categorie_values: ["Doku"],
		value: null,
		select_title: "The wall",
		select_content: "Koralle",
		show: false,
		items: [
			{
				icon: "mdi-magnify",
				iconClass: "grey lighten-1 white--text",
				title: "Photos1",
				subtitle: "Jan 9, 2014"
			},
			{
				icon: "mdi-magnify",
				iconClass: "grey lighten-1 white--text",
				title: "Photos2",
				subtitle: "Jan 9, 2014"
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
			console.log("nav2Play")
		},
		messenger_onMessage(type, data) {
			console.log("incoming message to edit", type, data);
			if (type == "edit_query_available_sources_answer") {
				this.select_source_items = data.select_source_items
				this.select_source_values = data.select_source_values
			}
		},
		edit_query_available_sources() {
			console.log("edit_query_available_sources");
			messenger.emit("edit_query_available_sources", { select_source_values: this.select_source_values });
		},
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
