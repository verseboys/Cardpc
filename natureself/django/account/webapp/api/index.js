import request from '@webapp/request.js'

function login (data) {
  /*
   * 用户名/邮箱/手机号+密码登录，data 中包含以下字段：
   * username, password
   *
   * 手机号+验证码登录，data 中包含以下字段：
   * phone, code
   *
   * 邮箱+验证码登录，data 中包含以下字段：
   * email, code
   *
   * 邮箱/手机号+验证码登录，data 中包含以下字段：
   * identity, code (后端会自动检测 identity 是手机号还是邮箱)
   *
   * 对于验证码登录，鼓励使用 phone+code 或 email+code，不鼓励使用 identity+code，
   * 但从后端实现的角度看没有区别。
   *
   * 所有情况下，可以增加一个 role 参数，当提供 role 参数时，
   * 只有指定角色的用户才可以登录。
   */
  return request({ url: '/api/account/login', method: 'POST', data })
}

function getInfo () {
  return request({ url: '/api/account/info' })
}

function logout () {
  return request({ url: '/api/account/logout', method: 'POST' })
}

function sendCode (data) {
  /*
   * 发送短信验证码，data 包含以下字段：
   * phone, usage
   *
   * 发送邮件验证码，data 包含以下字段：
   * email, usage
   *
   * 自动决定发送短信还是邮件验证码，data 包含以下字段：
   * identity, usage
   *
   * 与登录 API 类似，鼓励使用 phone+usage 或 email+usage
   *
   * usage 支持的取值：register, reset-password, login
   */
  return request({ url: '/api/account/send-code', method: 'POST', data })
}

function verifyCode (data) {
  /*
   * 参数与 sendCode() 类似，在其基础上增加 code 字段，为用户填写的验证码
   */
  return request({ url: '/api/account/verify-code', method: 'POST', data })
}

function resetPassword (data) {
  /*
   * 参与与 login() 类似，在其基础上增加 new_password 字段，为用户填写的新密码
   */
  return request({ url: '/api/account/reset-password', method: 'POST', data })
}

function register (data) {
  /*
   * 手机号+验证码+密码注册，data 包含以下字段：
   * phone, code, password
   *
   * 邮箱+验证码+密码注册，data 包含以下字段：
   * email, code, password
   *
   * 类似的，手机号/邮箱+验证码+密码注册，data 包含以下字段：
   * identity, code, password （后端会自动检测 identity 是邮箱还是手机号，写入用户相应的字段 ）
   */
  return request({ url: '/api/account/register', method: 'POST', data })
}

const ERRORS = {
  1001: { code: 1001, message: '无效的手机号' },
  1002: { code: 1002, message: '无效的邮箱' },
  1003: { code: 1003, message: '无效的手机号或邮箱' },
  1004: { code: 1004, message: '验证码错误' },
  1005: { code: 1005, message: '手机号已注册' },
  1006: { code: 1006, message: '邮箱已注册' },
  1007: { code: 1007, message: '请求太频繁，请稍后再试' },
}

function isApplicationError (code) {
  return !!ERRORS[code]
}

export default {
  account: {
    login,
    getInfo,
    logout,
    sendCode,
    verifyCode,
    resetPassword,
    register,

    ERRORS,
    isApplicationError,
  },
}
