# -*- coding: utf-8 -*-
# Copyright 2013-2014 Eucalyptus Systems, Inc.
#
# Redistribution and use of this software in source and binary forms,
# with or without modification, are permitted provided that the following
# conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Pyramid views for Eucalyptus and AWS Accounts

"""
import csv
import simplejson as json
import StringIO
from urllib import urlencode

from boto.exception import BotoServerError
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config

from ..forms.accounts import AccountForm, AccountUpdateForm, DeleteAccountForm
from ..forms.quotas import QuotasForm
from ..i18n import _
from ..models import Notification
from ..models.quotas import Quotas
from ..views import BaseView, LandingPageView, JSONResponse
from . import boto_error_handler
from .users import PasswordGeneration


class AccountsView(LandingPageView):
    TEMPLATE = '../templates/accounts/accounts.pt'

    def __init__(self, request):
        super(AccountsView, self).__init__(request)
        self.conn = self.get_connection(conn_type="iam")
        self.initial_sort_key = 'account_name'
        self.prefix = '/accounts'
        self.delete_form = DeleteAccountForm(self.request, formdata=self.request.params or None)

    @view_config(route_name='accounts', renderer=TEMPLATE)
    def accounts_landing(self):
        json_items_endpoint = self.request.route_path('accounts_json')
        if self.request.GET:
            json_items_endpoint += '?{params}'.format(params=urlencode(self.request.GET))
        # filter_keys are passed to client-side filtering in search box
        self.filter_keys = ['account_name', 'account_id']
        # sort_keys are passed to sorting drop-down
        self.sort_keys = [
            dict(key='account_name', name=_(u'Account name: A to Z')),
            dict(key='-account_name', name=_(u'Account name: Z to A')),
        ]

        return dict(
            filter_fields=False,
            filter_keys=self.filter_keys,
            sort_keys=self.sort_keys,
            prefix=self.prefix,
            initial_sort_key=self.initial_sort_key,
            json_items_endpoint=json_items_endpoint,
            delete_form=self.delete_form,
        )

    @view_config(route_name='accounts_delete', request_method='POST')
    def accounts_delete(self):
        location = self.request.route_path('accounts')
        account_name = self.request.params.get('name')
        if self.delete_form.validate():
            with boto_error_handler(self.request, location):
                self.log_request(_(u"Deleting account {0}").format(account_name))
                params = {'AccountName': account_name, 'Recursive': 'true'}
                self.conn.get_response('DeleteAccount', params)
                msg = _(u'Successfully deleted account')
                self.request.session.flash(msg, queue=Notification.SUCCESS)
        else:
            msg = _(u'Unable to delete account.')  # TODO Pull in form validation error messages here
            self.request.session.flash(msg, queue=Notification.ERROR)
        return HTTPFound(location=location)


class AccountsJsonView(BaseView):
    """Accounts returned as JSON"""
    def __init__(self, request):
        super(AccountsJsonView, self).__init__(request)
        self.conn = self.get_connection(conn_type="iam")

    @view_config(route_name='accounts_json', renderer='json', request_method='POST')
    def accounts_json(self):
        # TODO: take filters into account??
        accounts = []
        for account in self.get_items():
            policies = []
            try:
                policies = self.conn.get_response('ListAccountPolicies', params={'AccoutnName':account.account_name}, list_marker='PolicyNames')
                policies = policies.policy_names
            except BotoServerError as exc:
                pass
            accounts.append(dict(
                account_name=account.account_name,
                account_id=account.account_id,
                policy_count=len(policies),
            ))
        return dict(results=accounts)

    def get_items(self):
        with boto_error_handler(self.request):
            return self.conn.get_response('ListAccounts', params={}, list_marker='Accounts').accounts


class AccountView(BaseView):
    """Views for single Account"""
    TEMPLATE = '../templates/accounts/account_view.pt'

    def __init__(self, request):
        super(AccountView, self).__init__(request)
        self.conn = self.get_connection(conn_type="iam")
        self.account = self.get_account()
        self.account_route_id = self.request.matchdict.get('name')
        self.account_form = AccountForm(self.request, account=self.account, formdata=self.request.params or None)
        self.account_update_form = AccountUpdateForm(self.request, account=self.account, formdata=self.request.params or None)
        self.delete_form = DeleteAccountForm(self.request, formdata=self.request.params)
        self.quotas_form = QuotasForm(self.request, account=self.account, conn=self.conn)
        self.render_dict = dict(
            account=self.account,
            account_route_id=self.account_route_id,
            account_form=self.account_form,
            account_update_form=self.account_update_form,
            delete_form=self.delete_form,
            quota_err=_(u"Requires non-negative integer (or may be empty)"),
            quotas_form=self.quotas_form,
        )

    def get_account(self):
        account_param = self.request.matchdict.get('name')
        # Return None if the request is to create new account. Prob. No accountname "new" can be created
        if account_param == "new" or account_param is None:
            return None
        account = None
        try:
            accounts = self.conn.get_response('ListAccounts', params={}, list_marker='Accounts').accounts
            account = [account for account in accounts if account.account_name == account_param][0] 
        except BotoServerError as err:
            pass
        return account

    @view_config(route_name='account_view', renderer=TEMPLATE)
    def account_view(self):
        if self.account is not None:
            users = self.conn.get_response('ListUsers', params={'DelegateAccount':self.account.account_name}, list_marker='Users')
            self.render_dict['users'] = users.list_users_response.list_users_result.users
        return self.render_dict
 
    @view_config(route_name='account_create', request_method='POST', renderer='json')
    def account_create(self):
        if self.account_form.validate():
            new_account_name = self.request.params.get('account_name') 
            location = self.request.route_path('account_view', name=new_account_name)
            with boto_error_handler(self.request, location):
                self.log_request(_(u"Creating account {0}").format(new_account_name))
                self.conn.get_response('CreateAccount', params={'AccountName':new_account_name})
                admin_password = PasswordGeneration.generate_password()
                params = {'UserName':'admin', 'Password':admin_password, 'DelegateAccount':new_account_name}
                result = self.conn.get_response('CreateLoginProfile', params=params, verb='POST')
                params = {'UserName':'admin', 'DelegateAccount':new_account_name}
                creds = self.conn.get_response('CreateAccessKey', params=params, verb='POST')
                access_id = creds.access_key.access_key_id
                secret_key = creds.access_key.secret_access_key

                quotas = Quotas()
                quotas.create_quota_policy(self, account=new_account_name)

                users_json = self.request.params.get('users')
                user_list = []
                if users_json:
                    users = json.loads(users_json)
                    path = '/'
                    for (name, email) in users.items():
                        self.log_request(_(u"Creating user {0}").format(name))
                        user = self.conn.get_response('CreateUser', params={'UserName':name, 'Path':path, 'DelegateAccount':new_account_name})
                        self.log_request(_(u"Generating password for user {0}").format(name))
                        password = PasswordGeneration.generate_password()
                        self.conn.get_response('CreateLoginProfile', params={'UserName':name, 'Password':password, 'DelegateAccount':new_account_name})
                        self.log_request(_(u"Creating access keys for user {0}").format(name))
                        creds = self.conn.get_response('CreateAccessKey', params={'UserName':name, 'DelegateAccount':new_account_name})
                        user_list.append([new_account_name, name, password, creds.access_key.access_key_id, creds.access_key.secret_access_key])

                # assemble file response
                string_output = StringIO.StringIO()
                csv_w = csv.writer(string_output)
                header = [_(u'Account'), _(u'User Name'), _(u'Password'), _(u'Access Key'), _(u'Secret Key')]
                csv_w.writerow(header)
                row = [new_account_name, 'admin', admin_password, access_id, secret_key]
                csv_w.writerow(row)
                for user in user_list:
                    csv_w.writerow(user)
                self._store_file_("{acct}-users.csv".format(acct=new_account_name),
                                  'text/csv', string_output.getvalue())

                return dict(
                    message=_(u"Successfully created account {account}").format(account=new_account_name),
                    results=dict(hasFile='y')
                )

        return self.render_dict

    @view_config(route_name='account_update', request_method='POST', renderer=TEMPLATE)
    def account_update(self):
        if self.account_update_form.validate():
            location = self.request.route_path('account_view', name=self.account.account_name)
            with boto_error_handler(self.request, location):
                quotas = Quotas()
                quotas.update_quotas(self, account=self.account.account_name, as_account='')
            return HTTPFound(location=location)

        return self.render_dict

    @view_config(route_name='account_delete', request_method='POST')
    def account_delete(self):
        if not self.delete_form.validate():
            return JSONResponse(status=400, message="missing CSRF token")
        location = self.request.route_path('accounts')
        if self.account is None:
            raise HTTPNotFound()
        with boto_error_handler(self.request, location):
            self.log_request(_(u"Deleting account {0}").format(self.account.account_name))
            params = {'AccountName': self.account.account_name, 'IsRecursive': 'true'}
            self.conn.get_response('DeleteAccount', params)
            msg = _(u'Successfully deleted account')
            self.request.session.flash(msg, queue=Notification.SUCCESS)
        return HTTPFound(location=location)

    def account_update_name(self, new_account_name ):
        this_account_name = new_account_name if new_account_name is not None else self.account.account_name
        self.conn.update_account(self.account.account_name, new_account_name=new_account_name)
        msg_template = _(u'Successfully modified account {account}')
        msg = msg_template.format(account=this_account_name)
        self.request.session.flash(msg, queue=Notification.SUCCESS)
        return

    @view_config(route_name='account_policies_json', renderer='json', request_method='GET')
    def account_policies_json(self):
        """Return account policies list"""
        with boto_error_handler(self.request):
            policies = self.conn.get_response('ListAccountPolicies', params={'AccountName':self.account.account_name}, list_marker='PolicyNames')
            return dict(results=policies.policy_names)

    @view_config(route_name='account_policy_json', renderer='json', request_method='GET')
    def account_policy_json(self):
        """Return account policies list"""
        with boto_error_handler(self.request):
            policy_name = self.request.matchdict.get('policy')
            policy = self.conn.get_response('GetAccountPolicy', params={'AccountName':self.account.account_name, 'PolicyName':policy_name}, verb='POST')
            parsed = json.loads(policy.policy_document)
            return dict(results=json.dumps(parsed, indent=2))

    @view_config(route_name='account_update_policy', request_method='POST', renderer='json')
    def account_update_policy(self):
        if not(self.is_csrf_valid()):
            return JSONResponse(status=400, message="missing CSRF token")
        # calls iam:PutAccountPolicy
        policy = self.request.matchdict.get('policy')
        with boto_error_handler(self.request):
            self.log_request(_(u"Updating policy {0} for account {1}").format(policy, self.account.account_name))
            policy_text = self.request.params.get('policy_text')
            result = self.conn.get_response('PutAccountPolicy', params={'AccountName':self.account.account_name, 'PolicyName':policy, 'PolicyDocument':policy_text}, verb='POST')
            return dict(message=_(u"Successfully updated account policy"), results=result)

    @view_config(route_name='account_delete_policy', request_method='POST', renderer='json')
    def account_delete_policy(self):
        if not self.is_csrf_valid():
            return JSONResponse(status=400, message="missing CSRF token")
        # calls iam:DeleteAccountPolicy
        policy = self.request.matchdict.get('policy')
        with boto_error_handler(self.request):
            self.log_request(_(u"Deleting policy {0} for account {1}").format(policy, self.account.account_name))
            result = self.conn.get_response('DeleteAccountPolicy', params={'AccountName':self.account.account_name, 'PolicyName':policy}, verb='POST')
            return dict(message=_(u"Successfully deleted account policy"), results=result)

