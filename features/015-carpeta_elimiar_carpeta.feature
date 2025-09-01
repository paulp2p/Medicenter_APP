Feature: carpetas - eliminar carpeta
  Background: Aplicacion abierta
    Given aplicación está abierta
    
    Scenario: eliminar carpeta creada
      Then presionar boton sing in
      When ingreso el usuario "danielruiz" y la contraseña "Test12345"
      And presionar boton ingresar
      When buscar carpeta creada
      Then eliminar carpeta