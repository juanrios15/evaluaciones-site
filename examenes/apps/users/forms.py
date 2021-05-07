from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate
from django import forms
from django.contrib.auth import get_user_model, password_validation
User = get_user_model()


class AuthenticationEmailForm(AuthenticationForm):
    
    def clean(self):
        
        try:
            user = User.objects.get(email=self.cleaned_data.get('username'))
            username= user.username
        except:            
            username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

class UserRegistroForm(UserCreationForm):
    

    def __init__(self, *args, **kwargs):
        super(UserRegistroForm, self).__init__(*args, **kwargs)


        self.fields['password1'].widget.attrs['class'] = 'form-control mt-1'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
    
    
    class Meta:
        model = User
        fields = ('username','email','full_name','foto','genero','fecha_nacimiento','pais','codigo_pais')
        
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class':'form-control',
                    'placeholder':'Nombre de usuario'
                }
            ),
            'email': forms.EmailInput(
                attrs= {
                    'placeholder': 'Correo electronico',
                    'class': 'form-control'
                }
            ),
            'full_name': forms.TextInput(
                attrs= {
                    'placeholder': 'Nombres',
                    'class': 'form-control'
                }
            ),
            'foto': forms.FileInput(
                attrs= {
                    'class': 'form-control',
                    'style': "font-size: 0.8rem;",
                    'id': "inputimg"
                }
            ),
            'genero':forms.Select(
                attrs= {
                    'class': 'form-select',
                }
            ),
            'pais':forms.Select(
                attrs= {
                    'class': 'form-select',
                }
            ),
            'fecha_nacimiento':forms.SelectDateWidget(
                years=range(2020, 1930,-1),
                 attrs= {
                    'class': 'form-select me-1 px-2',
                    'style': 'display: inline-block;',
                }
                
            ),
        }
        

class UpdateUserForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ('username','foto','full_name','genero','fecha_nacimiento','pais','codigo_pais')
        
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class':'form-control',
                    'placeholder':'Nombre de usuario'
                }
            ),

            'full_name': forms.TextInput(
                attrs= {
                    'placeholder': 'Nombres',
                    'class': 'form-control'
                }
            ),
            'foto': forms.FileInput(
                attrs= {
                    'class': 'form-control',
                    'style': "font-size: 0.8rem;",
                    'id': "inputimg"
                }
            ),
            'genero':forms.Select(
                attrs= {
                    'class': 'form-select',
                }
            ),
            'pais':forms.TextInput(
                attrs= {
                    'class': 'form-control',
                }
            ),
            'fecha_nacimiento':forms.SelectDateWidget(
                years=range(2020, 1930,-1),
                 attrs= {
                    'class': 'form-select me-1 px-2',
                    'style': 'display: inline-block;',
                }
                
            ),
        }


class CreatePasswordForm(forms.Form):
    
    email= forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'Correo Eléctronico'
            }
        )
    )
    
    password1 = forms.CharField(
        label='Contraseña',
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Contraseña Actual'
            }
        )
    )
    password2 = forms.CharField(
        label='Contraseña',
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Contraseña Nueva'
            }
        )
    )
    
    def __init__(self, *args, **kwargs):
        self.email = kwargs.pop('email', None)
        super(CreatePasswordForm, self).__init__(*args, **kwargs)
    
    
    def clean(self):
        cleaned_data = super(CreatePasswordForm, self).clean()
        email = self.cleaned_data['email']

        if email == self.email:
            return self.cleaned_data
        else:
            raise forms.ValidationError('Email incorrecto')
    
    def clean_password2(self):
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            self.add_error('password2', 'Las contraseñas no son iguales')
    
    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error('password2', error)
        
        