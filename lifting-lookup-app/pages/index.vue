<template>
  <div>
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-model.trim="userSearch"
            variant="outlined"
            hide-details
            label="Search for a name or meet"
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <LifterTable :lifters="lifters" :search="userSearch"></LifterTable>
        </v-col>
      </v-row>
      <v-btn @click="fetch_lifters">lifters</v-btn>
    </v-container>
  </div>
</template>

<script>
export default {
  data() {
    return {
      userSearch: null,
      lifters: [
        {
          lifter_name: "Gunther Kroth",
          lifter_id: "djfkdjf",
          meet_name: "Collegiate Nationals",
          meet_date: "4/14/23",
          meet_id: "djkfjdfk",
        },
      ],
    };
  },
  // computed: {
  //   displayedLifters() {
  //     if (!this.userSearch) return this.lifters;
  //     return this.lifters.filter((lifter) => {
  //       return Object.values(lifter).some((value) => {
  //         return value.toLowerCase().includes(this.userSearch.toLowerCase());
  //       });
  //     });
  //   },
  // },
  methods: {
    async fetch_lifters() {
      const res = await this.$axios.get("/lifters");
      const lifters = JSON.parse(res.data);
      this.lifters = lifters;
    },
  },
};
</script>
