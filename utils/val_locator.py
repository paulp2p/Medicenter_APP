# LOCALIZADORES DE ELEMENTOS 
# DATOS DE INGRESO 
# TEXTOS DE VALIDACION 


class Localizadores:
    # HEADER COMPLETAR PERFIL
    VALIDATE_STEPS = [
        "20%, 1/5 Complete your profile Validate your identity",
        "40%, 2/5 Complete your profile Validate your identity",
        "60%, 3/5 Complete your profile Validate your identity",
        "80%, 4/5 Complete your profile Validate your identity",
        "100%, 5/5 Complete your profile Validate your identity"
    ]
    # LOCALIZADORES DE MODULO  DE INICIO - SING IN -  CREATE ACCOUNT 
    SLICE_1 = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.view.View/android.view.View[2]'
    SLICE_2 = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.view.View/android.view.View[3]'
    SLICE_3 = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.view.View/android.view.View[4]'
    SLICE_4 = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.view.View/android.view.View[5]'
    
    # MODULO DE: PERFIL - OTRAS CUENTAS - CENTRO DE CUENTAS
    BTN_SIGN_IN = '//android.widget.Button[@content-desc="Sign in"]' 
    CREATE_ACCOUNT = '//android.widget.Button[@content-desc="Create account"]'
    BTN_PERFIL = 'new UiSelector().className("android.widget.ImageView").instance(3)'
    BTN_LOGOUT = 'new UiSelector().description("Log out")'
    BTN_OK_LOGOUT = 'new UiSelector().description("Ok")'
    X = 'new UiSelector().className("android.widget.ImageView").instance(2)'
    YES_DELETE = 'new UiSelector().description("Yes, delete")'
    IMG_LOGO = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.view.View/android.widget.ImageView[1]'
    BTN_OTRA_CUENTA = 'new UiSelector().description("Sign in with another account")'
    INPUT_INVALIDO = '//android.widget.ImageView[@text="lromano"]'

    # LOCALIZADORES DE PANTALLA LOGIN
    IMG_MC_APP_LOGIN = '//android.widget.ImageView'
    CAMPO_USER = 'new UiSelector().className("android.widget.EditText").instance(0)'
    CAMPO_PASSW = 'new UiSelector().className("android.widget.EditText").instance(1)'
    BTN_SING_IN = '//android.widget.Button[@content-desc="Sign in"]'
    INVALID_PASSW = '//android.view.View[@content-desc="Invalid password"]'
    INVALID_USER = '//android.view.View[@content-desc="Invalid username"]'
    IMG_LOGEADO = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.view.View/android.widget.ImageView[1]'

    # LOCALIZADORES DE MODULO DE REGISTRO
    TEXTO_PANTALLA_REGISTRO = 'new UiSelector().description("Sign up to digitize your health and take it with you wherever you go")'
    CREATE_EMAIL = 'new UiSelector().className("android.widget.EditText").instance(0)'
    CREATE_USERNAME = 'new UiSelector().className("android.widget.EditText").instance(1)'
    CREATE_PASSW = 'new UiSelector().className("android.widget.EditText").instance(2)'
    CREATE_PASSW_CONFIRM = 'new UiSelector().className("android.widget.EditText").instance(3)'
    CHECK_BOX_CONDITIONS = 'new UiSelector().className("android.widget.CheckBox")'
    BTN_NEXT = 'new UiSelector().description("Next")'
    INPUT_CODIGO = 'new UiSelector().className("android.widget.EditText").instance(0)'
    VALIDACION_EXITOSA = 'new UiSelector().description("Validated e-mail")'
    CODIGO_1 = 'new UiSelector().className("android.widget.EditText").instance(0)'
    CODIGO_2 = 'new UiSelector().className("android.widget.EditText").instance(1)'
    CODIGO_3 = 'new UiSelector().className("android.widget.EditText").instance(2)'
    CODIGO_4 = 'new UiSelector().className("android.widget.EditText").instance(3)'
    RESEND_CODE = 'new UiSelector().description("Resend code")'
    LOGO_MC_APP = 'new UiSelector().className("android.widget.ImageView").instance(0)'
    BTN_BACK  = 'new UiSelector().description("Back")'
    REQUIRED_FIELD_1 = '(//android.view.View[@content-desc="Required field"])[1]'
    REQUIRED_FIELD_2 = '(//android.view.View[@content-desc="Required field"])[2]'
    REQUIRED_FIELD_3 = '(//android.view.View[@content-desc="Required field"])[3]'
    REQUIRED_FIELD_4 = '(//android.view.View[@content-desc="Required field"])[4]'
    # LOCALIZADORES DE MODULO COMPLETAR VALIDAR PERFIL
    H_PROFILE = ('//android.widget.ImageView[contains(@content-desc, "Validate your identity")]')
    PANTALLA_V_YOUR_IDENTITY = 'new UiSelector().description("We need to validate your identity")' 
    BTN_STAR = 'new UiSelector().description("Start")'
    PANTALLA_INDICACION = 'new UiSelector().resourceId("com.siltium.medicenter:id/tvTitle")'
    """SIGUIENTE #CONFIRMAR SELECTION # TAKE A PHOTO"""
    BTN_ACTION_PRIMARY = 'new UiSelector().resourceId("com.siltium.medicenter:id/btnActionPrimary")' 
    """GALLERY"""
    BTN_ACTION_SECUNDARY = 'new UiSelector().resourceId("com.siltium.medicenter:id/btnActionSecondary")'
    CLICK_LISTA_PAIS = 'new UiSelector().resourceId("com.siltium.medicenter:id/etSearchCountry")'
    ABRIR_LISTA_PAIS = 'com.siltium.medicenter:id/tvSelectedCountry'
    SELECT_PAIS = 'new UiSelector().text("Argentina")'
    SELECT_DNI_EXTRANJERO = 'new UiSelector().resourceId("com.siltium.medicenter:id/rbItem").instance(1)'
    TEXT_FRONT_SIDE = 'new UiSelector().resourceId("com.siltium.medicenter:id/tvDocSide")'
    BTN_GO_TO_HOME = 'new UiSelector().description("Go to home")'
    #LOCALIZADORES DE CARGAR DOCUMENTOS
    DNI_FRENTE = 'new UiSelector().resourceId("com.google.android.documentsui:id/icon_thumb").instance(1)'
    YES_UPLOAD = 'new UiSelector().resourceId("com.siltium.medicenter:id/ivUploadCTA")'
    #BTN_ACTION_PRIMARY
    #LOCALIZADORES DE HOSTORIA CLINICA 
    BTN_VER_MAS= 'new UiSelector().description("View more")'
    BTN_EDITAR_DATOS_PERSONALES = 'new UiSelector().className("android.widget.ImageView").instance(2)'
    # EDITAR_DATOS_PERSONALES
    INPUT_NAME_DATOS_PERSONALES = 'new UiSelector().className("android.view.View").instance(5)'
    INPUT_LASTNAME_DATOS_PERSONALES = 'new UiSelector().className("android.view.View").instance(6)'
    INPTU_FECHA = 'new UiSelector().className("android.view.View").instance(7)'
    INPUT_EDAD = 'new UiSelector().className("android.view.View").instance(8)'
    INPUT_OCUPACION = 'new UiSelector().className("android.widget.EditText")'
    # editar datos de domicilio
    # eliminar datos de domicilio  new UiSelector().className("android.widget.ImageView").instance(2)
    DELETE_COUNTRY = 'new UiSelector().className("android.view.View").instance(7)'
    DELETE_COUNTRY_POPUP = 'new UiSelector().className("android.widget.ImageView").instance(2)'
    DELETE_OTHER_COUNTRY = 'new UiSelector().className("android.widget.ImageView").instance(5)'
    DELETE_ADDRESS = 'new UiSelector().text("Google Building 43, 43 Amphitheatre Pkwy, Mountain View, CA 94043, USA").instance(0)'
    # EDITAR DOMICILIO NUEVA DIRECCION
    BUSCADOR = 'new UiSelector().className("android.widget.EditText")'
    INPUT_COUNTRY = 'new UiSelector().className("android.view.View").instance(7)'
    SELECT_PAIS = 'new UiSelector().description("Argentina")' 
    INPUT_PROVINCE = 'new UiSelector().className("android.view.View").instance(9)'
    SELECT_PROVINCE = 'new UiSelector().description("Distrito federal (CABA)")'
    # USUAR RESIDENCIA POR CHECK BOX
    CLICK_EN_PANTALLA = 'new UiSelector().description("Place of residence *")'
    INPUT_DOMICILIO = 'new UiSelector().className("android.widget.EditText").instance(1)'
    #     
    CHECK_BOX_RESIDENCE = 'new UiSelector().className("android.widget.CheckBox")'
    BTN_SAVE = 'new UiSelector().description("Save changes")'
    #
    UBICACION_ACTUAL = 'new UiSelector().description("Use current location")'
    LINK_EDIT_PERSONAL_DATA = 'new UiSelector().description("Edit personal data")'
    POPUP_MJS = 'new UiSelector().description("Are you sure you want to go back? You will lose the changes you have made so far.")'
    MSJ_CAMPO_OBLIGATORIO1 = 'new UiSelector().description("You must enter at least the country").instance(0)'
    MSJ_CAMPO_OBLIGATORIO2 = 'new UiSelector().description("You must enter at least the country").instance(1)'
    #
    BUSCADOR_DE_PAIS = 'new UiSelector().className("android.widget.ImageView").instance(2)'
    # LOCALIZADORES DE HOSTORIA CLINICA - INFORMACION DE SALUD
    BTN_EDITAR_INFORMACION_DESALUD = 'new UiSelector().className("android.widget.ImageView").instance(3)'
    BG_A = 'new UiSelector().description("A")'
    BG_B = 'new UiSelector().description("B")'
    BG_C = 'new UiSelector().description("C")'
    BG_D = 'new UiSelector().description("D")'
    BF_POSITIVO = 'new UiSelector().description("Positive")'
    BF_NEGATIVO = 'new UiSelector().description("Negative")'
    ALCOHOL_S = '(//android.view.View[@content-desc="Yes"])[1]'
    ALCOHOL_N = '(//android.view.View[@content-desc="No"])[1]'
    FUMAR_S = '(//android.view.View[@content-desc="Yes"])[2]'
    FUMSR_N = '(//android.view.View[@content-desc="No"])[2]'
    DRUG_S = '(//android.view.View[@content-desc="Yes"])[3]'
    DRUG_N = '(//android.view.View[@content-desc="No"])[3]'
    ELIMINAR_ALERGIA = 'new UiSelector().className("android.widget.ImageView").instance(3)'
    ESCRIBIR_ALERGIA = 'new UiSelector().className("android.widget.EditText")'
    BTN_GUARDAR_INF_SALUD = 'new UiSelector().description("Save changes")'
    # LOCALIZADORES DE MODULO CARPETAS 
    BTN_MAS = 'new UiSelector().className("android.widget.ImageView").instance(13)' 
    NEW_FOLDER = '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View[1]/android.view.View/android.view.View'
    NOMBRE_DE_CARPETA = '//android.widget.EditText' #xpath
    BTN_CREAR_CARPETA = '//android.widget.Button[@content-desc="Create"]' #xpath
    BTN_CANCELAR_CREAR_CARPETA = 'new UiSelector().description("Cancel")'
    PATH_CARPETA_CREADA = 'new UiSelector().description("Test 0 Items")'
    OPCIONES_DE_CARPETA = 'new UiSelector().className("android.widget.ImageView").instance(14)'
    RENOMBRAR_CARPETA = '//android.widget.ImageView[@content-desc="Rename"]'
    CAMBIAR_NOMBRE = '//android.widget.Button[@content-desc="Change name"]'
    CARPETA_CREADA = '//android.view.View[@content-desc="Test2 0 Items"]/android.widget.ImageView[1]'
    BTN_MAS_EN_CARPETA = 'new UiSelector().className("android.widget.ImageView").instance(3)'
    OPCIONES_CARPETA2 = '//android.view.View[@content-desc="Test2 0 Items"]/android.widget.ImageView[2]'
    CARPETA_RENOMBRADA = 'new UiSelector().description("Test2 0 Items")'
    DELETE_CARPETA = '//android.widget.ImageView[@content-desc="Delete"]'
    BTN_DELETE_CARPETA = '//android.widget.Button[@content-desc="Delete"]'
    ERROR_CARPETA_SIN_NOMBRE = 'new UiSelector().description("You must enter a name")'
    # LOCALIZADORES DE MODULO CUENTA
    NAV_CUENTA = 'new UiSelector().description("Account")'
    
