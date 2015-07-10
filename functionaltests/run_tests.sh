#!/bin/bash
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# How many seconds to wait for the API to be responding before giving up
API_RESPONDING_TIMEOUT=20

if ! timeout ${API_RESPONDING_TIMEOUT} sh -c "while ! curl -s http://127.0.0.1:8989/v2/ 2>/dev/null | grep -q 'Authentication required' ; do sleep 1; done"; then
    echo "Mistral API failed to respond within ${API_RESPONDING_TIMEOUT} seconds"
    exit 1
fi

echo "Successfully contacted Mistral API"

export BASE=/opt/stack
export MISTRALCLIENT_DIR="$BASE/new/python-mistralclient"

# Get demo credentials.
cd ${BASE}/new/devstack
source openrc demo demo

export OS_ALT_USERNAME=${OS_USERNAME}
export OS_ALT_TENANT_NAME=${OS_TENANT_NAME}
export OS_ALT_PASSWORD=${OS_PASSWORD}

# Get admin credentials.
source openrc admin admin

# Store these credentials into the config file.
CREDS_FILE=${MISTRALCLIENT_DIR}/functional_creds.conf
cat <<EOF > ${CREDS_FILE}
# Credentials for functional testing
[auth]
uri = $OS_AUTH_URL
[admin]
user = $OS_USERNAME
tenant = $OS_TENANT_NAME
pass = $OS_PASSWORD
[demo]
user = $OS_ALT_USERNAME
tenant = $OS_ALT_TENANT_NAME
pass = $OS_ALT_PASSWORD
EOF

cd $MISTRALCLIENT_DIR

# Run tests
tox -efunctional -- nosetests -sv mistralclient/tests/functional
