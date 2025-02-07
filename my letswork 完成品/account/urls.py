from django.urls import path
from account import views

app_name = 'account'
urlpatterns = [
    path('login/', views.user_login, name='user_login'), #ログイン
    path('logout/', views.LogoutView.as_view(), name='user_logout'), #ログアウト
    path('signup/', views.admin_signup, name='a_signup'), #管理者新規登録
    path('signup/confirm/', views.signup_confirm, name='a_signup_confirm'), #管理者登録確認
    path('e_register/', views.E_RegisterView.as_view(),name='e_register'), #従業員新規登録
    path('employee/<int:e_id>/change_name/',views.ChangeNameView.as_view(), name='change_name'),#従業員氏名変更
    path('employee/<int:e_id>/delete/', views.E_DeleteView.as_view(), name='delete'),# #従業員削除
]