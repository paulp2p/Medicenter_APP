Feature: Cuenta 
    Background: Aplicacion abierta
      Given aplicación está abierta
              
        Scenario: Cuenta - Editar imagen de prefil - información de cuenta
            Then presionar boton sing in
            When ingreso el usuario "danielruiz" y la contraseña "Test12345"
            And presionar boton ingresar
            When presionar boton cuenta
            When cambiar imagen de perfil seleccionar de la galeria
            Then validar cambio de imagen de perfil