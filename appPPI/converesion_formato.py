import json

# Ruta del archivo original y del archivo convertido
ruta_original = 'appPPI/static/assets/coordenadas.json'
ruta_convertido = 'appPPI/static/assets/coordenadas_gym.json'

# Nombre del modelo y de la aplicación
nombre_modelo = 'loginapp.Gym'

def convertir_datos():
    with open(ruta_original, 'r') as archivo_original:
        datos_originales = json.load(archivo_original)
    
    datos_convertidos = []
    pk = 1  # Clave primaria inicial
    
    for item in datos_originales:
        datos_convertidos.append({
            "model": nombre_modelo,
            "pk": pk,
            "fields": {
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "name": item.get("name"),
                
            }
        })
        pk += 1  # Incrementa la clave primaria
    
    with open(ruta_convertido, 'w') as archivo_convertido:
        json.dump(datos_convertidos, archivo_convertido, indent=4)

if __name__ == "__main__":
    convertir_datos()

