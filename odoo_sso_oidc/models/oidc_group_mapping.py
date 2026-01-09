# -*- coding: utf-8 -*-
from odoo import models, fields, api


class OIDCGroupMapping(models.Model):
    _name = 'oidc.group.mapping'
    _description = 'OIDC to Odoo Group Mapping'
    _order = 'provider_id, oidc_group_name'

    provider_id = fields.Many2one(
        'oidc.provider',
        string='OIDC Provider',
        required=True,
        ondelete='cascade'
    )
    oidc_group_name = fields.Char(
        string='OIDC Group Name',
        required=True,
        help='Group name as it appears in the OIDC provider (case-sensitive)'
    )
    odoo_group_id = fields.Many2one(
        'res.groups',
        string='Odoo Group',
        required=True,
        ondelete='cascade',
        help='Odoo group to assign to users who are members of the OIDC group'
    )
    active = fields.Boolean(string='Active', default=True)
    
    _sql_constraints = [
        (
            'unique_oidc_group_per_provider',
            'unique(provider_id, oidc_group_name)',
            'Each OIDC group can only be mapped once per provider!'
        ),
    ]
