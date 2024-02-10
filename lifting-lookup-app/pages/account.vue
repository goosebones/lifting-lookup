<template>
  <div>
    <Authenticator>
      <template v-slot="{ user, signOut }">
        <v-row>
          <v-col cols="12"> Hello, {{ user.signInDetails.loginId }} </v-col>
          <v-col cols="12" md="2">
            <v-card variant="outlined">
              <v-card-title>Navigation</v-card-title>
              <v-list>
                <v-list-item :to="'/account/vip'" nuxt>
                  VIP Lifter Notifications
                </v-list-item>
                <v-list-item @click="handleSignOut(signOut)">
                  Sign Out
                </v-list-item>
              </v-list>
            </v-card>
          </v-col>
          <v-col cols="12" md="10">
            <NuxtPage :user-info="user"></NuxtPage>
          </v-col>
        </v-row>
      </template>
    </Authenticator>
  </div>
</template>

<script setup lang="ts">
import { Authenticator } from "@aws-amplify/ui-vue";
import "@aws-amplify/ui-vue/styles.css";
import { useRouter } from "vue-router";

const router = useRouter();
const handleSignOut = (callback: Function) => {
  callback();
  router.push({ name: "account" });
};
</script>
