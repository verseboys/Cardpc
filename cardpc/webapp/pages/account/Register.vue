<template>
  <div
    id="register-box"
  >
    <div
      v-show="!registerState"
      class="account-form-box register-box"
    >
      <div class="login">
        <h2>注册</h2>
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
                :class="{'disable': validateDisable==true}"
                :disabled="validateDisable"
                @click="sendValidateCode()"
                v-text="validateDisable ? countDownNum + '秒' : '获取验证码'"
              />
            </div>
          </div>
          <div class="input-item">
            <input
              id="password"
              v-model="formdata.password"
              type="password"
              placeholder="填写密码"
            >
          </div>
          <div class="agreement">
            <p>注册即同意<span @click="showDocs">《中国基层呼吸疾病防治联盟（官网）用户协议》</span></p>
          </div>
        </div>
        <button @click="registerFn">
          注册
        </button>
        <div class="clearfix login-link">
          <div class="float-right">
            <p>已有账号，<a href="/account/login">去登录</a></p>
          </div>
        </div>
      </div>
    </div>
    <div
      v-show="registerState"
      class="account-form-box"
    >
      <div class="login register-status">
        <div class="status-icon" />
        <p>注册成功！正在返回首页</p>
        <p>如果未返回，请点击<a href="/zhixiang/">这里&gt;</a></p>
      </div>
    </div>
    <div
      v-show="isDocs"
      class="maskdocs"
      :class="{'active':isDocs}"
    >
      <div
        v-scrollBar
        class="docs"
      >
        <i
          class="close"
          @click="hiddenDocs"
        />
        <h1>《中国基层呼吸疾病防治联盟（官网）用户协议》</h1>
        <p>欢迎使用中国基层呼吸疾病防治联盟网站服务平台。您在使用中国基层呼吸疾病防治联盟网站服务平台时，即表示您已阅读并同意接受下列条款的约束。></p>
        <p><strong>请认真阅读下列条款：</strong></p>
        <p>1.中国基层呼吸疾病防治联盟网站服务平台帐号注册采用实名制，用户在申请使用时需要填写一些必要的信息（包括但不限于姓名、手机号、邮箱），请保持这些信息的真实、准确、合法、有效并注意及时更新。若用户填写的信息不完整或不准确，则可能无法正常使用本服务或在使用过程中受到限制。</p>
        <p>2.任何由于电子邮箱、手机号码等信息错误，导致用户未收到相关通知、提示等信息的，由此产生的一切后果及责任由用户自行承担。</p>
        <p>3.用户有义务保证密码和帐号的安全，用户本人利用该密码和帐号所进行的一切活动引起的任何损失或损害，自行承担全部责任，本站不承担任何责任。如您发现帐号遭到未授权的使用或发生其他任何安全问题，应立即修改帐号密码并妥善保管，如有必要，请及时通知本站。因黑客行为或您的保管疏忽导致帐号非法使用，本站不承担任何责任。</p>
        <p>4.用户有违反相关法律法规以及本须知规定的任何行为时，本站有权依照违反情况，随时单方限制、中止或终止提供服务，冻结或终止个人帐号的使用，并有权追究相关责任。由此带来的损失，由用户自行承担。</p>
        <p>5.本站在中华人民共和国境内收集和产生的个人信息将存储在中华人民共和国境内。</p>
        <p>6.本站仅在业务办理必须的期限内及法律法规要求的时限内保存您的个人信息。</p>
        <p>7.为保障用户的信息安全，我们设立了专门的信息安全团队，制定了专门的信息安全制度，对用户的信息进行保护。在技术层面，我们努力采用行之有效的技术措施来保障用户的信息安全。</p>
        <p>8.当不幸发生个人信息泄露等安全事件时，我们将启动安全预警机制，通过推送通知、发布公告等方式告知用户，并努力阻止安全事件扩大，减少事件造成的影响。</p>
        <p>9.本站收集的用户信息仅用于在中国基层呼吸疾病防治联盟进行相关业务的办理和为用户提供的服务，不做他用。在不透露单个用户隐私资料的前提下，本站有权对整个用户数据进行分析，以便为用户提供更好的服务。</p>
        <p>10.本站不对外公开或向第三方提供用户的注册资料及用户在使用网络服务时存储在本站的非公开内容，但下列情况除外：</p>
        <p>(1)事先获得用户的明确授权；</p>
        <p>(2)根据有关的法律法规要求；</p>
        <p>(3)按照相关政府主管部门的要求；</p>
        <p>(4)为维护社会公众的利益。</p>
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
        password: '',
      },
      validateDisable: false, // 验证按钮是否失效
      checkValidateState: false,
      countDownNum: 60, // 倒计时总秒数
      timer: null,
      registerState: false,
      isDocs: false,
    }
  },
  methods: {
    // 显示协议
    showDocs () {
      this.isDocs = true
      var mo = function (e) { e.preventDefault() }
      document.body.style.overflow = 'hidden'
      document.addEventListener('touchmove', mo, false)// 禁止页面滑动
    },
    hiddenDocs () {
      this.isDocs = false
      var mo = function (e) { e.preventDefault() }
      document.body.style.overflow = ''// 出现滚动条
      document.removeEventListener('touchmove', mo, false)
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
        usage: 'register',
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
        usage: 'register',
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
    // 校验注册
    checkRegister () {
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
      if (!$.trim(vm.formdata.password)) {
        vm.loginError = '密码不能为空'
        return false
      }
      return true
    },
    // 注册函数
    registerFn () {
      let vm = this
      if (vm.checkRegister()) {
        vm.loginError = ''

        api.account.register(vm.formdata).then(response => {
          if (response.status === 200) {
            if (response.data.code === 0) {
              vm.registerState = true
              // 用户注册成功
              setTimeout(() => {
                vm.goBack('/zhixiang/')
              }, 3000)
            } else {
              vm.loginError = response.data.message
            }
          } else if (response.status === 400) {
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
