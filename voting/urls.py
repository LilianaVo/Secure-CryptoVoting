from django.urls import path
from . import views

# ---------------------------------------------------------
# CONFIGURACIÓN DEL ESPACIO DE NOMBRES (Namespace)
# ---------------------------------------------------------
# Esto es vital. Define el "apellido" de las rutas de esta app.
# Nos permite usar {% url 'voting:vote_submit' %} en los templates HTML
# sin confundirnos con rutas de otras aplicaciones.
app_name = 'voting' 

urlpatterns = [
    # ---------------------------------------------------------
    # 1. RUTAS PRINCIPALES (El flujo de votación)
    # ---------------------------------------------------------
    # Portada de la aplicación de votación
    path('', views.index_view, name='index'), 
    
    # Guía o manual de usuario (paso obligatorio tras el login)
    path('guia/', views.guide_view, name='guide'),
    
    # Paso 1 de seguridad: Generar y descargar llaves RSA
    path('generate-keys/', views.key_generation_view, name='generate_keys'),
    
    # Paso 2: Formulario de votación (donde se firma y encripta)
    path('vote/', views.vote_submission_view, name='vote_submit'), 
    
    # Paso 3: Pantalla final con el comprobante
    path('success/', views.success_page, name='success_page'), 
    
    # ---------------------------------------------------------
    # 2. RUTAS DE RESULTADOS Y AUDITORÍA (Transparencia)
    # ---------------------------------------------------------
    # Tablero Público: Gráficos de resultados (visible para todos)
    path('results/', views.results_dashboard_view, name='results_dashboard'), 
    
    # Auditoría Detallada: Tabla técnica con hashes (SOLO para Admins)
    path('auditoria/', views.audit_view, name='audit_view'), 
    
    # Verificación Personal: El usuario revisa su propio historial de voto
    path('verify/', views.verification_page, name='verification_page'),
    
    # Página de créditos del equipo y materia
    path('creditos/', views.credits_view, name='credits'),
    
    # ---------------------------------------------------------
    # 3. RUTAS DE AUTENTICACIÓN (Gestión de cuenta)
    # ---------------------------------------------------------
    # Conectan con tus funciones personalizadas en views.py
    path('login/', views.login_view, name='login'), 
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # ---------------------------------------------------------
    # 4. HERRAMIENTAS EXTRA
    # ---------------------------------------------------------
    # Herramienta para que el usuario pruebe si su archivo .key es válido
    path('verificar-llave/', views.check_key_status, name='check_key'),
]