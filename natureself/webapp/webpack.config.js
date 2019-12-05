const fs = require('fs')
const path = require('path')
const webpack = require('webpack')
const BundleTracker = require('webpack-bundle-tracker')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const TerserPlugin = require('terser-webpack-plugin')
const OptimizeCSSAssetsPlugin = require('optimize-css-assets-webpack-plugin')
const VueLoaderPlugin = require('vue-loader/lib/plugin')
const StyleLintPlugin = require('stylelint-webpack-plugin')

const devMode = process.env.NODE_ENV !== 'production'

// this file (webpack.config.js) is located in natureself/webapp/,
// the calculated PROJECT_DIR is root of django project.
const PROJECT_DIR = path.resolve(__dirname, '../..')
const PYNS_DIR = path.resolve(PROJECT_DIR, 'natureself')
// all built output goes to $PROJECT_DIR/build/admin/
const BUILD_DIR = path.resolve(PROJECT_DIR, 'build/webapp/')
// public assets path
const PUBLIC_PATH = '/static/'

const defaultAlias = {
  vue: 'vue/dist/vue.js',

  // these are just two global aliases, for accessing project root and django's project dir
  '@': path.resolve(PROJECT_DIR),
  '@nsproject': path.resolve(PROJECT_DIR, 'nsproject'),
  // @natureself points to py-natureself root dir
  '@natureself': PYNS_DIR,

  // application aliases, point to app dir, when import, should use '@$app/webapp' or '@$app/admin'
  '@ns-account': path.resolve(PYNS_DIR, 'django/account'),
  '@ns-media': path.resolve(PYNS_DIR, 'django/media'),
  '@ns-notification': path.resolve(PYNS_DIR, 'django/notification'),
  '@ns-course': path.resolve(PYNS_DIR, 'django/course'),
  '@ns-ums': path.resolve(PYNS_DIR, 'ums'),

  // these two aliases are a little bit different, note the directory they point to
  '@webapp': path.resolve(PYNS_DIR, 'webapp/webapp'),
  '@admin': path.resolve(PYNS_DIR, 'admin/admin'),

  // sometimes we need to use icon svg directly instead of SvgIcon
  '@ns-icons': path.resolve(PYNS_DIR, 'icons'),
}

const WEBAPP_CONFIG_FILE = path.resolve(PROJECT_DIR, 'nsproject/webapp.js')
const WebappConfig = fs.existsSync(WEBAPP_CONFIG_FILE) ? require(WEBAPP_CONFIG_FILE) : {}

const { entry = {}, alias = {} } = WebappConfig
Object.assign(alias, defaultAlias)

// 注意，这里本来要检查 entry 是否为空，但是 admin/webpack.config.js 会依赖 webapp/webpack.config.js，
// 如果这里检查 entry 为空而退出，会导致 admin/webpack.config.js 无法使用

module.exports = {
  mode: process.env.NODE_ENV || 'development',
  // set context to django project root
  context: PROJECT_DIR,

  entry,

  output: {
    path: BUILD_DIR,
    filename: devMode ? 'js/[name].js' : 'js/[name].[hash:7].js',
    chunkFilename: devMode ? 'js/chunk.[id].js' : 'js/chunk.[id].[hash:7].js',
    publicPath: PUBLIC_PATH,
  },

  resolve: {
    modules: [
      'node_modules',
      // add django project root, so we can require('$app-path/some-module.js')
      PROJECT_DIR,
    ],
    alias,
  },

  module: {
    rules: [
      {
        enforce: 'pre',
        test: /\.(js|vue)$/,
        exclude: /node_modules/,
        loader: 'eslint-loader',
        options: {
          formatter: require('eslint-friendly-formatter'),
        },
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: [
          { loader: 'thread-loader' },
          {
            loader: 'babel-loader',
            options: {
              cacheDirectory: true,
            },
          },
        ],
      },
      {
        test: /\.vue$/,
        loader: 'vue-loader',
      },
      {
        test: /\.(sa|sc|c)ss$/,
        use: [
          // style-loader: creates style nodes from JS strings
          // mini-css-extract-plugin: extract CSS into seperate file
          // devMode ? 'style-loader' : MiniCssExtractPlugin.loader,
          {
            loader: MiniCssExtractPlugin.loader,
            options: {
              hmr: devMode,
            },
          },
          // translates CSS into CommonJS
          { loader: 'css-loader' },
          {
            loader: 'postcss-loader',
            options: {
              plugins: (loader) => [
                // use future CSS features today. https://github.com/csstools/postcss-preset-env
                require('postcss-preset-env')(),
                // contains plugins for Sass-like features, like variables, nesting, and mixins. https://github.com/jonathantneal/precss
                require('precss'),
                // adds vendor prefixes, using data from Can I Use. https://github.com/postcss/autoprefixer
                require('autoprefixer'),
              ],
            },
          },
          // compile sass/scss into css, using node-sass by default
          { loader: 'fast-sass-loader' },
        ],
      },
      {
        test: /\.svg$/,
        include: /\/icons\/svg\/.*\.svg$/,
        loader: 'svg-sprite-loader',
        options: {
          symbolId: 'icon-[name]',
        },
      },
      {
        test: /\.(svg|png|jpg|gif|ico)$/,
        exclude: [/\/icons\/svg\/.*\.svg$/, /node_modules/],
        loader: 'url-loader',
        options: {
          limit: 8192,
          name: 'img/[name].[contenthash:7].[ext]',
        },
      },
      {
        test: /\.(ttf|eot|woff)$/,
        loader: 'file-loader',
        options: {
          name: 'font/[name].[contenthash:7].[ext]',
        },
      },
    ],
  },

  plugins: [
    new BundleTracker({ path: BUILD_DIR, filename: '../webpack-stats-webapp.json' }),
    new webpack.ProgressPlugin(),
    new MiniCssExtractPlugin({
      filename: devMode ? 'css/[name].css' : 'css/[name].[contenthash:7].css',
      chunkFilename: devMode ? 'css/chunk.[id].css' : 'css/chunk.[id].[contenthash:7].css',
    }),
    new webpack.HotModuleReplacementPlugin(),
    new VueLoaderPlugin(),
    new StyleLintPlugin({
      files: ['**/*.{vue,htm,html,css,sss,less,scss,sass}'],
    }),
  ],

  optimization: {
    minimizer: [
      new TerserPlugin({
        cache: true,
        parallel: true,
        sourceMap: false,
      }),
      new OptimizeCSSAssetsPlugin({}),
    ],
    // chunks 支持三种值：initial，async，all
    //   initial: 表示网页加载时就必须全都加载的包，分割 initial 的目的一般是可以多线程加载资源，可以起到加速作用
    //   async: 表示按需异步加载的包，分割这类包的做法也叫 code spliting，可以不用加载用户没有用到的东西
    //   all: 表示两者都加载
    // 如果我们使用 HtmlWebpackPlugin 来注入生成的网页，那么 initial 被分成多个文件后，文件都会被注入网页，
    // 但是在 django 中，我们使用 render_bundle 来引入文件时，只会引入第一个文件，导致不全。
    // 因此，在 django 中使用时，我们只能将 chunks 设置为 initial，从而不对 initial 拆包。
    splitChunks: {
      chunks: 'async',
    },
  },

  devtool: devMode ? 'eval-source-map' : 'none',
  devServer: {
    contentBase: BUILD_DIR,
    host: process.env.HOST || '0.0.0.0',
    port: process.env.PORT || 8080,
    open: false,
    useLocalIp: true,
    overlay: true,
    proxy: {
      '/api': 'http://localhost:8000',
      '/media': 'http://localhost:8000',
      '/download': 'http://localhost:8000',
    },
    writeToDisk: true,
    hot: true,
  },
}
