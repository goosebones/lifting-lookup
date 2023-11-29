<template>
  <v-card variant="outlined">
    <div
      v-if="loading"
      class="d-flex flex-column align-center text-center py-3"
    >
      <v-progress-circular :size="100" indeterminate></v-progress-circular>
      <div class="pa-3 text-h6">Loading lifters...</div>
    </div>
    <v-data-table
      v-else-if="lifters.length"
      :headers="headers"
      :items="lifters"
      :search="search"
      item-value="lifter_id"
      :items-per-page-options="[
        { value: 25, title: '25' },
        { value: 50, title: '50' },
        { value: 100, title: '100' },
        { value: 250, title: '250' },
      ]"
      items-per-page="25"
    >
      <template v-slot:item.liftingcast_link="{ item: lifter }">
        <NuxtLink
          :to="`https://liftingcast.com/meets/${lifter.meet_id}/lifter/${lifter.lifter_id}/info`"
          target="_blank"
        >
          Details
        </NuxtLink>
      </template>
    </v-data-table>
    <div v-else class="d-flex flex-column align-center py-3 text-h6">
      No lifters to display
    </div>
  </v-card>
</template>

<script>
export default {
  props: {
    lifters: {
      type: Array,
      required: true,
    },
    search: {
      type: String,
      default: null,
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      headers: [
        {
          title: "Lifter",
          key: "lifter_name",
          sortable: false,
        },
        {
          title: "Meet",
          key: "meet_name",
          sortable: false,
        },
        {
          title: "Meet Date",
          key: "meet_date",
          sortable: false,
        },
        {
          title: "Link",
          key: "liftingcast_link",
          sortable: false,
        },
      ],
    };
  },
};
</script>

<style>
.v-card {
  overflow-x: hidden;
}
</style>
