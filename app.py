"""
Elastic License 2.0

Copyright Clack and/or licensed to Clack under one
or more contributor license agreements. Licensed under the Elastic License;
you may not use this file except in compliance with the Elastic License.
"""
from apiflask import APIFlask
from dotenv import load_dotenv

from clack import ratelimiter
from clack.guilds.routes import guilds
from clack.json import ORJSONDecoder, ORJSONEncoder
from clack.relationships.routes import relationships
from clack.users.routes import registerr, users

load_dotenv()

from clack.database import connect, sync_tables

connect()
sync_tables()

app = APIFlask(
    __name__,
    title='Clack API',
    version='v1',
    spec_path='/__development/developer-kelp.open.json',
    docs_path='/__development/developer_ke-lp-dash.board',
    docs_ui='elements',
)

ratelimiter.limiter.init_app(app=app)
app.config['INFO'] = {
    'description': 'The API for Clack.',
    'termsOfService': 'https://derailed.one/terms',
    'contact': {'name': 'Support', 'email': 'support@derailed.one'},
    'license': {
        'name': 'Apache-2.0',
        'url': 'https://www.apache.org/licenses/LICENSE-2.0',
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


if __name__ == "__main__":
    app.run(debug=True)
