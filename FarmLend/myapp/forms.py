from django import forms
from .models import CustomUser
from .models import Schedule, Car 
from .models import CarReview
from .models import Review



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


class ScheduleForm(forms.ModelForm):
    date = forms.DateField(input_formats=['%Y-%m-%d'])
    
    class Meta:
        model = Schedule
        fields = ['car', 'date', 'time']


class CarReviewForm(forms.ModelForm):
    class Meta:
        model = CarReview
        fields = ['rating', 'review_text']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = CarReview
        fields = ['review_text', 'rating']