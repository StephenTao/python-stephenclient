# Copyright 2014 - Mirantis, Inc.
# Copyright 2015 - StackStorm, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import six

from highlanderclient.api import httpclient

from highlanderclient.api.v1 import maccleods



class Client(object):
    def __init__(self, highlander_url=None, username=None, api_key=None,
                 project_name=None, auth_url=None, project_id=None,
                 endpoint_type='publicURL', service_type='maccleodv1',
                 auth_token=None, user_id=None, cacert=None):

        if highlander_url and not isinstance(highlander_url, six.string_types):
            raise RuntimeError('Highlander url should be string')

        if auth_url:
            (highlander_url, auth_token, project_id, user_id) = (
                self.authenticate(highlander_url, username, api_key,
                                  project_name, auth_url, project_id,
                                  endpoint_type, service_type, auth_token,
                                  user_id, cacert))

        if not highlander_url:
            highlander_url = "http://localhost:8989/v1"

        self.http_client = httpclient.HTTPClient(highlander_url,
                                                 auth_token,
                                                 project_id,
                                                 user_id)
        # Create all resource managers.
        self.maccleods = maccleods.MaccleodManager(self)
       

    def authenticate(self, highlander_url=None, username=None, api_key=None,
                     project_name=None, auth_url=None, project_id=None,
                     endpoint_type='publicURL', service_type='maccleodv1',
                     auth_token=None, user_id=None, cacert=None):

        if project_name and project_id:
            raise RuntimeError('Only project name or '
                               'project id should be set')

        if username and user_id:
            raise RuntimeError('Only user name or user id'
                               ' should be set')

        keystone_client = _get_keystone_client(auth_url)

        keystone = keystone_client.Client(
            username=username,
            user_id=user_id,
            password=api_key,
            token=auth_token,
            tenant_id=project_id,
            tenant_name=project_name,
            auth_url=auth_url,
            endpoint=auth_url,
            cacert=cacert)

        keystone.authenticate()
        token = keystone.auth_token
        user_id = keystone.user_id
        project_id = keystone.project_id

        if not highlander_url:
            catalog = keystone.service_catalog.get_endpoints(
                service_type=service_type,
                endpoint_type=endpoint_type
            )
            if service_type in catalog:
                service = catalog.get(service_type)
                highlander_url = service[0].get('url') if service else None

        return highlander_url, token, project_id, user_id


def _get_keystone_client(auth_url):
    if "v2.0" in auth_url:
        from keystoneclient.v2_0 import client
    else:
        from keystoneclient.v3 import client

    return client
