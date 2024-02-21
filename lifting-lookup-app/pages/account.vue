<template>
  <div>
    <Authenticator>
      <template v-slot="{ user, signOut }">
        <AccountDashboard :sign-out-function="signOut"></AccountDashboard>
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
