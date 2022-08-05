from dotenv import load_dotenv

from twattle.database import connect, sync_tables
from twattle.users import routes

load_dotenv()

connect()
sync_tables()

user = routes.create_user(
    {'email': 'example@example.org', 'username': 'example', 'password': 'example'}
)

print(routes.create_token(user_id=user.id, user_password=user.password))
