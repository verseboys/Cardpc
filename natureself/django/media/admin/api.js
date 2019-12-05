import request from '@webapp/request.js'

function listFile (variant, {
  ownerId = null,
  filename = null,
  sizeLt = null, sizeGt = null,
  bucket = null,
  orderBy = null,
  page = null, pageSize = null,
} = {}) {
  let params = {}
  if (ownerId) { params.owner = ownerId }
  if (filename) { params.filename = filename }
  if (sizeLt) { params.size_lt = sizeLt }
  if (sizeGt) { params.size_gt = sizeGt }
  if (bucket) { params.bucket = bucket }
  if (orderBy) { params.order_by = orderBy }
  if (page) { params.page = page }
  if (pageSize) { params.page_size = pageSize }

  return request({ method: 'GET', url: `/api/admin/media/${variant}`, params })
}

function getFile (variant, { id }) {
  return request({ method: 'GET', url: `/api/admin/media/${variant}/${id}` })
}

function deleteFile (variant, { id }) {
  return request({ method: 'DELETE', url: `/api/admin/media/${variant}/${id}` })
}

function patchFile (variant, { id, filename = null, title = null } = {}) {
  let data = {}
  if (filename !== null) { data.filename = filename }
  if (title !== null) { data.title = title }
  return request({ method: 'PATCH', url: `/api/admin/media/${variant}/${id}`, data })
}

function uploadFile (variant, bucket, param) {
  // 本函数有两种调用情况，一种是我们自己的代码调用，一种是 el-upload 的 http-request
  // 如果是前者，那么 param 中只需包含一个字段：file
  // 如果是 el-upload，那么 param 中还会包含一些回调函数（onProgress, onSuccess, onError）
  //
  // 在我们自己调用时，我们直接返回 request()，也就是一个 Promise，由调用者处理后续逻辑
  // 如果是 el-upload 调用，我们则直接在这里面处理好各种回调
  let isElUpload = !!param.onProgress

  let headers = { 'Content-Type': 'multipart/form-data' }
  let form = new FormData()
  form.append('bucket', bucket)
  form.append('file', param.file)

  if (!isElUpload) {
    return request({ method: 'POST', url: `/api/admin/media/${variant}`, data: form, headers })
  }

  return request({
    method: 'POST',
    url: `/api/admin/media/${variant}`,
    data: form,
    headers,
    // 不知道为什么，onUploadProgress 函数从来没有被调用过
    onUploadProgress: event => {
      let percent = (event.loaded / event.total * 100 | 0)
      param.onProgress({ percent })
    },
  }).then(response => {
    if (response.data.code === 0) {
      return response
    } else {
      return Promise.reject(response)
    }
  })
}

function listPresentation ({ title = null, page = null, page_size = null } = {}) {
  let params = {}
  if (title) { params.title = title }
  if (page) { params.page = page }
  if (page_size) { params.page_size = page_size }
  return request({ method: 'GET', url: '/api/admin/media/presentations', params })
}

function getPresentation ({ id }) {
  return request({ method: 'GET', url: `/api/admin/media/presentations/${id}` })
}

function createPresentation (data) {
  return request({ method: 'POST', url: '/api/admin/media/presentations', data })
}

function patchPresentation (id, data) {
  return request({ method: 'PATCH', url: `/api/admin/media/presentations/${id}`, data })
}

function deletePresentation ({ id }) {
  return request({ method: 'DELETE', url: `/api/admin/media/presentations/${id}` })
}

function getPresentationForm (form) {
  return request({ method: 'GET', url: `/api/admin/media/presentations/forms/${form}` })
}

function listVideo (params) {
  return request({ method: 'GET', url: `/api/admin/media/videos`, params })
}

function getVideo ({ id }) {
  return request({ method: 'GET', url: `/api/admin/media/videos/${id}` })
}

function createVideo (data) {
  return request({ method: 'POST', url: `/api/admin/media/videos`, data })
}

function patchVideo (id, data) {
  return request({ method: 'PATCH', url: `/api/admin/media/videos/${id}`, data })
}

function deleteVideo ({ id }) {
  return request({ method: 'DELETE', url: `/api/admin/media/videos/${id}` })
}

function getVideoForm (form) {
  return request({ method: 'GET', url: `/api/admin/media/videos/forms/${form}` })
}

export default {
  media: {
    uploadFile,
    patchFile,

    listImage: (args) => listFile('images', args),
    getImage: (args) => getFile('images', args),
    deleteImage: (args) => deleteFile('images', args),
    imageUploadUrl: '/api/admin/media/images',
    uploadImageTo: (bucket) => (args) => uploadFile('images', bucket, args),

    listDocument: (args) => listFile('documents', args),
    getDocument: (args) => getFile('documents', args),
    patchDocument: (args) => patchFile('documents', args),
    deleteDocument: (args) => deleteFile('documents', args),
    documentUploadUrl: '/api/admin/media/documents',
    uploadDocumentTo: (bucket) => (args) => uploadFile('documents', bucket, args),

    listSlide: (args) => listFile('slides', args),
    getSlide: (args) => getFile('slides', args),
    deleteSlide: (args) => deleteFile('slides', args),
    slideUploadUrl: '/api/admin/media/slides',
    uploadSlide: (args) => uploadFile('slides', 'slides', args),

    listPresentation,
    getPresentation,
    createPresentation,
    patchPresentation,
    deletePresentation,
    getPresentationSearchForm: () => getPresentationForm('search'),
    getPresentationEditForm: () => getPresentationForm('edit'),

    listVideo,
    getVideo,
    createVideo,
    patchVideo,
    deleteVideo,
    getVideoSearchForm: () => getVideoForm('search'),
    getVideoEditForm: () => getVideoForm('edit'),
  },
}
