Feature: Login otras cuentas 
  Background: Aplicacion abierta
    Given aplicación está abierta

    Scenario: Login desde Ingresar con otra cuenta
      Then presionar boton sing in
      When ingreso el usuario "pacienteqa" y la contraseña "Test1234"
      When presionar boton ingresar
      When Cerrar sesion
      Then Iniciar sesion con otra cuenta
      When ingreso el usuario "danielruiz" y la contraseña "Test12345"
      When presionar boton ingresar
      When Cerrar sesion

