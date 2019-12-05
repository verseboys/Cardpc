import axios from 'axios'
import Cookies from 'js-cookie'

const client = axios.create({
  baseURL: '',
  validateStatus: function (status) {
    return true
  },
})

function request ({ url, method = 'GET', data = null, params = null, headers = {}, responseType = 'json' }) {
  const csrftoken = Cookies.get('csrftoken')
  if (csrftoken !== undefined && ['POST', 'PUT', 'PATCH', 'DELETE'].indexOf(method) >= 0) {
    headers['X-CSRFToken'] = csrftoken
  }
  return client({ method, url, data, params, headers, responseType })
}

export default request
