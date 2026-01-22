from django import forms
from django.contrib.auth.models import User
from .models import ClassGroup, StudentProfile
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class SignupForm(forms.Form):
    username = forms.CharField(max_length=150, label="Usuario")
    first_name = forms.CharField(max_length=150, label="Nombre(s)")
    last_name = forms.CharField(max_length=150, label="Apellidos")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")
    group_code = forms.CharField(max_length=20, label="Código de grupo")

    def clean(self):
        
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

    # Valida contraseña con política de Django
        try:
            validate_password(p1)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)

        if User.objects.filter(username=cleaned.get("username")).exists():
            raise forms.ValidationError("Ese usuario ya existe.")
        if not ClassGroup.objects.filter(code=cleaned.get("group_code")).exists():
            raise forms.ValidationError("Código de grupo inválido.")
        return cleaned

    def save(self):
        data = self.cleaned_data
        group = ClassGroup.objects.get(code=data["group_code"])
        user = User.objects.create_user(
            username=data["username"],
            password=data["password1"],
            first_name=data["first_name"],
            last_name=data["last_name"],
        )
        StudentProfile.objects.create(user=user, group=group)
        return user
