Feature: Cuenta 
  Background: Aplicacion abierta
    Given aplicación está abierta

    Scenario: Cuenta - guardar datos sin completar - mensaje de error - obra social
        Then presionar boton sing in
        When ingreso el usuario "danielruiz" y la contraseña "Test12345"
        And presionar boton ingresar
        When presionar boton cuenta
        When guardar sin completat datos de obra social
        Then validar mensaje de error de campos obligatorios

    
