<template>
  <div class="login-form-container">
    <el-card shadow="always">
      <div slot="header">
        <span>请登录</span>
      </div>
      <el-form
        ref="loginForm"
        :model="loginForm"
        :rules="rules"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            autofocus
            autocomplete="on"
          >
            <svg-icon
              slot="prefix"
              name="user"
            />
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            placeholder="密码"
            type="password"
            autocomplete="on"
            @keyup.enter.native="handleLogin()"
          >
            <svg-icon
              slot="prefix"
              name="password"
            />
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button
            class="submit-button"
            type="primary"
            :disabled="loading"
            @click="handleLogin()"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
export default {
  data () {
    return {
      loginForm: {
        username: '',
        password: '',
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blue' },
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blue' },
        ],
      },
      loading: false,
    }
  },
  methods: {
    handleLogin () {
      this.$refs.loginForm.validate((valid) => {
        if (valid) {
          let vm = this
          vm.loading = true
          vm.$api.account.login({ ...vm.loginForm, role: 'admin' }).then(response => {
            vm.loading = false

            if (response.data.code === 0) {
              this.$router.replace(this.$route.query.redirect || '/')
            } else if (response.status === 500) {
              this.$message.error('服务器发生错误')
            } else {
              this.$message.error(response.data.message)
            }
          })
        } else {
          return false
        }
      })
    },
  },
}
</script>

<style lang="scss" scope>
$form-max-width: 300px;

.login-form-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;

  .el-card {
    margin: 0 auto;
    box-sizing: border-box;
    width: 100vw;
    max-width: 100vw;

    @media (min-width: $form-max-width) {
      max-width: $form-max-width;
    }
  }

  .el-form-item:last-child {
    margin-bottom: 0 !important;
  }

  .submit-button {
    float: right;
  }
}
</style>
