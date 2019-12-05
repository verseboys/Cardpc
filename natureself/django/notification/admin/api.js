import request from '@webapp/request.js'

function listEmail ({
  subject = null, from = null, recipient = null,
  sentRange = null,
  sentBefore = null, sentAfter = null,
  status = null,
  page = null, pageSize = null,
} = {}) {
  let params = {}
  if (subject) { params.subject = subject }
  if (from) { params.from = from }
  if (recipient) { params.recipient = recipient }
  if (sentRange) {
    params.sent_range = `${sentRange[0]},${sentRange[1]}`
  } else if (sentBefore && !sentAfter) {
    params.sent_range = `,${sentBefore}`
  } else if (!sentBefore && sentAfter) {
    params.sent_range = `${sentAfter},`
  } else if (sentBefore && sentAfter) {
    params.sent_range = `${sentAfter},${sentBefore}`
  }
  if (status) { params.status = status }
  if (page) { params.page = page }
  if (pageSize) { params.page_size = pageSize }

  return request({ method: 'GET', url: '/api/admin/notification/emails', params })
}

function getEmail ({ id }) {
  return request({ method: 'GET', url: `/api/admin/notification/emails/${id}` })
}

function getEmailSearchForm () {
  return request({ method: 'GET', url: `/api/admin/notification/emails/forms/search` })
}

function getEmailEditForm () {
  return request({ method: 'GET', url: `/api/admin/notification/emails/forms/edit` })
}

function listAliSms ({ phone = null, content = null, status = null, sentBefore = null, sentAfter = null, sentRange = null, page = null, pageSize = null }) {
  let params = {}
  if (phone) { params.phone = phone }
  if (content) { params.content = content }
  if (status) { params.status = status }
  if (sentRange) {
    params.sent_range = `${sentRange[0]},${sentRange[1]}`
  } else if (sentBefore && !sentAfter) {
    params.sent_range = `,${sentBefore}`
  } else if (!sentBefore && sentAfter) {
    params.sent_range = `${sentAfter},`
  } else if (sentBefore && sentAfter) {
    params.sent_range = `${sentAfter},${sentBefore}`
  }
  if (status) { params.status = status }
  if (page) { params.page = page }
  if (pageSize) { params.page_size = pageSize }

  return request({ method: 'GET', url: '/api/admin/notification/alisms', params })
}

function getAliSms ({ id }) {
  return request({ method: 'GET', url: `/api/admin/notification/alisms/${id}` })
}

function getAliSmsSearchForm () {
  return request({ method: 'GET', url: `/api/admin/notification/alisms/forms/search` })
}

function getAliSmsEditForm () {
  return request({ method: 'GET', url: `/api/admin/notification/alisms/forms/edit` })
}

const EMAIL_STATUSES = {
  pending: { value: 'pending', display: '待发送', type: 'warning' },
  reject: { value: 'reject', display: '拒绝发送', type: 'danger' },
  sent: { value: 'sent', display: '已发送', type: 'success' },
  success: { value: 'success', display: '发送成功', type: 'success' },
  failed: { value: 'failed', display: '发送失败', type: 'danger' },
  dryrun: { value: 'dryrun', display: '本地测试', type: 'success' },
}

const ALISMS_STATUSES = {
  pending: { value: 'pending', display: '待发送', type: 'warning' },
  reject: { value: 'reject', display: '拒绝发送', type: 'danger' },
  sent: { value: 'sent', display: '已发送', type: 'success' },
  success: { value: 'success', display: '发送成功', type: 'success' },
  failed: { value: 'failed', display: '发送失败', type: 'danger' },
  dryrun: { value: 'dryrun', display: '本地测试', type: 'success' },
}

function getEmailStatus (status) {
  if (EMAIL_STATUSES[status]) {
    return EMAIL_STATUSES[status]
  } else {
    return { value: 'unknown', display: '未知', type: 'warning' }
  }
}

function getAliSmsStatus (status) {
  if (ALISMS_STATUSES[status]) {
    return ALISMS_STATUSES[status]
  } else {
    return { value: 'unknown', display: '未知', type: 'warning' }
  }
}

export default {
  notification: {
    listEmail,
    getEmail,
    EMAIL_STATUSES,
    getEmailStatus,
    getEmailSearchForm,
    getEmailEditForm,

    listAliSms,
    getAliSms,
    ALISMS_STATUSES,
    getAliSmsStatus,
    getAliSmsSearchForm,
    getAliSmsEditForm,
  },
}
