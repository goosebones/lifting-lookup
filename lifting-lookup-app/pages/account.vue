<template>
  <div>
    <Authenticator>
      <template v-slot="{ user, signOut }">
        <v-row>
          <v-col cols="12"> Hello, {{ userInfo.email }} </v-col>

          <v-col cols="12" md="2">
            <v-card variant="outlined">
              <v-card-title>Navigation</v-card-title>
              <v-list>
                <v-list-item :to="'/account/vip'" nuxt>
                  VIP Lifter Notifications (Beta)
                </v-list-item>
                <v-list-item @click="handleSignOut(signOut)">
                  Sign Out
                </v-list-item>
              </v-list>
            </v-card>
          </v-col>
          <v-col cols="12" md="10">
            <NuxtPage :user-info="userInfo"></NuxtPage>
          </v-col>
        </v-row>
      </template>
    </Authenticator>
  </div>
</template>

<script setup lang="ts">
import { Authenticator } from "@aws-amplify/ui-vue";
import "@aws-amplify/ui-vue/styles.css";
import {
  fetchUserAttributes,
  signOut,
  type FetchUserAttributesOutput,
} from "aws-amplify/auth";
import { useRouter } from "vue-router";

const router = useRouter();
const handleSignOut = (callback: Function) => {
  callback();
  router.push({ name: "account" });
};

let userInfo: FetchUserAttributesOutput = {};
try {
  userInfo = await fetchUserAttributes();
  if (!userInfo || !userInfo.email) {
    throw new Error("Invalid user attributes");
  }
} catch {
  handleSignOut(signOut);
  router.push({ name: "account" });
}
</script>
