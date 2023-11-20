import axios from "axios";

export default defineNuxtPlugin((nuxtApp) => {
  const config = nuxtApp.$config;
  const baseURL = config.public.apiBaseUrl;
  const instance = axios.create({
    baseURL,
    timeout: 9000,
  });
  return {
    provide: {
      axios: instance,
    },
  };
});
