// 一下自定定义的 js 文件

// 回到顶部
function gotoTop(min_height) {
    //预定义返回顶部的html代码，它的css样式默认为不显示
    var gotoTop_html = '<div id="gotoTop"></div>';
    //将返回顶部的html代码插入页面上id为page的元素的末尾
    $("#page").append(gotoTop_html);
    $("#gotoTop").click(//定义返回顶部点击向上滚动的动画
        function () {
            $('html,body').animate({scrollTop: 0}, 700);
        }).hover(//为返回顶部增加鼠标进入的反馈效果，用添加删除css类实现
        function () {
            $(this).addClass("hover");
        },
        function () {
            $(this).removeClass("hover");
        });
    //获取页面的最小高度，无传入值则默认为600像素
    min_height ? min_height = min_height : min_height = 1000;
    //为窗口的scroll事件绑定处理函数
    $(window).scroll(function () {
        //获取窗口的滚动条的垂直位置
        var s = $(window).scrollTop();
        //当窗口的滚动条的垂直位置大于页面的最小高度时，让返回顶部元素渐现，否则渐隐
        if (s > min_height) {
            $("#gotoTop").fadeIn(100);
        } else {
            $("#gotoTop").fadeOut(200);
        }
    });
}

// 调用该函数
gotoTop();




