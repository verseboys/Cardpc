import $ from 'jquery'
import request from '@webapp/request.js'

// 点击弹框确定按钮
$('#btn').click(function () {
  $('#dialog').fadeOut()
})

// 未参与课程调研 点击课程
$('.to_cource_video').click(function () {
  $('#dialog').fadeIn()
})

// 课程调研-立即参与
$('#investigation_join_btn').click(function () {
  request({
    method: 'POST',
    url: '/zhixiang/training/',
    data: { action: 'start-a' } })
    .then(response => {
      if (response.status === 200 && response.data && response.data.code === 0) {
        window.location.href = response.data.data.redirect
      }
    })
})
// 资格认证-立即参与
$('#qualification_join_btn').click(function () {
  request({
    method: 'POST',
    url: '/zhixiang/training/',
    data: { action: 'start-c' } })
    .then(response => {
      if (response.status === 200 && response.data && response.data.code === 0) {
        window.location.href = response.data.data.redirect
      }
    })
})
