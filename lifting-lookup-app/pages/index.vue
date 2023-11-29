<template>
  <div>
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-model.trim="userSearch"
            variant="outlined"
            hide-details
            label="Search for a lifter or meet"
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <LifterTable
            :lifters="lifters"
            :search="userSearch"
            :loading="loading"
          ></LifterTable>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" class="text-center">
          <div>Data is refreshed every 24 hours</div>
          <div v-if="lastUpdated">Last updated {{ lastUpdated }}</div>
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
      lifters: [],
      lastUpdated: null,
      loading: false,
    };
  },
  async created() {
    try {
      this.loading = true;
      const res = (await this.$axios.get("/lifter")).data.data;
      this.lifters = JSON.parse(res.lifters);
      this.lastUpdated = res.last_updated;
    } catch {
      // TODO toast
      // something went wrong
    } finally {
      this.loading = false;
    }
  },
};
</script>
