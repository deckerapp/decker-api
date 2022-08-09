"""
Elastic License 2.0

Copyright Discorse and/or licensed to Discorse under one
or more contributor license agreements. Licensed under the Elastic License;
you may not use this file except in compliance with the Elastic License.
"""
import logging
import os

from apiflask import APIFlask
from dotenv import load_dotenv

from discorse import ratelimiter
from discorse.guilds.routes import guilds
from discorse.json import ORJSONDecoder, ORJSONEncoder
from discorse.relationships.routes import relationships
from discorse.users.routes import registerr, users

load_dotenv()

import sentry_sdk

from discorse.database import connect, sync_tables

# TODO: Test and maybe modify traces_sample_rate.
sentry_sdk.init(dsn=os.getenv('SENTRY_DSN'), traces_sample_rate=1.0)
connect()
sync_tables()

app = APIFlask(
    __name__,
    title='Discorse API',
    version='v1',
    spec_path='/__development/openapi.json',
    docs_path='/__development/board',
    docs_ui='elements',
)

ratelimiter.limiter.init_app(app=app)
app.config['INFO'] = {
    'description': 'The API for Discorse.',
    'termsOfService': 'https://derailed.one/terms',
    'contact': {'name': 'Support', 'email': 'support@derailed.one'},
    'license': {
        'name': 'ELv2',
        'url': 'https://www.elastic.co/licensing/elastic-license',
    },
}
app.tags = ['Users', 'Relationships', 'Guilds']
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
