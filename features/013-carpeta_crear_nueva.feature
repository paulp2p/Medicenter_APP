Feature: carpetas - crear nueva carpeta
  Background: Aplicacion abierta
    Given aplicación está abierta
     
    Scenario: crear nueva carpeta 
      Then presionar boton sing in
      When ingreso el usuario "danielruiz" y la contraseña "Test12345"
      And presionar boton ingresar
      When presionar boton MAS
      When crear una carpeta
      Then validar creacion de la carpeta
       