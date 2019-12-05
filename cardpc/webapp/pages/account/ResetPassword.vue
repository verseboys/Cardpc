<template>
  <div id="forgetpwd-box">
    <div class="account-form-box forgetpwd-box">
      <div class="login">
        <h2>重置密码</h2>
        <div class="error">
          <transition name="fade">
            <p
              v-if="loginError!=''"
              v-text="loginError"
            />
          </transition>
        </div>
        <div class="input-group">
          <div class="input-item">
            <input
              v-model="formdata.identity"
              type="text"
              placeholder="请输入手机号/邮箱"
            >
          </div>
          <div class="input-item validate clearfix">
            <div class="float-left validate-input">
              <input
                v-model="formdata.code"
                type="text"
                placeholder=" 填写验证码"
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
                :class="{'disable':validateDisable==true}"
                :disabled="validateDisable"
                @click="sendValidateCode()"
                v-text="validateDisable?countDownNum+'秒':'获取验证码'"
              />
            </div>
          </div>
          <div class="input-item">
            <input
              id="password"
              v-model="formdata.new_password"
              type="password"
              placeholder="设置新密码"
            >
          </div>
        </div>
        <button @click="forgetpwd">
          确认
        </button>
        <div class="clearfix login-link">
          <div class="float-right">
            <p>想起密码，<a href="/account/login">返回登录</a></p>
          </div>
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
      loginError: '',
      formdata: {
        identity: '',
        code: '',
        new_password: '',
      },
      validateDisable: false, // 验证按钮是否失效
      checkValidateState: false,
      countDownNum: 60, // 倒计时总秒数
      timer: null,
    }
  },
  methods: {
    // 显示协议
    showDocsFn () {
      this.isDocs = true
    },
    // 发送验证码
    sendValidateCode () {
      let vm = this
      if (!vm.checkAccount(vm.formdata.identity)) return false
      vm.validateDisable = true
      vm.loginError = ''
      vm.countDown.call(this)

      api.account.sendCode({
        identity: vm.formdata.identity,
        usage: 'reset-password',
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
    },
    // 校验验证码
    checkValidate () {
      let vm = this
      let validateObj = {
        identity: vm.formdata.identity,
        usage: 'reset-password',
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
    // 校验找回密码
    checkForgetpwd () {
      let vm = this
      vm.loginError = ''
      if (!vm.checkAccount(vm.formdata.identity)) return false
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
      if (!$.trim(vm.formdata.new_password)) {
        vm.loginError = '密码不能为空'
        return false
      }
      return true
    },
    // 找回密码提交函数
    forgetpwd () {
      let vm = this
      if (vm.checkForgetpwd()) {
        vm.loginError = ''

        api.account.resetPassword(vm.formdata).then(response => {
          if (response.status === 200) {
            if (response.data.code === 0) {
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
