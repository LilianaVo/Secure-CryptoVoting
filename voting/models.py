from django.db import models
# Importamos el modelo de usuario por defecto de Django
from django.contrib.auth.models import User 
from django.db.models.signals import post_save
from django.dispatch import receiver

# ---------------------------------------------------------
# 1. MODELO DE PERFIL DE VOTANTE (VoterProfile)
# ---------------------------------------------------------
# Aquí extiendo la información del usuario normal. 
# No me basta con nombre y contraseña; necesito guardar sus llaves criptográficas 
# y saber si ya votó para evitar fraudes.
class VoterProfile(models.Model):
    # Conecto este perfil "uno a uno" con el usuario de Django.
    # Si se borra el usuario, se borra este perfil (CASCADE).
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Aquí guardo la "Identidad Pública" del votante.
    # Servirá para validar que la firma digital del voto le pertenece a él.
    public_key = models.TextField(
        blank=True,         
        null=True,          
        help_text="Llave pública RSA del votante, usada para verificar la firma digital."
    )
    
    # ESTO ES CRÍTICO: Este campo actúa como un interruptor.
    # False = Puede votar. True = Ya votó, bloquéalo.
    has_voted = models.BooleanField(default=False) 

    def __str__(self):
        return f"Perfil de {self.user.username}"

# ---------------------------------------------------------
# SEÑAL (AUTOMATIZACIÓN)
# ---------------------------------------------------------
# Esta función es un "vigilante". Escucha cuando se crea un nuevo usuario (User)
# y automáticamente le crea su ficha de votante (VoterProfile) vacía.
# Así no tengo que crearlo manualmente cada vez que alguien se registra.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        VoterProfile.objects.create(user=instance)

# ---------------------------------------------------------
# 2. MODELO DE VOTO (Vote)
# ---------------------------------------------------------
# Esta tabla actúa como la "Urna Digital". 
# Cada fila aquí es una papeleta depositada.
class Vote(models.Model):
    # Vinculo el voto con el perfil del votante para saber quién fue.
    voter = models.ForeignKey(
        'VoterProfile', 
        on_delete=models.CASCADE, 
        help_text="Perfil del votante que emitió este voto."
    )
    
    # Aquí guardo por quién votó (el texto plano, ej: "Partido A").
    option = models.CharField(
        max_length=100,
        help_text="La opción seleccionada por el votante."
    )
    
    # SEGURIDAD (Integridad y No Repudio):
    # Guardo el hash firmado. Si alguien intenta alterar el voto en la base de datos,
    # esta firma ya no coincidirá y sabremos que hubo trampa.
    digital_signature = models.TextField(
        help_text="Firma digital (Hash RSA) del voto, prueba de no repudio."
    )
    
    # SEGURIDAD (Confidencialidad):
    # Además del texto plano, guardo el voto encriptado con AES.
    # Esto demuestra que sé ocultar la información sensible.
    encrypted_vote = models.TextField(
        blank=True,
        null=True,
        help_text="Voto cifrado con AES-256 para demostrar confidencialidad."
    )
    
    # Guardo la fecha y hora exacta del voto para auditoría.
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Voto de {self.voter.user.username} por {self.option}"
