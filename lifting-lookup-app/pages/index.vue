<template>
  <div>
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
        <div v-if="lastUpdated">Last updated {{ lastUpdated }} UTC</div>
      </v-col>
    </v-row>
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
      const res = (
        await this.$axios.get("/lifter", {
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
        })
      ).data.body;
      const data = JSON.parse(res);
      this.lifters = data.lifters
      this.lastUpdated = data.last_updated
    } catch (e) {
      console.log(e);
      this.$toast.error("Error loading lifters");
    } finally {
      this.loading = false;
    }
  },
};
</script>
