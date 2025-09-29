Feature: Historia clinica - Validar mesajes de error en campos obligatorios
  Background: Aplicacion abierta
    Given aplicación está abierta

    Scenario:  Ingresar a datos personales -> ver mensajes de campo obligatorios
      Then presionar boton sing in
      When ingresar un usuario y contraseña validos
      And presionar boton ingresar
      When ingresar a ver mas folder de historia clinica
      And dar click en editar datos personales
      When eliminar toda la informacion de domicilio
      Then guardar datos personales
      And validar mensjaes de error en campos obligatorios
      