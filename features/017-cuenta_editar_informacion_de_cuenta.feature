Feature: Cuenta 
  Background: Aplicacion abierta
    Given aplicación está abierta
        
    Scenario: Cuenta - Editar Username de información de cuenta
        Then presionar boton sing in
        When ingreso el usuario "danielruiz" y la contraseña "Test12345"
        And presionar boton ingresar
        When presionar boton cuenta
        When editar username
        Then validar que se cambion el username
      
   