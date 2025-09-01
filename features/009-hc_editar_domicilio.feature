Feature: Historia clinica - Completar Datos personales exitosamente
  Background: Aplicacion abierta
    Given aplicación está abierta

    Scenario:  Ingresar datos pérsonales -> editar ocupacion y domicilio
      Then presionar boton sing in
      When ingresar el usuario y la contraseña registrados
      And presionar boton ingresar
      When ingresar a ver mas folder de historia clinica
      And dar click en editar datos personales
      When completar datos personales
      When seleccionar pais
      When seleccionar cuidad y agregar direccion 
      Then guardar datos personales
    
    