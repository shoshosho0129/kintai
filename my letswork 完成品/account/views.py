from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from django.contrib.auth import login, logout, authenticate
from .forms import A_LoginForm, A_SignupForm, E_RegisterForm, ChangeNameForm
from django.views.generic.edit import FormView
from .models import Account_a, Account_e
from django.urls import reverse_lazy
from django.urls import reverse

#管理者
#ログイン
class A_LoginView(View):
    def post(self, request, *args, **kwargs):
        """
        管理者ログインビュー。フォーム入力内容を検証し、認証に成功した場合ログイン処理を行う。
        """
        form = A_LoginForm(request.POST)
        if form.is_valid():
            # フォームからデータ取得
            a_no = form.cleaned_data['a_no']
            a_pass = form.cleaned_data['a_pass']

            # カスタム認証バックエンドを利用した認証
            user = authenticate(request, a_no=a_no, password=a_pass)

            if user is not None:
                # 認証成功時にログイン処理
                login(request, user)
                return redirect(reverse('letswork:employee_list'))
            else:
                # 認証失敗時のエラーメッセージ
                messages.error(request, "ログイン情報が正しくありません。")
        else:
            # フォームの入力内容が無効な場合
            messages.error(request, "入力内容に誤りがあります。")
        return render(request, 'account/a_login.html', {'form': form})

    def get(self, request, *args, **kwargs):
        """
        GETリクエスト時にログインページを表示。
        """
        form = A_LoginForm()
        return render(request, 'account/a_login.html', {'form': form})

#ログアウト
class LogoutView(View):
    def get(self, request):
        """
        ログアウト処理を行い、ログインページへリダイレクト。
        """
        logout(request)
        messages.success(request, "ログアウトしました")
        return redirect('account:user_login')  # ログインページへリダイレクト
    
#管理者新規登録
class AdminSignupView(FormView):
    """
    管理者登録ビュー。登録情報をセッションに保存し、確認ページに遷移する。
    """
    template_name = "account/a_register.html"
    form_class = A_SignupForm
    success_url = reverse_lazy("account:a_signup_confirm")

    def form_valid(self, form):
        self.request.session['signup_data'] = form.cleaned_data
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "入力内容に誤りがあります。")
        return super().form_invalid(form)

#管理者確認
class SignupConfirmView(FormView):
    """
    管理者登録の確認ビュー。確認後、アカウントを作成する。
    """
    template_name = "account/a_confirmation.html"
    success_url = reverse_lazy("account:user_login")

    def get(self, request, *args, **kwargs):
        signup_data = self.request.session.get('signup_data')
        if not signup_data:
            return redirect("account:signup")
        password_length = len(signup_data['password1'])
        masked_password = '*' * password_length
        return render(request, self.template_name, {
            "signup_data": signup_data,
            "masked_password": masked_password
        })

    def post(self, request, *args, **kwargs):
        signup_data = self.request.session.get('signup_data')
        if not signup_data:
            return redirect("account:signup")
        admin = Account_a(
            a_no=signup_data['a_no'],
            a_first=signup_data['a_first'],
            a_last=signup_data['a_last']
        )
        admin.set_password(signup_data['password1'])
        admin.save()
        del self.request.session['signup_data']
        messages.success(request, "管理者アカウントが作成されました！")
        return redirect(self.success_url)
    
#従業員
#従業員新規登録
class E_RegisterView(FormView):
    template_name="account/e_register.html"
    form_class = E_RegisterForm                  
    success_url = reverse_lazy("letswork:employee_list")  # 後で帰る

    def form_valid(self, form): 
        account_e = form.save(commit=False)  # インスタンスを取得（まだ保存しない）
        account_e.hour = 1000  # デフォルト時給を設定（例: 1000円）
        account_e.save()  # 保存
        return redirect(self.success_url)

    def form_invalid(self, form):
        # フォームが無効な場合の処理
        messages.error(self.request, "入力内容に誤りがあります。")
        return super().form_invalid(form)
    
#従業員氏名変更
class ChangeNameView(View):
    template_name = 'account/e_changename.html'
   # success_url = 'letswork/attendance informationdetails.html'
    
    def get(self, request, e_id, *args, **kwargs):
        employee = Account_e.objects.get(e_id=e_id)
        form = ChangeNameForm(instance=employee)  # 初期値に従業員情報を設定
        return render(request, self.template_name, {'form': form, 'employee': employee})

    def post(self, request, e_id, *args, **kwargs):
        # 該当する従業員データを取得
        employee = get_object_or_404(Account_e, e_id=e_id)
        form = ChangeNameForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()  # フォームからのデータで従業員情報を更新
            return redirect(reverse('letswork:employee_detail', kwargs={'e_id': e_id}))
        return render(request, self.template_name, {'form': form, 'employee': employee})
    
#従業員削除
class E_DeleteView(View):
    template_name = "account/e_infomathiondeletion.html"
    
    def get(self, request, e_id):
        # 従業員情報を取得
        employee = get_object_or_404(Account_e, e_id=e_id)
        
        return render(request, self.template_name, {'employee': employee})
    
    def post(self, request, e_id):
        # 従業員情報を取得
        employee = get_object_or_404(Account_e, e_id=e_id)
        
        # 従業員を削除
        employee.delete()

        # 従業員一覧ページにリダイレクト
        return redirect('letswork:employee_list')  # 'employee_list'は適切なURL名に変更


# ビュー関数
admin_signup = AdminSignupView.as_view()
user_login = A_LoginView.as_view()
user_logout = LogoutView.as_view()
signup_confirm = SignupConfirmView.as_view()
e_register = E_RegisterView.as_view()
e_delete = E_DeleteView.as_view()