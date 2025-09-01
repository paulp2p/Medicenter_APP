Feature: Cuenta 
  Background: Aplicacion abierta
    Given aplicación está abierta

      Scenario: Cuenta - eliminar imagen de prefil - información de cuenta
        Then presionar boton sing in
        When ingreso el usuario "danielruiz" y la contraseña "Test12345"
        And presionar boton ingresar
        When presionar boton cuenta
        When eliminar imagen de perfil
        Then screen shot de imagen de perfil
              
    

   