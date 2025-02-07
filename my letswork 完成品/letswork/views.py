from django.shortcuts import get_object_or_404, render,redirect
from django.views import View
from django.utils import timezone
from django.contrib import messages
from letswork.models import Work, Paid, Salary
from .forms import TimeStampForm, PaidForm
from account .models import Account_e, Account_a
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import now
from django.conf import settings
from django.db.models import Sum
import json
import os
from django.db.models import Q
from account.models import Paid
from barcode import JAN
from datetime import timedelta
from datetime import datetime
from barcode.writer import ImageWriter
from django.utils.dateparse import parse_datetime
from django.db.models.functions import ExtractMonth, ExtractDay
from django.utils.timezone import localtime



#打刻
class SearchView(View):
    def get(self, request, e_id):
        last_work = []
        if e_id:
            today = datetime.today()
            current_month = today.month
            current_day = today.day            
            
            # 最後の出勤記録を取得
            last_work = Work.objects.annotate(
                    month=ExtractMonth('w_start'),
                    day=ExtractDay('w_start')
                ).filter(e_id=e_id, month=current_month, day=current_day).first()
            if last_work:
                result_data = {
                    'w_start': last_work.w_start.isoformat() if last_work.w_start else None,
                    'w_end': last_work.w_end.isoformat() if last_work.w_end else None,
                    'b_start': last_work.b_start.isoformat() if last_work.b_start else None,
                    'b_end': last_work.b_end.isoformat() if last_work.b_end else None,
                }
            else:
                result_data = []
        
        print(result_data)
        return JsonResponse({'results': result_data})


class TimeStampView(View):
    def get(self, request):
        # 空のフォームを初期状態で渡す
        form = TimeStampForm()
        return render(request, 'letswork/stamp.html', {'form': form})
    
    def post(self, request):
        form = TimeStampForm(request.POST)
        
        action = request.POST.get('action')
        if action == 'w_start':
            if form.is_valid():
                e_id = form.cleaned_data.get('e_id')  # 入力された従業員IDを取得
                today = datetime.today()
                current_month = today.month
                current_day = today.day            
                
                # 最後の出勤記録を取得
                last_work = Work.objects.annotate(
                        month=ExtractMonth('w_start'),
                        day=ExtractDay('w_start')
                    ).filter(e_id=e_id, month=current_month, day=current_day).first()
            
                if last_work:
                    start_time = localtime(last_work.w_start)  # 出勤時間をローカルタイムに変換
                    print(f"直前の出勤時間（ローカルタイム）: {start_time}")
                else:
                    print("出勤記録が見つかりませんでした。")
                    start_time = form.cleaned_data.get('w_start')  # 出勤記録がない場合

                    # 新しい勤怠データを保存
                    work = form.save(commit=False)
                    work.e_id = e_id
                    work.save()
                
                return redirect('letswork:stamp')
            
        elif action == 'w_end':
            if form.is_valid():
                e_id = form.cleaned_data.get('e_id')
                today = datetime.today()
                current_month = today.month
                current_day = today.day

                # 当日の出勤記録を取得
                work = Work.objects.annotate(
                    month=ExtractMonth('w_start'),
                    day=ExtractDay('w_start')
                ).filter(e_id=e_id, month=current_month, day=current_day).first()

                if work:
                    work.w_end = timezone.now()  # 現在時刻を退勤時間に設定
                    work.save()
                    messages.success(request, "退勤時間を登録しました。")
                else:
                    messages.error(request, "出勤記録が見つかりません。先に出勤を登録してください。")

                return redirect('letswork:stamp')

        
        elif action == 'b_start':
            if form.is_valid():
                e_id = form.cleaned_data.get('e_id')
                today = datetime.today()
                current_month = today.month
                current_day = today.day

                # 当日の出勤記録を取得
                work = Work.objects.annotate(
                    month=ExtractMonth('w_start'),
                    day=ExtractDay('w_start')
                ).filter(e_id=e_id, month=current_month, day=current_day).first()
 
                if work:
                    work.b_start = timezone.now()  # 現在時刻を休憩開始時間に設定
                    work.save()
                    messages.success(request, "休憩開始時間を登録しました。")
                else:
                    messages.error(request, "出勤記録が見つかりません。先に出勤を登録してください。")

                return redirect('letswork:stamp')
            
        elif action == 'b_end':
            if form.is_valid():
                e_id = form.cleaned_data.get('e_id')
                today = datetime.today()
                current_month = today.month
                current_day = today.day

                # 当日の出勤記録を取得
                work = Work.objects.annotate(
                    month=ExtractMonth('w_start'),
                    day=ExtractDay('w_start')
                ).filter(e_id=e_id, month=current_month, day=current_day).first()

                if work:
                    work.b_end = timezone.now()  # 現在時刻を休憩終了時間に設定
                    work.save()
                    messages.success(request, "休憩終了時間を登録しました。")
                else:
                    messages.error(request, "出勤記録が見つかりません。先に出勤を登録してください。")

                return redirect('letswork:stamp')

            
            
        else:
            # 入力エラーの場合、再度フォームを表示
            print(form.errors.as_data())
            return redirect('letswork:stamp')

#従業員一覧
class EmployeeListView(View):
    model = Account_e
    template_name = 'letswork/e_list.html'
    paginate_by = 10 #１ページ当たり10件表示
    
    
    
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('q','')
        employees = self.model.objects.all()
        
        if search_query:

            employees = employees.filter(
                Q(e_first1__icontains=search_query) |
                Q(e_last1__icontains=search_query) |
                Q(e_first2__icontains=search_query) |
                Q(e_last2__icontains=search_query)  
            )
        
        paginator = Paginator(employees, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Account_a のデータを取得
        account_admins = Account_a.objects.filter(is_active=True)
        
        context = {
            'page_obj': page_obj,
            'account_admins': request.user, 
        }# Account_a のデータをコンテキストに追加
        
        return render(request, self.template_name, context)

#従業員詳細
class EmployeeDetailView(View):
    template_name = 'letswork/attendance informationdetails.html'

    def get(self, request, e_id, *args, **kwargs):
        save_previous_day_attendance()

        employee = get_object_or_404(Account_e, e_id=e_id)
        paid_entries = Paid.objects.filter(e_id=e_id)  # Paidモデルから特定ユーザーの情報を取得

        # URLパラメータから月情報を取得
        month_param = request.GET.get('month')
        if month_param:
            year, month = map(int, month_param.replace("年", "").replace("月", "").split())
        else:
            # デフォルトで現在の年月を取得
            now_date = timezone.now()
            year, month = now_date.year, now_date.month

        # 指定月の出勤日数を取得
        attendance_days = Work.objects.filter(
            e_id=e_id,
            attendance_date__year=year,
            attendance_date__month=month
        ).values('attendance_date').distinct().count()

        # 指定月の労働時間の合計を計算
        work_entries = Work.objects.filter(
            e_id=e_id,
            attendance_date__year=year,
            attendance_date__month=month
        )

        total_work_duration = timedelta(0)  # 合計労働時間の初期化
        
        # **過去のすべての勤務データを取得**
        all_work_entries = Work.objects.filter(e_id=e_id)  # すべての出勤データを取得
        for work in all_work_entries:
            if work.w_start and work.w_end:
                work_duration = work.w_end - work.w_start  # 1回の労働時間
                
                # 休憩時間を引く
                if work.b_start and work.b_end:
                    work_duration -= (work.b_end - work.b_start)

                total_work_duration += work_duration  # 合計時間に加算
        
        # データがない場合は "00:00" を設定
        if not all_work_entries.exists():
            total_work_duration_formatted = "00:00"
            total_hours, total_minutes = 0, 0  # 給与計算エラー回避のため
        else:
            # 合計労働時間を HH:MM 形式に変換
            total_hours = total_work_duration.total_seconds() // 3600
            total_minutes = (total_work_duration.total_seconds() % 3600) // 60
            total_work_duration_formatted = f"{int(total_hours):02}:{int(total_minutes):02}"

        # **月給を計算**
        hourly_wage = employee.hour  # 時給
        total_salary = hourly_wage * (total_hours + total_minutes / 60)  # 時給 × 労働時間

        # **有給の日数分を時給に加算（1日8時間として計算）**
        paid_days = Paid.objects.filter(
            e_id=e_id,
            p_time__year=year,
            p_time__month=month
        ).count()  # 指定月の有給日数をカウント
        
        # 8時間×有給日数分の給与を追加
        total_salary += hourly_wage * 8 * paid_days
        
        # **前日までの給与合計を取得**
        previous_salary_total = (
            Salary.objects.filter(
                e_id=employee,
                date__year=year,
                date__month=month,
            )
            .exclude(date=timezone.now().date())  # 今日のデータを除外
            .aggregate(Sum('total_salary'))['total_salary__sum'] or 0  # データがない場合は0
        )

        # **今日の給与データを保存（更新or新規作成）**
        salary_entry, created = Salary.objects.get_or_create(
            e_id=employee,
            date=timezone.now().date(),
            defaults={'total_salary': total_salary}  # 既存の給与を加算
        )

        if not created:
            salary_entry.total_salary = previous_salary_total + total_salary  # 加算処理
            salary_entry.save()

        # 選択肢用に過去12ヶ月のリストを生成
        months = [f"{year}年{m:02d}月" for m in range(1, 13)]

        return render(request, self.template_name, {
            'employee': employee,
            'attendance_days': attendance_days,
            'total_work_duration': total_work_duration_formatted,  # 合計労働時間
            'total_salary': round(total_salary),  # 月給（四捨五入）
            'month': f"{year}年{month:02d}月",
            'months': months,
            'account_admin': request.user,
            'paid_entries': paid_entries
        })
        
#勤怠情報修正
class attendance_edit(View):
    template_name = "letswork/attendance_infomation_correction.html"

    def get(self, request, e_id, *args, **kwargs):
        employee = get_object_or_404(Account_e, e_id=e_id)
        work = Work.objects.filter(e_id=e_id).last()  # 最新の勤怠情報を取得

        
        return render(request, self.template_name,{
            "employee": employee,
            "work": work,
            'account_admin': request.user,
            })

    def post(self, request, e_id, *args, **kwargs):
        work = Work.objects.filter(e_id=e_id).last()
        if not work:
            messages.error(request, "勤怠記録が存在しません。")
            return redirect("letswork:attendance_edit", e_id=e_id)

        # 入力値を取得
        work_date = request.POST.get("date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        break_start = request.POST.get("break_start")
        break_end = request.POST.get("break_end")

        try:
            # 文字列を datetime に変換
            if work_date and start_time:
                work.w_start = parse_datetime(f"{work_date}T{start_time}:00")

            if work_date and end_time:
                work.w_end = parse_datetime(f"{work_date}T{end_time}:00")

            if work_date and break_start:
                work.b_start = parse_datetime(f"{work_date}T{break_start}:00")

            if work_date and break_end:
                work.b_end = parse_datetime(f"{work_date}T{break_end}:00")

            work.save()
            messages.success(request, "勤怠記録を更新しました。")
        except ValueError:
            messages.error(request, "入力値に誤りがあります。")

        return redirect("letswork:employee_detail", e_id=e_id)
    
#勤怠情報詳細に必要
class EmployeeWorkSummaryAPI(View):
    def get(self, request, e_id, *args, **kwargs):
        employee = get_object_or_404(Account_e, e_id=e_id)

        # 月のパラメータを取得
        month_param = request.GET.get('month')
        if month_param:
            year, month = map(int, month_param.replace("年", "").replace("月", "").split())
        else:
            now_date = timezone.now()
            year, month = now_date.year, now_date.month

        # 指定月の労働時間合計
        work_entries = Work.objects.filter(
            e_id=e_id,
            attendance_date__year=year,
            attendance_date__month=month
        )

        total_work_duration = timedelta()
        for work in work_entries:
            total_work_duration += work.work_duration  # 各日の労働時間を加算

        # 労働時間を HH:MM 形式に変換
        total_hours = total_work_duration.total_seconds() // 3600
        total_minutes = (total_work_duration.total_seconds() % 3600) // 60
        total_work_duration_formatted = f"{int(total_hours):02}:{int(total_minutes):02}"

        # 月給の計算
        hourly_wage = employee.hour
        total_salary = hourly_wage * (total_hours + total_minutes / 60)

        return JsonResponse({
            "total_work_duration": total_work_duration_formatted,
            "total_salary": round(total_salary)
        })
        
#日付記録
def save_previous_day_attendance():
    # 今日の日付を取得
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    # 前日の勤怠情報が未保存の従業員を取得
    employees = Account_e.objects.all()
    
    for employee in employees:
        # 前日の勤怠記録があるか確認
        existing_record = Work.objects.filter(e_id=employee, attendance_date=yesterday).exists()
        
        if not existing_record:
            # 前日の勤怠記録がなければ、作成
            last_work_entry = Work.objects.filter(e_id=employee).order_by('-w_start').first()
            
            if last_work_entry and last_work_entry.w_start.date() == yesterday:
                # 勤怠開始と終了の時間を取得
                Work.objects.create(
                    e_id=employee,
                    w_start=last_work_entry.w_start,
                    w_end=last_work_entry.w_end,
                    attendance_date=yesterday,
                    p_hour=employee.hour  # その時点の時給を記録
                )
                
#出勤一覧
class WorkListView(View):
    def get(self, request, e_id):
        # 従業員IDに基づいて勤怠データをフィルタリング
        works = Work.objects.filter(e_id=e_id)
        
        # 従業員情報を取得（従業員IDに基づいて）
        employee = get_object_or_404(Account_e, e_id=e_id)
        
        # 取得したデータをテンプレートに渡してレンダリング
        return render(request, 'letswork/work_list.html', {'works': works, 'employee': employee})
    
#バーコード生成    
class GenerateJanBarcodeView(View):
    def get(self, request, e_id):
        # 従業員idにもとに従業員情報を取得
        try:
            employee = Account_e.objects.get(e_id=e_id)
        except Account_e.DoesNotExist:
            return JsonResponse({"error": "従業員が存在しません。"}, status=404)
        
        # JANコードは8桁
        jan_code = f"{employee.e_id:0>8}"[:8] #8桁にゼロ埋め
        
        # 出力ディレクトリ
        output_dir = os.path.join(settings.MEDIA_ROOT, 'barcodes')
        os.makedirs(output_dir, exist_ok=True)
        
        # JANコード画像の保存先パス
        file_path = os.path.join(output_dir,f"jan_code_{employee.e_id}.png")
        jan = JAN(jan_code, writer=ImageWriter())
        jan.save(file_path.replace('.png', ''),{"module_height": 15, "font_size": 10})
        
        # 画像を返す
        with open(file_path, 'rb') as image_file:
            return HttpResponse(image_file.read(), content_type="image/png")

#時給変更
class HourlyWageChangeView(View):
    template_name = 'letswork/hourly_wage_change.html'

    def get(self, request, e_id, *args, **kwargs):
        employee = get_object_or_404(Account_e, e_id=e_id)
        return render(request, self.template_name, {
            'employee': employee,
            'account_admins': request.user,  # ログインしている管理者を渡す
            })

    def post(self, request, e_id, *args, **kwargs):
        employee = get_object_or_404(Account_e, e_id=e_id)
        new_hourly_wage = request.POST.get('new_hourly_wage')
        if new_hourly_wage:
            try:
                employee.hour = float(new_hourly_wage)
                employee.save()
                messages.success(request, "時給を変更しました")
            except ValueError:
                messages.error(request, "無効な時給です")
        else:
            messages.error(request, "時給を入力してください")
        return redirect('letswork:employee_detail', e_id=e_id)


# hourly_wage_change 関数をクラス外部に定義
def hourly_wage_change(request):
    
    return render(request, 'letswork/hourly_wage_change.html')

# 有給登録
class PaidView(View):
    template_name = 'letswork/paid register.html'
    form_class = PaidForm

    def get(self, request, e_id, *args, **kwargs):
        # 該当の従業員情報を取得
        employee = get_object_or_404(Account_e, e_id=e_id)
        form = self.form_class(initial={'e_id': e_id})  # 空のフォームを初期化
        return render(request, self.template_name, {'employee': employee, 'form': form})

    def post(self, request, e_id, *args, **kwargs):
        # 従業員情報を取得
        employee = get_object_or_404(Account_e, e_id=e_id)
        form = self.form_class(request.POST)
        
        if form.is_valid():
            # フォームデータが正しい場合、有給情報を保存
            paid = form.save(commit=False)
            account_a = get_object_or_404(Account_a, a_no=request.user.a_no)  # `request.user.a_no`を使用
            paid.a_no = account_a # 現在のログイン中の管理者IDを設定
            paid.e_id = employee  # 従業員IDを設定 tuika
            paid.save()
            # 成功後、従業員詳細ページへリダイレクト
            return redirect('letswork:employee_detail', e_id=e_id)
        
        # エラーがあれば、再度フォームを表示
        return render(request, self.template_name, {'employee': employee, 'form': form})
    
#有給確認,削除
class PaidConfirmView(View):
    template_name = "letswork/paidconfirm.html"
    
    def get(self, request, e_id, *args, **kwargs):
        paid_entries = Paid.objects.filter(e_id=e_id)  # Paidモデルから特定ユーザーの情報を取得
        return render(request, self.template_name, {'paid_entries': paid_entries})
  
    def post(self, request, e_id):
        delete_id = request.POST.get('delete_id')  # 削除対象のIDを取得
        
        if delete_id:
            try:
                paid_entry = Paid.objects.get(id=delete_id)  # IDを基に対象のPaidオブジェクトを取得
                paid_entry.delete()  # 削除
            except Paid.DoesNotExist:
                pass  # 対象が存在しない場合は何もしない

        # 従業員一覧ページにリダイレクト
        return redirect('letswork:employee_detail', e_id=e_id)
    



