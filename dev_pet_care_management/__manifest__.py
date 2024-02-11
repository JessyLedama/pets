# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Pet Care Animal Management, Animal/Bird Care Veterinary Management',
    'version': '14.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Tools',
    'description':
        """
        - Type Breed configuration of pet
        - Pet screen:
            - basic details
            - guardian details
            - preferences of pet like food, brand, activity etc
            - Preventive Surgery
            - Feeding Schedule
            - Medication Schedule
            - vaccination details
            - Q&A
            - other details bedtime routine, allergies
        - Appointment:
            - generate boarding, service and Transportation from appointment
            - send by email
            - send mail to guardian when appointment is confirmed
        - Pet Care:
            - Pet Boarding:
                - pet and guardian details
                - services of pet like accommodation, feeding etc(may multiple)
                - services date and charge by separate line
                - generate agreement
                - generate invoice
                - send by email
            - Pet Service:
                - different from boarding , in boarding pet will stay number of days in pet care center
                but in service you pet can stay whole day or few hours for their service
                - services like body wash, training etc
                - add pet details and multiple services
                - generate invoices
                - send by email
            - Pet Transportation:
                - transport pet from one location to another
                - pass fixed charges
                - generate invoice
                - send by email
        - Contact:
            - guardians
          - Retail:
            - pet store owner can sell pet supplys, toys, foods
            - product and sale order screen is there
        - Agreement:
            - separate menu created for pet agreements and agreement documents
            - send by email
            - separate menu for agreement documents also
        - Mass Mailing:
            - send mass mail to guardians when any event like medical checkup is going to organize in pet store
        - Reports:
            - Pivot : Boarding Analysis
            - Pivot : Service Analysis
            - Pivot : Transportation Analysis
            - PDF : Appointment Details
            - PDF : Boarding Details
            - PDF : Service Details
            - PDF : Transportation Details
            - PDF : Pet Details
            - PDF : Agreement Details
            - Date Range PDF : Boarding History
            - Date Range PDF : Service History
            - Date Range PDF : Transportation History
            
 Pet care management system in Odoo
Odoo pet care software
Efficient pet care management in Odoo
Streamlining pet care operations with Odoo
Customizable pet care management solution in Odoo
Odoo pet care module
Simplifying pet scheduling and appointments in Odoo
Odoo pet care management features
Enhancing pet health records with Odoo
Odoo pet care best practices
Effective pet care administration in Odoo
Odoo pet care management for veterinary clinics and pet services
Improving pet care efficiency with Odoo
Odoo pet care management integration options
Automated pet care management in Odoo

odoo app manage a Pet Care Management, pet management in odoo, odoo pet care software,pet scheduling and appointments in Odoo, Bird pet care, animal pet care, animal Veterinary, bird Veterinary, appoitment animal boarding veterinary birds services management
           
    """,
    'summary': 'odoo app manage a Pet Care Management, pet management in odoo, odoo pet care software,pet scheduling and appointments in Odoo, Bird pet care, animal pet care, animal Veterinary, bird Veterinary, appoitment animal boarding veterinary birds services management',
    'depends': ['sale_management','account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/main_menu.xml',
        'views/res_config_view.xml',
        'views/config_views.xml',
        'views/pet_views.xml',
        'views/product_template.xml',
        'views/res_partner_views.xml',
        'views/hr_employee.xml',
        'views/pet_boarding_views.xml',
        'views/pet_service_views.xml',
        'report/pet_service_report.xml',
        'report/pet_boarding_report.xml',
        'report/report_menu.xml',
        'data/mail_template.xml',
        
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':49.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
    'license':'LGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
