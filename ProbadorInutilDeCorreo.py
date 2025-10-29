#!/usr/bin/env python3
"""
Script de prueba para envío de correos con servidor personalizado
"""

import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import getpass

def test_smtp_connection(smtp_config):
    """Prueba completa de conexión SMTP con máximo debugging"""
    
    print("🚀 INICIANDO PRUEBA DE ENVÍO DE CORREO")
    print("=" * 60)
    
    # Mostrar configuración (ocultar password)
    print(f"📧 Configuración SMTP:")
    print(f"   Servidor: {smtp_config['server']}")
    print(f"   Puerto: {smtp_config['port']}")
    print(f"   Usuario: {smtp_config['username']}")
    print(f"   Password: {'*' * len(smtp_config['password'])}")
    print(f"   Use TLS: {smtp_config.get('use_tls', False)}")
    print(f"   Use SSL: {smtp_config.get('use_ssl', False)}")
    print("=" * 60)
    
    server = None
    try:
        # Paso 1: Resolución DNS
        print(f"\n1. 🔍 RESOLUCIÓN DNS...")
        try:
            ip_address = socket.gethostbyname(smtp_config['server'])
            print(f"   ✅ Servidor resuelto: {smtp_config['server']} -> {ip_address}")
        except socket.gaierror as e:
            print(f"   ❌ Error DNS: No se pudo resolver {smtp_config['server']}")
            print(f"   💡 Verifica: El nombre del servidor es correcto?")
            return False

        # Paso 2: Conexión al servidor
        print(f"\n2. 🔌 CONECTANDO AL SERVIDOR...")
        print(f"   Conectando a {smtp_config['server']}:{smtp_config['port']}")
        
        timeout_seconds = 30
        if smtp_config.get('use_ssl', False):
            print(f"   Usando SSL...")
            server = smtplib.SMTP_SSL(smtp_config['server'], smtp_config['port'], timeout=timeout_seconds)
        else:
            server = smtplib.SMTP(smtp_config['server'], smtp_config['port'], timeout=timeout_seconds)
        
        # Activar debugging máximo
        server.set_debuglevel(2)
        print(f"   ✅ Conexión establecida")
        
        # Paso 3: EHLO/HELO
        print(f"\n3. 🤝 SALUDO AL SERVIDOR (EHLO)...")
        ehlo_response = server.ehlo()
        print(f"   Respuesta EHLO: {ehlo_response}")
        
        # Paso 4: STARTTLS (si está configurado)
        if smtp_config.get('use_tls', False) and not smtp_config.get('use_ssl', False):
            print(f"\n4. 🔒 INICIANDO STARTTLS...")
            if server.has_extn('STARTTLS'):
                starttls_response = server.starttls()
                print(f"   ✅ STARTTLS exitoso: {starttls_response}")
                
                # Re-enviar EHLO después de STARTTLS
                ehlo_response = server.ehlo()
                print(f"   EHLO después de STARTTLS: {ehlo_response}")
            else:
                print(f"   ⚠️  El servidor no soporta STARTTLS")
        
        # Paso 5: Autenticación
        print(f"\n5. 🔐 AUTENTICACIÓN...")
        print(f"   Intentando login con usuario: {smtp_config['username']}")
        
        try:
            server.login(smtp_config['username'], smtp_config['password'])
            print(f"   ✅ Autenticación exitosa")
        except smtplib.SMTPAuthenticationError as e:
            print(f"   ❌ Error de autenticación: {e}")
            print(f"   💡 Verifica:")
            print(f"     - Usuario y contraseña correctos?")
            print(f"     - La cuenta existe en el servidor?")
            return False

        # Paso 6: Crear mensaje de prueba
        print(f"\n6. 📝 CREANDO MENSAJE DE PRUEBA...")
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"PRUEBA SMTP - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        msg['From'] = smtp_config['username']
        msg['To'] = smtp_config['username']  # Enviarse a sí mismo para prueba
        
        # Cuerpo del mensaje
        test_body = f"""
        <html>
        <body>
            <h2>✅ Prueba de correo exitosa</h2>
            <p>Este es un mensaje de prueba enviado el {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}</p>
            <p><strong>Configuración usada:</strong></p>
            <ul>
                <li>Servidor: {smtp_config['server']}</li>
                <li>Puerto: {smtp_config['port']}</li>
                <li>Usuario: {smtp_config['username']}</li>
                <li>TLS: {smtp_config.get('use_tls', False)}</li>
                <li>SSL: {smtp_config.get('use_ssl', False)}</li>
            </ul>
            <p>Si recibes este correo, la configuración SMTP es correcta.</p>
        </body>
        </html>
        """
        
        part1 = MIMEText("Este es un mensaje de prueba SMTP", 'plain')
        part2 = MIMEText(test_body, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        print(f"   ✅ Mensaje creado")
        print(f"   Asunto: {msg['Subject']}")
        print(f"   De: {msg['From']}")
        print(f"   Para: {msg['To']}")

        # Paso 7: Envío del mensaje
        print(f"\n7. 📤 ENVIANDO MENSAJE...")
        send_response = server.send_message(msg)
        print(f"   ✅ Mensaje enviado al servidor")
        if send_response:
            print(f"   Respuesta: {send_response}")

        # Paso 8: Cerrar conexión
        print(f"\n8. 🚪 CERRANDO CONEXIÓN...")
        quit_response = server.quit()
        print(f"   ✅ Conexión cerrada: {quit_response}")

        print("\n" + "=" * 60)
        print("🎉 ¡PRUEBA EXITOSA!")
        print(f"✅ El correo fue enviado correctamente a: {msg['To']}")
        print("💡 Revisa tu bandeja de entrada en unos minutos")
        return True

    except smtplib.SMTPConnectError as e:
        print(f"❌ Error de conexión: {e}")
        print("💡 Verifica:")
        print("  - El servidor y puerto son correctos?")
        print("  - El firewall bloquea el puerto?")
        print("  - El servidor está online?")
        return False
        
    except smtplib.SMTPServerDisconnected as e:
        print(f"❌ Servidor desconectado: {e}")
        print("💡 El servidor cerró la conexión abruptamente")
        return False
        
    except socket.timeout as e:
        print(f"❌ Timeout de conexión: {e}")
        print("💡 El servidor no respondió en 30 segundos")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        print("📋 Traceback completo:")
        traceback.print_exc()
        return False
        
    finally:
        if server:
            try:
                server.close()
            except:
                pass

def get_custom_smtp_config():
    """Solicita configuración SMTP personalizada"""
    print("\n🔧 CONFIGURACIÓN SMTP PERSONALIZADA")
    print("=" * 50)
    
    config = {}
    
    config['server'] = input("Servidor SMTP (ej: mail.midominio.com, smtp.corpre.cl): ").strip()
    
    # Opciones de puerto
    print("\n📡 Puertos comunes:")
    print("   587 - Con STARTTLS (recomendado)")
    print("   25  - Sin encriptación")
    print("   465 - Con SSL")
    
    config['port'] = int(input("Puerto SMTP: ").strip())
    
    config['username'] = input("Usuario/email completo: ").strip()
    config['password'] = getpass.getpass("Contraseña: ")
    
    # Configurar SSL/TLS basado en puerto
    if config['port'] == 465:
        config['use_ssl'] = True
        config['use_tls'] = False
        print("🔒 Configuración: SSL (puerto 465)")
    elif config['port'] == 587:
        config['use_ssl'] = False
        config['use_tls'] = True
        print("🔒 Configuración: STARTTLS (puerto 587)")
    elif config['port'] == 25:
        config['use_ssl'] = False
        config['use_tls'] = False
        print("🔓 Configuración: Sin encriptación (puerto 25)")
    else:
        # Para puertos personalizados, preguntar
        use_ssl = input("¿Usar SSL? (s/n): ").lower().strip() == 's'
        if use_ssl:
            config['use_ssl'] = True
            config['use_tls'] = False
        else:
            config['use_ssl'] = False
            config['use_tls'] = input("¿Usar STARTTLS? (s/n): ").lower().strip() == 's'
    
    return config

def quick_test_common_ports(server, username, password):
    """Prueba rápidamente puertos comunes"""
    common_ports = [
        (587, False, True, "STARTTLS"),
        (25, False, False, "Sin encriptación"),
        (465, True, False, "SSL"),
    ]
    
    print(f"\n🔍 PROBANDO PUERTOS COMUNES PARA: {server}")
    print("=" * 50)
    
    for port, use_ssl, use_tls, desc in common_ports:
        print(f"\n🧪 Probando puerto {port} ({desc})...")
        
        config = {
            'server': server,
            'port': port,
            'username': username,
            'password': password,
            'use_ssl': use_ssl,
            'use_tls': use_tls
        }
        
        try:
            # Prueba rápida de conexión
            if use_ssl:
                server_conn = smtplib.SMTP_SSL(server, port, timeout=10)
            else:
                server_conn = smtplib.SMTP(server, port, timeout=10)
            
            if use_tls:
                server_conn.starttls()
            
            server_conn.login(username, password)
            server_conn.quit()
            
            print(f"   ✅ Puerto {port} FUNCIONA - {desc}")
            return config
            
        except Exception as e:
            print(f"   ❌ Puerto {port} falló: {e}")
    
    return None

def main():
    """Función principal"""
    print("🧪 TESTER DE ENVÍO DE CORREOS SMTP - SERVIDOR PERSONALIZADO")
    print("=" * 60)
    
    # Opción directa a servidor personalizado
    print("\n1. 📋 Ingresar configuración manualmente")
    print("2. 🔍 Descubrir configuración automáticamente")
    
    choice = input("\nSelecciona opción (1 o 2): ").strip()
    
    if choice == "2":
        print("\n🎯 MODO DESCUBRIMIENTO AUTOMÁTICO")
        server = input("Servidor SMTP (ej: mail.empresa.com): ").strip()
        username = input("Usuario/email: ").strip()
        password = getpass.getpass("Contraseña: ")
        
        config = quick_test_common_ports(server, username, password)
        
        if config:
            print(f"\n🎉 ¡Configuración encontrada!")
            print(f"   Usar: {server}:{config['port']}")
            confirm = input("\n¿Probar envío completo con esta configuración? (s/n): ").lower().strip()
            if confirm == 's':
                test_smtp_connection(config)
        else:
            print("\n❌ No se pudo encontrar una configuración funcionando")
            print("💡 Prueba con configuración manual")
            config = get_custom_smtp_config()
            test_smtp_connection(config)
    
    else:
        # Configuración manual
        config = get_custom_smtp_config()
        test_smtp_connection(config)

if __name__ == "__main__":
    main()
