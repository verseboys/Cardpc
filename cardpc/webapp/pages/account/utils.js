import 'url-search-params-polyfill'
import $ from 'jquery'
// 注册登录公共函数
const mixin = {
  methods: {
    // 校验用户手机号或者邮箱
    checkAccount (identity) {
      let _this = this
      if (!$.trim(identity)) {
        _this.loginError = '手机号或邮箱不能为空'
        return false
      }
      if (!this.isMobile(identity) && !this.isEmail(identity)) {
        _this.loginError = '请输入正确的手机号或邮箱'
        return false
      }
      return true
    },
    // 校验手机号
    checkPhone (identity) {
      let _this = this
      if (!$.trim(identity)) {
        _this.loginError = '手机号不能为空'
        return false
      }
      if (!this.isMobile(identity)) {
        _this.loginError = '请输入正确的手机号'
        return false
      }
      return true
    },
    // 校验手机
    isMobile (value) {
      let reg = /^(?:\+?86)?1(?:3\d{3}|5[^4\D]\d{2}|8\d{3}|7(?:[35678]\d{2}|4(?:0\d|1[0-2]|9\d))|9[189]\d{2}|66\d{2})\d{6}$/
      if (!reg.test(value)) return false
      return true
    },
    // 校验邮箱
    isEmail (value) {
      let reg = /^\w+((-\w+)|(\.\w+))*@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z0-9]+$/
      if (!reg.test(value)) return false
      return true
    },
    // 倒计时
    countDown () {
      let _this = this
      _this.timer = setInterval(function () {
        if (_this.countDownNum !== 0) {
          _this.countDownNum--
        } else {
          _this.validateDisable = false
          _this.countDownNum = 60
          clearInterval(_this.timer)
        }
      }, 1000)
    },
    goBack (url) {
      const urlParams = new URLSearchParams(window.location.search)
      const next = urlParams.get('next') || url
      window.location.href = next
    },
  },
}

export default mixin
