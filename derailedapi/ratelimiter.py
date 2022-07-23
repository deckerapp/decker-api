"""
Copyright 2021-2022 Derailed.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os

import jwt
from flask import request
from flask_limiter import Limiter, util

from .database import Token

AUTH_KEY = None


def key_func():
    auth = request.headers.get('Authorization', None)

    if auth is None:
        return util.get_remote_address()

    try:
        real_token = jwt.decode(auth, AUTH_KEY, ['HS256'])
    except:
        return util.get_remote_address()

    try:
        token: Token = Token.objects(
            Token.token == real_token['token'], Token.user_id == real_token['user_id']
        ).get()
    except:
        return util.get_remote_address()
    else:
        return str(token.user_id)


limiter = Limiter(
    key_func=key_func,
    key_prefix='derailed_limiting',
    headers_enabled=True,
    strategy='fixed-window-elastic-expiry',
    storage_uri=os.getenv('STORAGE_URI'),
    default_limits=['50/second'],
)
