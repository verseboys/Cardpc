<template>
  <div
    id="login-box"
    class="account-form-box"
  >
    <div class="login">
      <h2 v-text="loginType === 'password'?'登录':'短信登录'" />
      <div class="error">
        <transition name="fade">
          <p
            v-if="loginError!=''"
            v-text="loginError"
          />
        </transition>
      </div>
      <div
        v-if="loginType === 'password'"
        class="input-group"
      >
        <div class="input-item">
          <input
            v-model="formdata.username"
            type="text"
            placeholder="请输入手机号/邮箱"
            autocomplete="on"
          >
        </div>
        <div class="input-item">
          <input
            id="password"
            v-model="formdata.password"
            type="password"
            placeholder="填写密码"
            autocomplete="on"
            @keyup.enter="doLogin"
          >
        </div>
      </div>
      <div
        v-else
        class="input-group"
      >
        <div class="input-item">
          <input
            v-model="formdata.identity"
            type="text"
            placeholder="请输入手机号"
            autocomplete="on"
          >
        </div>
        <div class="input-item validate clearfix">
          <div class="float-left validate-input">
            <input
              v-model="formdata.code"
              type="text"
              placeholder=" 填写验证码"
              @keyup.enter="doLogin"
              @blur="checkValidate"
            >
            <img
              v-show="checkValidateState"
              src="../../img/check-green.svg"
            >
          </div>
          <div class="float-right">
            <button
              class="validate-btn"
              :class="{'disable': validateDisable==true}"
              :disabled="validateDisable"
              @click="sendValidateCode()"
              v-text="validateDisable ? countDownNum + '秒' : '获取验证码'"
            />
          </div>
        </div>
      </div>
      <button @click="doLogin">
        登录
      </button>
      <div class="clearfix login-link">
        <div class=" float-left">
          <a :href="'/account/register/'+locationSearch">注册</a> |
          <a :href="'/account/reset-password/'+locationSearch">忘记密码</a>
        </div>
        <div class="float-right switch-login">
          <span
            v-if="loginType === 'password'"
            @click="switchMethod('smscode')"
          >短信登录</span>
          <span
            v-else
            @click="switchMethod('password')"
          >密码登录</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import $ from 'jquery'
import api from '@cardpc/webapp/api'
import mixin from './utils'

export default {
  mixins: [mixin],
  data () {
    return {
      loginType: 'password',
      loginError: '',
      formdata: {
        username: '',
        password: '',
        identity: '',
        code: '',
      },
      validateDisable: false, // 验证按钮是否失效
      checkValidateState: false,
      countDownNum: 60,
      timer: null,
      search: '',
    }
  },
  computed: {
    locationSearch () { return window.location.search },
  },
  methods: {
    switchMethod (method) {
      let vm = this
      vm.loginError = ''
      vm.loginType = method
    },
    // 发送验证码
    sendValidateCode () {
      let vm = this
      if (vm.checkPhone(vm.formdata.identity)) {
        vm.validateDisable = true
        vm.loginError = ''
        vm.countDown.call(this)

        api.account.sendCode({
          phone: vm.formdata.identity,
          usage: 'login',
        }).then(response => {
          if (response.status === 200) {
            vm.validateDisable = true
            vm.loginError = ''
          } else if (response.status === 400) {
            vm.loginError = '发送验证码间隔时间太短，请稍候再发'
          } else {
            // 发生了其他错误，例如网络断了或者服务器发生了异常
            vm.loginError = '发送验证码失败，请稍候再发'
          }
        })
      }
    },
    // 校验验证码
    checkValidate () {
      let vm = this
      let validateObj = {
        identity: vm.formdata.identity,
        usage: 'login',
        code: vm.formdata.code,
      }
      // if (vm.checkValidateState) return
      api.account.verifyCode(validateObj).then(response => {
        if (response.status === 200) {
          vm.checkValidateState = true
          vm.loginError = ''
        } else if (response.status === 400) {
          vm.checkValidateState = false
          vm.loginError = '验证码错误'
        } else {
          // 发生了其他错误，例如网络断了或者服务器发生了异常
          vm.loginError = ''
        }
      })
    },
    // 校验登录
    checkLogin () {
      let vm = this
      vm.loginError = ''
      if (vm.loginType === 'password') {
        if (!vm.checkAccount(vm.formdata.username)) return false
        if (!$.trim(vm.formdata.password)) {
          vm.loginError = '密码不能为空'
          return false
        }
      } else if (vm.loginType === 'smscode') {
        if (!vm.checkPhone(vm.formdata.identity)) return false
        if (!$.trim(vm.formdata.code)) {
          vm.loginError = '验证码不能为空'
          return false
        }
        if (vm.checkValidateState) {
          vm.loginError = ''
        } else {
          vm.loginError = '验证码错误'
          return false
        }
      }
      return true
    },
    doLogin () {
      let vm = this
      if (vm.checkLogin()) {
        vm.loginError = ''
        let formdata = null
        if (vm.loginType === 'password') {
          formdata = {
            username: vm.formdata.username,
            password: vm.formdata.password,
          }
        } else {
          formdata = {
            identity: vm.formdata.identity,
            code: vm.formdata.code,
          }
        }

        api.account.login(formdata).then(response => {
          if (response.status === 200) {
            if (response.data.code === 0) {
              // 登录成功，跳转回原来的页面。
              // 读取 Query String 中 'next' 值，如果没有，则跳转到首页
              vm.goBack('/zhixiang/')
            } else {
              vm.loginError = response.data.message
            }
          } else if (response.status === 400) {
          // 登录失败，用户名或密码错误
            vm.loginError = response.data.message
          } else {
          // 发生了其他错误，例如网络断了或者服务器发生了异常
            vm.loginError = '网络异常，请稍候重试'
          }
        })
      }
    },
  },
}
</script>
