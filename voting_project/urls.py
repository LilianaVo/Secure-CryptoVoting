"""
URL configuration for voting_project project.
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from voting import views as voting_views # Importamos las funciones (vistas) de tu app de votación

urlpatterns = [
    # ---------------------------------------------------------
    # 1. PANEL DE ADMINISTRACIÓN
    # ---------------------------------------------------------
    # Esta ruta habilita el panel de superusuario de Django (ej: sitio.com/admin)
    path('admin/', admin.site.urls),

    # ---------------------------------------------------------
    # 2. AUTENTICACIÓN (ENTRADA Y SALIDA)
    # ---------------------------------------------------------
    # Conecta la URL '/login/' con la función personalizada 'login_view' en views.py
    path('login/', voting_views.login_view, name='login'),
    
    # Para cerrar sesión, usamos la vista genérica de Django, pero le indicamos
    # específicamente qué plantilla (HTML) mostrar cuando el usuario salga.
    path('logout/', auth_views.LogoutView.as_view(template_name='logged_out.html'), name='logout'),
    
    # ---------------------------------------------------------
    # 3. REGISTRO DE NUEVOS USUARIOS
    # ---------------------------------------------------------
    # Ruta dedicada para que nuevos usuarios creen su cuenta (llama a 'register_view')
    path('register/', voting_views.register_view, name='register'), 
    
    # Esta línea mágica incluye rutas predefinidas de Django para cosas como
    # recuperar contraseña o cambiarla, para no tener que escribirlas desde cero.
    path('', include('django.contrib.auth.urls')), 

    # ---------------------------------------------------------
    # 4. CONEXIÓN CON LA APP 'VOTING'
    # ---------------------------------------------------------
    # Aquí le decimos a Django: "Si la URL empieza con 'voting/', deja de mirar aquí 
    # y vete a buscar al archivo urls.py que está DENTRO de la carpeta voting".
    # Esto mantiene el proyecto ordenado.
    path('voting/', include('voting.urls')),
    
    # ---------------------------------------------------------
    # 5. PÁGINA DE INICIO (RAÍZ)
    # ---------------------------------------------------------
    # Cuando alguien entra al dominio principal (sin nada más), 
    # lo enviamos directamente a la función 'index_view' (tu portada).
    path('', voting_views.index_view, name='home'), 
]