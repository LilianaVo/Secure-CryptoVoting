
-----

# 🗳️ Sistema de Votación Electrónica Seguro (Criptografía)

Este proyecto es una **plataforma web** robusta desarrollada en **Django** que implementa un **sistema de votación electrónica seguro**. Su núcleo se basa en la implementación de **estándares criptográficos avanzados** (RSA y AES) para garantizar la **confidencialidad, integridad y no repudio** de cada voto emitido.

-----

## 🔗 Enlaces Importantes

  * **Página Pública (Demo):** [https://sistema-de-votacion-de-criptografia.onrender.com](https://sistema-de-votacion-de-criptografia.onrender.com)
    > ⚠️ **Nota de Despliegue:** El servidor puede tardar entre **30 y 50 segundos** en despertar y cargar la aplicación la primera vez debido a las políticas de ahorro de energía del servicio gratuito.

-----

## ✨ Características Principales

El sistema se basa en un esquema criptográfico híbrido que asegura el proceso de votación:

### 1\. 🔑 Infraestructura de Llave Pública (PKI)

  * Cada votante genera un par de llaves **RSA de 2048 bits**.
  * La **llave pública** se almacena en el servidor para su validación.
  * La **llave privada** se descarga al dispositivo del usuario (archivo `.key`) y es **esencial para votar**.

### 2\. 🛡️ Seguridad del Voto

  * **Firma Digital:** Se genera un hash **SHA-256** del voto y se firma con la **llave privada** del usuario, asegurando el **no repudio** y la **integridad**.
  * **Cifrado Híbrido:** El voto se cifra con **AES-256 CBC** antes de ser transmitido, garantizando su **confidencialidad**.

### 3\. 📈 Transparencia y Auditoría

  * **Resultados en Tiempo Real:** Panel de resultados con visualizaciones gráficas.
  * **Módulo de Auditoría:** Interfaz para administradores para visualizar y validar firmas y *hashes*.
  * **Validación de Llaves:** Módulo para que el votante verifique el estado de su par de llaves.

-----

## 🛠️ Stack Tecnológico

| Componente | Tecnología / Librería | Versión | Descripción |
| :--- | :--- | :--- | :--- |
| **Backend** | Django | 5.2.8 | Framework web principal. |
| **Criptografía** | PyCryptodome | 3.23.0 | Implementación de **RSA, AES y SHA256**. |
| **Configuración** | Python-Decouple | 3.8 | Gestión de variables de entorno. |
| **Base de Datos** | DJ-Database-URL | 3.0.1 | Conexión agnóstica (SQLite / PostgreSQL). |
| **Estáticos** | WhiteNoise | 6.11.0 | Manejo de archivos estáticos en producción. |
| **Servidor WSGI** | Gunicorn | 23.0.0 | Servidor WSGI para despliegue. |

-----

## 🚀 Guía de Instalación y Ejecución Local

Esta guía detalla los **pasos mínimos y exactos** para poner el proyecto en marcha desde **Visual Studio Code (VS Code)**.

### ⚙️ Requisitos Previos

Asegúrate de tener instalados los siguientes componentes:

1.  **Python 3.10 o superior**
      * Descarga: [https://www.python.org/downloads/](https://www.python.org/downloads/)
      * > **¡Importante\!** Marca la opción **"Add Python to PATH"** durante la instalación.
2.  **VS Code** (Editor recomendado)
      * Descarga: [https://code.visualstudio.com/](https://code.visualstudio.com/)
3.  **Extensión de Python para VS Code** (Búscala como `Python (Microsoft)` en el *marketplace*).
4.  **Git** (Opcional, pero recomendado para clonar el repositorio).
      * Descarga: [https://git-scm.com/downloads](https://git-scm.com/downloads)

### 💻 Pasos de Ejecución

1.  **Clonar el Repositorio** (Si usas Git):

    ```bash
    git clone [URL-DE-TU-REPOSITORIO]
    cd sistema-de-votacion-electronica
    ```

2.  **Crear y Activar un Entorno Virtual**

    > Django se instala **dentro** de un entorno virtual para aislar las dependencias del proyecto.

    ```bash
    # Crear el entorno
    python -m venv venv

    # Activar el entorno
    # En Windows:
    .\venv\Scripts\activate
    # En Mac/Linux:
    source venv/bin/activate
    ```

3.  **Instalar Dependencias**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Aplicar Migraciones**

    ```bash
    python manage.py migrate
    ```

5.  **Crear Usuario Administrador**

    ```bash
    python manage.py createsuperuser
    ```

6.  **Ejecutar el Servidor Local**

    ```bash
    python manage.py runserver
    ```

      * Abrir en el navegador: 👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

-----

## ☁️ Despliegue en Producción (Render)

### **Build Command**

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

### **Start Command**

```bash
gunicorn voting_project.wsgi:application
```

-----

## 🔄 Mantenimiento: Reinicio Rápido del Sistema

> ⚠️ **Advertencia:** Estos comandos **eliminan todos los usuarios** (excepto el superusuario) **y votos**. ¡Realiza un respaldo si deseas conservar datos reales\!

1.  **Abrir la Consola de Django:**

    ```bash
    python manage.py shell
    ```

2.  **Ejecutar Comandos de Limpieza:**

    ```python
    # A) Importar modelos
    from django.contrib.auth.models import User
    from voting.models import Vote, VoterProfile

    # B) Eliminar todos los usuarios que NO sean superusuario
    User.objects.filter(is_superuser=False).delete()

    # C) Borrar todos los votos y reiniciar el estado de voto de los perfiles
    Vote.objects.all().delete()
    VoterProfile.objects.update(has_voted=False)

    # D) Salir de la consola
    exit()
    ```

-----

## 👥 Desarrollado por

  * **Lee Obando Ileana Verónica**
  * **Rojas Mares Luis Iván**

### 📚 Datos Académicos

  * **Materia:** Criptografía
  * **Profesor:** Dr. Alfonso Francisco De Abiega L Eglisse
  * **Grupo:** 02
  * **Facultad de Ingeniería - UNAM**

-----

