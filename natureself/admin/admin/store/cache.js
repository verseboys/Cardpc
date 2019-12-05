import _ from 'lodash'

export default {
  state: {
    searchForms: {},
  },

  getters: {
    searchForms: state => state.searchForms,
  },

  mutations: {
    CACHE_FORM_DATA (state, userdata) {
      let { pageName, data } = userdata
      state.searchForms[pageName] = _.cloneDeep(data)
    },
  },
}
