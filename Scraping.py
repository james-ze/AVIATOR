import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuración de ChromeOptions para usar tu perfil
ruta_perfil = r'C:\Users\yijam\AppData\Local\Google\Chrome\User Data'
nombre_perfil = 'Profile 1'  # Nombre del perfil que deseas usar

chrome_options = Options()
chrome_options.add_argument(f'--user-data-dir={ruta_perfil}')  # Ruta de la carpeta de perfiles
chrome_options.add_argument(f'--profile-directory={nombre_perfil}')  # Nombre del perfil
chrome_options.add_argument('--disable-gpu')  # Desactivar GPU para evitar problemas
chrome_options.add_argument('--no-sandbox')  # Desactivar sandbox para evitar problemas de permisos
chrome_options.add_argument('--disable-dev-shm-usage')  # Evitar problemas de memoria
chrome_options.add_argument('--log-level=3')  # Reducir el nivel de logs de Chrome (solo errores críticos)
chrome_options.add_argument('--disable-logging')  # Desactivar logs adicionales

# Inicializar el driver de Chrome con las opciones
try:
    driver = webdriver.Chrome(options=chrome_options)
except Exception as e:
    print(f"Error al iniciar Chrome: {e}")
    exit()

# Variables globales
ultimo_primer_valor = None  # Almacenar el último primer valor procesado

# Abrir la URL
driver.get('https://1woqab.top/casino/play/aviator')

# Esperar a que el iframe esté presente
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div[3]/div/main/article/main/div/div/div[2]/div/iframe'))
    )
except Exception as e:
    print(f"Error al cargar el iframe: {e}")
    driver.quit()
    exit()

# Cambiar al iframe
iframe = driver.find_element(By.XPATH, '/html/body/div/div/div/div[3]/div/main/article/main/div/div/div[2]/div/iframe')
driver.switch_to.frame(iframe)

# Esperar a que el elemento dentro del iframe esté presente
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/app-root/app-game/div/div[1]/div[2]/div/div[2]/div[1]/app-stats-widget/div/div[1]/div'))
    )
except Exception as e:
    print(f"Error al cargar el elemento dentro del iframe: {e}")
    driver.quit()
    exit()

# Función para extraer y procesar el resultado
def resultado():
    global ultimo_primer_valor  # Hacer referencia a la variable global

    try:
        # Extraer el elemento
        resultado = driver.find_element(By.XPATH, '/html/body/app-root/app-game/div/div[1]/div[2]/div/div[2]/div[1]/app-stats-widget/div/div[1]/div').text

        # Inicializar lista
        lista = resultado.split()

        # Procesar los primeros 12 elementos
        nuevos_datos = []
        for x in range(len(lista[0:12])):
            numero = lista[x].translate(str.maketrans('', '', 'x'))  # Eliminar 'x' si existe
            numero = numero.replace(",", "")  # Eliminar comas de los números
            nuevos_datos.append(float(numero))  # Convertir a float

        return nuevos_datos
    except Exception as e:
        print(f"Error al procesar el resultado: {e}")
        return None

# Función para guardar los resultados en un archivo
def guardar_resultados(datos):
    with open('resultados.txt', 'a') as archivo:
        archivo.write(f"{datos}\n")

# Bucle principal
while True:
    datos = resultado()  # Llamar a la función para obtener los datos
    if datos:  # Verificar que haya datos
        primer_valor = datos[0]  # Obtener el primer valor de la lista
        if primer_valor != ultimo_primer_valor:  # Solo procesar si el primer valor es nuevo
            ultimo_primer_valor = primer_valor  # Actualizar el último primer valor procesado
            print(datos)  # Imprimir la lista completa
            guardar_resultados(datos)  # Guardar la lista completa en el archivo
    time.sleep(2)  # Esperar antes de la siguiente iteración
