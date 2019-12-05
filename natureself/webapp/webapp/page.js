const pages = []

function getDataJS (raw) {
  let value = document.querySelector('body').dataset.js
  return raw ? value : (value || '').trim().replace(/ +/, ' ').split(' ')
}

export const registerPageJs = (entry, activator) => {
  if (activator === undefined) {
    activator = () => activators.datajsIs(name)
  }

  pages.push({ entry, activator })
}

export const runPageJs = () => {
  pages.forEach(({ entry, activator }) => {
    if (
      (activator instanceof RegExp && window.location.pathname.match(activator)) ||
      (activator instanceof Function && activator()) ||
      (typeof activator === 'boolean' && activator)
    ) {
      entry()
    }
  })
}

export const activators = {
  elementExists (selector) {
    return document.querySelector(selector) !== null
  },
  datajsIs (value) {
    return getDataJS(true) === value
  },
  datajsContains (value) {
    return getDataJS().indexOf(value) !== -1
  },
}

export default {}
