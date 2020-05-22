<template>
	<v-expansion-panels>
		<v-expansion-panel>
			<v-expansion-panel-header>{{$t('edit_select_header')}}</v-expansion-panel-header>
			<v-expansion-panel-content>
				<v-col cols="12">
					<v-form ref="edit_select">
						<v-autocomplete
							v-model="select_source_values"
							:items="select_source_items"
							outlined
							chips
							small-chips
							:label="$t('edit_select_source')"
							multiple
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
						<v-text-field v-model="select_content" :label="$t('edit_select_content')" ></v-text-field>
						<v-text-field v-model="select_name" :label="$t('edit_select_name')" ></v-text-field>
					</v-form>
				</v-col>
			</v-expansion-panel-content>
		</v-expansion-panel>
	</v-expansion-panels>
</template>

<script>
import router from "../router";
export default {
	name: "Edit",
	data() {
		return {
			id: 0,
			select_source_items: ["TV", "Mediathek", "Podcasts", "YouTube"],
			select_source_values: ["Mediathek", "TV"],
			select_provider_items: ["ARD", "ZDF", "ARTE", "3SAT"],
			select_provider_values: ["ARD", "3SAT"],
			select_categorie_items: ["Krimi", "Fantasie", "Action", "Doku"],
			select_categorie_values: ["Doku"],
			value: null,
      select_content: "Koralle",
      select_name: "Dokumentationen",
		};
	},
	computed: {
		onsides: function() {
			return "43 ?!";
		}
	},
	created() {
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
