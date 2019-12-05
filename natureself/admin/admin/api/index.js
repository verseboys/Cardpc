import request from '@webapp/request.js'

const api = {
  request,
}
export default api

export const registerApi = (moduleApi) => {
  if (moduleApi) {
    Object.assign(api, moduleApi)
  }
}
