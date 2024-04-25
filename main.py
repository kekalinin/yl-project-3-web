import db_session
from app import app

if __name__ == '__main__':
    db_session.global_init("photo.db")

    app.run(port=8080, host='127.0.0.1')
