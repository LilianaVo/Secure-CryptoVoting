from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

# ---------------------------------------------------------
# 1. FORMULARIO DE REGISTRO (CustomRegisterForm)
# ---------------------------------------------------------
# No usamos el formulario por defecto de Django porque queremos:
# A) Usar el Email como nombre de usuario.
# B) Forzar contraseñas más seguras manualmente.
class CustomRegisterForm(forms.ModelForm):
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'nombre@ejemplo.com'}),
        label="Correo Electrónico"
    )
    
    # --- CONFIGURACIÓN DE CONTRASEÑA ---
    password = forms.CharField(
        min_length=8,  # <--- REGLA DE SEGURIDAD: Longitud mínima obligatoria
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '********'}),
        label="Contraseña",
        error_messages={'min_length': 'La contraseña debe tener al menos 8 caracteres.'}
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '********'}),
        label="Confirmar Contraseña"
    )

    class Meta:
        model = User
        # Solo le pedimos estos dos datos al usuario (el resto se llena automático)
        fields = ['email', 'password']

    def clean_email(self):
        """
        VALIDACIÓN PERSONALIZADA:
        Verifica que el correo no exista ya en la base de datos.
        Evita duplicados antes de intentar guardar.
        """
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(username=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado. Por favor inicia sesión.")
        return email

    def clean(self):
        """
        VALIDACIÓN GENERAL:
        Verifica que las dos contraseñas ingresadas sean idénticas.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Las contraseñas no coinciden.")
        
        return cleaned_data

    def save(self, commit=True):
        """
        GUARDADO PERSONALIZADO:
        Django obliga a tener un 'username'. Aquí copiamos el email al campo username
        para que el usuario no tenga que inventarse un apodo.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email'] # Truco: Username = Email
        
        # set_password se encarga de HASHING (encriptar la contraseña para no guardarla en texto plano)
        user.set_password(self.cleaned_data["password"])
        
        if commit:
            user.save()
        return user


# ---------------------------------------------------------
# 2. FORMULARIO DE INICIO DE SESIÓN (CustomLoginForm)
# ---------------------------------------------------------
class CustomLoginForm(AuthenticationForm):
    # Aunque internamente Django usa 'username', en la etiqueta mostramos "Correo Electrónico"
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre@ejemplo.com'}),
        label="Correo Electrónico"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '********'}),
        label="Contraseña"
    )

    def clean(self):
        """
        LÓGICA DE AUTENTICACIÓN:
        Verifica si las credenciales son reales.
        """
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = None
            # Intentamos autenticar asumiendo que el username ES el email
            from django.contrib.auth import authenticate
            self.user_cache = authenticate(self.request, username=username, password=password)
            
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Correo electrónico o contraseña incorrectos."
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError("Esta cuenta está inactiva.")
        
        return self.cleaned_data
    
# ---------------------------------------------------------
# 3. FORMULARIO DE VERIFICACIÓN DE LLAVE (KeyCheckForm)
# ---------------------------------------------------------
# Este es un formulario simple para subir archivos. 
# No guarda nada en la BD, solo sirve para pasar el archivo a la vista 'check_key_status'.
class KeyCheckForm(forms.Form):
    private_key = forms.FileField(
        label="Selecciona tu archivo de Llave Privada (.key)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.key,.pem'}),
        help_text="Sube el archivo que descargaste al generar tu llave. No guardaremos este archivo."
    )