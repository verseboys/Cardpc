const path = require('path')
const merge = require('webpack-merge')
const HtmlWebpackPlugin = require('html-webpack-plugin')

// this file (webpack.config.js) is located in natureself/admin/,
// the calculated PROJECT_DIR is root of django project.
const PROJECT_DIR = path.resolve(__dirname, '../..')
// all built output goes to $PROJECT_DIR/build/admin/
const BUILD_DIR = path.resolve(PROJECT_DIR, 'build/admin/')
// the admin project is assumed to be accessed via http://$app-domain/admin/
const ADMIN_ROOT_URL = '/admin/'
const ADMIN_PUBLIC_PATH = ADMIN_ROOT_URL

const webappWebpackConfig = require('../webapp/webpack.config.js')

const bundleTrackerRemovedConfig = merge({
  customizeArray (a, b, key) {
    if (key === 'plugins') {
      // bundle tracker plugin use 'Plugin' as the constructor name
      // see: https://github.com/owais/webpack-bundle-tracker/issues/45
      return a.filter(p => p.constructor.name !== 'Plugin')
    }
    // Fall back to default merging
    return undefined
  },
})(webappWebpackConfig, { plugins: [] })

module.exports = merge.strategy({ entry: 'replace' })(bundleTrackerRemovedConfig, {
  // set context to django project root
  context: PROJECT_DIR,

  // add admin entry
  entry: {
    admin: path.resolve(PROJECT_DIR, 'natureself/admin/admin/index.js'),
  },

  output: {
    path: BUILD_DIR,
    publicPath: ADMIN_PUBLIC_PATH,
  },

  plugins: [
    new HtmlWebpackPlugin({
      template: 'natureself/admin/admin/index.html',
      favicon: 'natureself/assets/logo/admin-256.png',
    }),
  ],

  optimization: {
    splitChunks: {
      // since we're using SPA, index.html is injected by webpack, all initial chunks will be injected,
      // so we can set chunks to 'all' here.
      chunks: 'all',
    },
  },

  devServer: {
    host: process.env.HOST || '0.0.0.0',
    port: process.env.PORT || 8081,
    open: true,
    openPage: 'admin/',
    writeToDisk: true,
  },
})
