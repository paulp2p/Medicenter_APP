Feature: Login tradicional
  Background: Aplicacion abierta
    Given aplicación está abierta
     
    Scenario: Login exitoso 
      Then presionar boton sing in
      When ingreso el usuario "danielruiz" y la contraseña "Test12345"
      And presionar boton ingresar
      Then debería ver la pantalla principal

        
       
        
