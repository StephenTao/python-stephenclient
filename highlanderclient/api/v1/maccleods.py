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

from highlanderclient.api import base


class Maccleod(base.Resource):
    resource_name = 'Maccleod'


class MaccleodManager(base.ResourceManager):
    resource_class = Maccleod

    def create(self, definition):
        self._ensure_not_empty(definition=definition)

        resp = self.client.http_client.post(
            '/maccleods',
            definition,
            headers={'content-type': 'text/plain'}
        )

        if resp.status_code != 201:
            self._raise_api_exception(resp)

        return self.resource_class(self, base.extract_json(resp, None))

    def update(self, definition):
        self._ensure_not_empty(definition=definition)

        resp = self.client.http_client.put(
            '/maccleods',
            definition,
            headers={'content-type': 'text/plain'}
        )

        if resp.status_code != 200:
            self._raise_api_exception(resp)

        return self.resource_class(self, base.extract_json(resp, None))

    def list(self):
        return self._list('/maccleods', response_key='maccleod')

    def get(self, name):
        self._ensure_not_empty(name=name)

        return self._get('/maccleod/%s' % name)

    def delete(self, name):
        self._ensure_not_empty(name=name)

        self._delete('/maccleods/%s' % name)

    def validate(self, definition):
        self._ensure_not_empty(definition=definition)

        resp = self.client.http_client.post(
            '/maccleods/validate',
            definition,
            headers={'content-type': 'text/plain'}
        )

        if resp.status_code != 200:
            self._raise_api_exception(resp)

        return base.extract_json(resp, None)
