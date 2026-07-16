import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'
export default defineNuxtConfig({
  devtools: {enabled: false},
  build: {
    transpile: ['vuetify', 'vue-toastification'],
  },
  modules: [
    (_options, nuxt) => {
      nuxt.hooks.hook('vite:extendConfig', (config) => {
        // @ts-expect-error
        config.plugins.push(vuetify({ autoImport: true }))
      })
    },
    //...
  ],
  alias: {
    './runtimeConfig': './runtimeConfig.browser'
  },
  nitro: {
    // Force static output to .output/public. Without this, Nitro auto-detects
    // the Amplify build env (AWS_APP_ID) and switches to the `aws-amplify`
    // preset, which writes to .amplify-hosting/ and breaks the Console's
    // `.output/public` artifact directory.
    preset: 'static'
  },
  vite: {
    vue: {
      template: {
        transformAssetUrls,
      },
    },
    define: {
      'window.global': {}
    }
  },
  runtimeConfig: {
    public: {
      apiBaseUrl: 'https://bnx2iizo91.execute-api.us-east-2.amazonaws.com/prod'
    }
  }
})