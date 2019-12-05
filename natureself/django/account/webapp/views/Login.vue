<template>
  <div class="container justify-content-center">
    <div
      id="login-form"
      class="card mx-auto p-2"
    >
      <div class="card-body">
        <h1>{{ title }}</h1>
        <p class="text-muted">
          {{ subTitle }}
        </p>
        <b-input-group class="mb-3">
          <b-input-group-text slot="prepend">
            <svg-icon name="user" />
          </b-input-group-text>
          <b-form-input
            v-model="loginForm.username"
            type="text"
            auto-complete="on"
            :placeholder="usernamePlaceholder"
            @keyup.enter.native="handleLogin"
          />
        </b-input-group>
        <b-input-group class="mb-4">
          <b-input-group-text slot="prepend">
            <svg-icon name="password" />
          </b-input-group-text>
          <b-form-input
            v-model="loginForm.password"
            type="password"
            auto-complete="on"
            :placeholder="passwordPlaceholder"
            @keyup.enter.native="handleLogin"
          />
        </b-input-group>
        <p
          v-if="!!message"
          class="text-danger"
        >
          {{ message }}
        </p>
        <b-row>
          <b-col cols="6">
            <b-button
              v-if="!!resetPasswordUrl"
              variant="link"
              class="px-0"
              :href="resetPasswordUrl"
            >
              忘记密码？
            </b-button>
          </b-col>
          <b-col
            cols="6"
            class="text-right"
          >
            <b-button
              variant="primary"
              class="px-4"
              :disabled="loading"
              @click="handleLogin"
            >
              登录
            </b-button>
          </b-col>
        </b-row>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    title: { type: String, required: false, default: '登录' },
    subTitle: { type: String, required: false, default: '请登录' },
    usernamePlaceholder: { type: String, required: false, default: '用户名' },
    passwordPlaceholder: { type: String, required: false, default: '密码' },
    role: { type: String, required: false, default: null },
    next: { type: String, required: false, default: '/' },
    resetPasswordUrl: { type: String, required: false, default: '' },
  },
  data: () => ({
    loginForm: {
      username: '',
      password: '',
    },
    loading: false,
    message: '',
  }),
  methods: {
    handleLogin () {
      let vm = this
      vm.loading = true
      vm.$api.login({ ...vm.loginForm, role: vm.role }).then(response => {
        vm.loading = false

        if (response.data.code === 0) {
          window.location = vm.next
        } else {
          vm.message = response.data.message
        }
      })
    },
  },
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
$form-max-width: 400px;

#login-form {
  box-sizing: border-box;
  width: 100vw;
  max-width: 100vw;

  @media (min-width: $form-max-width) {
    max-width: $form-max-width;
  }
}

.btn-link:hover {
  text-decoration: none;
}
</style>
