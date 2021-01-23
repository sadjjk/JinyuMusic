$(document).keydown(function (event) {
    // /? 显示/隐藏快捷键列表
    if (event.keyCode === 191) {
        if ($('.cfp-hotkeys-container.in').length === 1) {
            $('.cfp-hotkeys-container').removeClass('in')
        } else {
            $('.cfp-hotkeys-container').addClass('in')
        }
    }

    // p 播放/暂停
    if (event.keyCode === 80) {
        ap.toggle();
    }

    // [{ 上一首
    if (event.keyCode === 219) {
        ap.skipBack();
    }

    // ]} 下一首
    if (event.keyCode === 221) {
        ap.skipForward();
    }

    // Q 静音/取消静音
    if (event.keyCode === 81) {
        $('.aplayer-icon-volume-down').trigger("click");

    }

    // L 打开/关闭播放列表
    if (event.keyCode === 76){
        $('.aplayer-icon-menu').trigger("click");
    }

    // W 切换播放模式（顺序/随机）
        if (event.keyCode === 87){
        $('.aplayer-icon-order').trigger("click");
    }
});