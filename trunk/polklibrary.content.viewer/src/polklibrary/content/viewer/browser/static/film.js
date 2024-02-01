var ShowMore = {
        
    Pattern : function() {
        $('.pat-showmore').each(function(i,t) {
            ShowMore.Attach(t);
        });
    },
    
   
    Attach : function(e) {
        var element = e;
        var i = parseInt($(element).attr('data-len'));
        var text = $(element).text();
        var show = $('<span>').html( text.substring(0, i) ).addClass("showmore-show");
        var hide = $('<span>').html( text.substring(i, text.length) ).addClass("showmore");
        var toggle = $('<span>').html('...  Show More').addClass("showmore-toggle").click(function(){
            $(this).parent().find('.showmore').show();
            $(this).hide();
        });
        
        $(element).html(""); // destroy text
        if ($(e).is('.pat-limit'))
            $(element).append(show).append('<span>...</span>');
        else
            $(element).append(show).append(toggle).append(hide);
    }
    
}


var Images = {

    Threshold : 0,
    
    Pattern : function(){
        setInterval(function(){
            Images.Process();
        }, 1000);
    },
    
    Process : function(){
        $('.pat-images:not([style]').each(function(){
            if(Images.IsOnScreen(this)){
                var style = $(this).attr('data-style');
                $(this).attr('style', style);
            }
        });
    },
    
    IsOnScreen : function(element){  
        var wt = $(window).scrollTop(),
            wb = wt + $(window).height(),
            wl = $(window).scrollLeft()
            wr = wl + $(window).width(),
            
            et = $(element).offset().top,
            eb = et + $(element).height(),
            el = $(element).offset().left,
            er = el + $(element).width();
            
            
        return eb >= wt - Images.Threshold && et <= wb + Images.Threshold && er >= wl - Images.Threshold && el <= wr + Images.Threshold;
    },

}

var Player = {
    
    Thread : null,
    LoginWindow : null,
    
    Pattern : function(){
        var player = $('.pat-player');
        if (player.length > 0)
        {
            var width = $(player).width();
            var scaledheight = $(player).height() - 30;
            
            // Set proper height based off width
            var h = Math.floor(width/3);
            var height = (h*2) + 25; // +25 for padding
            $(player).css('height', height+'px');
            var scaledheight = height - 30;
            
            
            var src = $(player).find('iframe').attr('src');
            src = src.replace(new RegExp('{WIDTH}', 'g'), width);
            src = src.replace(new RegExp('{HEIGHT}', 'g'), scaledheight);
             $(player).find('iframe').attr('src', src);
            
             $(player).find('iframe').show();
        }
    },
    
    Pattern2 : function(){
        $('.pat-player-login').click(function(){
            Player.LoginWindow = window.open("https://www.remote.uwosh.edu/login?url=" + $('body').attr('data-portal-url') + "/close_view", "Off Campus Login", "");
            Player.Thread = window.setInterval(function() {
                if (Player.LoginWindow.closed !== false) {
                    window.clearInterval(Player.Thread);
                    document.location.href =  "http://www.remote.uwosh.edu/login?url=" + document.location.href;
                }
            }, 500);
        });
    },
    
    
}


var Scroll = {

    ImageSpace : 160, // 150px record image + 10px margin

    Pattern : function() {
        $('.pat-scroll .collection').hover(
            function(){
                $(this).find('.scroll-left,.scroll-right').show();
            },
            function(){
                $(this).find('.scroll-left,.scroll-right').hide();
            }
        );
        
        // Tap or Mouse
        $('.pat-scroll .scroll-right').click(function(){
            Scroll.GoRight($(this).parent().find('.scrollbox'));
        });
        $('.pat-scroll .scroll-left').click(function(){
            Scroll.GoLeft($(this).parent().find('.scrollbox'));
        });
        
        // Swipes
        $('.pat-scroll .collection').on( "swiperight", function(){
            Scroll.GoLeft($(this).find('.scrollbox'));
        });
        $('.pat-scroll .collection').on( "swipeleft", function(){
            Scroll.GoRight($(this).find('.scrollbox'));
        });
        
        // $('.pat-scroll .collection').on('flick', function(e) {
            // if (1 == e.direction) {
                // Scroll.GoLeft($(this).find('.scrollbox'));
            // }
            // else {
                // Scroll.GoRight($(this).find('.scrollbox'));
            // }
        // });
                
    },
    
    GetScrollDistance : function(){
        var scroll_distance = $('.collection').width();
        var distance = 0;
        
        if (this.ImageSpace >= scroll_distance)
            distance = this.ImageSpace;
        else if (this.ImageSpace*2 >= scroll_distance)
            distance =  this.ImageSpace*2;
        else if (this.ImageSpace*3 >= scroll_distance)
            distance =  this.ImageSpace*3;
        else if (this.ImageSpace*4 >= scroll_distance)
            distance =  this.ImageSpace*4;
        else if (this.ImageSpace*5 >= scroll_distance)
            distance =  this.ImageSpace*5;
        else if (this.ImageSpace*6 >= scroll_distance)
            distance =  this.ImageSpace*6;
        else if (this.ImageSpace*7 >= scroll_distance)
            distance =  this.ImageSpace*7;
        else if (this.ImageSpace*8 >= scroll_distance)
            distance =  this.ImageSpace*8;
        else
            distance =  this.ImageSpace*9;
            
        return distance - this.ImageSpace; // back up one
        
    },
    
    
    GoRight : function(scrollbox){
        //var scrollbox = $(element).parent().find('.scrollbox');
        var left = parseInt($(scrollbox).css('left').replace('px',''));
        var max_distance = (parseInt($(scrollbox).attr('data-items')) * Scroll.ImageSpace) + Scroll.ImageSpace; // +  "View More"
        var scroll_distance = Scroll.GetScrollDistance();
        
        if(scroll_distance < 600)
            $(scrollbox).addClass('fast');
        else
            $(scrollbox).removeClass('fast');
        
        
        if (-max_distance < left-scroll_distance)
            $(scrollbox).css({'left': (left - scroll_distance) + "px"});
    },
    
    GoLeft : function(scrollbox){
        //var scrollbox = $(element).parent().find('.scrollbox');
        var left = parseInt($(scrollbox).css('left').replace('px',''));
        var scroll_distance = Scroll.GetScrollDistance();

        if(scroll_distance < 600)
            $(scrollbox).addClass('fast');
        else
            $(scrollbox).removeClass('fast');
        
        if (left+scroll_distance <= 0) 
            $(scrollbox).css({'left': (left + scroll_distance) + "px"});
    },

    
    
    
}



var Overlay = {
    
    Thread: null,
    Width: 400,
    PushLeft: 160,
    PushRight: 425,
    
    Pattern : function(){
    
        $('.pat-overlay').hover(
            function(e){
                clearTimeout(Overlay.Thread);
                //var element = this;
            
                var position = $(this).offset();
                var window_width = $(window).width();
                var left = position.left + Overlay.PushLeft;
                var top = position.top;
                
                if ((left + Overlay.Width) < window_width){
                    $('#overlay').css({'left': left, 'top': position.top});
                    $('#overlay').addClass('rightside');
                    $('#overlay').removeClass('leftside');
                }
                else {
                    var right = position.left - Overlay.PushRight;
                    $('#overlay').css({'left': right, 'top': position.top});
                    $('#overlay').addClass('leftside');
                    $('#overlay').removeClass('rightside');
                }
                Overlay.Set(this);                
                Overlay.Show();
            },
            function(){                
                Overlay.Thread = setTimeout(function(){
                        Overlay.Clear();
                        Overlay.Hide();
                }, 500);
            }
        );
        
        $('#overlay').hover(
            function(e){
                clearTimeout(Overlay.Thread);
            },
            function(){
                Overlay.Clear();
                Overlay.Hide();
            }
        );
    },

    Set : function(element){
        $('#overlay').find('.title').html($(element).attr('data-overlay-title'));
        $('#overlay').find('.description').html($(element).attr('data-overlay-description'));
        ShowMore.Attach($('#overlay').find('.description'));
        
        $('#overlay').find('.runtime span').html($(element).attr('data-overlay-runtime'));
        
        var span = $(element).find('.add-to-list span').clone(true, true);
        $(span).removeClass('suppress-add-to-list');
        Films.Attach(span);
        if (span != null && span.length > 0)
            $('#overlay').find('.add-to-list span').replaceWith(span);
    },
    
    Clear : function(element){
        $('#overlay').find('.title').html('');
        $('#overlay').find('.description').html('');
        $('#overlay').find('.runtime span').html('');
    },
    
    Show : function(){
        $('#overlay').css({'opacity':'1','visibility': 'visible'});
    },
    
    Hide : function(){
        $('#overlay').css({'opacity':'0','visibility': 'hidden'});
    },
    
}


var Share = {

    Pattern : function() {
        $('.pat-share').click(function(){
            $('#share').css({'opacity':'1','visibility': 'visible'});
            var url = $('body').attr('data-base-url');
            var embed = '<iframe width="600px" height="420px" frameborder="0" scrolling="no" src="' + url + '/share"></iframe>';
            $('#share textarea').text(embed);
            
            
        });
        $('#share .close').click(function(){
            $('#share').css({'opacity':'0','visibility': 'hidden'});
        });
    },

}










var Films = {
    
    Items : {},
    
    Pattern : function(){
        
        $('span.pat-film-list').each(function(i, t){
            // Set if has or does not
            if (Films.Items.hasOwnProperty($(t).attr('data-id'))) {
                $(t).attr('data-added', '1').attr('title', 'Remove from your playlist');
            }
            else {
                $(t).attr('data-added', '0').attr('title', 'Add to your playlist');
            }
            
            // Add Clicks
            Films.Attach(t);
            
        });
        
    },
    
    Attach : function(element){
        $(element).click(function(e){
            e.preventDefault();
            if ($(e.target).attr('data-added') == '1') {
                Films.Remove($(e.target).attr('data-id'), function(response){
                    if(response.status == 200)
                        $(element).attr('data-added', '0').attr('title', 'Add to your playlist');
                });
            }
            else {
                Films.Add($(e.target).attr('data-id'), function(response){
                    if(response.status == 200)
                        $(element).attr('data-added', '1').attr('title', 'Remove from your playlist');
                });
            }
            
        });
    },
        
    Get : function(callback) {
        $.getJSON($('body').attr('data-portal-url') + '/setFilm', function(response){
            if (response.status == 200) {
                var items = response.data.split('|');
                for(var i in items)
                    if (items[i] != '')
                        Films.Items[items[i]] = items[i];
                callback();
             }
             else {
                callback();
             }
        });
    },
    
    Add : function(id, callback){
        $.getJSON($('body').attr('data-portal-url') + '/setFilm?type=add&id=' + id, function(response){
            console.log(response);
            callback(response);
        });
    },

    Remove : function(id, callback){
        $.getJSON($('body').attr('data-portal-url') + '/setFilm?type=remove&id=' + id, function(response){
            console.log(response);
            callback(response);
        });
    },

}


$(document).ready(function(){
    Films.Get(function(response){
        Films.Pattern();
    });
    Scroll.Pattern();
    ShowMore.Pattern();
    Overlay.Pattern();
    Share.Pattern();
    Player.Pattern();
    Player.Pattern2();
    Images.Pattern();
});

