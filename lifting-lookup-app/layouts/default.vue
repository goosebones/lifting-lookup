<template>
  <v-app>
    <v-main>
      <v-container>
        <v-row>
          <v-col cols="12" class="d-flex">
            <v-btn :to="'/'" icon="mdi-home"></v-btn>
            <v-spacer />
            <v-btn :to="'/account'" variant="outlined">Account</v-btn>
          </v-col>
        </v-row>
        <slot />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
export default {};
</script>
