Feature: Login otras cuentas 
  Background: Aplicacion abierta
    Given aplicación está abierta

    Scenario: Login desde Centro de Cuentas
      Then presionar boton sing in
      When ingreso el usuario "danielruiz" y la contraseña "Test12345"
      When presionar boton ingresar
      When Cerrar sesion
      Then Iniciar sesion desde el centro de cuentas