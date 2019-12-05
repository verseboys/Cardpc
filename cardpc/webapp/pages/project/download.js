import $ from 'jquery'

$(function () {
  $('.project-download ul li').on('click', function () {
    $(this).addClass('selected').siblings().removeClass('selected')

    let tag = $(this).html()
    let docItemElem = $('.project-download-file .documents-item')
    docItemElem.each(function (item) {
      let docItemTag = $(this).data('tag')
      if (tag === '全部') {
        docItemElem.addClass('d-flex').show()
        return
      }
      if (tag === docItemTag) $(this).addClass('d-flex').show().siblings().removeClass('d-flex').hide()
    })
  })
})
