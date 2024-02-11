odoo.define('tk_veterinary_management.HospitalDashboard', function (require) {
    'use strict';
    const AbstractAction = require('web.AbstractAction');
    const ajax = require('web.ajax');
    const core = require('web.core');
    const rpc = require('web.rpc');
    const session = require('web.session')
    const web_client = require('web.web_client');
    const _t = core._t;
    const QWeb = core.qweb;
    var self = this;
    const ActionMenu = AbstractAction.extend({
        template: 'hospitalDashboard',
        events: {
            'click .active-appointment-grooming': 'view_active_appointment_grooming',
            'click .active-appointment-procedure': 'view_active_appointment_procedure',
            'click .active-appointment-training': 'view_active_appointment_training',
            'click .active-doctors': 'view_active_doctors',
            'click .active-nurses': 'view_active_nurses',
            'click .active-surgery': 'view_action_surgery',
            'click .maintain-count': 'view_maintain_count',
            'click .today-appointment-grooming': 'view_today_appointment_grooming',
            'click .today-appointment-procedure': 'view_today_appointment_procedure',
            'click .today-appointment-training': 'view_today_appointment_training',
            'click .today-surgeries': 'view_today_surgeries',
            'click .action-doctors': 'view_actions_doctors',
            'click .action-nurses': 'view_action_nurses',
        },
        renderElement: function (ev) {
            const self = this;
            $.when(this._super())
                .then(function (ev) {
                    rpc.query({
                        model: "hospital.patient",
                        method: "get_hospital_stats",
                    }).then(function (result) {
                        $('#active_grooming').empty().append(result['active_grooming']);
                        $('#active_training').empty().append(result['active_training']);
                        $('#active_procedure').empty().append(result['active_procedure']);
                        $('#doctor').empty().append(result['doctor']);
                        $('#nurse').empty().append(result['nurse']);
                        $('#surgery').empty().append(result['surgery']);
                        $('#maintain_count').empty().append(result['maintain_count']);
                        $('#today_procedure_count').empty().append(result['today_procedure_count']);
                        $('#today_training_count').empty().append(result['today_training_count']);
                        $('#today_grooming_count').empty().append(result['today_grooming_count']);
                        $('#today_surgery_count').empty().append(result['today_surgery_count']);
                        $('#doctor_day').empty().append(result['doctor_day']);
                        $('#nurse_day').empty().append(result['nurse_day']);
                        self.hospitalAppointmentMonthly(result['months_appointment_details']);
                        self.hospitalAppointmentDate(result['active_appointment_date']);
                        self.groomingProduct(result['grooming_product']);
                        self.medicine(result['medicine_product']);
                        self.paymentMonth(result['invoice'])

                    });
                });
        },
        view_active_appointment_grooming: function (ev) {
            ev.preventDefault();
            return this.do_action({
                name: _t('Active Grooming Appointments'),
                type: 'ir.actions.act_window',
                res_model: 'grooming.details',
                domain: [['state', '=', 'in_consultation']],
                views: [[false, 'list'], [false, 'form']],
                context: { 'create': false },
                target: 'current'
            });
        },
        view_active_appointment_procedure: function (ev) {
            ev.preventDefault();
            return this.do_action({
                name: _t('Active Procedure Appointments'),
                type: 'ir.actions.act_window',
                res_model: 'patient.case',
                domain: [['state', '=', 'in_consultation']],
                views: [[false, 'list'], [false, 'form']],
                context: { 'create': false },
                target: 'current'
            });
        },
        view_active_appointment_training: function (ev) {
            ev.preventDefault();
            return this.do_action({
                name: _t('Active Training Appointments'),
                type: 'ir.actions.act_window',
                res_model: 'training.details',
                domain: [['state', '=', 'in_consultation']],
                views: [[false, 'list'], [false, 'form']],
                context: { 'create': false },
                target: 'current'
            });
        },
        view_maintain_count: function (ev) {
            ev.preventDefault();
            return this.do_action({
                name: _t('Maintenance Request'),
                type: 'ir.actions.act_window',
                res_model: 'hospital.maintenance',
                domain: [['stages', '=', 'draft']],
                views: [[false, 'list'], [false, 'form']],
                context: { 'create': false },
                target: 'current'
            });
        },
        view_actions_doctors: function (ev) {
            ev.preventDefault();
            return this.do_action({
                name: _t('Doctors'),
                type: 'ir.actions.act_window',
                res_model: 'hospital.staff',
                domain: [['staff', '=', 'doctor']],
                views: [[false, 'list'], [false, 'form']],
                context: { 'create': false },
                target: 'current'
            });
        },
        view_action_nurses: function (ev) {
            ev.preventDefault();
            return this.do_action({
                name: _t('Nurses'),
                type: 'ir.actions.act_window',
                res_model: 'hospital.staff',
                domain: [['staff', '=', 'nurse']],
                views: [[false, 'list'], [false, 'form']],
                context: { 'create': false },
                target: 'current'
            });
        },
        view_action_surgery: function (ev) {
            ev.preventDefault();
            return this.do_action({
                name: _t('Surgeries'),
                type: 'ir.actions.act_window',
                res_model: 'hospital.surgery',
                domain: [],
                views: [[false, 'list'], [false, 'form']],
                context: { 'create': false },
                target: 'current'
            });
        },
        view_today_appointment_grooming: function (ev) {
            ev.preventDefault();
            let today = new Date();
            let start = new Date(today);
            let end = new Date(today.setDate(today.getDate() + 1));
            start.setHours(0, 0, 0, 0);
            end.setHours(0, 0, 0, 0);
            let domain = [['appointment_date', '>=', start], ['appointment_date', '<', end], ['state', '=', 'in_consultation']]
            return this.do_action({
                name: _t('Today Grooming Appointment'),
                type: 'ir.actions.act_window',
                res_model: 'grooming.details',
                domain: domain,
                views: [[false, 'list'], [false, 'form']],
                context: { 'create': false },
                target: 'current'
            });
        },
        view_today_appointment_procedure: function (ev) {
            ev.preventDefault();
            let today = new Date();
            let start = new Date(today);
            let end = new Date(today.setDate(today.getDate() + 1));
            start.setHours(0, 0, 0, 0);
            end.setHours(0, 0, 0, 0);
            let domain = [['appointment_date', '>=', start], ['appointment_date', '<', end], ['state', '=', 'in_consultation']]
            return this.do_action({
                name: _t('Today Procedure Appointment'),
                type: 'ir.actions.act_window',
                res_model: 'patient.case',
                domain: domain,
                context: { 'create': false },
                views: [[false, 'list'], [false, 'form']],
                target: 'current'
            });
        },
        view_today_appointment_training: function (ev) {
            ev.preventDefault();
            let today = new Date();
            let start = new Date(today);
            let end = new Date(today.setDate(today.getDate() + 1));
            start.setHours(0, 0, 0, 0);
            end.setHours(0, 0, 0, 0);
            let domain = [['appointment_date', '>=', start], ['appointment_date', '<', end], ['state', '=', 'in_consultation']]
            return this.do_action({
                name: _t('Today Training Appointment'),
                type: 'ir.actions.act_window',
                res_model: 'training.details',
                domain: domain,
                context: { 'create': false },
                views: [[false, 'list'], [false, 'form']],
                target: 'current'
            });
        },
        view_today_surgeries: function (ev) {
            ev.preventDefault();
            let today = new Date();
            let start = new Date(today);
            let end = new Date(today.setDate(today.getDate() + 1));
            start.setHours(0, 0, 0, 0);
            end.setHours(0, 0, 0, 0);
            let domain = [['schedule_date', '>=', start], ['schedule_date', '<', end]]
            return this.do_action({
                name: _t('Today Surgeries'),
                type: 'ir.actions.act_window',
                res_model: 'hospital.surgery',
                domain: domain,
                context: { 'create': false },
                views: [[false, 'list'], [false, 'form']],
                target: 'current'
            });
        },
        view_active_doctors: function (ev) {
            ev.preventDefault();
            const weekday = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];
            const d = new Date();
            let day = weekday[d.getDay()];
            return this.do_action({
                name: _t('Available Doctor'),
                type: 'ir.actions.act_window',
                res_model: 'hospital.staff',
                domain: [['staff', '=', 'doctor'], [day, '=', true]],
                views: [[false, 'list'], [false, 'form']],
                context: { 'create': false },
                target: 'current'
            });
        },
        view_active_nurses: function (ev) {
            ev.preventDefault();
            const weekday = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];
            const d = new Date();
            let day = weekday[d.getDay()];
            return this.do_action({
                name: _t('Available Nurses'),
                type: 'ir.actions.act_window',
                res_model: 'hospital.staff',
                domain: [['staff', '=', 'nurse'], [day, '=', true]],
                views: [[false, 'list'], [false, 'form']],
                context: { 'create': false },
                target: 'current'
            });
        },
        get_action: function (ev, name, res_model) {
            ev.preventDefault();
            return this.do_action({
                name: _t(name),
                type: 'ir.actions.act_window',
                res_model: res_model,
                views: [[false, 'tree'], [false, 'form']],
                target: 'current'
            });
        },

        apexGraph: function () {
            Apex.grid = {
                padding: {
                    right: 0,
                    left: 0,
                    top: 10,
                }
            }
            Apex.dataLabels = {
                enabled: false
            }
        },
        hospitalAppointmentMonthly: function (data) {
            const options = {
                series: [{
                    name: 'Procedure',
                    data: data[0]
                }, {
                    name: 'Grooming',
                    data: data[1]
                }, {
                    name: 'Training',
                    data: data[2]
                }],
                chart: {
                    type: 'bar',
                    height: 350
                }, colors: ['#F0A8B0', '#9BC4D8', '#82D982', '#CFD0EF', '#E6D0A0'],
                plotOptions: {
                    bar: {
                        horizontal: false,
                        columnWidth: '55%',
                        endingShape: 'rounded'
                    },
                },
                dataLabels: {
                    enabled: false
                },
                stroke: {
                    show: true,
                    width: 2,
                    colors: ['transparent']
                },
                xaxis: {
                    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                },
                yaxis: {
                    title: {
                        text: 'Appointment Count'
                    }
                },
                fill: {
                    opacity: 1,
                },
            };
            this.renderGraph("#hospital_appointment_monthly", options);
        },
        hospitalAppointmentDate: function (data) {
            const options = {
                series: [{
                    name: 'Procedures',
                    data: data[1]
                },
                {
                    name: 'Grooming',
                    data: data[2]
                },
                {
                    name: 'Training',
                    data: data[3]
                }],
                chart: {
                    type: 'bar',
                    height: 350,
                    stacked: true,
                    toolbar: {
                        show: true
                    },
                    zoom: {
                        enabled: true
                    }
                },
                colors: ['#F0A8B0', '#9BC4D8', '#82D982', '#CFD0EF', '#E6D0A0'],
                responsive: [{
                    breakpoint: 480,
                    options: {
                        legend: {
                            position: 'bottom',
                            offsetX: -10,
                            offsetY: 0
                        }
                    }
                }],
                plotOptions: {
                    bar: {
                        horizontal: false,
                        borderRadius: 10,
                        dataLabels: {
                            total: {
                                enabled: true,
                                style: {
                                    fontSize: '13px',
                                    fontWeight: 900,
                                }
                            }
                        }
                    },
                },
                dataLabels: {
                    style: {
                        fontSize: '14px',
                        fontFamily: 'Helvetica, Arial, sans-serif',
                        fontWeight: 'normal',
                        colors: ['#292828']
                    },
                },
                xaxis: {
                    categories: data[0],
                }, yaxis: {
                    title: {
                        text: 'Appointment Count'
                    }
                },
                legend: {
                    position: 'bottom',
                    offsetY: -19,
                },
                fill: {
                    opacity: 1,
                },
            };
            this.renderGraph("#hospital_appointment_date", options);

        },
        groomingProduct: function (data) {
            const options = {
                series: data[1],
                chart: {
                    height: 390,
                    type: 'donut',
                },
                colors: ['#F0A8B0', '#9BC4D8', '#82D982', '#CFD0EF', '#E6D0A0'],
                legend: {
                    position: 'bottom'
                },
                labels: data[0],
                responsive: [{
                    breakpoint: 480,
                    options: {
                        chart: {
                            width: 200
                        },
                        legend: {
                            position: 'bottom'
                        }
                    }
                }]
            };
            this.renderGraph("#grooming_product", options);
        },
        medicine: function (data) {
            const options = {
                series: data[1],
                chart: {
                    height: 390,
                    type: 'polarArea'
                },
                colors: ['#F0A8B0', '#9BC4D8', '#82D982', '#CFD0EF', '#E6D0A0'],
                labels: data[0],
                fill: {
                    opacity: 1
                },
                stroke: {
                    width: 1,
                    colors: ['#46C2CB', '#54478c', '#0db39e', '#b9e769', '#83e377', '#16db93', '#D09CFA', '#048ba8', '#2c699a', '#FFFFD0'],
                },
                yaxis: {
                    show: false
                },
                legend: {
                    position: 'bottom'
                },
                theme: {
                    colors: ['#46C2CB', '#54478c', '#0db39e', '#b9e769', '#83e377', '#16db93', '#D09CFA', '#048ba8', '#2c699a', '#FFFFD0'],
                }
            };
            this.renderGraph("#top_medicine", options);
        },
        paymentMonth: function (data) {
            const options = {
                series: [{
                    name: "Total Payment",
                    data: data[1]
                }],
                chart: {
                    height: 350,
                    type: 'line',
                    zoom: {
                        enabled: true,
                    },
                    toolbar: {
                        show: false
                    }
                }, colors: ['#82D982'],
                dataLabels: {
                    enabled: false
                },
                stroke: {
                    curve: 'straight'
                },
                title: {
                    align: 'left'
                },
                grid: {
                    row: {
                        colors: ['transparent'],
                        opacity: 0.5
                    },
                }, markers: {
                    size: 0.5,
                },
                xaxis: {
                    categories: data[0],
                    title: {
                        text: 'Month'
                    }
                }, yaxis: {
                    title: {
                        text: ''
                    },
                    labels: {
                        formatter: function (val) {
                            return val.toFixed(0);
                        }
                    },
                },
                legend: {
                    position: 'top',
                    horizontalAlign: 'right',
                }
            };
            this.renderGraph("#payment_month", options);
        },
        renderGraph: function (render_id, options) {
            $(render_id).empty();
            const graphData = new ApexCharts(document.querySelector(render_id), options);
            graphData.render();
        },
        willStart: function () {
            const self = this;
            self.drpdn_show = false;
            return Promise.all([ajax.loadLibs(this), this._super()]);
        },
    });
    core.action_registry.add('hospital_dashboard', ActionMenu);
});
