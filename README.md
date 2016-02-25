Highlander client
==============

Python client for Highlander REST API. Includes python library for Highlander API and Command Line Interface (CLI) library.

There can be only one!

Installation
------------

First of all, clone the repo and go to the repo directory:

    git clone https://github.com/stratus/python-highlanderclient.git
    cd python-highlanderclient

Then just run:

    pip install -e .

or

    python setup.py install


Running Highlander client
----------------------

If Highlander authentication is enabled, provide the information about OpenStack auth to environment variables. Type:

    export OS_AUTH_URL=http://<Keystone_host>:5000/v2.0
    export OS_USERNAME=admin
    export OS_TENANT_NAME=tenant
    export OS_PASSWORD=secret
    export OS_HIGHLANDER_URL=http://<Highlander host>:8989/v1  (optional, by default URL=http://localhost:8989/v1)

and in the case that you are authenticating against keystone over https:

    export OS_CACERT=<path_to_ca_cert>

>***Note:** In client, we can use both Keystone auth versions - v2.0 and v3. But server supports only v3.*

To make sure Highlander client works, type:

    highlander claymore-list

You can see the list of available commands typing:

    highlander --help
