Feature: carpetas - Crear carpeta sin nombre
  Background: Aplicacion abierta
    Given aplicación está abierta
        
    Scenario: crear una carpeta sin nombre - validar error 
        Then presionar boton sing in
        When ingreso el usuario "danielruiz" y la contraseña "Test12345"
        And presionar boton ingresar
        Then crear carpeta sin nombre
        