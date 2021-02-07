odoo.define('ess.check_notification_link', function (require) {
    'use strict';
    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc')

    publicWidget.registry.notification = publicWidget.Widget.extend({
        selector: '.newselector',
        events: {'click .visitedlink': '_getNotification',},

        start: function () {
            var def = this._super.apply(this, arguments);
            var self = this;
            return def;
        },

        _getNotification: function () {
           var self = this;
           $(window).bind('hashchange', function() {
                self._rpc({
                    route: '/change/notification',
                    params: {
                        course_id: decodeURI(window.location.href),
                    },
                }).then(function (result) {
                    $('#notify'+result['result']).css({"color":"black"});
                });
            });
        },
    });

    publicWidget.registry.announcement = publicWidget.Widget.extend({
        selector: '.announcement_selector',
        events: {'click .visitedlink': '_ChangeAnnouncementColor',},

        start: function () {
            var def = this._super.apply(this, arguments);
            var self = this;
            return def;
        },

        _ChangeAnnouncementColor: function () {
           var self = this;
           $(window).bind('hashchange', function() {
                self._rpc({
                    route: '/change/announcement_color',
                    params: {
                        url: decodeURI(window.location.href),
                    },
                }).then(function (result) {
                $('td').find('#announcement'+result['result']).css({"color":"black"});
                });
            });
        },
    });

    publicWidget.registry.public_announcement = publicWidget.Widget.extend({
        selector: '.public_announcement_selector',
        events: {'click .visitedlink': '_ChangePublicAnnouncementColor',},

        start: function () {
            var def = this._super.apply(this, arguments);
            var self = this;
            return def;
        },

        _ChangePublicAnnouncementColor: function () {
           var self = this;
           $(window).bind('hashchange', function() {
                self._rpc({
                    route: '/change/announcement_color',
                    params: {
                        url: decodeURI(window.location.href),
                    },
                }).then(function (result) {
//                $('#announcement'+result['result']).css({"background_color":"black"});
$('td').find('#announcement'+result['result']).css({"color":"black"});
                });
            });
        },
    });

//function show_notification(id_notify){
//alert(id_notify);
//alert(document.getElementById(id_notify););
////make an ajax call and get status value using the same 'id'
////var var1= document.getElementById("status").value;
////$.ajax({
////
////        type:"GET",//or POST
////        url:'http://localhost:7080/ajaxforjson/Testajax',
////                           //  (or whatever your url is)
////        data:{data1:var1},
////        //can send multipledata like {data1:var1,data2:var2,data3:var3
////        //can use dataType:'text/html' or 'json' if response type expected
////        success:function(responsedata){
////               // process on data
////               alert("got response as "+"'"+responsedata+"'");
////
////        }
////     })
//
//}



//$(this).click(function(event){
//function UpdateStatus(Status)
//event.preventDefault();
//alert(">>>>>>>>>>>>>>>>>>")
//});
});


