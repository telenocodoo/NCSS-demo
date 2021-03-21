odoo.define('ess.report', function (require) {
    'use strict';
    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc')

    publicWidget.registry.print_report = publicWidget.Widget.extend({
        selector: '#ReportForm',
        events: {
            'click #print_salary_button': '_adaptCityForm',
        },
        start: function () {
            var def = this._super.apply(this, arguments);
            alert("LLLLLLLLLLLLLL");
            return def;
        },

        _adaptCityForm: function () {
            var self = this;
//            var report_id = document.getElementById("report_id");
            self._rpc({
                route: '/salary/information',
                params: {
                    report_id: document.getElementById("report_id").value,
                    direction_id: document.getElementById("direction_id").value,
                },
            }).then(function (result) {
//                document.getElementById('place_id').value = result['val'];
            });

        },
    });


});
