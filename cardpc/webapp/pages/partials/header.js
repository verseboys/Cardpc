// 适用于 partials/header.html

import $ from 'jquery'

$(function () {
  // 公共导航
  var index = $('body').attr('data-nav')
  $('.tab-menu').children().eq(index).addClass('hover')
  $('.tab-menu li').mouseover(function () {
    $(this).addClass('hover')
    $(this).children('.innerPage').fadeIn()
    $(this).siblings().removeClass('hover')
  })
  $('.tab-menu li').mouseleave(function () {
    $(this).removeClass('hover')
    $(this).children('.innerPage').fadeOut()
    $('.tab-menu').children().eq(index).addClass('hover')
  })
})
