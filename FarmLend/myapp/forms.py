from django import forms
from .models import Car
from .models import CustomUser

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = '__all__'


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'nickname', 'age', 'phone_number', 'email', 'address', 'profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

