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
          <LifterTable :lifters="displayedLifters"></LifterTable>
        </v-col>
      </v-row>
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
          name: "Gunther Kroth",
          meet: "Collegiate Nationals",
          meet_date: "4/14/23",
          liftingcast_link:
            "https://liftingcast.com/meets/meu6667bbobu/lifter/l1h32gb3jfk7/info",
        },
      ],
    };
  },
  computed: {
    displayedLifters() {
      if (!this.userSearch) return this.lifters;
      return this.lifters.filter((lifter) => {
        return Object.values(lifter).some((value) => {
          return value.toLowerCase().includes(this.userSearch.toLowerCase());
        });
      });
    },
  },
};
</script>
