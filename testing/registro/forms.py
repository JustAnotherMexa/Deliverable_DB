from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegistration(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]

    def __init__(self, *args, **kwargs):
        super(UserRegistration, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = '<br/><small>Requerido. Únicamente letras, dígitos y @/./+/-/_</small>'
        self.fields['password1'].help_text = '<br/><small><li>Su contraseña no puede asemejarse tanto a su otra información personal.</li><li>Su contraseña debe contener al menos 8 caracteres.</li><li>Su contraseña no puede ser una clave utilizada comunmente.</li><li>Su contraseña no puede ser completamente numérica.</li></small>'
        self.fields['password2'].help_text = '<br/><small>Para verificar, introduzca la misma contraseña anterior.</small>'


    def save(self, commit=True):
        user = super(UserRegistration, self).save(commit=False)
        user.fisrt_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user
