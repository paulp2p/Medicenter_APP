Feature: Registro de usuario - verificavion de reenvio de codigo
  Background: Aplicacion abierta
    Given aplicación está abierta


    Scenario: Registro exitoso con validacion de codigo
      When Ingresar a crear cuenta y validar pantalla de campos input
      And ingresar email - username - password - confirmar password
      And clicar en checkbox y btn Next
      Then obtener y validar el código de verificación
      When ingresar código de verificación recibido
      Then valida que paso el codigo de verificacion
