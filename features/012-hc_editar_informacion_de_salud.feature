Feature: Historia clinica - editar informacion de salud 
  Background: Aplicacion abierta
    Given aplicación está abierta

    Scenario:  Ingresar a datos personales -> editar datos de salud
      Then presionar boton sing in
      When ingresar un usuario y contraseña validos
      And presionar boton ingresar
      When ingresar a ver mas folder de historia clinica
      And dar click en editar datos de salud
      When editar datos de salud
      Then guardar datos editados