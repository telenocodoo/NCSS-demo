odoo.define('s2u_portal_avatar.main', function (require) {
    'use strict';

    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var _t = core._t;

    publicWidget.registry.PortalAvatar = publicWidget.Widget.extend({
        selector: '#s2u_portal_avatar',
        read_events: {
            'click .s2u_portal_avatar_edit': '_onEditAvatarClick',
            'change .s2u_portal_avatar_upload': '_onAvatarUploadChange',
            'click .s2u_portal_avatar_clear': '_onClearAvatarClick',
        },

        init: function () {
            this._super.apply(this, arguments);
        },

        start: function () {
            var self = this;
        },

        _onEditAvatarClick: function (ev) {
            ev.preventDefault();
            $(ev.currentTarget).closest('form').find('.s2u_portal_avatar_upload').trigger('click');
        },

        _onAvatarUploadChange: function (ev) {
            if (!ev.currentTarget.files.length) {
                return;
            }
            var $form = $(ev.currentTarget).closest('form');
            var reader = new window.FileReader();
            reader.readAsDataURL(ev.currentTarget.files[0]);
            reader.onload = function (ev) {
                $form.find('.s2u_portal_avatar_img').attr('src', ev.target.result);
                $form.find('.s2u_portal_avatar_img').attr('style', 'border-radius: 50%; width: 128px; height: 128px;')
            };
            $form.find('#portal_clear_avatar').remove();
        },

        _onClearAvatarClick: function (ev) {
            var $form = $(ev.currentTarget).closest('form');
            $form.find('.s2u_portal_avatar_img').attr('src', '/web/static/src/img/placeholder.png');
            $form.find('.s2u_portal_avatar_img').attr('style', 'border-radius: 50%; width: 128px; height: 128px;')
            $form.append($('<input/>', {
                name: 'clear_avatar',
                id: 'portal_clear_avatar',
                type: 'hidden',
            }));
        },
    })
});
