// 布局相关的功能函数

function autoMainHeight ({ headerId = 'header', mainId = 'main', footerId = 'footer' } = {}) {
  // 设置正文 main 的最小高度，计算方法为：屏幕高度 - 导航高度 - 页脚高度
  // 当正文内容比较少时，页脚总是显示在页面底部，当正文内容比较多时（超出屏幕高度），页脚显示在正文后面
  // 注意，#header, #main, #footer 都不能设置 margin，因为 margin 的大小无法简易的在 js 里获取
  // 这些容器里如果需要上下空间，请用 padding。
  let header = document.getElementById(headerId)
  let main = document.getElementById(mainId)
  let footer = document.getElementById(footerId)

  if (!header || !main || !footer) {
    return
  }

  let minHeight = window.innerHeight - header.offsetHeight - footer.offsetHeight
  minHeight = minHeight > 0 ? minHeight : 0
  main.style.minHeight = `${minHeight}px`
}

function setupResponsiveLayoutSizes () {
  autoMainHeight()

  window.addEventListener('resize', () => {
    autoMainHeight()
  })
}

export default {
  setupResponsiveLayoutSizes,
}
