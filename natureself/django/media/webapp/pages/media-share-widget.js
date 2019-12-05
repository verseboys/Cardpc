import QRCode from 'qrcodejs2'
import $ from 'jquery'

function isWX () {
  return navigator.appVersion.match(/MicroMessenger/i)
}

$('#media-share-widget').on('click', function () {
  if (isWX()) {
    $('.wx-share-box').fadeIn()
  } else {
    $('.qrcode-box').is(':hidden') ? $('.qrcode-box').fadeIn() : $('.qrcode-box').fadeOut()
  }
})
$('.wx-share-box').on('click', function () {
  setTimeout(function () {
    $('.wx-share-box').fadeOut()
  }, 500)
})

// eslint-disable-next-line no-new
new QRCode('qrcode-current-location', {
  width: 83,
  height: 83,
  text: window.location.href,
})
