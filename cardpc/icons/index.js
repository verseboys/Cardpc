import icons from '@natureself/icons'

const req = require.context('./svg', true, /\.svg$/)
icons.importAll(req)
