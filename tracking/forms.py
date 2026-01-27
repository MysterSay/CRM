from django import forms

class TrackingForm(forms.Form):
    app_number = forms.CharField(
        label='Номер заявки',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введіть номер заявки'
        })
    )
    
    ttn = forms.CharField(
        label='ТТН',
        max_length=14,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введіть номер ТТН'
        })
    )
    
    social = forms.CharField(
        label='Соц мережа',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введіть соцмережу'
        })
    )