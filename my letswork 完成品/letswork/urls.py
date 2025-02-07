from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static
from .views import EmployeeWorkSummaryAPI

app_name = "letswork"
urlpatterns = [
    path('stamp/',views.TimeStampView.as_view(), name='stamp'), #打刻
    path('stamp/search/<int:e_id>',views.SearchView.as_view(), name='stamp_search'),
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),  # 従業員一覧
    path('employees/<int:e_id>/', views.EmployeeDetailView.as_view(), name='employee_detail'),# 従業員詳細
    path('api/employee-work-summary/<int:e_id>/', EmployeeWorkSummaryAPI.as_view(), name='employee_work_summary'),# 勤怠情報詳細に必要
    path("attendance/edit/<int:e_id>/", views.attendance_edit.as_view(), name="attendance_edit"),  # 勤怠修正
    path('hourly_wage_change/', views.hourly_wage_change, name='hourly_wage_change_debug'),  # 時給変更デバック用
    path('employees/hourly_wage_change/<int:e_id>', views.HourlyWageChangeView.as_view(), name='hourly_wage_change'),
    path('employees/paid_register/<int:e_id>/', views.PaidView.as_view(), name='paid_register'), #有給登録
    path('employees/paid_confirm/<int:e_id>/', views.PaidConfirmView.as_view(), name='paid_confirm'), #有給確認
    path('generate_barcode/<int:e_id>/', views.GenerateJanBarcodeView.as_view(), name='generate_jan_barcode'), #JANコード生成URL
    path('works/<int:e_id>/', views.WorkListView.as_view(), name='works'),
]

