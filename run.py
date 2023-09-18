from app import create_app, db
from app.models import User

if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        db.create_all()
        if User.query.filter_by(name='denis').first() is None:
            User.register('denis', '42')
        if User.query.filter_by(name='nikita').first() is None:
            User.register('nikita', 'tzolkin')
    app.run()
