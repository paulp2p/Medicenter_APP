Feature: carpetas - editar nombre de carpeta
  Background: Aplicacion abierta
    Given aplicación está abierta
    
    Scenario: editar nombre de carpeta 
      Then presionar boton sing in
      When ingreso el usuario "danielruiz" y la contraseña "Test12345"
      And presionar boton ingresar
      When buscar carpeta creada
      When cambiar nombre de la carpeta
      Then validar que se cambio el nombre de la carpeta