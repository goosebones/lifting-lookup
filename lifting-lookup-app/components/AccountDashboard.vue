<template>
  <v-row v-if="userInfo">
    <v-col cols="12"> Hello, {{ userInfo.email }} </v-col>

    <v-col cols="12" md="2">
      <v-card variant="outlined">
        <v-card-title>Navigation</v-card-title>
        <v-list>
          <v-list-item :to="'/account/vip'" nuxt>
            VIP Lifter Notifications
          </v-list-item>
          <v-list-item @click="handleSignOut"> Sign Out </v-list-item>
        </v-list>
      </v-card>
    </v-col>
    <v-col cols="12" md="10">
      <NuxtPage :user-info="userInfo"></NuxtPage>
    </v-col>
  </v-row>
</template>

<script>
import { fetchUserAttributes } from "aws-amplify/auth";

export default {
  props: {
    signOutFunction: {
      type: Function,
      required: true,
    },
  },
  data() {
    return {
      userInfo: null,
    };
  },
  async created() {
    try {
      const user = await fetchUserAttributes();
      if (!user || !user.email) {
        throw new Error("Invalid user attributes");
      }
      this.userInfo = user;
    } catch {
      this.handleSignOut();
      const router = useRouter();
      router.push({ name: "account" });
    }
  },
  methods: {
    handleSignOut() {
      this.signOutFunction();
    },
  },
};
</script>
