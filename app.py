"""
Elastic License 2.0

Copyright Decker and/or licensed to Decker under one
or more contributor license agreements. Licensed under the Elastic License;
you may not use this file except in compliance with the Elastic License.
"""
import logging
import os

from apiflask import APIFlask
from dotenv import load_dotenv

from decker import ratelimiter
from decker.guilds.routes import guilds
from decker.json import ORJSONDecoder, ORJSONEncoder
from decker.relationships.routes import relationships
from decker.users.routes import registerr, users

load_dotenv()

import sentry_sdk

from decker.database import connect, sync_tables

# TODO: Test and maybe modify traces_sample_rate.
sentry_sdk.init(dsn=os.getenv('SENTRY_DSN'), traces_sample_rate=1.0)
connect()
sync_tables()

app = APIFlask(
    __name__,
    title='Decker API',
    version='v1',
    spec_path='/__development/openapi.json',
    docs_path='/__development/board',
    docs_ui='elements',
)

ratelimiter.limiter.init_app(app=app)
app.config['INFO'] = {
    'description': 'The API for Decker.',
    'termsOfService': 'https://derailed.one/terms',
    'contact': {'name': 'Support', 'email': 'support@derailed.one'},
    'license': {
        'name': 'ELv2',
        'url': 'https://www.elastic.co/licensing/elastic-license',
    },
}
app.tags = [
    'Users',
    'Relationships',
    'Guilds',
    'Notes',
]
app.json_encoder = ORJSONEncoder
app.json_decoder = ORJSONDecoder


# register blueprints
app.register_blueprint(registerr)
app.register_blueprint(users)
app.register_blueprint(relationships)
app.register_blueprint(guilds)
ratelimiter.limiter.limit('2/hour')(registerr)


if __name__ == '__main__':
    app.run(debug=True)
