from flask_wtf import Form, FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField


class LoginForm(Form):
    name = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
