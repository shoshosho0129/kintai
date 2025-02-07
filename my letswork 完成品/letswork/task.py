from celery import shared_task
from letswork.views import save_previous_day_attendance

@shared_task
def scheduled_attendance_save():
    save_previous_day_attendance()