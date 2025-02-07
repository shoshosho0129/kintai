from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account_a, Account_e

#管理者ログイン
class A_LoginForm(forms.Form):
    a_no = forms.IntegerField(
        min_value=1, 
        required=True, 
        label="No."  # ラベルを明示的に設定
    ) 
    a_pass = forms.CharField(
        widget=forms.PasswordInput, 
        required=True, 
        label="パスワード"  # ラベルを設定
    )


#管理者ログイン確認
class A_SignupForm(forms.ModelForm):
    # パスワード入力フィールドを追加
    password1 = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput,
        required=True,
        help_text="パスワードを入力してください。"
    )
    password2 = forms.CharField(
        label="パスワード(確認)",
        widget=forms.PasswordInput,
        required=True,
        help_text="確認のため、もう一度同じパスワードを入力してください。"
    )

    class Meta:
        model = Account_a
        fields = ['a_no', 'a_first', 'a_last']

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if len(password1) < 8:
            raise forms.ValidationError("パスワードは8文字以上である必要があります。")
        if not any(char.isdigit() for char in password1):
            raise forms.ValidationError("パスワードには少なくとも1つの数字が含まれている必要があります。")
        if not any(char.isalpha() for char in password1):
            raise forms.ValidationError("パスワードには少なくとも1つのアルファベットが含まれている必要があります。")
        return password1
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("パスワードが一致しません。")
        return cleaned_data

    def save(self, commit=True):
        admin = super().save(commit=False)
        admin.set_password(self.cleaned_data["password1"])  # パスワードをハッシュ化して保存
        if commit:
            admin.save()
        return admin

 #従業員登録       
class E_RegisterForm(forms.ModelForm):
        
    class Meta:
        model = Account_e
        fields = ['e_first1', 'e_last1', 'e_first2', 'e_last2',]
        widgets = {
            'e_first1': forms.TextInput(attrs={'placeholder': '例)　山田'}),
            'e_last1': forms.TextInput(attrs={'placeholder': '例)　名前'}),
            'e_first2': forms.TextInput(attrs={'placeholder': '例)　ヤマダ'}),
            'e_last2': forms.TextInput(attrs={'placeholder': '例)　タロウ'}),
        }
        
        
#氏名変更      
class ChangeNameForm(forms.ModelForm):
    
    class Meta:
        model = Account_e
        fields = ['e_first1', 'e_last1', 'e_first2', 'e_last2',]
        widgets = {
            'e_first1': forms.TextInput(attrs={'placeholder': '例)　山田'}),
            'e_last1': forms.TextInput(attrs={'placeholder': '例)　名前'}),
            'e_first2': forms.TextInput(attrs={'placeholder': '例)　ヤマダ'}),
            'e_last2': forms.TextInput(attrs={'placeholder': '例)　タロウ'}),
        }
        