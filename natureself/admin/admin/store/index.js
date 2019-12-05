import Vue from 'vue'
import Vuex from 'vuex'

import user from './user'
import app from './app'
import route from './route'
import cache from './cache'

Vue.use(Vuex)

const store = new Vuex.Store({
  modules: {
    user,
    route,
    app,
    cache,
  },
})

export default store
