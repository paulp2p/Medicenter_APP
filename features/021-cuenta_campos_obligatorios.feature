Feature: Cuenta 
  Background: Aplicacion abierta
    Given aplicación está abierta

    Scenario: Cuenta - campos obligatorios de mail y usuario  - información de cuenta
        Then presionar boton sing in
        When ingreso el usuario "danielruiz" y la contraseña "Test12345"
        And presionar boton ingresar
        When presionar boton cuenta
        When borrar campos de username y email
        Then validar mensaje alerta de campos obligatorios

    Scenario: Cuenta - cambiar nro de telefono y verificar codigo - información de cuenta
      Then presionar boton sing in
      When ingreso el usuario "danielruiz" y la contraseña "Test12345"
      And presionar boton ingresar
      When presionar boton cuenta
      When cambiar nro de telefono
      Then validar codigo de verificacion de cambio de nro de telefono
