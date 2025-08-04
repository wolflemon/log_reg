# apps/users/forms.py  
from django import forms  
from .models import UserProfile  

class ProfileUpdateForm(forms.ModelForm):  
    class Meta:  
        model = UserProfile  
        fields = [ 'bio', 'learning_goal']  
        widgets = {  
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),  
            'learning_goal': forms.TextInput(attrs={'class': 'form-control'}),  
        }  