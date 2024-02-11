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
    'name': 'Rating Pet Care Animal Management,  Animal/Bird Care Veterinary Rating',
    'version': '14.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Tools',
    'description':
        """
        This Module help to allow customer rating to salon order.
        
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
    'summary': 'odoo app manage a Pet Care Management rating, pet management in odoo, odoo pet care software,pet scheduling and appointments in Odoo, Bird pet care rating, animal pet care rating, animal Veterinary rating, bird Veterinary rating, appoitment animal boarding veterinary birds services management',
    'depends': ['dev_pet_care_management','rating'],
    'data': [
        'data/data.xml',
        'edi/mail_template.xml',
        'views/pet_service_views.xml',
        'views/pet_boarding_views.xml',
        'views/pet_transportation_views.xml',
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
    'price':12.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
    'license':'LGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
