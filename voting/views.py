from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
# Importamos las funciones de autenticación real
from django.contrib.auth import login, logout, authenticate
import json
from collections import Counter
import re 
from django.conf import settings 

# --- IMPORTACIONES LOCALES ---
# Traigo mis herramientas de seguridad y mis modelos de base de datos
from .crypto_utils import generate_rsa_keys, sign_vote, encrypt_vote_aes, verify_signature
from .models import VoterProfile, Vote 
# IMPORTANTE: Importamos los nuevos formularios que creamos en forms.py
from .forms import CustomRegisterForm, CustomLoginForm, KeyCheckForm

from Crypto.PublicKey import RSA

# ---------------------------------------------------------
# FUNCIONES AUXILIARES (Procesamiento de Texto)
# ---------------------------------------------------------

def parse_vote_content(vote_option):
    """
    Convierte el texto crudo del voto (ej: 'P1:ALTO|P2:FACIL') 
    en un diccionario de Python fácil de leer.
    """
    results = {}
    # Patrón: (P#):(VALOR)
    matches = re.findall(r'(P\d+):([A-Z0-9\-]+)', vote_option)
    for key, value in matches:
        results[key] = value
    return results

def get_legible_label(key, value):
    """
    Traduce los códigos internos (ej: 'RAPIDO') a texto legible para humanos (ej: 'Muy rápido').
    Esto se usa para mostrar gráficos y tablas bonitas.
    """
    if key == 'P1': 
        return {'ALTO': 'Alto', 'MEDIO': 'Medio', 'BAJO': 'Bajo'}.get(value, value)
    if key == 'P2': 
        return {'FACIL': 'Fáciles', 'ADECUADO': 'Adecuados', 'DIFICIL': 'Difíciles'}.get(value, value)
    if key == 'P3': 
        return {'MUCHO': 'Sí, mucho', 'TAL-VEZ': 'Tal vez', 'NO-DUDA': 'No, lo dudo'}.get(value, value)
    if key == 'P4': 
        return {'RAPIDO': 'Muy rápido', 'ADECUADO': 'Adecuados', 'LENTO': 'Muy lento'}.get(value, value)
    return value
# --- Fin de Funciones Auxiliares ---


# ---------------------------------------------------------
# VISTAS DE NAVEGACIÓN BÁSICA
# ---------------------------------------------------------

def index_view(request):
    """Renderiza la portada o redirige a la guía."""
    if request.user.is_authenticated:
        # CAMBIO: Si entra al inicio y ya es usuario, va a la guía para no perder tiempo.
        return redirect('voting:guide') 
        
    context = {
        'github_url': getattr(settings, 'GITHUB_REPO_URL', '#'), 
    }
        
    return render(request, 'voting/index.html', context)


def credits_view(request):
    """Muestra la página de créditos con los datos de la materia y alumnos."""
    context = {
        'github_url': getattr(settings, 'GITHUB_REPO_URL', '#'), 
        'materia': 'Criptografía',
        'profesor': 'Dr. Alfonso Francisco De Abiega L Eglisse',
        'grupo_semestre': '02 / 2026-1',
        'institucion': 'Facultad de Ingeniería UNAM',
        'integrantes': ['Roja Mares Luis Iván', 'Lee Obando Ileana Verónica'],
        'descripcion': 'Proyecto final de la materia.',
    }
    return render(request, 'voting/credits.html', context)


# ---------------------------------------------------------
# VISTAS DE AUTENTICACIÓN (Login / Registro)
# ---------------------------------------------------------

def login_view(request):
    """
    Maneja el inicio de sesión.
    Si el usuario se loguea bien, lo forzamos a ir a la GUÍA.
    """
    # 1. Si ya está dentro, mándalo a la guía (evita bucles).
    if request.user.is_authenticated:
        return redirect('voting:guide') 

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user() 
            login(request, user)
            messages.success(request, f"Bienvenido de nuevo.")
            
            # --- CAMBIO CRÍTICO ---
            # Ignoramos a dónde quería ir el usuario y lo mandamos a la guía
            # para asegurarnos que lea las instrucciones.
            return redirect('voting:guide') 
            
        else:
            messages.error(request, "Correo electrónico o contraseña incorrectos.")
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """Cierra la sesión y limpia las cookies del usuario."""
    logout(request)
    messages.info(request, "Has cerrado sesión exitosamente.")
    return redirect('login')


def register_view(request):
    """
    Registra un nuevo usuario.
    Aquí es donde validamos que el correo sea real y no sea temporal.
    """
    if request.user.is_authenticated:
        return redirect('voting:vote_submit')

    if request.method == 'POST':
        # Usamos CustomRegisterForm (definido en forms.py) que tiene las reglas de validación.
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '¡Registro exitoso! Tu cuenta ha sido creada con tu correo electrónico.')
            return redirect('login') 
        else:
            messages.error(request, 'Hubo un error en el registro. Revisa las alertas en el formulario.')
    else:
        form = CustomRegisterForm()
        
    return render(request, 'register.html', {'form': form})


# ---------------------------------------------------------
# GESTIÓN DE LLAVES (PKI)
# ---------------------------------------------------------

@login_required
def key_generation_view(request):
    """
    Genera el par de llaves RSA (Pública y Privada).
    """
    profile = get_object_or_404(VoterProfile, user=request.user)

    # 🛑 RESTRICCIÓN DE INTEGRIDAD 🛑
    # Si el usuario ya votó, NO le dejo generar llaves nuevas.
    # Esto evita que alguien repudie su voto anterior diciendo "esa no era mi llave".
    if profile.has_voted:
        messages.error(request, 
                       "Tu voto ya ha sido emitido: No es posible generar una nueva llave pública una vez que se ha registrado un voto.")
        return redirect('voting:verification_page') 

    # Si el usuario es nuevo o no ha votado:
    if request.method == 'POST':
        # Llamamos a la función matemática para crear las llaves
        public_key_pem, private_key_pem = generate_rsa_keys()
        
        # Guardamos la PÚBLICA en la base de datos (la identidad visible)
        profile.public_key = public_key_pem
        profile.save()
        
        # Preparamos la PRIVADA para descargarla como archivo (el secreto del usuario)
        safe_filename = "".join([c for c in request.user.username if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        filename = f"{safe_filename}_private.key"
        
        response = HttpResponse(private_key_pem, content_type='application/x-pem-file')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        messages.success(request, "Llave privada generada y descargada con éxito. Guárdala de forma segura. Ya puedes votar.")
        return response 
    
    return render(request, 'voting/key_generation.html', {'profile': profile})


# ---------------------------------------------------------
# PROCESO DE VOTACIÓN (NÚCLEO DEL SISTEMA)
# ---------------------------------------------------------

@login_required
def vote_submission_view(request):
    """
    Recibe el voto, verifica la llave, FIRMA y ENCRIPTA.
    """
    profile = get_object_or_404(VoterProfile, user=request.user)
    
    # 1. Validaciones previas
    if profile.has_voted:
        messages.warning(request, "Ya has votado. No puedes votar de nuevo.")
        return redirect('voting:success_page') 

    if not profile.public_key:
        messages.error(request, "No tienes una llave pública registrada. Por favor, genera tu llave primero.")
        return redirect('voting:generate_keys')


    if request.method == 'POST':
        # 2. Capturamos lo que el usuario eligió
        pregunta_1 = request.POST.get('pregunta_1')
        pregunta_2 = request.POST.get('pregunta_2')
        pregunta_3 = request.POST.get('pregunta_3')
        pregunta_4 = request.POST.get('pregunta_4')
        # Capturamos el archivo de la llave privada que subió
        private_key_file = request.FILES.get('private_key') 

        if not all([pregunta_1, pregunta_2, pregunta_3, pregunta_4]) or not private_key_file:
            messages.error(request, "Debes responder todas las preguntas y subir tu llave privada.")
            return render(request, 'voting/vote_form.html', {'profile': profile})

        try:
            # Leemos el contenido de la llave privada subida
            private_key_pem = private_key_file.read().decode('utf-8')

            # 3. Creamos el "paquete" de voto concatenando las respuestas
            vote_content = (
                f"USUARIO:{request.user.username}|P1:{pregunta_1}|P2:{pregunta_2}|P3:{pregunta_3}|P4:{pregunta_4}"
            )

            # 4. FIRMA DIGITAL (Autenticación)
            # Usamos la llave privada subida para firmar el contenido.
            signature_hex = sign_vote(vote_content, private_key_pem)
            
            # 5. VERIFICACIÓN INMEDIATA
            # Comprobamos que la llave privada que subió coincide con la pública que tenemos guardada.
            if not verify_signature(vote_content, signature_hex, profile.public_key):
                 messages.error(request, "La llave privada subida no corresponde a su llave pública registrada.")
                 return redirect(reverse('voting:vote_submit')) 

            # 6. ENCRIPTACIÓN (Confidencialidad)
            # Encriptamos el voto con AES para que nadie pueda leerlo en la BD.
            encrypted_vote_hex = encrypt_vote_aes(vote_content)

            # 7. GUARDADO EN BASE DE DATOS
            # Usamos transaction.atomic para asegurar que se guarde todo o nada.
            with transaction.atomic():
                Vote.objects.create(
                    voter=profile,
                    option=vote_content, # Guardamos el texto plano (opcional según requisitos)
                    digital_signature=signature_hex, # Guardamos la firma
                    encrypted_vote=encrypted_vote_hex # Guardamos el cifrado
                )
                # Marcamos al usuario como "ya votó"
                profile.has_voted = True
                profile.save()
            
            messages.success(request, "¡Voto firmado y procesado con éxito!")
            # Guardamos la firma en sesión para mostrarla en la pantalla de éxito
            request.session['last_signature'] = signature_hex
            return redirect('voting:success_page')

        except Exception as e:
            messages.error(request, f"Error Criptográfico o de Archivo: {e}")
            return render(request, 'voting/vote_form.html', {'profile': profile})

    return render(request, 'voting/vote_form.html', {'profile': profile})


@login_required
def success_page(request):
    """Muestra el comprobante digital después de votar."""
    signature = request.session.pop('last_signature', "Comprobante no disponible.")
    return render(request, 'voting/success.html', {'signature': signature})


# ---------------------------------------------------------
# VISTAS DE RESULTADOS Y AUDITORÍA
# ---------------------------------------------------------

def get_counts_for_question(question_key, votes):
    """Cuenta cuántos votos tiene cada opción para generar gráficos."""
    results = []
    for vote in votes:
        parsed_data = parse_vote_content(vote.option)
        if question_key in parsed_data:
            results.append(parsed_data[question_key])
    
    counts = Counter(results)
    options = [get_legible_label(question_key, key) for key in counts.keys()]
    
    return {
        'options': json.dumps(options), 
        'counts': json.dumps(list(counts.values()))
    }

@login_required 
def results_dashboard_view(request):
    """
    Tablero Público: Muestra estadísticas generales.
    Cualquier usuario logueado puede ver esto.
    """
    is_admin = request.user.is_staff
    all_votes = Vote.objects.all().select_related('voter').order_by('id') 
    
    # Preparamos datos para los 4 gráficos
    data_p1 = get_counts_for_question('P1', all_votes)
    data_p2 = get_counts_for_question('P2', all_votes)
    data_p3 = get_counts_for_question('P3', all_votes)
    data_p4 = get_counts_for_question('P4', all_votes)

    total_votes = len(all_votes)

    context = {
        'total_votes': total_votes,
        'options_json_p1': data_p1['options'], 'counts_json_p1': data_p1['counts'],
        'options_json_p2': data_p2['options'], 'counts_json_p2': data_p2['counts'],
        'options_json_p3': data_p3['options'], 'counts_json_p3': data_p3['counts'],
        'options_json_p4': data_p4['options'], 'counts_json_p4': data_p4['counts'],
        
        'is_admin': is_admin, 
        'is_verification_page': False, 
        'is_audit_page': False, 
    }
    
    return render(request, 'voting/results_dashboard.html', context)


@login_required
def audit_view(request):
    """
    Auditoría Detallada: Muestra tabla cruda con firmas y encriptación.
    SOLO accesible para administradores (Staff).
    """
    if not request.user.is_staff:
        messages.error(request, "Acceso Denegado: Solo el personal de administración puede acceder a la auditoría.")
        return redirect('voting:results_dashboard')
        
    all_votes = Vote.objects.all().select_related('voter').order_by('id') 
    
    processed_votes = []
    for vote in all_votes:
        parsed_data = parse_vote_content(vote.option)
        
        processed_votes.append({
            'id': vote.id,
            'voter_username': vote.voter.user.username,
            'encrypted_vote': vote.encrypted_vote,   # Mostramos el hash AES
            'digital_signature': vote.digital_signature, # Mostramos la firma RSA
            'timestamp': vote.timestamp,
            'P1': get_legible_label('P1', parsed_data.get('P1', 'N/A')),
            'P2': get_legible_label('P2', parsed_data.get('P2', 'N/A')),
            'P3': get_legible_label('P3', parsed_data.get('P3', 'N/A')),
            'P4': get_legible_label('P4', parsed_data.get('P4', 'N/A')),
        })
    
    context = {
        'votes': processed_votes, 
        'is_admin': True, 
        'is_verification_page': False, 
        'is_audit_page': True, 
    }
    
    return render(request, 'voting/results_dashboard.html', context)


@login_required
def verification_page(request):
    """
    Verificación Personal: Muestra al usuario SU propio historial y firmas.
    """
    user_votes = Vote.objects.filter(voter__user=request.user).select_related('voter').order_by('-timestamp')
    
    context = {
        'votes': user_votes,
        'is_admin': False, 
        'is_verification_page': True, 
        'is_audit_page': False,
    }
    
    return render(request, 'voting/results_dashboard.html', context)

def guide_view(request):
    """Muestra la guía de usuario."""
    return render(request, 'voting/guide.html')

# ---------------------------------------------------------
# VALIDACIÓN DE ARCHIVOS DE LLAVE (Herramienta Extra)
# ---------------------------------------------------------

@login_required
def check_key_status(request):
    """
    Permite al usuario subir un archivo .key para ver si funciona.
    No guarda nada, solo verifica.
    """
    profile = get_object_or_404(VoterProfile, user=request.user)
    key_status = None # Estados posibles: 'valid_ready', 'valid_used', 'invalid_format', etc.
    
    if request.method == 'POST':
        form = KeyCheckForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['private_key']
            try:
                # 1. Intentamos leer la llave (Detectar si es Falsa/Corrupta)
                key_content = uploaded_file.read().decode('utf-8')
                private_key_obj = RSA.import_key(key_content)
                
                # 2. Verificamos si el usuario tiene una llave registrada en el sistema
                if not profile.public_key:
                    key_status = 'no_key_registered'
                else:
                    # 3. Generamos la pública desde la privada subida y comparamos con la guardada
                    uploaded_public_pem = private_key_obj.publickey().export_key('PEM').decode('utf-8').strip()
                    stored_public_pem = profile.public_key.strip()
                    
                    if uploaded_public_pem != stored_public_pem:
                        key_status = 'mismatch' # La llave sirve, pero no es la tuya
                    else:
                        # 4. Verificar si ya se usó
                        if profile.has_voted:
                            key_status = 'valid_used'
                        else:
                            key_status = 'valid_ready'

            except (ValueError, IndexError, TypeError) as e:
                # Si RSA.import_key falla, el archivo es basura
                key_status = 'invalid_format'
    else:
        form = KeyCheckForm()

    return render(request, 'voting/check_key.html', {
        'form': form, 
        'key_status': key_status,
        'profile': profile
    })