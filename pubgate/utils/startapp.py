from sanic.log import logger

from pubgate.db import User


def register_extensions(app):

    extensions = app.config.EXTENSIONS
    if app.config.get('UI_APP'):
        ui_app = __import__(app.config.UI_APP)
        app.ui_app_index = getattr(ui_app, 'index_view', None)
        extensions.append(app.config.UI_APP)
    else:
        app.ui_app_index = None

    for extension in extensions:
        ext = __import__(extension)

        ext_bps = getattr(ext, 'pg_blueprints', [])
        for bp in ext_bps:
            app.blueprint(bp)

        ext_tasks = getattr(ext, 'pg_tasks', [])
        for task in ext_tasks:
            app.add_task(task)


def on_deploy_user(app):
    if app.config.get('USER_ON_DEPLOY'):
        user_data = app.config.USER_ON_DEPLOY
        username = user_data["username"].lower()
        password = user_data["password"]
        if username and password:
            is_uniq = await User.is_unique(doc=dict(name=username))
            if is_uniq in (True, None):
                user = await User.create(user_data, app.base_url)
                logger.info(f"On-deploy user {username} created")
