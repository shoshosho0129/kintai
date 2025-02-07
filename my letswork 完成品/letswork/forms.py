from django import forms
from django.utils import timezone
from .models import Paid, Work
from account .models import Account_e


#打刻
class TimeStampForm(forms.ModelForm):
    e_id = forms.ModelChoiceField(
        queryset=Account_e.objects.all(),  # ここで Account_e の全てのオブジェクトを指定
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': 'true',
        }),
        label="従業員ID"
    )

    class Meta:
        model = Work
        fields = ['e_id', 'w_start', 'b_start', 'b_end', 'w_end']  # e_id を含む
        widgets = {
            'w_start': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': 'true',
            }),
            'b_start': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': 'true',
            }),
            'b_end': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': 'true',
            }),
            'w_end': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': 'true',
            }),
        }

    def clean(self):
        """
        バリデーション: 入力時間の一貫性を確認
        - 出勤時間 (w_start) < 休憩開始時間 (b_start)
        - 休憩終了時間 (b_end) < 退勤時間 (w_end)
        """
        cleaned_data = super().clean()
        w_start = cleaned_data.get('w_start')
        b_start = cleaned_data.get('b_start')
        b_end = cleaned_data.get('b_end')
        w_end = cleaned_data.get('w_end')

        # バリデーションルール: 時間の順序を確認
        if w_start and b_start and w_start > b_start:
            self.add_error('b_start', '休憩開始時間は出勤時間より後である必要があります。')
        if b_start and b_end and b_start > b_end:
            self.add_error('b_end', '休憩終了時間は休憩開始時間より後である必要があります。')
        if b_end and w_end and b_end > w_end:
            self.add_error('w_end', '退勤時間は休憩終了時間より後である必要があります。')

        return cleaned_data
    
#有給
class PaidForm(forms.ModelForm):
    class Meta:
        model = Paid
        fields = ['p_time']  # モデルで定義した有給日付を使用
        widgets = {
            'p_time': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            
        }
        labels = {
            'p_time': '有給日付',
        }
        
        
        