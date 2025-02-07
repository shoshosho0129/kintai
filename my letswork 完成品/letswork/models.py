from django.db import models
from django.utils.timezone import now
from datetime import timedelta

#打刻
class Work(models.Model):
    class Meta:
        db_table = 'work'
    
    id = models.AutoField(verbose_name='勤怠id', primary_key=True)
    w_start = models.DateTimeField(verbose_name='勤怠開始時間')
    b_start = models.DateTimeField(verbose_name='休憩開始', null=True, blank=True)
    b_end = models.DateTimeField(verbose_name='休憩終了', null=True, blank=True)
    w_end = models.DateTimeField(verbose_name='勤怠終了時間', null=True, blank=True)
    p_hour = models.IntegerField(verbose_name='過去の時給',null=True, blank=True)
    attendance_date = models.DateField(default=now)
    work_duration_formatted = models.CharField(
        verbose_name='労働時間（HH:MM形式）',
        max_length=10,
        default='',
        blank=True
    )
    e_id = models.ForeignKey('account.Account_e', on_delete=models.CASCADE, verbose_name='従業員id')
    
    def save(self, *args, **kwargs):
        """ 勤怠時間を自動計算し、保存時に `work_duration_formatted` を更新する """
        if self.w_start and self.w_end:
            work_duration = self.w_end - self.w_start
            if self.b_start and self.b_end:
                work_duration -= (self.b_end - self.b_start)  # 休憩時間を引く
            
            # 労働時間を HH:MM 形式に変換
            hours = work_duration.seconds // 3600
            minutes = (work_duration.seconds % 3600) // 60
            self.work_duration_formatted = f"{hours:02}:{minutes:02}"
        
        super(Work, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"勤怠ID: {self.id} / 従業員: {self.e_id}"


#有給登録
class Paid(models.Model):
    class Meta:
        db_table = 'paid'
        
    id = models.AutoField(verbose_name='有給id', primary_key=True)
    p_time = models.DateField(verbose_name='有給日付')
    a_no = models.ForeignKey('account.Account_a', on_delete=models.CASCADE, verbose_name='管理者id')
    e_id = models.ForeignKey('account.Account_e', on_delete=models.CASCADE, verbose_name='従業員id', null=True, blank=True)
    
    def __str__(self):
        return str(self.e_id)
    
    
class Salary(models.Model):
    e_id = models.ForeignKey('account.Account_e', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)  # 記録した日
    total_salary = models.FloatField(default=0)  # 累積の給与
    
    def __str__(self):
        return f"{self.e_id.e_id} - {self.date}: {self.total_salary}円"