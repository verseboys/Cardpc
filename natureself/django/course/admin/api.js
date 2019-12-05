import request from '@webapp/request.js'

function listCourse ({ title = null, page = null, page_size = null } = {}) {
  let params = {}
  if (title) { params.title = title }
  if (page) { params.page = page }
  if (page_size) { params.page_size = page_size }
  return request({ method: 'GET', url: '/api/admin/course/courses', params })
}

function getCourse ({ id }) {
  return request({ method: 'GET', url: `/api/admin/course/courses/${id}` })
}

function deleteCourse ({ id }) {
  return request({ method: 'DELETE', url: `/api/admin/course/courses/${id}` })
}

function createCourse (data) {
  return request({ method: 'POST', url: '/api/admin/course/courses', data })
}

function patchCourse (id, data) {
  return request({ method: 'PATCH', url: `/api/admin/course/courses/${id}`, data })
}

function getCourseForm (form) {
  return request({ method: 'GET', url: `/api/admin/course/courses/forms/${form}` })
}

function listPresentation ({ title = null, status = null, page = null, page_size = null } = {}) {
  let params = {}
  if (title) { params.title = title }
  if (status !== null) { params.status = status }
  if (page) { params.page = page }
  if (page_size) { params.page_size = page_size }
  return request({ method: 'GET', url: '/api/admin/course/presentations', params })
}

function getPresentation ({ id }) {
  return request({ method: 'GET', url: `/api/admin/course/presentations/${id}` })
}

function deletePresentation ({ id }) {
  return request({ method: 'DELETE', url: `/api/admin/course/presentations/${id}` })
}

function createPresentation (data) {
  return request({ method: 'POST', url: '/api/admin/course/presentations', data })
}

function patchPresentation (id, data) {
  return request({ method: 'PATCH', url: `/api/admin/course/presentations/${id}`, data })
}

function getPresentationForm (form) {
  return request({ method: 'GET', url: `/api/admin/course/presentations/forms/${form}` })
}

export default {
  course: {
    listCourse,
    getCourse,
    createCourse,
    patchCourse,
    deleteCourse,
    getCourseSearchForm: () => getCourseForm('search'),
    getCourseEditForm: () => getCourseForm('edit'),

    listPresentation,
    getPresentation,
    createPresentation,
    patchPresentation,
    deletePresentation,
    getPresentationSearchForm: () => getPresentationForm('search'),
    getPresentationEditForm: () => getPresentationForm('edit'),
  },
}
