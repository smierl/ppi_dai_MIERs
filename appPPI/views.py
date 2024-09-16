from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from django.http import HttpResponse
from django.contrib import messages
from loginapp.models import User, Gym, Ejercicio
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
import folium
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from sqlalchemy import create_engine
from django.shortcuts import render
import requests
from .forms import MuscleForm, EjercicioForm

def index(request):
    """
    Vista para la página de inicio.

    Esta función maneja las solicitudes a la página de inicio de la aplicación.
    Renderiza y devuelve el archivo de plantilla 'index.html'.

    Parámetros:
    - request: Un objeto HttpRequest que contiene los datos de la solicitud.

    Retorna:
    - HttpResponse: Un objeto HttpResponse que contiene el contenido renderizado de 'index.html'.
    """
    return render(request, "index.html")

def imc(request):
    """
    Vista para calcular el Índice de Masa Corporal (IMC) y las calorías recomendadas.

    Esta función maneja las solicitudes POST para calcular el IMC y las calorías recomendadas
    basándose en el peso, la altura, la edad y el nivel de actividad proporcionados por el usuario.

    Parámetros:
    - request: Un objeto HttpRequest que contiene los datos de la solicitud. En este caso, se espera
      que contenga los valores 'weight', 'height', 'age' y 'activity-level' en el cuerpo de la solicitud POST.

    Retorna:
    - HttpResponse: Un objeto HttpResponse que contiene el contenido renderizado de 'imc.html' con el
      cálculo del IMC y las calorías recomendadas.

    Lógica:
    1. Inicializa variables para almacenar el valor a mostrar, el IMC y las calorías recomendadas.
    2. Si la solicitud es de tipo POST, realiza los siguientes cálculos:
        a. Obtiene los valores de peso, altura, edad y nivel de actividad del formulario.
        b. Calcula el IMC usando la fórmula IMC = peso / (altura^2).
        c. Calcula las calorías base usando la fórmula de Harris-Benedict.
        d. Ajusta el cálculo de calorías según el nivel de actividad.
        e. Redondea los resultados a dos decimales.
    3. Prepara el contexto con los resultados y el valor de display.
    4. Renderiza y devuelve la plantilla 'imc.html' con el contexto.
    """
    display_value = 0
    imc_re = None
    calorias_re = None
    
    if request.method == 'POST':
        display_value = 1
        
        peso = float(request.POST['weight'])
        altura = float(request.POST['height']) / 100
        edad = int(request.POST['age'])
        nivel_actividad = request.POST['activity-level']
        
        # Cálculo del IMC usando NumPy
        imc = np.divide(peso, np.square(altura))
        
        # Cálculo de calorías recomendadas usando NumPy
        calorias_base = 10 * peso + 6.25 * altura * 100 - 5 * edad + 5
        
        actividad_multiplicadores = {
            'sedentario': 1.2,
            'ligero': 1.375,
            'moderado': 1.55,
            'intenso': 1.725
        }
        
        multiplicador = actividad_multiplicadores.get(nivel_actividad, 1.2)
        calorias = np.multiply(multiplicador, calorias_base)
        
        imc_re = round(imc, 2)
        calorias_re = round(calorias, 2)
        
    contexto = {
        'display_value': display_value,
        "imc_re": imc_re,
        "calorias_re": calorias_re
    }

    return render(request, "imc.html", contexto)


def mapa(request):
    """
    Vista para mostrar un mapa con la ubicación de gimnasios y calcular el gimnasio más cercano a un punto dado.

    Esta función maneja la visualización de un mapa interactivo con marcas para cada gimnasio y 
    calcula cuál gimnasio está más cercano a una ubicación proporcionada por el usuario.

    Parámetros:
    - request: Un objeto HttpRequest que contiene los datos de la solicitud. En este caso, se espera
      que contenga 'coordenadas' en el cuerpo de la solicitud POST si se desea calcular el gimnasio más cercano.

    Retorna:
    - HttpResponse: Un objeto HttpResponse que contiene el contenido renderizado de 'mapa.html' con
      el mapa interactivo y el nombre del gimnasio más cercano (si se ha proporcionado una ubicación).

    Lógica:
    1. Obtiene todas las instancias de gimnasios desde la base de datos.
    2. Crea un mapa interactivo usando Folium, centrado en una ubicación predeterminada.
    3. Añade marcadores para cada gimnasio en el mapa.
    4. Convierte el mapa a formato HTML para su inclusión en la plantilla.
    5. Configura la conexión con la base de datos PostgreSQL para leer los datos de gimnasios.
    6. Lee los datos de los gimnasios en un DataFrame de Pandas y los convierte a un GeoDataFrame de GeoPandas.
    7. Si se recibe una solicitud POST con coordenadas:
        a. Convierte las coordenadas recibidas en un punto de referencia.
        b. Recalcula las coordenadas del GeoDataFrame y del punto de referencia a un sistema de referencia compatible.
        c. Calcula la distancia entre el punto de referencia y todos los gimnasios.
        d. Identifica el gimnasio más cercano y guarda su nombre.
    8. Renderiza la plantilla 'mapa.html' con el mapa interactivo y el nombre del gimnasio más cercano (si corresponde).
    """
    gyms = Gym.objects.all()
    m = folium.Map(location=[6.25184, -75.56359], zoom_start=12)

    for gym in gyms:
        folium.Marker(
            location=[gym.latitude, gym.longitude],
            popup=gym.name
        ).add_to(m)

    map_html = m._repr_html_()

    engine = create_engine('postgresql://postgres:NPCucr62@localhost:5432/loginapp')

    query = "SELECT name, latitude, longitude FROM loginapp_gym"
    df = pd.read_sql(query, engine)
    df['geometry'] = df.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)

    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

    reference_point = Point(0, 0)
    nombre_cercano = "Seleccione su ubicación"

    if request.method == 'POST':
        coordenadas = request.POST['coordenadas']
        partes = coordenadas.split(',')
        lat = float(partes[0])
        lng = float(partes[1])

        reference_point = Point(lng, lat)
        reference_gdf = gpd.GeoDataFrame({'geometry': [reference_point]}, crs="EPSG:4326")

        gdf = gdf.to_crs("EPSG:3857")
        reference_gdf = reference_gdf.to_crs("EPSG:3857")

        gdf['distance'] = gdf.distance(reference_gdf.iloc[0].geometry)
        closest_point = gdf.loc[gdf['distance'].idxmin()]

        nombre_cercano = closest_point["name"]

    return render(request, 'mapa.html', {'map_html': map_html, 'punto_cercano': nombre_cercano})


def logIn(request):
    """
    Vista para manejar el inicio de sesión y registro de usuarios.

    Esta función maneja solicitudes POST para registrar un nuevo usuario o autenticar a un usuario existente.
    Dependiendo del tipo de formulario enviado ('registro' o 'acceso'), realiza las acciones correspondientes.

    Parámetros:
    - request: Un objeto HttpRequest que contiene los datos de la solicitud. Se espera que contenga
      datos de formulario para registro o acceso, dependiendo de la acción deseada.

    Retorna:
    - HttpResponse: Un objeto HttpResponse que renderiza una plantilla. Dependiendo de la acción,
      puede ser la plantilla de registro/login o una plantilla de éxito (entrada.html).

    Lógica:
    1. Si la solicitud es de tipo POST:
        a. Obtiene el tipo de formulario enviado ('tipoFormulario') desde el formulario.
        b. Si el tipo de formulario es 'registro':
            i. Obtiene los valores de nombre de usuario, email y contraseña.
            ii. Verifica si el nombre de usuario ya existe en la base de datos. Si es así, muestra un mensaje de error.
            iii. Verifica si el email ya está registrado. Si es así, muestra un mensaje de error.
            iv. Crea un nuevo usuario con los datos proporcionados.
            v. Muestra un mensaje de éxito y redirige a la plantilla 'entrada.html'.
        c. Si el tipo de formulario es 'acceso':
            i. Obtiene los valores de nombre de usuario y contraseña.
            ii. Autentica al usuario usando los valores proporcionados.
            iii. Si la autenticación es exitosa, inicia sesión al usuario y redirige a la plantilla 'entrada.html'.
            iv. Si la autenticación falla, muestra un mensaje de error.
    2. Si la solicitud no es de tipo POST o el tipo de formulario no coincide, renderiza la plantilla 'registration/login.html'.
    """
    if request.method == 'POST':
        accion = request.POST.get("tipoFormulario")

        if accion == "registro":
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')

            if User.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya existe.')
                return render(request, 'registration/login.html')

            if User.objects.filter(email=email).exists():
                messages.error(request, 'El email ya está registrado.')
                return render(request, 'registration/login.html')

            User.objects.create_user(
                username=username,
                email=email,
                password=password
            )  

            messages.success(request, '¡Registro exitoso!')
            return redirect('entrada')
        
        elif accion == "acceso":
            username = request.POST.get('username1')
            password = request.POST.get('password1')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('entrada')
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos')

    return render(request, "registration/login.html")

def privacidad(request):
    """
    Vista para mostrar la página de aviso de privacidad.

    Esta función maneja las solicitudes a la página de aviso de privacidad y renderiza la plantilla
    correspondiente.

    Parámetros:
    - request: Un objeto HttpRequest que contiene los datos de la solicitud.

    Retorna:
    - HttpResponse: Un objeto HttpResponse que contiene el contenido renderizado de 'aviso-privacidad.html'.
    """
    return render(request, "aviso-privacidad.html")


@login_required
def entrada(request):
    """
    Vista para manejar el formulario de adición de ejercicios.

    Si el método de la solicitud es POST y el formulario es válido,
    guarda el nuevo ejercicio en la base de datos y redirige a la vista
    de estadísticas. Si el método es GET, muestra un formulario vacío.

    Args:
        request (HttpRequest): Objeto que contiene la información de la solicitud HTTP.

    Returns:
        HttpResponse: Renderiza el template 'agregar_ejercicio.html' con el formulario.
    """
    if request.method == 'POST':
        form = EjercicioForm(request.POST)
        if form.is_valid():
            ejercicio = form.save(commit=False)
            ejercicio.user = request.user  # Asocia el usuario actual
            ejercicio.save()
            return redirect('estadisticas')
    else:
        form = EjercicioForm()

    return render(request, 'entrada.html', {'form': form})

@login_required
def estadisticas(request):
    """
    Vista para mostrar la gráfica de estadísticas de ejercicios.

    Recupera todos los ejercicios de la base de datos, prepara los datos
    y crea una gráfica con las repeticiones y el peso de cada ejercicio.
    La gráfica se convierte a formato PNG y se envía al template.

    Args:
        request (HttpRequest): Objeto que contiene la información de la solicitud HTTP.

    Returns:
        HttpResponse: Renderiza el template 'estadisticas.html' con la gráfica en formato base64.
    """
     # Recupera solo los ejercicios del usuario actual
    ejercicios = Ejercicio.objects.filter(user=request.user)

    # Preparar los datos para la gráfica
    nombres = [ejercicio.nombre for ejercicio in ejercicios]
    repeticiones = [ejercicio.repeticiones for ejercicio in ejercicios]
    pesos = [ejercicio.peso for ejercicio in ejercicios]

    # Crear la gráfica con Matplotlib
    plt.figure(figsize=(10, 6))
    plt.bar(nombres, repeticiones, color='blue', label='Repeticiones')
    plt.plot(nombres, pesos, color='green', marker='o', label='Peso (kg)', linestyle='--')
    plt.xlabel('Ejercicios')
    plt.ylabel('Cantidad')
    plt.title('Estadísticas de los Ejercicios')
    plt.legend()

    # Convertir la gráfica a formato PNG y enviarla al template
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    return render(request, 'estadisticas.html', {'graphic': graphic})
    

def ejercicios(request):
    """
    Vista para obtener un ejercicio basado en un grupo muscular específico desde una API externa.

    Realiza una solicitud a la API externa para obtener ejercicios relacionados con un músculo
    específico (en este caso, 'biceps'). Si la solicitud es exitosa, selecciona el primer ejercicio
    de la lista recibida y lo pasa al template. En caso de error durante la solicitud, muestra un mensaje
    de error al usuario.

    Args:
        request (HttpRequest): Objeto que contiene la información de la solicitud HTTP.

    Returns:
        HttpResponse: Renderiza el template 'ejercicios.html' con los detalles del ejercicio.
        En caso de error, devuelve un HttpResponse con el mensaje de error.
    """
    form = MuscleForm(request.POST or None)
    exercises = []

    if request.method == 'POST' and form.is_valid():
        muscle = form.cleaned_data['muscle']
        api_url = f'https://api.api-ninjas.com/v1/exercises?muscle={muscle}'
        #abdominals,abductors,adductors,biceps,calves,chest,forearms,glutes,
        #hamstrings,lats,lower_back,middle_back,neck,quadriceps,traps,triceps.
        #musculos que se pueden consultar en la api

        headers = {'X-Api-Key': "pyHrDCKJGD1AsmnJ8OYzBQ==AenVvW1aSLs0LXs6"}
        
        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            exercises = response.json()[:1] 
        except requests.RequestException as e:
            return HttpResponse(f"Error: {e}", status=500)

    return render(request, 'ejercicios.html', {'form': form, 'exercises': exercises})

@login_required
def change_password(request):
    """
    Vista para permitir a los usuarios cambiar su contraseña.

    Si el método de la solicitud es POST, valida y procesa el formulario
    de cambio de contraseña. Si el formulario es válido, actualiza la contraseña
    del usuario y mantiene la sesión activa. Redirige a la vista de confirmación 
    después de cambiar la contraseña. Si el método es GET, muestra un formulario 
    vacío para cambiar la contraseña.

    Args:
        request (HttpRequest): Objeto que contiene la información de la solicitud HTTP.

    Returns:
        HttpResponse: Renderiza el template 'registration/cambio.html' con el formulario de cambio de contraseña.
                    Redirige a la vista 'password_change_done' después de cambiar la contraseña.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Mantiene la sesión del usuario activa
            return redirect('password_change_done')
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'registration/cambio.html', {'form': form})

@login_required
def password_change_done(request):
    """
    Vista para mostrar la confirmación de cambio de contraseña.

    Renderiza una página de confirmación después de que el usuario ha cambiado su contraseña
    correctamente.

    Args:
        request (HttpRequest): Objeto que contiene la información de la solicitud HTTP.

    Returns:
        HttpResponse: Renderiza el template 'confirmacion.html' para mostrar un mensaje de confirmación.
    """
    return render(request, 'confirmacion.html')