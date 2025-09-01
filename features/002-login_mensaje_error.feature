Feature: Login alerta de username invalido y password invalido
  Background: Aplicacion abierta
    Given aplicación está abierta

    Scenario: Login con username Invalido y Contraseña Inválida
      Then presionar boton sing in
      When ingreso el usuario "lromano" y la contraseña "Test1234"
      And presionar boton ingresar
      Then mensaje de error por usuario inválido
      And  borrar las credenciales ingresadas
      When ingreso el usuario "danielruiz" y la contraseña "clave1234"
      And presionar boton ingresar
      Then mensaje de error por contraseña incorrecta

    Scenario: Login Sin Identidad Validada
      Then presionar boton sing in
      When ingreso el usuario "pacienteqa" y la contraseña "Test1234"
      When presionar boton ingresar
      And Visualizar Steps en el header
      Then Cerrar sesion 
