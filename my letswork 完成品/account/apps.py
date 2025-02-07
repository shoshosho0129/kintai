from django.apps import AppConfig
from django.contrib.auth.signals import user_logged_in


class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'

    def ready(self):
        # ログイン時の last_login 更新を無効化
        from django.utils.timezone import now

        def disable_last_login_update(sender, request, user, **kwargs):
            # last_loginを更新せず何もしない
            pass

        # シグナルに空の処理を登録する
        user_logged_in.disconnect(dispatch_uid="update_last_login")
        user_logged_in.connect(disable_last_login_update, dispatch_uid="disable_last_login_update")
