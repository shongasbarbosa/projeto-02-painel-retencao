import '@quasar/extras/material-icons/material-icons.css'
import 'quasar/src/css/index.sass'

import ptBR from 'quasar/lang/pt-BR'
import { createPinia } from 'pinia'
import { Notify, Quasar } from 'quasar'
import { createApp } from 'vue'

import App from './App.vue'
import { initTheme } from './composables/useTheme'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Quasar, {
  plugins: { Notify },
  lang: ptBR,
})

initTheme()

app.mount('#app')
