from django import forms
from .models import CustomUser, Schedule, Car, CarReview

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'name', 'description', 'horsepower', 'image', 'is_available',
            'contact_owner', 'morning_price', 'morning_custom_price', 'afternoon_price', 'afternoon_custom_price', 'price_per_rai', 'time_per_rai'
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'horsepower': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'contact_owner': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'morning_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'morning_custom_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'afternoon_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'afternoon_custom_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_per_rai': forms.NumberInput(attrs={'class': 'form-control'}),
            'time_per_rai': forms.NumberInput(attrs={'class': 'form-control'}),
        }


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

class BookingForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['date', 'start_time', 'end_time', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'time': forms.Select(choices=Schedule.TIME_CHOICES, attrs={'class': 'form-control'}),
        }
