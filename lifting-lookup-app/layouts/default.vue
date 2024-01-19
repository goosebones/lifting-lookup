<template>
  <v-app>
    <v-main>
      <v-container>
        <v-row>
          <v-col cols="12" class="d-flex">
            <v-btn :to="'/'" icon="mdi-home"></v-btn>
            <v-spacer />
            <v-btn :to="'/account'">Account</v-btn>
          </v-col>
        </v-row>
        <slot />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { getCurrentUser } from "aws-amplify/auth";

export default {};
</script>
