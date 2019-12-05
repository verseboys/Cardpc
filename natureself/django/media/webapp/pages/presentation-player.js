import Swiper from 'swiper'
import 'swiper/dist/css/swiper.css'
import request from '@webapp/request.js'
import $ from 'jquery'

import 'bootstrap-vue/dist/bootstrap-vue.css'
import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
Vue.use(BootstrapVue)

// eslint-disable-next-line no-new
let modalApp = new Vue({
  methods: {
    show (title, message, buttonText) {
      this.$bvModal.msgBoxOk(
        message,
        {
          title: title,
          okTitle: buttonText,
          okVariant: 'success',
          centered: true,
        },
      )
    },
  },
  template: '<div></div>',
})

class LessonWatchRecordTracker {
  constructor () {
    let lessonMeta = document.querySelector('#lesson-meta').dataset
    this.lessonId = lessonMeta.lessonId
    this.watchedSeconds = parseInt(lessonMeta.watchedSeconds || 0)
    this.minWatchSeconds = (lessonMeta.minWatchSeconds || 0)

    // minWatchMinutes 是一个快捷方式（因为在展示时需要按分钟展示）
    this.minWatchMinutes = this.minWatchSeconds / 60

    // 本地未上报的时间
    this.notReportedSeconds = this.loadNotReported()
    // 本地累加时间的计时器
    this.ticker = null
    // 定时上报计时器
    this.reportTicker = null
  }

  getTotalWatchedSeconds () {
    return this.watchedSeconds + this.notReportedSeconds
  }

  startTicker () {
    if (!this.ticker) {
      let vm = this
      this.ticker = setInterval(() => {
        vm.notReportedSeconds++
        vm.updateWatchedTimer()
      }, 1000)
    }
  }

  stopTicker () {
    if (this.ticker) {
      clearInterval(this.ticker)
      this.ticker = null
    }
  }

  reportWatchedSeconds () {
    let vm = this
    vm.cacheNotReported()
    request({ method: 'POST', url: window.location.href, data: { add_watch_time: this.notReportedSeconds } }).then(res => {
      if (res.status === 200) {
        vm.clearNotReported()
        vm.notReportedSeconds = 0
        vm.watchedSeconds = res.data.data.watched_seconds
      }
    })
  }

  reportWatchEnd () {
    let vm = this
    vm.cacheNotReported()
    request({
      method: 'POST',
      url: window.location.href,
      data: {
        watch_end: true,
        add_watch_time: this.notReportedSeconds,
      },
    }).then(res => {
      if (res.status === 200) {
        vm.clearNotReported()
        vm.notReportedSeconds = 0
        vm.watchedSeconds = res.data.data.watched_seconds

        if (!res.data.data.mark_watched) {
          modalApp.show('课程提醒', '这么快就学完了，要不要再仔细看看', '好的')
        } else {
          vm.markLessonWatched()
        }
      }
    })
  }

  startReportTicker () {
    if (!this.reportTicker) {
      let vm = this
      this.reportTicker = setInterval(() => { vm.reportWatchedSeconds() }, 10000)
    }
  }

  stopReportTicker () {
    if (this.reportTicker) {
      clearInterval(this.reportTicker)
      this.reportTicker = null
    }
  }

  cacheNotReported () {
    let watchRecords = JSON.parse(localStorage.getItem('PresentationWatchRecords') || '{}')
    watchRecords[this.lessonId] = this.notReportedSeconds
    localStorage.setItem('PresentationWatchRecords', JSON.stringify(watchRecords))
  }

  clearNotReported () {
    let watchRecords = JSON.parse(localStorage.getItem('PresentationWatchRecords') || '{}')
    watchRecords[this.lessonId] = 0
    localStorage.setItem('PresentationWatchRecords', JSON.stringify(watchRecords))
  }

  loadNotReported () {
    let watchRecords = JSON.parse(localStorage.getItem('PresentationWatchRecords') || '{}')
    return watchRecords[this.lessonId] || 0
  }

  markLessonWatched () {
    let statusElem = document.querySelector('#course-info a.current span.lesson-status')
    if (statusElem) { statusElem.classList.add('watched') }
  }

  updateWatchedTimer () {
    let timerDom = document.querySelector('#watchedTimer')
    let watchedSeconds = this.getTotalWatchedSeconds()
    let text = `已学习 ${this.formatDuration(watchedSeconds)}`
    let color = watchedSeconds >= this.minWatchSeconds ? 'white' : 'red'

    timerDom.textContent = text
    timerDom.style.color = color
  }

  formatDuration (seconds) {
    // 返回 hh:mm:ss （小时数可能会大于 24）
    let hh = parseInt(seconds / 3600)
    let mm = parseInt((seconds % 3600) / 60)
    let ss = seconds % 60

    hh = hh >= 10 ? hh : hh === 0 ? '00' : '0' + hh
    mm = mm >= 10 ? mm : mm === 0 ? '00' : '0' + mm
    ss = ss >= 10 ? ss : ss === 0 ? '00' : '0' + ss

    return `${hh}:${mm}:${ss}`
  }
}

let watchRecordTracker = new LessonWatchRecordTracker()
watchRecordTracker.startTicker()
watchRecordTracker.startReportTicker()

if (watchRecordTracker.watchedSeconds === 0 && watchRecordTracker.minWatchSeconds > 0) {
  modalApp.show('课程提醒', `本 PPT 课程请至少学习 ${watchRecordTracker.minWatchMinutes} 分钟`, '好的')
}

let thumbnailSwiper = new Swiper('.ppt-thumbnail', {
  allowTouchMove: true,
  slidesPerView: 6,
  spaceBetween: 4,
  watchSlidesVisibility: true,
  watchSlidesProgress: true,
  lazy: {
    loadPrevNext: true,
  },
  navigation: {
    nextEl: '.thumbnail-button-next',
    prevEl: '.thumbnail-button-prev',
  },
})

// eslint-disable-next-line no-new
let mainSwiper = new Swiper('.ppt-main', {
  spaceBetween: 10,
  navigation: {
    nextEl: '.main-button-next',
    prevEl: '.main-button-prev',
  },
  lazy: {
    loadPrevNext: true,
  },
  pagination: {
    el: '.main-swiper-pagination',
    type: 'fraction',
  },
  on: {
    reachEnd: () => watchRecordTracker.reportWatchEnd(),
  },
  thumbs: {
    swiper: thumbnailSwiper,
  },
})

let fullscreenSwiper = null

function toggleFullscreen () {
  if (fullscreenSwiper) {
    mainSwiper.slideTo(fullscreenSwiper.realIndex, 0)
    $('.ppt-fullscreen').fadeOut('fast')
    fullscreenSwiper.destroy()
    fullscreenSwiper = null
    document.removeEventListener('keyup', ESCcloseFullscreen, false)
  } else {
    fullscreenSwiper = initFullscreenSwiper()
    $('.ppt-fullscreen').fadeIn('fast')
    document.addEventListener('keyup', ESCcloseFullscreen, false)
  }
}
// 通过ESC关闭全屏
function ESCcloseFullscreen (e) {
  if (e.key === 'Escape') {
    toggleFullscreen()
  }
}

function initFullscreenSwiper () {
  return new Swiper('.ppt-fullscreen', {
    width: document.documentElement.clientWidth,
    initialSlide: mainSwiper.realIndex,
    lazy: {
      loadPrevNext: true,
    },
    pagination: {
      el: '.swiper-pagination',
      type: 'fraction',
    },
    navigation: {
      nextEl: '.fullscreen-button-next',
      prevEl: '.fullscreen-button-prev',
    },
    on: {
      reachEnd: () => watchRecordTracker.reportWatchEnd(),
    },
  })
}

function reinitFullscreenSwiper () {
  // 如果当前不在全屏状态，则立即退出逻辑
  if (!fullscreenSwiper) { return }

  mainSwiper.slideTo(fullscreenSwiper.realIndex, 0)
  fullscreenSwiper.destroy()
  fullscreenSwiper = initFullscreenSwiper()
  $('.ppt-fullscreen').show()
}

// 注意，一个页面中可能有多个 fullscreen-controller
$('.fullscreen-controller').click(toggleFullscreen)

// 当屏幕大小发生变化时（包括横屏、竖屏切换时），重新初始化全屏 swiper
window.addEventListener('resize', reinitFullscreenSwiper)
