Feature: Registro de usuario 
  Background: Aplicacion abierta
    Given aplicación está abierta

    Scenario: Registro - validar alerta campos obligatorios
      When Ingresar a crear cuenta y validar pantalla de campos input
      And clicar en checkbox y btn Next
      Then validar alerta mensajes de campos obligatorios

    Scenario: Registro - formato invalido email y contraseña
      When Ingresar a crear cuenta y validar pantalla de campos input
      When ingresar email invalido
      And clicar en checkbox y btn Next
      Then ferificar mensaje de mail invalido
      When reingresar a sección de crear cuenta
      When ingresar contraseña invalida
      Then verificar mensaje de contraseña invalida
      
    

      
   
  
    
   
    
   
  