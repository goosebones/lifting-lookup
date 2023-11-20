<template>
  <v-card variant="outlined">
    <v-data-table
      :headers="headers"
      :items="lifters"
      :search="search"
      item-value="lifter_id"
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
  },
  data() {
    return {
      headers: [
        {
          title: "Lifter",
          key: "lifter_name",
        },
        {
          title: "Meet",
          key: "meet_name",
        },
        {
          title: "Meet Date",
          key: "meet_date",
        },
        {
          title: "Link",
          key: "liftingcast_link",
        },
      ],
    };
  },
};
</script>
