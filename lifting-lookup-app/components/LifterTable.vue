<template>
  <v-card variant="outlined">
    <v-table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Meet</th>
          <th>Date</th>
          <th>Link</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="lifter in lifters" :key="lifter.lifter_id">
          <td>{{ lifter.name }}</td>
          <td>{{ lifter.meet }}</td>
          <td>{{ lifter.meet_date }}</td>
          <td>
            <NuxtLink :to="lifter.liftingcast_link" target="_blank">
              Details
            </NuxtLink>
          </td>
        </tr>
      </tbody>
    </v-table>
  </v-card>
</template>

<script>
export default {
  props: {
    lifters: {
      type: Array,
      required: true,
    },
  },
};
</script>
