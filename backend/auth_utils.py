import jwt
import datetime
from config import SECRET_KEY

def generate_token(user):
    return jwt.encode({
        "id": user[0],
        "role": user[4],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=5)
    }, SECRET_KEY, algorithm="HS256")