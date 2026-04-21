from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(
        label='Nombre',
        max_length=120,
        widget=forms.TextInput(attrs={'placeholder': 'Tu nombre'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'nombre@correo.com'}),
    )
    phone = forms.CharField(
        label='Telefono',
        max_length=40,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '+54 9 ...'}),
    )
    subject = forms.CharField(
        label='Asunto',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Motivo de tu consulta'}),
    )
    message = forms.CharField(
        label='Mensaje',
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Contanos en que podemos ayudarte'}),
    )
