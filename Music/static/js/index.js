var _currPage = 1;

$(document).ready(function () {


    var obj = $('.nav.masthead-nav li').filter('.active');
    showRecommendPlaylist(obj);

    const curPlayingList = getLocalObj('curPlayingList');
    if (curPlayingList != null) {
        ap.list.add(curPlayingList);
    }

    const curPlayingSong = getLocalObj('curPlayingSong');
    if (curPlayingSong != null) {
        const curPlayingIndex = ap.list.audios.findIndex(item => item.song_id === curPlayingSong.song_id && item.platform === curPlayingSong.platform)
        ap.list.switch(curPlayingIndex);
    }

    // 初始化 加载收藏的歌单
    var favoriteList = getLocalObj('favoriteList');
    $(".favorite-playlist").html(template("favorite-playlist-tmpl", {
        playlists: favoriteList
    }));

    // 初始化 加载我的歌单
    var myPlaylist = getLocalObj('myPlaylist');
    $(".nav.my-playlist").html(template("my-playlist-tmpl", {
        playlists: myPlaylist
    }));

    // 增加清空播放列表
    $('.aplayer-time').append("<div class=\"aplayer-volume-wrap\">\n<button type=\"button\" onclick=\"clearPlayer()\" class=\"aplayer-icon \">\n<svg t=\"1607262172047\" class=\"icon\" viewBox=\"0 0 1024 1024\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" p-id=\"5629\" width=\"32\" height=\"32\"><path d=\"M221.115733 911.633067c0 18.961067 16.5376 34.286933 37.000534 34.286933h580.437333c20.462933 0 37.000533-15.325867 37.000533-34.286933V379.682133H221.115733v531.950934z m455.2704-442.658134c0-6.5024 5.717333-11.793067 12.731734-11.793066h3.328c7.0144 0 12.731733 5.290667 12.731733 11.793066V852.309333c0 6.5024-5.717333 11.793067-12.731733 11.793067h-3.328c-7.0144 0-12.731733-5.290667-12.731734-11.793067V468.974933z m-142.506666 0c0-6.5024 5.717333-11.793067 12.731733-11.793066h3.328c7.0144 0 12.731733 5.290667 12.731733 11.793066V852.309333c0 6.5024-5.717333 11.793067-12.731733 11.793067h-3.328c-7.0144 0-12.731733-5.290667-12.731733-11.793067V468.974933z m-142.6432 0c0-6.5024 5.717333-11.793067 12.731733-11.793066h3.328c7.0144 0 12.731733 5.290667 12.731733 11.793066V852.309333c0 6.5024-5.717333 11.793067-12.731733 11.793067h-3.328c-7.0144 0-12.731733-5.290667-12.731733-11.793067V468.974933zM902.792533 153.480533H698.5216c1.6896-1.6896 2.730667-4.0448 2.730667-6.656V91.7504c0-5.12-4.164267-9.403733-9.403734-9.403733H404.548267c-5.239467 0-9.403733 4.164267-9.403734 9.403733v55.074133c0 2.6112 1.041067 4.9664 2.730667 6.656H193.7408c-19.985067 0-36.283733 16.298667-36.283733 36.283734v109.2096c0 19.985067 16.298667 36.283733 36.283733 36.283733h709.034667c19.985067 0 36.283733-16.298667 36.283733-36.283733v-109.329067c0.017067-19.985067-16.2816-36.164267-36.266667-36.164267z\" p-id=\"5630\"></path></svg>\n</button>\n</div>");

    // 增加到我的歌单
    $('.aplayer-time').append("<div class=\"aplayer-volume-wrap\"><button type=\"button\" onclick=\"addMyPlaylistDialog('playerlist',event)\" class=\"aplayer-icon \">\n" +
        "<svg t=\"1607256546048\" class=\"icon\" viewBox=\"0 0 1024 1024\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" p-id=\"8092\" width=\"32\" height=\"32\"><path d=\"M916.746 444.643h-334.597v-334.597c0-8.010-6.554-14.563-14.563-14.563h-111.047c-8.010 0-14.563 6.554-14.563 14.563v334.597h-334.597c-8.010 0-14.563 6.554-14.563 14.563v111.047c0 8.010 6.554 14.563 14.563 14.563h334.597v334.597c0 8.010 6.554 14.563 14.563 14.563h111.047c8.010 0 14.563-6.554 14.563-14.563v-334.597h334.597c8.010 0 14.563-6.554 14.563-14.563v-111.047c0-8.010-6.554-14.563-14.563-14.563z\" fill=\"\" p-id=\"8093\"></path></svg></button></div>")

});


// 生成guid
function guid() {
    function s4() {
        return Math.floor((1 + Math.random()) * 0x10000)
            .toString(16)
            .substring(1);
    }

    return `${s4() + s4()}-${s4()}-${s4()}-${
        s4()}-${s4()}${s4()}${s4()}`;
}


// 获取本地localStorage对象
function getLocalObj(key) {
    if (localStorage.getItem(key) != null) {
        return JSON.parse(localStorage.getItem(key));
    } else {
        return null
    }
}

function getCurDateStr(isFull = 0) {
    var mydate = new Date();
    var dateStr = mydate.getFullYear() + '-' + (mydate.getMonth() + 1) + '-' + mydate.getDate()
    if (isFull) {
        dateStr = dateStr + ' ' + mydate.getHours() + ':' + mydate.getMinutes() + ':' + mydate.getSeconds()
    }
    return dateStr
}

// 关闭通用浮窗
function closeDialog() {
    $('.shadow').addClass('ng-hide');
    $('.dialog').addClass('ng-hide');
    $('.dialog .dialog-body').children().addClass('ng-hide');
    $(".dialog-playlist .detail-add").attr('data-from', '');
}

// 关闭歌曲歌词页浮窗
function closeSongDetailDialog() {
    $('.songdetail-page').addClass('ng-hide')
}

// 关闭快捷键浮窗
function closeCheatSheetDialog() {
    $('.cfp-hotkeys-container').removeClass('in')
}

// 打开快捷键浮窗
function showCheatSheetDialog() {
    $('.cfp-hotkeys-container').addClass('in')
}

// 歌曲歌词详情页浮窗
function showSongDetailDialog(flag = 1) {

    function parseLyric(lyric) {
        var lines = lyric.split('\n'),
            result = [];

        lines[lines.length - 1].length === 0 && lines.pop();
        _.each(lines, function (data, step) {
            var index = data.indexOf(']');
            var time = data.substring(0, index + 1),
                value = data.substring(index + 1);
            var timeString = time.substring(1, time.length - 2);
            var timeArr = timeString.split(':');
            result.push([parseInt(timeArr[0], 10) * 60 + parseFloat(timeArr[1]), value]);

        });
        result.sort(function (a, b) {
            return a[0] - b[0];
        });
        return result;
    }

    function loadLyric(lyric) {
        var lyricContent = $('#lyric');
        _.each(lyric, function (content, index, $) {
            lyricContent.append('<p name="lyric" style="color:#000000" id=' + index + '>' + content[1] + '</p>');
        });
    }

    var is_flag = $('.songdetail-page.ng-hide').length === 1;
    if (flag == 0) {
        is_flag = is_flag == false
    }

    if (is_flag) {
        const curPlayingSong = getLocalObj('curPlayingSong');
        if (curPlayingSong != null) {
            $('.songdetail-page').removeClass('ng-hide');
            const curPlayingAp = ap.list.audios.find(item => item.song_id === curPlayingSong.song_id && item.platform === curPlayingSong.platform);
            $('.songdetail-wrapper').html(template('song-detail-tmpl',
                {
                    cover: curPlayingAp.cover,
                    name: curPlayingAp.name,
                    artist: curPlayingAp.artist,
                    artist_id: curPlayingAp.artist_id,
                    album: curPlayingAp.album,
                    album_id: curPlayingAp.album_id,
                    platform: curPlayingAp.platform
                }
            ));

            const lyric = parseLyric(curPlayingAp.lrc);
            loadLyric(lyric);


            ap.audio.ontimeupdate = function () {

                var audioCurrentTime = this.currentTime;

                if (this.ended) {
                        $('.playsong-detail').html(template('song-detail-tmpl',
                            {}
                        ));

                }

                const scrollTop = document.getElementById('lyric').scrollTop;

                for (var i = 0; i < lyric.length; i++) {
                    if (audioCurrentTime > lyric[i][0]) {
                        $('p[name=lyric]').css('color', '#000000');
                        $('p#' + i).css('color', '#ff4444');
                        const curTop = document.getElementById(i).offsetTop;
                        if (((curTop - scrollTop) >= 300) || ((scrollTop - curTop) >= 300)) {
                            document.getElementById('lyric').scrollTop = curTop - 300
                        }
                    }
                }
                ;

                if (this.currentTime < 10) {
                    document.getElementById('lyric').scrollTop = 0
                }
            }


        }
    } else {
        $('.songdetail-page').addClass('ng-hide');
    }

}


// 导入歌单Dialog
function loadPlaylistDialog() {
    $('.shadow').removeClass('ng-hide');
    $('.dialog').removeClass('ng-hide');
    $('.dialog .dialog-body').children().addClass('ng-hide');
    $('.dialog .dialog-header span:first').text('导入歌单');
    $('.dialog-open-url').removeClass('ng-hide');
    $('.dialog-open-url input').val('');


}

// 添加到我的歌单Dialog
function addMyPlaylistDialog(from, event) {
    if (from) {
        if (from === 'player') {
            event.stopPropagation();
        }
        $('.shadow').removeClass('ng-hide');
        $('.dialog').removeClass('ng-hide');
        $('.dialog .dialog-body').children().addClass('ng-hide');
        $('.dialog .dialog-header span:first').text('添加到我的歌单');
        $('.dialog .dialog-body .dialog-playlist').removeClass('ng-hide');

        var myPlaylist = getLocalObj('myPlaylist');
        $(".dialog-playlist.my-playlist").html(template("my-playlist-more-tmpl", {
            playlists: myPlaylist,
            from: from
        }));

        $(".dialog-playlist .detail-add").attr('data-from', from)
    }
}

// 新建歌单Dialog
function newMyPlaylistDialog() {
    $('.shadow').removeClass('ng-hide');
    $('.dialog').removeClass('ng-hide');
    $('.dialog .dialog-header span:first').text('新建歌单');
    $('.dialog .dialog-body .dialog-playlist').addClass('ng-hide');
    $('.dialog .dialog-body .dialog-newplaylist').removeClass('ng-hide');
    $('.dialog .dialog-body .dialog-newplaylist input').val('');
}

// 编辑我的歌单Dialog
function editMyPlaylistDialog() {

    $('.shadow').removeClass('ng-hide');
    $('.dialog').removeClass('ng-hide');
    $('.dialog .dialog-header span:first').text('编辑歌单');
    $('.dialog .dialog-body > div:not(.dialog-editplaylist)').addClass('ng-hide');
    $('.dialog .dialog-body .dialog-editplaylist').removeClass('ng-hide');
    $('.dialog .dialog-body .dialog-editplaylist input').val($('.playlist-detail .detail-head-title h2').text());

}

function loadPlaylistUrl() {
    $('.shadow').addClass('ng-hide');
    $('.dialog').addClass('ng-hide');
    var url = $('.dialog-open-url input').val();

    $.ajax({
        url: '/api/v1/playlist_load',
        type: 'get',
        dataType: 'json',
        data: {'url': url},
        success: function (resp) {
            if (resp.code !== 200) {
                $.load(resp.errmsg);
            } else {
                var favoriteList = getLocalObj('favoriteList');
                if (!favoriteList) {
                    favoriteList = []
                }

                const songlist_type = resp.data.songlist_type;
                const songlist_id = resp.data.songlist_id;
                const platform = resp.data.platform;
                const title = resp.data.title;
                if (favoriteList.length > 0 && favoriteList.filter(item => item.songlist_id === songlist_id && item.songlist_type === songlist_type && item.platform === platform).length > 0) {
                    $.load('该歌单已导入!')
                } else {
                    favoriteList.push(
                        {
                            'songlist_type': songlist_type,
                            'songlist_id': songlist_id,
                            'platform': platform,
                            'title': title
                        }
                    );

                    localStorage.setItem('favoriteList', JSON.stringify(favoriteList));
                    $(".nav.favorite-playlist").html(template("favorite-playlist-tmpl", {
                        playlists: favoriteList
                    }));
                    $.load('该歌单导入成功!');
                    setTimeout(function () {
                        $.loaded()
                    }, 1000);
                }
            }
        }
    })
    setTimeout(function () {
        $.loaded()
    }, 1000);
}

// 点击展示歌单
function showPlaylist(obj, platform, page_num = 1, page_size = 40) {
    const params = {
        'platform': platform,
        'page_num': page_num,
        'page_size': page_size
    };
    $(obj).siblings('.source-button').filter('.active').removeClass('active');
    $(obj).addClass('active');


    $('.loading_bottom').removeClass('ng-hide');

    $.ajax({
        url: '/api/v1/recommend_playlist',
        type: 'get',
        dataType: 'json',
        data: params,
        timeout: 5000,
        success: function (resp) {
            if (page_num === 1) {
                _currPage = 1;
                $(".playlist-covers").html(template("playlist-tmp", {
                    playlists: [],
                    func: 'showPlaylistDetail',
                    class_name: 'playlist'
                }));
                setTimeout(function () {
                    $(".playlist-covers").html(template("playlist-tmp", {
                        playlists: resp.data,
                        func: 'showPlaylistDetail',
                        class_name: 'playlist'
                    }));
                }, 300);
            } else {
                $(".playlist-covers").append(template("playlist-tmp", {
                    playlists: resp.data,
                    func: 'showPlaylistDetail',
                    class_name: 'playlist'
                }));
            }

        }
    })

}

// 推荐歌单底部追加
function handlePlayScroll(e) {

    var scrollTop = e.target.scrollTop;
    var scrollHeight = e.target.scrollHeight;
    var offsetHeight = Math.ceil(e.target.getBoundingClientRect().height);
    var currentHeight = Math.ceil(scrollTop + offsetHeight);
    const pre_platform = $('.recommand-page .source-button.active').attr('id');
    if (currentHeight >= scrollHeight) {
        _currPage += 1;
        showPlaylist($('#' + pre_platform), pre_platform, _currPage)
    }
};

// 展示左侧推荐歌单
async function showRecommendPlaylist(obj) {

    $('.recommand-page').removeClass('ng-hide');
    $('.recommand-page').siblings().addClass('ng-hide');
    $('.nav.masthead-nav li').filter('.active').removeClass('active');
    $(obj).addClass('active');

    const pre_platform = $('.recommand-page .source-button.active').attr('id');

    const getPlatform = () => new Promise(resolve => {
        $.get("/api/v1/platform", function (resp) {
            const data = resp.data.filter(item => item.is_support_playlist > 0);

            $(".recommand-page .source-list").html(template("platforms-tmpl", {
                platforms: data,
                func: 'showPlaylist'
            }));

            if ((pre_platform) && (data.filter(item => item.name === pre_platform).length === 1)) {
                platform = pre_platform
            } else {
                platform = data.sort(function (a, b) {
                    return b.is_support_playlist - a.is_support_playlist;
                })[0].name;
            }
            resolve(platform);
        });
    })
    const _platform = await getPlatform();

    $('li.toplist').addClass('ng-hide');
    $('li.fmlist').addClass('ng-hide');

    if ($('li.playlist').length === 0) {
        showPlaylist($('#' + _platform), _platform, 1)
    } else {
        $('#' + _platform).siblings('.source-button').filter('.active').removeClass('active');
        $('#' + _platform).addClass('active');
        $('li.playlist').removeClass('ng-hide');

    }


    const browserEle = document.querySelector('.browser.flex-scroll-wrapper');
    browserEle.addEventListener('scroll', handlePlayScroll);
}

// 点击展示排行榜
function showToplist(obj, platform) {
    $('.playlist-covers li').addClass('ng-hide');
    $('li.toplist').remove();
    $(obj).siblings('.source-button').filter('.active').removeClass('active');
    $(obj).addClass('active');
    $.ajax({
        url: '/api/v1/toplist',
        type: 'get',
        dataType: 'json',
        data: {'platform': platform},
        timeout: 5000,
        success: function (resp) {
            $(".playlist-covers").append(template("playlist-tmp", {
                playlists: resp.data,
                func: 'showToplistDetail',
                class_name: 'toplist'
            }));
        }
    });

    $('.loading_bottom').addClass('ng-hide')

}

// 左侧点击展示推荐排行榜
function showRecommendToplist(obj) {
    $('.recommand-page').removeClass('ng-hide');
    $('.recommand-page').siblings().addClass('ng-hide');
    $('.nav.masthead-nav li').filter('.active').removeClass('active');
    $(obj).addClass('active');

    const browserEle = document.querySelector('.browser.flex-scroll-wrapper');
    browserEle.removeEventListener('scroll', handlePlayScroll);

    const pre_platform = $('.source-button.active').attr('id');

    $('li.playlist').addClass('ng-hide');
    $('li.fmlist').addClass('ng-hide');


    $.get("/api/v1/platform", function (resp) {

        const data = resp.data.filter(item => item.is_support_toplist > 0);

        $(".recommand-page .source-list").html(template("platforms-tmpl", {
            platforms: data,
            func: 'showToplist'
        }));

        if ((pre_platform) && (data.filter(item => item.name === pre_platform).length === 1)) {
            platform = pre_platform
        } else {
            platform = data.sort(function (a, b) {
                return b.is_support_toplist - a.is_support_toplist;
            })[0].name;

        }


        $('li.playlist').addClass('ng-hide');
        if ($('li.toplist').length === 0) {
            showToplist($('#' + platform), platform)
        } else {
            $('#' + platform).siblings('.source-button').filter('.active').removeClass('active');
            $('#' + platform).addClass('active');
            $('li.toplist').removeClass('ng-hide')
        }


    });

}


// 左侧点击展示广播电台
function showRecommendFMlist(obj) {
    $('.recommand-page').removeClass('ng-hide');
    $('.recommand-page').siblings().addClass('ng-hide');
    $('.nav.masthead-nav li').filter('.active').removeClass('active');
    $(obj).addClass('active');

    const browserEle = document.querySelector('.browser.flex-scroll-wrapper');
    browserEle.removeEventListener('scroll', handlePlayScroll);

    $.get("/api/v1/fm/cate", function (resp) {

        const data = resp.data;
        $(".recommand-page .source-list").html(template("platforms-tmpl", {
            platforms: data,
            func: 'showFMlist'
        }));

        platform = data[0].name;

        $('.playlist-covers li').addClass('ng-hide');

        showFMlist($('#' + platform), platform)


    });

}


// 点击展示电台
function showFMlist(obj, cate_id) {
    $('.playlist-covers li').addClass('ng-hide');
    $('li.fmlist').remove();
    $(obj).siblings('.source-button').filter('.active').removeClass('active');
    $(obj).addClass('active');
    $.ajax({
        url: '/api/v1/fm/radio',
        type: 'get',
        dataType: 'json',
        data: {'cate_id': cate_id},
        timeout: 5000,
        success: function (resp) {
            $(".playlist-covers").append(template("playlist-tmp", {
                playlists: resp.data,
                func: 'showFMlistDetail',
                class_name: 'fmlist'
            }));
        }
    });

    $('.loading_bottom').addClass('ng-hide')

}




// 显示推荐歌单详情
function showPlaylistDetail(playlist_id, platform) {

    const browserEle = document.querySelector('.browser.flex-scroll-wrapper');
    browserEle.removeEventListener('scroll', handlePlayScroll);

    $('.playlist-page').removeClass('ng-hide');
    $('.playlist-page').siblings().addClass('ng-hide');
    $(".playlist-page .playlist-detail").html(template("songlist-detail-tmpl", {
        songlist: {
            'img_url': '/static/images/loading.svg',
            'title': '正在获取详情,请稍后',
            'songlist': [],
            'source_url': '',
            'song_total': 0
        }
    }));

    // 判断是否已收藏
    var favoriteList = getLocalObj('favoriteList');
    var isCollect = 0;
    if (favoriteList) {
        if (favoriteList.filter(item => item.songlist_type === 'playlist' && item.songlist_id === playlist_id && item.platform === platform).length > 0) {
            isCollect = 1;
        }
    }


    const params = {
        'platform': platform,
        'playlist_id': playlist_id
    };

    $.ajax({
        url: '/api/v1/playlist_detail',
        type: 'get',
        dataType: 'json',
        data: params,
        timeout: 5000,
        success: function (resp) {
            $(".playlist-page .playlist-detail").html(template("songlist-detail-tmpl", {
                songlist: resp.data,
                isCollect: isCollect,
                songlist_type: 'playlist',
                songlist_id: resp.data.playlist_id,
                from: 'playlist'
            }));
        }
    });

}


// 显示电台详情
function showFMlistDetail(radio_id, platform) {
    $('.playlist-page').removeClass('ng-hide');
    $('.playlist-page').siblings().addClass('ng-hide');
    $('.playlist-page .playlist-detail').html(template("songlist-detail-tmpl", {
        songlist: {
            'img_url': '/static/images/loading.svg',
            'title': '正在获取详情,请稍后',
            'songlist': [],
            'source_url': '',
            'song_total': 0
        }
    }));
    // 判断是否已收藏
    var favoriteList = getLocalObj('favoriteList');
    var isCollect = 0;
    if (favoriteList) {
        if (favoriteList.filter(item => item.songlist_type === 'fmlist' && item.songlist_id === radio_id && item.platform === platform).length > 0) {
            isCollect = 1;
        }
    }

    const params = {
        'platform': platform,
        'radio_id': radio_id
    };

    $.ajax({
        url: '/api/v1/fm/radio/detail',
        type: 'get',
        dataType: 'json',
        data: params,
        timeout: 10000,
        success: function (resp) {
            $(".playlist-page .playlist-detail").html(template("songlist-detail-tmpl", {
                songlist: resp.data,
                isCollect: isCollect,
                songlist_type: 'fmlist',
                songlist_id: resp.data.radio_id,
                from: 'playlist'
            }));
        }
    });

}




// 显示排行榜详情
function showToplistDetail(toplist_id, platform) {
    $('.playlist-page').removeClass('ng-hide');
    $('.playlist-page').siblings().addClass('ng-hide');
    $('.playlist-page .playlist-detail').html(template("songlist-detail-tmpl", {
        songlist: {
            'img_url': '/static/images/loading.svg',
            'title': '正在获取详情,请稍后',
            'songlist': [],
            'source_url': '',
            'song_total': 0
        }
    }));
    // 判断是否已收藏
    var favoriteList = getLocalObj('favoriteList');
    var isCollect = 0;
    if (favoriteList) {
        if (favoriteList.filter(item => item.songlist_type === 'toplist' && item.songlist_id === toplist_id && item.platform === platform).length > 0) {
            isCollect = 1;
        }
    }

    const params = {
        'platform': platform,
        'toplist_id': toplist_id
    };

    $.ajax({
        url: '/api/v1/toplist_detail',
        type: 'get',
        dataType: 'json',
        data: params,
        timeout: 10000,
        success: function (resp) {
            $(".playlist-page .playlist-detail").html(template("songlist-detail-tmpl", {
                songlist: resp.data,
                isCollect: isCollect,
                songlist_type: 'toplist',
                songlist_id: resp.data.toplist_id,
                from: 'playlist'
            }));
        }
    });

}

// 显示我的歌单详情
function showMyPlaylistDetail(obj, id) {
    $('.nav.masthead-nav li').filter('.active').removeClass('active');
    $(obj).addClass('active');
    const myPlaylistDetail = getLocalObj(id);
    $('.playlist-page').removeClass('ng-hide');
    $('.playlist-page').siblings().addClass('ng-hide');
    $('.playlist-page .playlist-detail').html(template("songlist-detail-tmpl", {
        songlist: {
            'img_url': '/static/images/loading.svg',
            'title': '正在获取详情,请稍后',
            'songlist': [],
            'source_url': '',
            'song_total': 0
        }
    }));
    $('.playlist-page .playlist-detail').html(template("songlist-detail-tmpl", {
        songlist: myPlaylistDetail,
        isCollect: 0,
        isMyPlaylist: 1
    }));
}

// 显示收藏详情
function showFavoriteDetail(obj, songlist_type, songlist_id, platform) {
    $('.nav.masthead-nav li').filter('.active').removeClass('active');
    $(obj).addClass('active');

    if (songlist_type === 'playlist') {
        showPlaylistDetail(songlist_id, platform)
    } else if (songlist_type === 'toplist') {
        showToplistDetail(songlist_id, platform)
    } else if (songlist_type === 'album') {
        showAlbumlist(songlist_id, platform)
    } else if (songlist_type === 'artist') {
        showArtistlist(songlist_id, platform)
    } else if (songlist_type === 'fmlist') {
        showFMlistDetail(songlist_id,platform)
    }
}

// 显示专辑详情
function showAlbumlist(album_id, platform) {
    if (album_id !== '') {
        $('.playlist-page').removeClass('ng-hide');
        $('.playlist-page').siblings().addClass('ng-hide');
        $('.playlist-page .playlist-detail').html(template("songlist-detail-tmpl", {
            songlist: {
                'img_url': '/static/images/loading.svg',
                'title': '正在获取详情,请稍后',
                'songlist': [],
                'source_url': '',
                'song_total': 0
            }
        }));

        // 判断是否已收藏
        var favoriteList = getLocalObj('favoriteList');
        var isCollect = 0;
        if (favoriteList) {
            if (favoriteList.filter(item => item.songlist_type === 'album' && item.songlist_id === album_id && item.platform === platform).length > 0) {
                isCollect = 1;
            }
        }

        $.ajax({
            url: '/api/v1/album_detail',
            type: 'get',
            dataType: 'json',
            data: {'album_id': album_id, 'platform': platform},
            timeout: 5000,
            success: function (resp) {
                $('.playlist-page .playlist-detail').html(template("songlist-detail-tmpl",
                    {
                        songlist: resp.data,
                        isCollect: isCollect,
                        songlist_type: 'album',
                        songlist_id: resp.data.album_id
                    }));
            }
        });
    }
}

// 显示歌手详情
function showArtistlist(artist_id, platform) {
    if (artist_id !== '') {
        $('.playlist-page').removeClass('ng-hide');
        $('.playlist-page').siblings().addClass('ng-hide');
        $('.playlist-page .playlist-detail').html(template("songlist-detail-tmpl", {
            songlist: {
                'img_url': '/static/images/loading.svg',
                'title': '正在获取详情,请稍后',
                'songlist': [],
                'source_url': '',
                'song_total': 0
            }
        }));

        // 判断是否已收藏
        var favoriteList = getLocalObj('favoriteList');
        var isCollect = 0;
        if (favoriteList) {
            if (favoriteList.filter(item => item.songlist_type === 'artist' && item.songlist_id === artist_id && item.platform === platform).length > 0) {
                isCollect = 1;
            }
        }

        $.ajax({
            url: '/api/v1/artist_detail',
            type: 'get',
            dataType: 'json',
            data: {'artist_id': artist_id, 'platform': platform},
            timeout: 5000,
            success: function (resp) {
                $('.playlist-page .playlist-detail').html(template("songlist-detail-tmpl",
                    {
                        songlist: resp.data,
                        isCollect: isCollect,
                        songlist_type: 'artist',
                        songlist_id: resp.data.artist_id
                    }));

            }
        });
    }


}

// 显示设置页 如果已显示 再次点击还原之前页面
function showSettings() {

    if ($('.setting-page.ng-hide').length === 1) {
        $('.page:not(.ng-hide)').addClass('pre-hide');
        $('.setting-page').removeClass('ng-hide');
        $('.setting-page').siblings().addClass('ng-hide');
    } else {
        $('.setting-page').addClass('ng-hide');
        $('.page.pre-hide').removeClass('ng-hide');
        $('.page.pre-hide').removeClass('pre-hide');
    }

}


// 显示歌曲操作icon
function showPlaylistSongTools(obj, isMyPlaylist = 0) {
    $(obj).siblings('.ng-scope.ng-show').find('.tools a').addClass('ng-hide');
    $(obj).siblings('.ng-scope.ng-show').removeClass('ng-show');
    $(obj).addClass('ng-show');
    // 如果是我的歌单则隐藏"添加到我的歌单icon" 显示"从我的歌单删除icon"
    // 否则反之
    if (isMyPlaylist === 1) {
        var showIcons = $(obj).find('.tools a:not(.detail-fav-button)')
    } else {
        var showIcons = $(obj).find('.tools a:not(.detail-delete-button)')
    }
    showIcons.removeClass('ng-hide');

}

// 移动到当前播放列表歌曲显示删除和添加到歌单icon
function showPlayerSongDel(obj) {
    $(obj).siblings().children('.li-del').addClass('ng-hide');
    $(obj).siblings().children('.li-add').addClass('ng-hide');
    $(obj).siblings().children('.aplayer-list-author').css('margin-right', '0px');
    $(obj).children('.li-del').removeClass('ng-hide');
    $(obj).children('.li-add').removeClass('ng-hide');
    $(obj).children('.aplayer-list-author').css('margin-right', '40px')
}

// 清空当前播放列表
function clearPlayer() {
    $.confirm('确定清空当前播放列表?', function (e) {
        if (e) {
            ap.list.clear();
            localStorage.removeItem('curPlayingList');
            localStorage.removeItem('curPlayingSong');
        }
    });

}

// 播放器删除当前歌曲
function removePlayerSong(obj, event) {
    var index = parseInt($(obj).siblings('.aplayer-list-index').text()) - 1;
    ap.list.remove(index);
    event.stopPropagation();

}

// 添加单曲到当前播放器 isPlaying = 1:立即播放 isPlaying = 0:仅添加
function addSongToPlayer(obj, isPlaying = 1) {
    const content_div = $(obj).parent().parent();

    const song_id = content_div.children('.song_id').text();
    const img_url = content_div.children('.img_url').text();
    const platform = content_div.children('.platform').text();
    const platform_name = content_div.find('.source a').text();
    const source_url = content_div.find('.source a').attr('href');
    const title = content_div.find('.title a').text();
    const artist = content_div.find('.artist a').text();
    const artist_id = content_div.find('.artist a').attr('data-value');
    const album = content_div.find('.album a').text();
    const album_id = content_div.find('.album a').attr('data-value');

    var curIndex = 0;
    if ((ap.list.audios.length === 0) || (ap.list.audios.filter(item => item.song_id === song_id && item.platform === platform).length === 0)) {

        ap.list.add([{
            name: title,
            artist: artist,
            cover: img_url,
            song_id: song_id,
            platform: platform,
            platform_name: platform_name,
            source_url: source_url,
            artist_id: artist_id,
            album: album,
            album_id: album_id
        }]);
        curIndex = ap.list.audios.length - 1;
        localStorage.setItem('curPlayingList', JSON.stringify(ap.list.audios));
    } else {
        curIndex = ap.list.audios.findIndex(item => item.song_id === song_id && item.platform === platform)
    }

    if (isPlaying) {

        ap.list.switch(curIndex);
        ap.play();

        $.load('正在切换当前歌曲!');
        setTimeout(function () {
            $.loaded()
        }, 500);
    } else {
        $.load('已添加到当前播放列表!');
        setTimeout(function () {
            $.loaded()
        }, 500);
    }

}

// 添加歌单的所有歌到播放列表
function addAllSongToPlayerList(isPlaying = 0) {

    var addSongs = [];
    var firstSongs = {};
    $('.playlist-page .detail-songlist .ng-scope').each(function (index) {

            const song_id = $(this).children('.song_id').text();
            const img_url = $(this).children('.img_url').text();
            const platform = $(this).children('.platform').text();
            const platform_name = $(this).find('.source a').text();
            const source_url = $(this).find('.source a').attr('href');
            const title = $(this).find('.title a').text();
            const artist = $(this).find('.artist a').text();
            const artist_id = $(this).find('.artist a').attr('data-value');
            const album = $(this).find('.album a').text();
            const album_id = $(this).find('.album a').attr('data-value');

            if (index === 0) {
                firstSongs = {
                    song_id: song_id,
                    platform: platform
                }
            }


            if ((ap.list.audios.length === 0) || (ap.list.audios.filter(item => item.song_id === song_id && item.platform === platform).length === 0)) {

                addSongs.push({
                    name: title,
                    artist: artist,
                    cover: img_url,
                    song_id: song_id,
                    platform: platform,
                    platform_name: platform_name,
                    source_url: source_url,
                    artist_id: artist_id,
                    album: album,
                    album_id: album_id
                })
            }
        }
    );

    ap.list.add(addSongs);
    localStorage.setItem('curPlayingList', JSON.stringify(ap.list.audios));

    if (isPlaying === 0) {
        $.load('已全部添加至当前播放列表');
        setTimeout(function () {
            $.loaded()
        }, 500);
    } else if (firstSongs) {
        const curIndex = ap.list.audios.findIndex(item => item.song_id === firstSongs.song_id && item.platform === firstSongs.platform);
        ap.list.switch(curIndex);
        ap.play();
    }
}

// 收藏 / 取消收藏
function createfavoriteList(obj, songlist_type, songlist_id, platform, title) {
    var favoriteList = getLocalObj('favoriteList');
    if (!favoriteList) {
        favoriteList = []
    }
    const isCollect = $(obj).children('.favorited').length;
    if (songlist_id) {
        if (!isCollect) {
            favoriteList.push(
                {
                    'songlist_type': songlist_type,
                    'songlist_id': songlist_id,
                    'platform': platform,
                    'title': title
                }
            );
            localStorage.setItem('favoriteList', JSON.stringify(favoriteList));

            $(obj).children().removeClass('notfavorite');
            $(obj).children().addClass('favorited');
            $(obj).find('span').text('已收藏');

        } else {
            favoriteList = favoriteList.filter(item => item.songlist_id !== songlist_id || item.songlist_type !== songlist_type && item.platform !== platform);

            localStorage.setItem('favoriteList', JSON.stringify(favoriteList));
            $(obj).children().addClass('notfavorite');
            $(obj).children().removeClass('favorited');
            $(obj).find('span').text('收藏');
        }

        $(".nav.favorite-playlist").html(template("favorite-playlist-tmpl", {
            playlists: favoriteList
        }));
    }


}

// 创建新建歌单
function createMyPlaylist() {
    var myPlaylist = getLocalObj('myPlaylist');
    if (!myPlaylist) {
        myPlaylist = []
    }
    const newPlatlistName = $('.dialog-newplaylist input').val();
    if (newPlatlistName) {
        const playlist_id = 'myPlaylist_' + guid();
        const img_url = '/static/images/mycover.jpg';
        myPlaylist.push(
            {
                'playlist_id': playlist_id,
                'title': newPlatlistName,
                'img_url': img_url
            }
        );

        localStorage.setItem('myPlaylist', JSON.stringify(myPlaylist));
        $(".nav.my-playlist").html(template("my-playlist-tmpl", {
            playlists: myPlaylist
        }));

        const myPlaylistDetail = {
            'playlist_id': playlist_id,
            'title': newPlatlistName,
            'img_url': img_url,
            'song_list': [],
            'song_total': 0,
            'create_time': getCurDateStr(),
            'description': '创建于:' + getCurDateStr()
        };

        localStorage.setItem(playlist_id, JSON.stringify(myPlaylistDetail));
    } else {
        $.load('请输入新建歌单名称');
        setTimeout(function () {
            $.loaded()
        }, 1000);
    }

    const from = $('.dialog-playlist .detail-add').attr('data-from');


    if (from) {
        addMyPlaylistDialog(from, event)
    } else {
        closeDialog()
    }
}

// 添加到我的歌单
function addMyPlaylist(playlist_id, type = 'song') {

    var myPlaylist = getLocalObj('myPlaylist');
    var myPlaylistDetail = getLocalObj(playlist_id);
    var addSongs = [];

    const origin_length = myPlaylistDetail['song_list'].length;

    if (type === 'song') {
        const content_div = $('.playlist-page .detail-songlist .ng-show');
        const song_id = content_div.children('.song_id').text();
        const img_url = content_div.children('.img_url').text();
        const platform = content_div.children('.platform').text();
        const platform_name = content_div.find('.source a').text();
        const source_url = content_div.find('.source a').attr('href');
        const title = content_div.find('.title a').text();
        const artist = content_div.find('.artist a').text();
        const artist_id = content_div.find('.artist a').attr('data-value');
        const album = content_div.find('.album a').text();
        const album_id = content_div.find('.album a').attr('data-value');


        if (myPlaylistDetail['song_list'].filter(item => item.song_id === song_id && item.platform === platform).length === 0) {
            // 头部插入
            // 修改歌单封面
            myPlaylist[myPlaylist.findIndex(item => item.playlist_id === playlist_id)].img_url = img_url;
            myPlaylistDetail['img_url'] = img_url;
            myPlaylistDetail['song_list'].unshift(
                {
                    'song_id': song_id,
                    'title': title,
                    'img_url': img_url,
                    'source_url': source_url,
                    'platform': platform,
                    'platform_name': platform_name,
                    'artist': artist,
                    'artist_id': artist_id,
                    'album': album,
                    'album_id': album_id
                }
            );
        }


    } else if (type === 'playlist') {
        $('.playlist-page .detail-songlist .ng-scope').each(function () {
                const song_id = $(this).children('.song_id').text();
                const img_url = $(this).children('.img_url').text();
                const platform = $(this).children('.platform').text();
                const platform_name = $(this).find('.source a').text();
                const source_url = $(this).find('.source a').attr('href');
                const title = $(this).find('.title a').text();
                const artist = $(this).find('.artist a').text();
                const artist_id = $(this).find('.artist a').attr('data-value');
                const album = $(this).find('.album a').text();
                const album_id = $(this).find('.album a').attr('data-value');

                if (myPlaylistDetail['song_list'].filter(item => item.song_id === song_id && item.platform === platform).length === 0) {
                    addSongs.push(
                        {
                            'song_id': song_id,
                            'title': title,
                            'img_url': img_url,
                            'source_url': source_url,
                            'platform': platform,
                            'platform_name': platform_name,
                            'artist': artist,
                            'artist_id': artist_id,
                            'album': album,
                            'album_id': album_id
                        }
                    )
                }
            }
        );

        myPlaylistDetail['song_list'] = addSongs.concat(myPlaylistDetail['song_list']);
        // 修改歌单封面
        const playlist_img_url = $('.detail-head-cover img').attr('src')
        myPlaylist[myPlaylist.findIndex(item => item.playlist_id === playlist_id)].img_url = playlist_img_url;
        myPlaylistDetail['img_url'] = playlist_img_url;

    } else if (type === 'playerlist') {

        $.each(ap.list.audios, function (index, item) {
            addSongs.push(
                {
                    'song_id': item.song_id,
                    'title': item.name,
                    'img_url': item.cover,
                    'source_url': item.source_url,
                    'platform': item.platform,
                    'platform_name': item.platform_name,
                    'artist': item.artist,
                    'artist_id': item.artist_id,
                    'album': item.album,
                    'album_id': item.album_id
                }
            )
        });


        myPlaylistDetail['song_list'] = addSongs.concat(myPlaylistDetail['song_list']);
        // 修改歌单封面
        myPlaylist[myPlaylist.findIndex(item => item.playlist_id === playlist_id)].img_url = addSongs[0].img_url;
        myPlaylistDetail['img_url'] = addSongs[0].img_url;
    } else if (type === 'player') {
        const curIndex = parseInt($('.aplayer-list li .li-add:not(.ng-hide)').siblings('.aplayer-list-index').text()) - 1
        const curSong = ap.list.audios[curIndex]
        if (myPlaylistDetail['song_list'].filter(item => item.song_id === curSong.song_id && item.platform === curSong.platform).length === 0) {
            // 头部插入
            // 修改歌单封面
            myPlaylist[myPlaylist.findIndex(item => item.playlist_id === playlist_id)].img_url = curSong.cover;
            myPlaylistDetail['img_url'] = curSong.cover;
            myPlaylistDetail['song_list'].unshift(
                {
                    'song_id': curSong.song_id,
                    'title': curSong.name,
                    'img_url': curSong.cover,
                    'source_url': curSong.source_url,
                    'platform': curSong.platform,
                    'platform_name': curSong.platform_name,
                    'artist': curSong.artist,
                    'artist_id': curSong.artist_id,
                    'album': curSong.album,
                    'album_id': curSong.album_id
                }
            );
        }
    } else if (type === 'nowplay') {
        const curPlayingSong = getLocalObj('curPlayingSong');
        const curSong = ap.list.audios.find(item => item.song_id === curPlayingSong.song_id && item.platform === curPlayingSong.platform);

        if (myPlaylistDetail['song_list'].filter(item => item.song_id === curSong.song_id && item.platform === curSong.platform).length === 0) {
            // 头部插入
            // 修改歌单封面
            myPlaylist[myPlaylist.findIndex(item => item.playlist_id === playlist_id)].img_url = curSong.cover;
            myPlaylistDetail['img_url'] = curSong.cover;
            myPlaylistDetail['song_list'].unshift(
                {
                    'song_id': curSong.song_id,
                    'title': curSong.name,
                    'img_url': curSong.cover,
                    'source_url': curSong.source_url,
                    'platform': curSong.platform,
                    'platform_name': curSong.platform_name,
                    'artist': curSong.artist,
                    'artist_id': curSong.artist_id,
                    'album': curSong.album,
                    'album_id': curSong.album_id
                }
            );
        }
    }

    myPlaylistDetail['song_total'] = myPlaylistDetail['song_list'].length;
    if ((myPlaylistDetail['song_list'].length - origin_length) > 0) {
        myPlaylistDetail['description'] = '创建于:' + getCurDateStr() + '<br />' + getCurDateStr(1) + ' 新增' + (myPlaylistDetail['song_list'].length - origin_length) + '首';
    }

    localStorage.setItem('myPlaylist', JSON.stringify(myPlaylist));
    localStorage.setItem(playlist_id, JSON.stringify(myPlaylistDetail));

    if ($('#' + playlist_id).attr('class') === 'active') {
        $(".playlist-detail").html(template("songlist-detail-tmpl", {
            songlist: {
                'img_url': '/static/images/loading.svg',
                'title': '正在获取详情,请稍后',
                'songlist': [],
                'source_url': '',
                'song_total': 0
            }
        }));
        $(".playlist-detail").html(template("songlist-detail-tmpl", {
            songlist: myPlaylistDetail,
            isCollect: 0,
            isMyPlaylist: 1
        }));
    }

    closeDialog();

    $.load('成功添加到我的歌单:' + myPlaylist[myPlaylist.findIndex(item => item.playlist_id === playlist_id)].title);
    setTimeout(function () {
        $.loaded()
    }, 500);
}

// 编辑我的歌单
function editMyPlaylist() {
    const playlist_id = $('.playlist-detail .detail-head-title .playlist-id').text();
    const new_title = $('.dialog .dialog-body .dialog-editplaylist input').val();
    $('.playlist-detail .detail-head-title h2').text(new_title);

    var myPlaylist = getLocalObj('myPlaylist');
    var myPlaylistDetail = getLocalObj(playlist_id);

    myPlaylist[myPlaylist.findIndex(item => item.playlist_id === playlist_id)].title = new_title;
    myPlaylistDetail.title = new_title;

    localStorage.setItem('myPlaylist', JSON.stringify(myPlaylist));
    localStorage.setItem(playlist_id, JSON.stringify(myPlaylistDetail));

    $(".nav.my-playlist").html(template("my-playlist-tmpl", {
        playlists: myPlaylist
    }));

    closeDialog();

}

// 删除我的歌单
function deleteMyPlaylist() {
    const playlist_id = $('.playlist-detail .detail-head-title .playlist-id').text();
    const title = $('.playlist-detail .detail-head-title h2').text();
    var myPlaylist = getLocalObj('myPlaylist');
    $.confirm('确定删除歌单:' + title, function (e) {
        if (e) {
            myPlaylist = myPlaylist.filter(item => item.playlist_id !== playlist_id);
            $(".nav.my-playlist").html(template("my-playlist-tmpl", {
                playlists: myPlaylist
            }));
            localStorage.setItem('myPlaylist', JSON.stringify(myPlaylist));
            localStorage.removeItem(playlist_id);
            showRecommendPlaylist($('.nav.masthead-nav li')[1])
        }
    });

}

// 从我的歌单中删除某首歌
function removeSongFromMyPlaylist(obj, song_id, platform) {
    const playlist_id = $('.playlist-detail .detail-head-title .playlist-id').text();
    var myPlaylistDetail = getLocalObj(playlist_id);

    const title = $(obj).parent().parent().find('.title a').text();

    myPlaylistDetail.song_list = myPlaylistDetail.song_list.filter(item => item.song_id !== song_id || item.platform !== platform)
    myPlaylistDetail['description'] = '创建于:' + getCurDateStr() + '<br />' + getCurDateStr(1) + ' 从歌单中删除歌曲:' + title;

    localStorage.setItem(playlist_id, JSON.stringify(myPlaylistDetail));

    $(".playlist-detail").html(template("songlist-detail-tmpl", {
        songlist: myPlaylistDetail,
        isCollect: 0,
        isMyPlaylist: 1
    }));
}

// 各平台搜索
function searchKeyword(obj, platform = '', pageNum = 1) {

    $(obj).siblings('.source-button').filter('.active').removeClass('active');
    $(obj).addClass('active');
    $('.searchspinner').attr('class', 'searchspinner');

    $('.searchbox .detail-songlist').html(template('search-detail-tmpl',
        {
            search_list: [],
        }));

    const keyword = $("#search-input").val();
    $.ajax({
        url: '/api/v1/search',
        type: 'get',
        dataType: 'json',
        data: {'keyword': keyword, 'platform': platform, 'page_num': pageNum},
        timeout: 5000,
        success: function (resp) {
            $(".searchbox .detail-songlist").html(template("search-detail-tmpl",
                {
                    search_list: resp.data.search_list,
                    curPage: resp.data.page_num,
                    platform: resp.data.platform,
                    previousPage: resp.data.page_num - 1,
                    nextPage: resp.data.page_num + 1
                }));

            $('.searchspinner').attr('class', 'searchspinner ng-hide')

        }
    });
}

// 搜索下一页
function searchPage(platform, pageNum) {
    const obj = $('.searchbox .source-button.active');
    if (platform !== 'QianqianMusic') {
        searchKeyword(obj, platform, pageNum);
    } else {
        $.load('千千音乐暂无下一页');
        setTimeout(function () {
            $.loaded()
        }, 500);
    }
}

// 顶部搜索
function search() {
    const browserEle = document.querySelector('.browser.flex-scroll-wrapper');
    browserEle.removeEventListener('scroll', handlePlayScroll);
    $('.nav.masthead-nav li').filter('.active').removeClass('active');

    $('.search-page').removeClass('ng-hide');
    $('.search-page').siblings().addClass('ng-hide');

    var index = $('.searchbox .source-button').index($('.searchbox .source-button.active'));
    if (index < 0) {
        index = 0
    }

    // 支持搜索的平台
    $.ajax({
        url: '/api/v1/platform',
        type: 'get',
        dataType: 'json',
        timeout: 5000,
        success: function (resp) {

            const data = resp.data.filter(item => item.is_support_search > 0);

            $(".searchbox .source-list").html(template("search-platforms-tmpl",
                {
                    platforms: data,
                    index: index
                }));

            var platform = '';
            if (index !== 0) {
                platform = data[index - 1].name
            }
            searchKeyword($('.searchbox .source-button.active'), platform)
        }
    });

}

//  下载文件
function downloadFile(fileName, fileType, content) {
    window.URL = window.URL || window.webkitURL;
    const blob = new Blob([content], {
        type: fileType,
    });
    const link = document.createElement('a');
    link.download = fileName;
    link.href = window.URL.createObjectURL(blob);
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    link.remove();
}

// 导出备份
function backupMySettings() {
    const items = {};
    Object.keys(localStorage).forEach((key) => {
        items[key] = JSON.parse(localStorage.getItem(key));
    });

    const content = JSON.stringify(items, null, 4);
    downloadFile('JinYuMusicBackup.json', 'application/json', content);

}

// 导入备份
function importMySettings() {
    const fileObject = event.target.files[0];
    if (fileObject === null) {
        Notification.warning('请选择备份文件');
        return;
    }
    const reader = new FileReader();
    reader.onloadend = (readerEvent) => {
        if (readerEvent.target.readyState === FileReader.DONE) {
            const data_json = readerEvent.target.result;
            let data = null;
            try {
                data = JSON.parse(data_json);
            } catch (e) {

                $.load('备份文件格式错误，请重新选择');
                setTimeout(function () {
                    $.loaded()
                }, 1000);
                return;
            }

            $.load('成功导入我的歌单');
            setTimeout(function () {
                $.loaded()
            }, 1000);

            Object.keys(data).forEach(item => localStorage.setItem(item, JSON.stringify(data[item])));

            const curPlayingList = getLocalObj('curPlayingList');
            if (curPlayingList != null) {
                ap.list.add(curPlayingList);
            }

            const curPlayingSong = getLocalObj('curPlayingSong');
            if (curPlayingSong != null) {
                const curPlayingIndex = ap.list.audios.findIndex(item => item.song_id === curPlayingSong.song_id && item.platform === curPlayingSong.platform)
                ap.list.switch(curPlayingIndex);
            }

            // 初始化 加载收藏的歌单
            var favoriteList = getLocalObj('favoriteList');
            $(".favorite-playlist").html(template("favorite-playlist-tmpl", {
                playlists: favoriteList
            }));

            // 初始化 加载我的歌单
            var myPlaylist = getLocalObj('myPlaylist');
            $(".nav.my-playlist").html(template("my-playlist-tmpl", {
                playlists: myPlaylist
            }));


        }
    };
    reader.readAsText(fileObject);
}


// 下载音乐
function downloadMusic(obj) {
    const content_div = $(obj).parent().parent();

    const song_id = content_div.children('.song_id').text();
    const platform = content_div.children('.platform').text();
    const title = content_div.find('.title a').text();
    const artist = content_div.find('.artist a').text();
    var song_name = title + '-' + artist;

    var form = $('<form action="/api/v1/download" method="post" target="_self" style="display: none"></form>');
    var song_name_input = $('<input type="text" name="song_name" style="display: none" />');
    var platform_input = $('<input type="text" name="platform" style="display: none" />');
    var song_id_input = $('<input type="text" name="song_id" style="display: none" />');

    song_name_input.attr('value', song_name);
    platform_input.attr('value', platform);
    song_id_input.attr('value', song_id);

    form.append(song_name_input);
    form.append(platform_input);
    form.append(song_id_input);
    $(document.body).append(form);
    form.submit();

}
