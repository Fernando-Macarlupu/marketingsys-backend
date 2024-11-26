from django.apps import AppConfig


class JobsConfig(AppConfig):
    name = 'jobs'
    def ready(self):
        print('ready...')
        from jobs import views
        views.start()
