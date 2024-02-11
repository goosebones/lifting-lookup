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