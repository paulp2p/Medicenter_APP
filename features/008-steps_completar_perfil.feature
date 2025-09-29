Feature: Completar perfil - Steps
  Background: Aplicacion abierta
    Given aplicación está abierta
     
    Scenario: completar perfil - STEPs
      Then presionar boton sing in
      When ingreso el usuario "danielruiz" y la contraseña "Test12345"
      When presionar boton ingresar
      #Then debería ver la pantalla principal
      # eliminar cuenta - eliminar datos previos
      When presionar boton cuenta
      When eliminar cuenta de usuario 
      When ingreso el usuario "danielruiz" y la contraseña "Test12345"
      When presionar boton ingresar
      When presionar boton go to home 
      # completar perfil 2 a 3
      When entrar a completar perfil 2
      When completar datos de ocupacion y domicilio
      Then verificar que el estado cambio de 2 a 3
      # completar perfil 3 a 4
      When entrar a completar perfil 3
      When guardar sin completar - alerta mensaje de error
      When cargar el primer documento
      Then verificar que el estado cambio de 3 a 4
      #completar perfil 4 a 5
      When entrar a completar perfil 4
      When seleccionar un interes 
      When validar interes seleccionado en tips
      Then verificar que el estado cambio de 4 a 5
      Then Cerrar sesion 
      
      
      

        