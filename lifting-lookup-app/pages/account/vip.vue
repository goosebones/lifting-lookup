<template>
  <div>
    <v-card variant="outlined" :disabled="fetchInProgress || saveInProgress">
      <v-card-title>VIP Lifter Notifications</v-card-title>
      <v-card-text>
        Create a list of lifters and get notified when they sign up for a meet.
        <br />
        You can also choose to get notified when a lifter gets removed from the
        roster of a meet. This removal notification will only happen if the meet
        is upcoming.
        <v-row>
          <v-col cols="12" class="d-flex justify-space-between align-end">
            <div
              class="text-h6"
              :class="isAtOrAboveSubscriptionCountLimit ? 'text-red' : ''"
            >
              Lifter limit:
              {{ this.lifters.length }} /
              {{ this.subscriptionCountLimit }}
            </div>
            <v-btn
              @click="fetchLifters"
              :disabled="saveInProgress"
              :loading="fetchInProgress"
            >
              Revert Changes
            </v-btn>
          </v-col>
        </v-row>
        <v-row
          v-for="lifter in lifters"
          :key="lifter.id"
          no-gutters
          class="my-5"
        >
          <v-col cols="10">
            <v-text-field
              v-model="lifter.lifter_name"
              label="Lifter Name"
              hide-details
              variant="outlined"
            ></v-text-field>
          </v-col>
          <v-col cols="2" class="d-flex justify-center">
            <v-btn
              class="ml-2"
              @click="removeLifter(lifter)"
              icon="mdi-delete"
            ></v-btn>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <v-btn
              @click="addLifter"
              icon="mdi-plus"
              :disabled="isAtOrAboveSubscriptionCountLimit"
            ></v-btn>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions class="d-flex justify-center">
        <v-btn
          @click="saveChanges"
          :disabled="fetchInProgress || isAboveSubscriptionCountLimit"
          :loading="saveInProgress"
          variant="outlined"
        >
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import { v4 as uuidv4 } from "uuid";
import { generateClient } from "aws-amplify/api";
import { listVIPLifterSubscriptions } from "~/src/graphql/queries";
import {
  createVIPLifterSubscription,
  updateVIPLifterSubscription,
} from "~/src/graphql/mutations";

export default {
  props: {
    userInfo: {
      type: Object,
      required: true,
    },
  },
  setup() {
    const apiClient = generateClient();
    return {
      apiClient,
    };
  },
  data() {
    return {
      lifters: [],
      user: null,
      fetchInProgress: false,
      saveInProgress: false,
      existingRecordId: null,
      subscriptionCountLimit: 25,
    };
  },
  computed: {
    isAtOrAboveSubscriptionCountLimit() {
      return this.lifters.length >= this.subscriptionCountLimit;
    },
    isAboveSubscriptionCountLimit() {
      return this.lifters.length > this.subscriptionCountLimit;
    },
  },
  async created() {
    await this.fetchLifters();
  },
  methods: {
    async fetchLifters() {
      try {
        this.fetchInProgress = true;
        const res = await this.apiClient.graphql({
          query: listVIPLifterSubscriptions,
        });
        if (!res.data.listVIPLifterSubscriptions.items.length) {
          this.existingRecordId = null;
          return this.lifters;
        }
        const existingRecord = res.data.listVIPLifterSubscriptions.items[0];
        const lifters = existingRecord.subscription_list;
        this.lifters = lifters.map((l) => {
          return {
            id: uuidv4(),
            lifter_name: l,
          };
        });
        this.existingRecordId = existingRecord.id;
        return this.lifters;
      } finally {
        if (this.lifters.length == 0) this.addLifter();
        this.fetchInProgress = false;
      }
    },
    async saveChanges() {
      if (this.isAboveSubscriptionCountLimit) {
        this.$toast.error("You have exceeded lifter limit");
      }
      try {
        this.saveInProgress = true;
        const res = await this.apiClient.graphql({
          query: !!this.existingRecordId
            ? updateVIPLifterSubscription
            : createVIPLifterSubscription,
          variables: {
            input: {
              subscriber_email: this.userInfo.signInDetails.loginId,
              subscription_list: this.lifters.map((l) => l.lifter_name),
              owner: this.userInfo.userId,
              ...(!!this.existingRecordId && { id: this.existingRecordId }),
            },
          },
        });
        await this.fetchLifters();
      } finally {
        this.saveInProgress = false;
      }
    },
    addLifter() {
      if (this.lifters.length == this.subscriptionCountLimit) {
        this.$toast.error(
          `${this.subscriptionCountLimit} lifter limit reached`
        );
        return;
      }
      this.lifters.push({
        id: uuidv4(),
        lifter_name: null,
      });
    },
    removeLifter(lifter) {
      this.lifters = this.lifters.filter((l) => l.id !== lifter.id);
    },
  },
};
</script>
