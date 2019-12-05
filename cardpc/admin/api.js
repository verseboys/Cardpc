import request from '@webapp/request.js'
import mediaApi from '@ns-media/admin/api.js'

function listNews ({ title = null, author_name = null, publish_range = null, page = null, page_size = null } = {}) {
  let params = {}
  if (title) { params.title = title }
  if (author_name) { params.author_name = author_name }
  if (publish_range) { params.publish_range = `${publish_range[0]},${publish_range[1]}` }
  if (page) { params.page = page }
  if (page_size) { params.page_size = page_size }
  return request({ method: 'GET', url: '/api/admin/cardpc/zhixiang/news', params })
}

function getNews ({ id }) {
  return request({ method: 'GET', url: `/api/admin/cardpc/zhixiang/news/${id}` })
}

function createNews (data) {
  return request({ method: 'POST', url: '/api/admin/cardpc/zhixiang/news', data })
}

function patchNews (id, data) {
  return request({ method: 'PATCH', url: `/api/admin/cardpc/zhixiang/news/${id}`, data })
}

function deleteNews ({ id }) {
  return request({ method: 'DELETE', url: `/api/admin/cardpc/zhixiang/news/${id}` })
}

function getNewsSearchForm () {
  return request({ method: 'GET', url: '/api/admin/cardpc/zhixiang/news/forms/search' })
}

function getNewsEditForm () {
  return request({ method: 'GET', url: '/api/admin/cardpc/zhixiang/news/forms/edit' })
}

function listExamination ({ page = null, page_size = null } = {}) {
  let params = {}
  if (page) { params.page = page }
  if (page_size) { params.page_size = page_size }
  return request({ method: 'GET', url: '/api/admin/cardpc/zhixiang/examinations', params })
}

function getExamination ({ id }) {
  return request({ method: 'GET', url: `/api/admin/cardpc/zhixiang/examinations/${id}` })
}

function createExamination (data) {
  return request({ method: 'POST', url: `/api/admin/cardpc/zhixiang/examinations`, data })
}

function patchExamination (id, data) {
  return request({ method: 'PATCH', url: `/api/admin/cardpc/zhixiang/examinations/${id}`, data })
}

function deleteExamination ({ id }) {
  return request({ method: 'DELETE', url: `/api/admin/cardpc/zhixiang/examinations/${id}` })
}

function getExaminationForm (form) {
  return request({ method: 'GET', url: `/api/admin/cardpc/zhixiang/examinations/forms/${form}` })
}

function listTraining ({ username = null, page = null, page_size = null, a_status = null, b_status = null, c_status = null, d_status = null } = {}) {
  let params = {}
  if (username) { params.username = username }
  if (page) { params.page = page }
  if (page_size) { params.page_size = page_size }
  if (a_status) { params.a_status = a_status }
  if (b_status) { params.b_status = b_status }
  if (c_status) { params.c_status = c_status }
  if (d_status) { params.d_status = d_status }
  return request({ method: 'GET', url: '/api/admin/cardpc/zhixiang/training', params })
}

function getTraining ({ id }) {
  return request({ method: 'GET', url: `/api/admin/cardpc/zhixiang/training/${id}` })
}

function patchTraining (id, data) {
  return request({ method: 'PATCH', url: `/api/admin/cardpc/zhixiang/training/${id}`, data })
}

function exportTrainingData () {
  return request({ method: 'POST', url: `/api/admin/cardpc/zhixiang/training/export`, responseType: 'blob' })
}

function trainingPassQualification (id, examination) {
  return request({
    method: 'PATCH',
    url: `/api/admin/cardpc/zhixiang/training/${id}`,
    data: { examination, c_status: 3 },
  })
}

function trainingRejectQualification (id) {
  return request({
    method: 'PATCH',
    url: `/api/admin/cardpc/zhixiang/training/${id}`,
    data: { c_status: 4 },
  })
}

function getTrainingForm (form) {
  return request({ method: 'GET', url: `/api/admin/cardpc/zhixiang/training/forms/${form}` })
}

function listProject (params) {
  return request({ method: 'GET', url: `/api/admin/cardpc/project/projects`, params })
}

function getProject ({ id }) {
  return request({ method: 'GET', url: `/api/admin/cardpc/project/projects/${id}` })
}

function createProject (data) {
  return request({ method: 'POST', url: `/api/admin/cardpc/project/projects`, data })
}

function patchProject (id, data) {
  return request({ method: 'PATCH', url: `/api/admin/cardpc/project/projects/${id}`, data })
}

function deleteProject ({ id }) {
  return request({ method: 'DELETE', url: `/api/admin/cardpc/project/projects/${id}` })
}

function getProjectForm (form) {
  return request({ method: 'GET', url: `/api/admin/cardpc/project/projects/forms/${form}` })
}

function listDocument (params) {
  return request({ method: 'GET', url: `/api/admin/cardpc/project/documents`, params })
}

function getDocument ({ id }) {
  return request({ method: 'GET', url: `/api/admin/cardpc/project/documents/${id}` })
}

function createDocument (data) {
  return request({ method: 'POST', url: `/api/admin/cardpc/project/documents`, data })
}

function patchDocument (id, data) {
  return request({ method: 'PATCH', url: `/api/admin/cardpc/project/documents/${id}`, data })
}

function deleteDocument ({ id }) {
  return request({ method: 'DELETE', url: `/api/admin/cardpc/project/documents/${id}` })
}

function getDocumentForm (form) {
  return request({ method: 'GET', url: `/api/admin/cardpc/project/documents/forms/${form}` })
}

function listPage (params) {
  return request({ method: 'GET', url: `/api/admin/cardpc/project/pages`, params })
}

function getPage ({ id }) {
  return request({ method: 'GET', url: `/api/admin/cardpc/project/pages/${id}` })
}

function createPage (data) {
  return request({ method: 'POST', url: `/api/admin/cardpc/project/pages`, data })
}

function patchPage (id, data) {
  return request({ method: 'PATCH', url: `/api/admin/cardpc/project/pages/${id}`, data })
}

function deletePage ({ id }) {
  return request({ method: 'DELETE', url: `/api/admin/cardpc/project/pages/${id}` })
}

function getPageForm (form, params = {}) {
  return request({ method: 'GET', url: `/api/admin/cardpc/project/pages/forms/${form}`, params })
}

function getPagePanel (panel) {
  return request({ method: 'GET', url: `/api/admin/cardpc/project/pages/panels/${panel}` })
}

function getPageTypes (params = {}) {
  return request({ method: 'GET', url: `/api/admin/cardpc/project/pages/pagetypes`, params })
}

function getMenu ({ id }) {
  return request({ method: 'GET', url: `/api/admin/cardpc/project/menus/${id}` })
}

function patchMenu (id, data) {
  return request({ method: 'PATCH', url: `/api/admin/cardpc/project/menus/${id}`, data })
}

function getMenuForm (form) {
  return request({ method: 'GET', url: `/api/admin/cardpc/project/menus/forms/${form}` })
}

function getCarouselItem ({ id }) {
  return request({ method: 'GET', url: `/api/admin/cardpc/project/carousel/${id}` })
}

function createCarouselItem (data) {
  return request({ method: 'POST', url: `/api/admin/cardpc/project/carousel`, data })
}

function deleteCarouselItem ({ id }) {
  return request({ method: 'DELETE', url: `/api/admin/cardpc/project/carousel/${id}` })
}

function patchCarouselItem (id, data) {
  return request({ method: 'PATCH', url: `/api/admin/cardpc/project/carousel/${id}`, data })
}

function getCarouselForm (form) {
  return request({ method: 'GET', url: `/api/admin/cardpc/project/carousel/forms/${form}` })
}

export default {
  cardpc: {
    zhixiang: {
      listNews,
      getNews,
      createNews,
      patchNews,
      deleteNews,
      getNewsSearchForm,
      getNewsEditForm,

      listExamination,
      getExamination,
      createExamination,
      patchExamination,
      deleteExamination,
      getExaminationSearchForm: () => getExaminationForm('search'),
      getExaminationEditForm: () => getExaminationForm('edit'),

      listTraining,
      getTraining,
      patchTraining,
      trainingPassQualification,
      trainingRejectQualification,
      getTrainingSearchForm: () => getTrainingForm('search'),
      getTrainingEditForm: () => getTrainingForm('edit'),
      exportTrainingData,
    },

    project: {
      listProject,
      getProject,
      createProject,
      patchProject,
      deleteProject,
      getProjectSearchForm: () => getProjectForm('search'),
      getProjectEditForm: () => getProjectForm('edit'),

      listDocument,
      getDocument,
      createDocument,
      patchDocument,
      deleteDocument,
      getDocumentSearchForm: () => getDocumentForm('search'),
      getDocumentEditForm: () => getDocumentForm('edit'),

      listPage,
      getPage,
      createPage,
      patchPage,
      deletePage,
      getPageForm,
      getPageSearchForm: () => getPageForm('search'),
      getPageEditForm: (pagetype) => getPageForm('edit', { pagetype }),
      getPagePanel,
      getPageTypes,

      getMenu,
      patchMenu,
      getMenuForm,

      uploadGalleryImage: (args) => mediaApi.media.uploadFile('cardpcgalleryimages', 'gallery', args),
      patchGalleryImage: (args) => mediaApi.media.patchFile('cardpcgalleryimages', args),

      getCarouselItem,
      deleteCarouselItem,
      createCarouselItem,
      patchCarouselItem,
      getCarouselSearchForm: () => getCarouselForm('search'),
      getCarouselEditForm: () => getCarouselForm('edit'),
    },
  },
}
