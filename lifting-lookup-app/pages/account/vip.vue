<template>
  <div>
    <v-card variant="outlined">
      <v-card-title>VIP Lifter Notifications</v-card-title>
      <v-card-text>
        Create a list of lifters and get notified when they sign up for a meet.
        <br />
        You can also choose to get notified when a lifter gets removed from the
        roster of a meet. This removal notification will only happen if the meet
        is upcoming.

        <v-row
          v-for="lifter in lifters"
          :key="lifter.id"
          no-gutters
          class="my-5"
        >
          <v-col cols="12" md="6" class="d-flex align-center">
            <v-text-field
              v-model="lifter.lifter_name"
              label="Lifter Name"
              hide-details
              variant="outlined"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="6" class="d-flex align-center">
            <v-checkbox
              v-model="lifter.notify_on_signup"
              label="Notify on sign up"
              hide-details
            ></v-checkbox>
            <v-checkbox
              v-model="lifter.notify_on_removal"
              label="Notify on removal"
              hide-details
            ></v-checkbox>
            <v-btn @click="removeLifter(lifter)" icon="mdi-delete"></v-btn>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <v-btn @click="addLifter" icon="mdi-plus"></v-btn>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions class="d-flex justify-center">
        <v-btn @click="saveChanges">Save</v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import { v4 as uuidv4 } from "uuid";
export default {
  data() {
    return {
      lifters: [],
      user: null,
    };
  },
  created() {
    if (this.lifters.length === 0) {
      this.addLifter();
    }
  },
  methods: {
    addLifter() {
      this.lifters.push({
        id: uuidv4(),
        lifter_name: null,
        notify_on_signup: true,
        notify_on_removal: false,
      });
    },
    removeLifter(lifter) {
      this.lifters = this.lifters.filter((l) => l.id !== lifter.id);
    },
    saveChanges() {},
  },
};
</script>
