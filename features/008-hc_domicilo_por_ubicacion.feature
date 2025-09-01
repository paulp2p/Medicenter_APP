Feature: Historia clinica - EDITAR DATOS DE DOCIMILIO
  Background: Aplicacion abierta
    Given aplicación está abierta

    Scenario:  Editar domicilio por ubicacion 
      Then presionar boton sing in
      When ingresar el usuario y la contraseña registrados
      And presionar boton ingresar
      When ingresar a ver mas folder de historia clinica
      And dar click en editar datos personales
      When editar ubicacion por ubicacion actual
      Then guardar datos personales
      