from datetime import timedelta
from flask import Flask
from data.db_session import global_init


class MainApp(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)
        self.config['SECRET_KEY'] = 'super-secret-key'
        self.template_folder = 'templates'
        global_init('db/data.db')

