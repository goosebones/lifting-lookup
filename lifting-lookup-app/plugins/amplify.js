import { defineNuxtPlugin } from "#app";
import awsExports from "~/aws-exports";
import { Amplify } from "aws-amplify";

export default defineNuxtPlugin((nuxtApp) => {
  Amplify.configure(awsExports);
  return {};
});
