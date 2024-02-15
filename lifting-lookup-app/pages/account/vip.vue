<template>
  <div>
    <v-card variant="outlined" :disabled="fetchInProgress || saveInProgress">
      <v-card-title>VIP Lifter Notifications (Beta)</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12">
            Create a list of lifters and get notified when they sign up for a
            meet.
            <br />
            <div class="font-weight-bold text-purple text-h6">
              This feature is still in beta. If you decide to use it, please be
              open to sharing any bugs or unexpected behaviors you may
              encounter.
            </div>
            <div
              @click="showDetails = !showDetails"
              class="my-1 text-decoration-underline"
            >
              {{ showDetails ? "Hide Details" : "Show Details" }}
              <v-icon size="small">{{
                showDetails
                  ? "mdi-chevron-double-up"
                  : "mdi-chevron-double-down"
              }}</v-icon>
            </div>
            <v-slide-y-transition>
              <div v-show="showDetails">
                • When a lifter signs up for a meet, you will recieve an email.
                If several of your lifters sign up for a meet, you will recieve
                one email detailing all of the signups.
                <br />
                • LiftingLookup refreshes every 24 hours - your list of lifters
                to get notified for will be checked during this refresh.
                <br />
                • Implementation notes: When checking to see if any of your
                lifters are new signups, the name of the lifter will be stripped
                of all whitespace characters, numbers, and hyphens. This is done
                to catch things like lot numbers in lifter names.
                <br />
                • Example: You choose to get notified when 'John Doe' signs up
                for a meet. If John Doe then signs up for a meet and gets
                assigned a lot number, his name will appear as '123 - John Doe'.
                LiftingLookup will convert both names to 'johndoe', a match will
                be found, and you will get a notification.
              </div>
            </v-slide-y-transition>
          </v-col>
        </v-row>

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
              variant="outlined"
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
              v-model.trim="lifter.lifter_name"
              label="Lifter Name"
              hide-details
              variant="outlined"
              :error="lifter.lifter_name == null || lifter.lifter_name == ''"
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
          :disabled="
            fetchInProgress ||
            isAboveSubscriptionCountLimit ||
            !isLiftersListValid
          "
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
      showDetails: false,
    };
  },
  computed: {
    isAtOrAboveSubscriptionCountLimit() {
      return this.lifters.length >= this.subscriptionCountLimit;
    },
    isAboveSubscriptionCountLimit() {
      return this.lifters.length > this.subscriptionCountLimit;
    },
    isLiftersListValid() {
      return this.lifters.every((l) => {
        return l.lifter_name !== null && l.lifter_name !== "";
      });
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
      } catch {
        this.$toast.error("Error initializing lifter list");
      } finally {
        if (this.lifters.length == 0) this.addLifter();
        this.fetchInProgress = false;
      }
    },
    async saveChanges() {
      if (this.isAboveSubscriptionCountLimit) {
        this.$toast.error("You have exceeded lifter limit");
        return;
      }
      if (!this.isLiftersListValid) {
        this.$toast.error("Invalid input(s)");
        return;
      }
      try {
        this.saveInProgress = true;
        const res = await this.apiClient.graphql({
          query: !!this.existingRecordId
            ? updateVIPLifterSubscription
            : createVIPLifterSubscription,
          variables: {
            input: {
              subscriber_email: this.userInfo.email,
              subscription_list: this.lifters.map((l) => l.lifter_name),
              owner: this.userInfo.sub,
              ...(!!this.existingRecordId && { id: this.existingRecordId }),
            },
          },
        });
        await this.fetchLifters();
        this.$toast.success("Save successful");
      } catch {
        this.$toast.error("Error saving changes. Please try again.");
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
