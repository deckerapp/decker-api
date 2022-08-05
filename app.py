"""
Copyright 2021-2022 twattle, Inc.

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
from apiflask import APIFlask
from dotenv import load_dotenv

from twattle import ratelimiter
from twattle.guilds.routes import guilds
from twattle.json import ORJSONDecoder, ORJSONEncoder
from twattle.relationships.routes import relationships
from twattle.users.routes import registerr, users

load_dotenv()

from twattle.database import connect, sync_tables

connect()
sync_tables()

app = APIFlask(
    __name__,
    title='Twattle API',
    version='v1',
    spec_path='/__development/developer-kelp.open.json',
    docs_path='/__development/developer_ke-lp-dash.board',
    docs_ui='elements',
)

ratelimiter.limiter.init_app(app=app)
app.config['INFO'] = {
    'description': 'The API for Twattle.',
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
