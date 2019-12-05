module.exports = {
  root: true,
  parserOptions: {
    parser: 'babel-eslint',
    sourceType: 'module',
    ecmaVersion: 2017,
  },
  env: {
    browser: true,
  },
  plugins: [
    'vue',
  ],
  extends: [
    'standard',
    'plugin:vue/recommended',
  ],
  rules: {
    // 'semi': ['error', 'always'],
    'comma-dangle': ['error', 'always-multiline'],
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'camelcase': ['off'],
    'indent': ['error', 2],
    'vue/max-attributes-per-line': ['error', {
      'singleline': 5,
      'multiline': {
        'max': 2,
        'allowFirstLine': false,
      },
    }],
    'vue/singleline-html-element-content-newline': ['off'],
  },
}
