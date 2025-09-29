Feature: Historia clinica - Validar popup 
  Background: Aplicacion abierta
    Given aplicación está abierta

    Scenario:  Ingresar a datos personales -> Guardar sin completar datos
      Then presionar boton sing in
      When ingresar un usuario y contraseña validos
      And presionar boton ingresar
      When ingresar a ver mas folder de historia clinica
      And dar click en editar datos personales
      When elimiar informacion de datos personales
      Then salir de datos personales
      And valiar el popup de mensaje
    