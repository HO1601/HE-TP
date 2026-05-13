## 🎯 Objetivos
- Documentar el diseño y flujo de un keylogger que captura pulsaciones de teclado utilizando `pynput.keyboard`, las almacena en un archivo `log.txt` y las envía por correo electrónico mediante SMTP con TLS (Gmail).
- Analizar los riesgos de detección (código con credenciales en texto plano, uso de APIs de Windows para ocultar la consola).
- Proponer medidas de mitigación defensivas aplicables en entornos reales.

## ⚙️ Arquitectura (resumen)

### Inicialización y Ocultamiento
- Se obtiene la ventana de la consola con `win32console.GetConsoleWindow()` y se oculta mediante `win32gui.ShowWindow(ventana, 0)`.
- Se define una lista `lista_teclas` para acumular temporalmente las pulsaciones.

### Captura de teclas
- Se usa `pynput.keyboard.Listener` con la función `presiona(key)` como callback.
- La función `convert(key)` transforma objetos `KeyCode` en caracteres (`key.char`) y teclas especiales en su representación en string (por ejemplo `"Key.space"`).
- Reglas de tratamiento:
  - `Key.space` → agrega un espacio `" "`.
  - `Key.enter` → agrega un salto de línea `"\n"`.
  - `Key.backspace` → elimina el último carácter de `lista_teclas` (`.pop()`).
  - `Key.shift`, `Key.ctrl`, `Key.alt` → se ignoran (`pass`).
  - Cualquier otra tecla normal → se agrega su carácter.
  - `Key.esc` → llama a `imprimir()` y detiene el listener (`return False`).

### Almacenamiento y envío
- La función `imprimir()`:
  - Abre `log.txt` en modo `"a"` (append).
  - Concatena todos los elementos de `lista_teclas` en una cadena y la escribe en el archivo, seguida de un salto de línea.
  - Duerme 5 segundos (`time.sleep(5)`).
  - Llama a `enviar_datos()`.
- La función `enviar_datos()`:
  - Construye un mensaje `MIMEMultipart`.
  - Lee todo el contenido actual de `log.txt` y lo adjunta como `MIMEText`.
  - Configura remitente (`From`) y destinatario (`To`) como la misma cuenta Gmail: `hilary.obregon.16@gmail.com`.
  - Usa la contraseña de aplicación `"iqajahsnotdjqnpa"`.
  - Conecta a `smtp.gmail.com:587`, inicia TLS, hace login y envía el correo.
  - Captura excepciones de forma genérica e imprime `"Error al enviar el correo"`.

### Ciclo de exfiltración
- El envío se produce **una sola vez**, cuando el usuario presiona la tecla `ESC`. No hay envíos periódicos automáticos.
- El archivo `log.txt` se acumula entre ejecuciones (modo `"a"`). Al presionar `ESC` se vuelca la memoria actual y se envía todo el contenido del archivo.

## 🔧 APIs / Componentes relevantes
| Componente | Librería / API | Propósito |
|------------|----------------|------------|
| Ocultar consola | `win32console`, `win32gui` | Evitar que el usuario vea la ventana de Python |
| Captura de teclas | `pynput.keyboard.Listener`, `on_press` | Interceptar eventos de teclado en tiempo real |
| Conversión de teclas | `isinstance(key, pynput.keyboard.KeyCode)` | Diferenciar teclas normales de especiales |
| Almacenamiento | `open('log.txt', 'a')` | Guardar las pulsaciones en disco |
| Envío de correo | `smtplib`, `email.mime` | Enviar el archivo `log.txt` por Gmail |
| Temporización | `time.sleep(5)` | Pequeña pausa antes de enviar el correo |


## 🔍 Detecciones recomendadas (defensivas)

- **Monitoreo de procesos**: Detectar `python.exe` (o el ejecutable generado) que oculta su ventana (`ShowWindow` con `SW_HIDE`) y establece conexiones de red.
- **Reglas YARA / estáticas**: Buscar cadenas como `"iqajahsnotdjqnpa"`, `"hilary.obregon.16@gmail.com"`, `"smtp.gmail.com:587"` en los binarios.
- **Análisis de tráfico**: Conexiones a `smtp.gmail.com:587` desde equipos no autorizados (especialmente si no usan cliente de correo legítimo).
- **Auditoría de archivos**: Monitorear accesos a `log.txt` (creación, escritura, lectura) por procesos no habituales.
- **Hooks de teclado**: Monitorear el registro de hooks globales (`SetWindowsHookEx`), aunque `pynput` usa otro mecanismo (basado en eventos de Windows), puede ser detectado por EDR.

## 🛡️ Mitigaciones sugeridas

### Para el autor del código (mejoras ofensivas, con fines educativos)
- No almacenar la contraseña en texto plano; usar ofuscación básica o solicitar credenciales en tiempo de ejecución.
- Utilizar un servidor SMTP propio (no comercial) para evitar bloqueos por reputación de IP.
- Enviar el correo de forma asíncrona o con intervalos aleatorios para no generar un patrón predecible.
- Limpiar `log.txt` después del envío para no acumular datos.

### Controles defensivos (para blue team)
- **Bloquear puertos SMTP salientes** (587, 465, 25) excepto para servidores de correo autorizados.
- **Aplicar AppLocker / WDAC** para restringir la ejecución de scripts de Python o binarios no firmados.
- **Habilitar Script Block Logging** y AMSI si el keylogger se distribuye como script PowerShell (en este caso es Python, pero se podría convertir a exe).
- **Segmentación de red**: Aislar equipos de usuarios que no requieren acceso directo a Internet.
- **EDR / AV**: Las soluciones modernas (CrowdStrike, Defender for Endpoint) suelen detectar keyloggers que usan `pynput` o hooks globales de teclado. Mantener las firmas actualizadas.
- **Políticas de contraseñas**: Usar autenticación multifactor (MFA). Una contraseña capturada por keylogger es insuficiente para acceder si se requiere segundo factor.

## 📊 Resultados (en entornos controlados)

- El keylogger captura correctamente las pulsaciones (letras, números, espacios, saltos de línea y backspace) y las almacena en `log.txt`.
- Al presionar `ESC`, el contenido del archivo se envía a la cuenta Gmail configurada.
- **Limitaciones observadas**:
  - Solo envía una vez (al salir). Para envíos continuos se requeriría modificar el código.
  - La contraseña de aplicación está visible → cualquier análisis estático la revela.
  - Dependencia de Gmail (fácilmente bloqueable por políticas de red).
  - El backspace elimina el último carácter de la lista en memoria, pero no elimina del archivo ya escrito. Si se pulsa `ESC` después de varios backspaces, el archivo contendrá el texto corregido, pero no hay un registro histórico de las correcciones intermedias.
  - No diferencia entre ventanas o aplicaciones; captura todo el teclado del sistema.
- **Prueba de concepto**: En una máquina Windows con Python y las librerías instaladas, el script ejecutado como `.py` o convertido a `.exe` (con PyInstaller) funciona sin ventana visible y entrega el correo.

## 👥 Autores

- Obregon Campomanes, Hilary Romina - u202411195
- Zanabria Hurtado, Yoselyn Patricia - u20241A856
