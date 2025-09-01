import json
import os
import random
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from appium.webdriver.common.appiumby import AppiumBy
import allure
from appium.webdriver.common.touch_action import TouchAction
from allure_commons.types import AttachmentType
import time

t = 0.5

class Funciones:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)

    @staticmethod
    def esperar_inicio_app(driver, timeout=90):
        print("[INFO] Esperando a que la app cargue completamente...")
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Sign up")')
            )
        )
        print("[INFO] La app cargó correctamente.")

    def tomar_screenshot(self, nombre="screenshot"):
        try:
            screenshot = self.driver.get_screenshot_as_png()
            allure.attach(screenshot, name=nombre, attachment_type=AttachmentType.PNG)
        except Exception as e:
            print(f"[!] Error al tomar screenshot: {e}")

    def escribir_por_xpath(self, xpath, texto, reintentos=2):
        for intento in range(reintentos):
            try:
                campo = self.wait.until(EC.presence_of_element_located((AppiumBy.XPATH, xpath)))
                campo.click()
                try:
                    campo.clear()
                except Exception:
                    pass
                campo.send_keys(texto)
                return
            except StaleElementReferenceException:
                print(f"[WARN] Elemento stale, reintentando ({intento + 1}/{reintentos})...")
                time.sleep(1)
        raise Exception(f"[ERROR] No se pudo interactuar con el elemento: {xpath}")

    def escribir_por_id(self, id, texto):
        if not texto:
            print(" Campo vacío: No se ingresó texto.")
            return
        campo = self.wait.until(EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, id)))
        campo.click()
        try:
            campo.clear()
        except Exception:
            pass
        campo.send_keys(texto)

    def escribir_por_uiautomator(self, uia_string, texto):
        try:
            print(f"[DEBUG] Esperando elemento: {uia_string}")
            campo = self.wait.until(EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, uia_string)))
            campo.click()
            campo.send_keys(texto)
        except TimeoutException:
            print(f"[ERROR] Timeout esperando el elemento con: {uia_string}")
            raise

    def capturar_texto_por_xpath(self, xpath, nombre_screenshot="mensaje_texto"):
        try:
            elemento = self.wait.until(EC.presence_of_element_located((AppiumBy.XPATH, xpath)))
            texto = elemento.text
            self.tomar_screenshot(nombre_screenshot)
            return texto
        except TimeoutException:
            self.tomar_screenshot(f"{nombre_screenshot}_not_found")
            print(f"[!] No se encontró el texto con XPATH: {xpath}")
            return None

    def capturar_texto_por_id(self, id, nombre_screenshot="mensaje_texto_id"):
        try:
            elemento = self.wait.until(EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, id)))
            texto = elemento.text
            self.tomar_screenshot(nombre_screenshot)
            return texto
        except TimeoutException:
            self.tomar_screenshot(f"{nombre_screenshot}_not_found")
            print(f"[!] No se encontró el texto con ACCESSIBILITY_ID: {id}")
            return None

    def capturar_imagen_por_uiautomator(self, localizador, nombre="imagen_uiautomator"):
        try:
            self.wait.until(EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, localizador)))
            png = self.driver.get_screenshot_as_png()
            allure.attach(png, name=nombre, attachment_type=AttachmentType.PNG)
            return True
        except TimeoutException:
            self.tomar_screenshot(f"{nombre}_not_found")
            print(f"[!] No se encontró la imagen con UIAutomator: {localizador}")
            return False

    def capturar_imagen_por_xpath(self, localizador, nombre="imagen_xpath"):
        try:
            self.wait.until(EC.presence_of_element_located((AppiumBy.XPATH, localizador)))
            png = self.driver.get_screenshot_as_png()
            allure.attach(png, name=nombre, attachment_type=AttachmentType.PNG)
            return True
        except TimeoutException:
            self.tomar_screenshot(f"{nombre}_not_found")
            print(f"[!] No se encontró la imagen con XPATH: {localizador}")
            return False

    def capturar_imagen_por_id(self, id, nombre_screenshot="imagen_id"):
        try:
            self.wait.until(EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, id)))
            self.tomar_screenshot(nombre_screenshot)
            return True
        except TimeoutException:
            self.tomar_screenshot(f"{nombre_screenshot}_not_found")
            print(f"[!] No se encontró la imagen con ACCESSIBILITY_ID: {id}")
            return False

    def click_y_screenshot_por_xpath(self, xpath, nombre_screenshot="click_elemento", reintentos=2):
        for intento in range(reintentos):
            try:
                elemento = self.wait.until(EC.presence_of_element_located((AppiumBy.XPATH, xpath)))
                if elemento.is_displayed() or elemento.is_enabled():
                    elemento.click()
                    time.sleep(0.5)
                    self.tomar_screenshot(nombre_screenshot)
                    return True
                else:
                    self.tomar_screenshot(f"{nombre_screenshot}_no_interactuable")
                    print(f"[!] Elemento encontrado pero no interactuable: {xpath}")
                    return False
            except StaleElementReferenceException:
                print(f"[WARN] Elemento stale, reintentando ({intento + 1}/{reintentos})...")
                time.sleep(1)
            except TimeoutException:
                self.tomar_screenshot(f"{nombre_screenshot}_no_encontrado")
                print(f"[!] No se encontró el elemento con XPATH: {xpath}")
                return False
        print(f"[!] Falló después de {reintentos} intentos por StaleElement.")
        return False

    def validar_y_clickear_por_xpath(self, xpath, nombre_screenshot="click_elemento", reintentos=2):
        for intento in range(reintentos):
            try:
                elemento = self.wait.until(EC.presence_of_element_located((AppiumBy.XPATH, xpath)))
                if elemento.is_displayed() or elemento.is_enabled():
                    self.tomar_screenshot(nombre_screenshot)
                    elemento.click()
                    return True
                else:
                    self.tomar_screenshot(f"{nombre_screenshot}_no_interactuable")
                    print(f"[!] Elemento encontrado pero no interactuable: {xpath}")
                    return False
            except StaleElementReferenceException:
                print(f"[WARN] Elemento stale, reintentando ({intento + 1}/{reintentos})...")
                time.sleep(1)
            except TimeoutException:
                self.tomar_screenshot(f"{nombre_screenshot}_no_encontrado")
                print(f"[!] No se encontró el elemento con XPATH: {xpath}")
                return False
        print(f"[!] Falló después de {reintentos} intentos por StaleElement.")
        return False

    def validar_y_clickear_por_uiautomator(self, ui_selector, nombre_screenshot="click_elemento"):
        try:
            elemento = self.wait.until(EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, ui_selector)))
            if elemento.is_displayed() or elemento.is_enabled():
                self.tomar_screenshot(nombre_screenshot)
                elemento.click()
                return True
            else:
                self.tomar_screenshot(f"{nombre_screenshot}_no_interactuable")
                print(f"[!] Elemento encontrado pero no interactuable: {ui_selector}")
                return False
        except TimeoutException:
            self.tomar_screenshot(f"{nombre_screenshot}_no_encontrado")
            print(f"[!] No se encontró el elemento con UIAutomator: {ui_selector}")
            return False

    def clickear_por_id(self, id_value, nombre_screenshot=None):
        try:
            print(f"[INFO] Buscando por ID: '{id_value}'")
            locator = (AppiumBy.ID, id_value)
            elemento = self.wait.until(EC.presence_of_element_located(locator))
            elemento.click()
            print(f"[OK] Click realizado en: '{id_value}'")
            if nombre_screenshot:
                screenshot = self.driver.get_screenshot_as_png()
                allure.attach(screenshot, name=nombre_screenshot, attachment_type=allure.attachment_type.PNG)
            return True
        except TimeoutException:
            print(f"[ERROR] No se encontró el elemento con ID: '{id_value}'")
            return False

    def validar_elemento_presente_uiautomator(self, texto_constante, nombre_screenshot="validacion_por_description"):
        time.sleep(3)
        try:
            self.wait.until(
                EC.presence_of_element_located((
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    f'new UiSelector().descriptionContains("{texto_constante}")'
                ))
            )
            screenshot = self.driver.get_screenshot_as_png()
            allure.attach(screenshot, name=nombre_screenshot, attachment_type=AttachmentType.PNG)
            return True
        except TimeoutException:
            print(f"[!] No se encontró un elemento con description que contenga: {texto_constante}")
            return False
        
    def esperar_elemento_visible(self, ui_selector: str, timeout: int = 10, nombre_screenshot: str | None = None):
        """
        Espera a que un elemento (ANDROID_UIAUTOMATOR) esté visible (displayed) o habilitado (enabled).
        :param ui_selector: string UiSelector, ej: 'new UiSelector().description("...")'
        :param timeout: segundos máximos de espera
        :param nombre_screenshot: si se pasa, adjunta captura (éxito/fallo) en Allure
        :return: WebElement si lo encuentra en estado visible/habilitado; None si hay timeout
        """
        wait = WebDriverWait(self.driver, timeout)

        try:
            print(f"[INFO] Esperando elemento (UIA): {ui_selector}")
            def _condicion(drv):
                try:
                    el = drv.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui_selector)
                    if el and (el.is_displayed() or el.is_enabled()):
                        return el
                except Exception:
                    pass
                return False

            elemento = wait.until(_condicion)

            if nombre_screenshot:
                png = self.driver.get_screenshot_as_png()
                allure.attach(png, name=nombre_screenshot, attachment_type=allure.attachment_type.PNG)

            print("[OK] Elemento visible/habilitado.")
            return elemento

        except TimeoutException:
            print(f"[ERROR] Timeout esperando elemento visible/habilitado: {ui_selector}")
            if nombre_screenshot:
                png = self.driver.get_screenshot_as_png()
                allure.attach(png, name=f"{nombre_screenshot}_no_visible", attachment_type=allure.attachment_type.PNG)
            return None

    def validar_elemento_presente_xpath(self, xpath, nombre_screenshot="validacion_por_xpath"):
        time.sleep(3)
        try:
            self.wait.until(EC.presence_of_element_located((AppiumBy.XPATH, xpath)))
            screenshot = self.driver.get_screenshot_as_png()
            allure.attach(screenshot, name=nombre_screenshot, attachment_type=AttachmentType.PNG)
            return True
        except TimeoutException:
            print(f"[!] No se encontró elemento por XPATH: {xpath}")
            return False

    def clickear_por_uiautomator(self, ui_selector, nombre_screenshot=None):
        try:
            print(f"[INFO] Buscando por UIAUTOMATOR: {ui_selector}")
            elemento = self.wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, ui_selector)))
            if elemento.is_displayed() or elemento.is_enabled():
                elemento.click()
                print(f"[OK] Click realizado en: {ui_selector}")
                if nombre_screenshot:
                    screenshot = self.driver.get_screenshot_as_png()
                    allure.attach(screenshot, name=nombre_screenshot, attachment_type=allure.attachment_type.PNG)
                return True
            else:
                print(f"[WARN] Elemento encontrado pero no interactuable: {ui_selector}")
                if nombre_screenshot:
                    screenshot = self.driver.get_screenshot_as_png()
                    allure.attach(screenshot, name=f"{nombre_screenshot}_no_interactuable", attachment_type=allure.attachment_type.PNG)
                return False
        except TimeoutException:
            print(f"[ERROR] No se encontró el elemento con UIAutomator: {ui_selector}")
            if nombre_screenshot:
                screenshot = self.driver.get_screenshot_as_png()
                allure.attach(screenshot, name=f"{nombre_screenshot}_no_encontrado", attachment_type=allure.attachment_type.PNG)
            return False

    def clickear_por_xpath(self, xpath_selector, nombre_screenshot=None):
        try:
            print(f"[INFO] Buscando por XPATH: '{xpath_selector}'")
            elemento = self.wait.until(EC.presence_of_element_located((AppiumBy.XPATH, xpath_selector)))
            if elemento.is_displayed() or elemento.is_enabled():
                elemento.click()
                print(f"[OK] Click realizado en: '{xpath_selector}'")
                if nombre_screenshot:
                    screenshot = self.driver.get_screenshot_as_png()
                    allure.attach(screenshot, name=nombre_screenshot, attachment_type=allure.attachment_type.PNG)
                return True
            else:
                print(f"[WARN] Elemento encontrado pero no interactuable: {xpath_selector}")
                if nombre_screenshot:
                    screenshot = self.driver.get_screenshot_as_png()
                    allure.attach(screenshot, name=f"{nombre_screenshot}_no_interactuable", attachment_type=allure.attachment_type.PNG)
                return False
        except TimeoutException:
            print(f"[ERROR] No se encontró el elemento con XPATH: {xpath_selector}")
            if nombre_screenshot:
                screenshot = self.driver.get_screenshot_as_png()
                allure.attach(screenshot, name=f"{nombre_screenshot}_no_encontrado", attachment_type=allure.attachment_type.PNG)
            return False

    def clear_por_xpath(self, xpath_selector, nombre_screenshot="clear_xpath"):
        try:
            elemento = self.wait.until(EC.presence_of_element_located((AppiumBy.XPATH, xpath_selector)))
            if elemento.is_displayed() or elemento.is_enabled():
                elemento.click()
                elemento.clear()
                return True
            else:
                self.tomar_screenshot(f"{nombre_screenshot}_no_interactuable")
                print(f"[!] Elemento encontrado pero no interactuable: {xpath_selector}")
                return False
        except TimeoutException:
            self.tomar_screenshot(f"{nombre_screenshot}_no_encontrado")
            print(f"[!] No se encontró el elemento con XPATH: {xpath_selector}")
            return False

    def clear_por_uiautomator(self, ui_selector, nombre_screenshot="clear_uia"):
        try:
            elemento = self.wait.until(EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, ui_selector)))
            if elemento.is_displayed() or elemento.is_enabled():
                elemento.click()
                elemento.clear()
                return True
            else:
                self.tomar_screenshot(f"{nombre_screenshot}_no_interactuable")
                print(f"[!] Elemento encontrado pero no interactuable: {ui_selector}")
                return False
        except TimeoutException:
            self.tomar_screenshot(f"{nombre_screenshot}_no_encontrado")
            print(f"[!] No se encontró el elemento con UIAutomator: {ui_selector}")
            return False

    def borrar_input_con_teclado(self, locator_uia):
        try:
            campo = self.wait.until(EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, locator_uia)))
            campo.click()
            time.sleep(0.5)
            texto_actual = campo.text or ""
            cantidad_caracteres = len(texto_actual)
            if cantidad_caracteres == 0:
                print("[INFO] El input ya estaba vacío.")
                return
            print(f"[INFO] Borrando {cantidad_caracteres} caracteres…")
            for _ in range(cantidad_caracteres):
                self.driver.press_keycode(67)
                time.sleep(0.05)
        except Exception as e:
            print(f"[ERROR] al borrar input con teclado: {e}")

    def borrar_input_y_capturar(self, locator_uiautomator):
        try:
            campo = self.wait.until(EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, locator_uiautomator)))
            campo.click()
            time.sleep(0.3)
            texto_actual = campo.text or ""
            for _ in range(len(texto_actual)):
                self.driver.press_keycode(67)
                time.sleep(0.05)
            screenshot = self.driver.get_screenshot_as_png()
            allure.attach(screenshot, name="campo_input_texto_borrado", attachment_type=AttachmentType.PNG)
            print("[OK] Campo borrado y captura tomada.")
        except TimeoutException:
            print(f"[ERROR] No se encontró el campo con locator: {locator_uiautomator}")
        except Exception as e:
            print(f"[ERROR] al borrar input y capturar: {e}")

    def obtener_content_desc_por_uiautomator(self, texto_parcial, nombre_screenshot="obtener_content_desc"):
        time.sleep(3)
        try:
            selector = f'new UiSelector().descriptionContains("{texto_parcial}")'
            elemento = self.wait.until(EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, selector)))
            content_desc = elemento.get_attribute("contentDescription")
            screenshot = self.driver.get_screenshot_as_png()
            allure.attach(screenshot, name=nombre_screenshot, attachment_type=AttachmentType.PNG)
            print(f"[INFO] content-desc encontrado: {content_desc}")
            return content_desc
        except TimeoutException:
            print(f"[!] No se encontró un elemento con description que contenga: {texto_parcial}")
            return None

    def borrar_input(self, elemento):
        try:
            elemento.clear()
            time.sleep(0.5)
            TouchAction(self.driver).tap(elemento).perform()
            time.sleep(0.5)
            TouchAction(self.driver).long_press(elemento, duration=1000).release().perform()
            time.sleep(0.5)
            for _ in range(10):
                elemento.send_keys("\b")
                time.sleep(0.1)
        except Exception as e:
            print(f"[!] Error al borrar input de forma robusta: {e}")

    def validar_n_mensajes_required_field(self, cantidad_esperada=3):
        try:
            xpath_base = '//android.view.View[@content-desc="Required field"]'
            time.sleep(1.5)
            elementos = self.driver.find_elements(AppiumBy.XPATH, xpath_base)
            if len(elementos) == cantidad_esperada:
                print(f"[INFO] Se detectaron {cantidad_esperada} mensajes de 'Required field'")
                screenshot = self.driver.get_screenshot_as_png()
                allure.attach(screenshot, name=f"{cantidad_esperada}_required_fields", attachment_type=AttachmentType.PNG)
                return True
            else:
                print(f"[WARN] Se encontraron {len(elementos)} mensajes, se esperaban {cantidad_esperada}")
                return False
        except Exception as e:
            print(f"[ERROR] No se pudo validar los mensajes 'Required field': {e}")
            return False

    def obtener_username_guardado(self):
        ruta = "datos_generados/username.txt"
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read().strip()

    def validar_y_clickear_validar_identidad(self):
        xpath = '//android.view.View[contains(@content-desc, "Validate your identity")]'
        try:
            print("[INFO] Buscando elemento con texto parcial 'Validate your identity'...")
            elemento = self.wait.until(EC.presence_of_element_located((AppiumBy.XPATH, xpath)))
            elemento.click()
            print("[INFO] Clic realizado sobre elemento 'Validate your identity'.")
            self.tomar_screenshot("click_validate_identity")
        except TimeoutException:
            print("[ERROR] No se encontró el elemento con 'Validate your identity' a tiempo.")
            raise

    def scroll_hasta_elemento(self, ui_selector, max_intentos=5):
        for intento in range(max_intentos):
            print(f"[INFO] Intento {intento+1} de scroll…")
            try:
                elemento = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui_selector)
                if elemento.is_displayed():
                    print("[INFO] Elemento encontrado.")
                    return elemento
            except Exception:
                pass
            try:
                self.driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    'new UiScrollable(new UiSelector().scrollable(true).instance(0)).scrollForward()'
                )
                time.sleep(0.5)
            except Exception as e:
                print(f"[WARN] Error al hacer scroll: {e}")
                break
        print(f"[WARN] No se encontró el elemento después de {max_intentos} intentos.")
        return None

    def click_random(self, locator1, locator2, tipo="uiautomator", descripcion=""):
        elegido = random.choice([locator1, locator2])
        print(f"[INFO] Se eligió aleatoriamente: {elegido} {descripcion}")
        by = AppiumBy.ANDROID_UIAUTOMATOR
        if tipo == "xpath":
            by = AppiumBy.XPATH
        elif tipo == "id":
            by = AppiumBy.ID
        try:
            elemento = self.wait.until(EC.element_to_be_clickable((by, elegido)))
            elemento.click()
            print(f"[INFO] Click en elemento: {elegido} ({descripcion})")
        except Exception as e:
            print(f"[ERROR] No se pudo hacer click en {elegido}: {e}")
            raise

    def click_por_xpath_touchaction(self, xpath, nombre_screenshot="click_touchaction_xpath"):
        try:
            elemento = self.wait.until(EC.presence_of_element_located((AppiumBy.XPATH, xpath)))
            location = elemento.location
            size = elemento.size
            x = location['x'] + size['width'] // 2
            y = location['y'] + size['height'] // 2
            TouchAction(self.driver).tap(x=x, y=y).perform()
            screenshot = self.driver.get_screenshot_as_png()
            allure.attach(screenshot, name=nombre_screenshot, attachment_type=AttachmentType.PNG)
            print(f"[OK] Click TouchAction realizado en ({x}, {y}) para xpath: {xpath}")
            return True
        except Exception as e:
            print(f"[ERROR] al hacer click TouchAction por xpath: {e}")
            screenshot_error = self.driver.get_screenshot_as_png()
            allure.attach(screenshot_error, name=f"{nombre_screenshot}_error", attachment_type=AttachmentType.PNG)
            return

    def click_por_coordenadas(self, x, y, *, adjuntar_screenshot: bool = False, nombre_screenshot: str = "click_por_coordenadas",
                              normalizado: bool = False, validar_bordes: bool = True, sleep_despues: float = 0.0):
        try:
            if normalizado:
                size = self.driver.get_window_size()
                x = int(round(x * size["width"]))
                y = int(round(y * size["height"]))
            if not isinstance(x, int) or not isinstance(y, int):
                raise ValueError("Las coordenadas deben ser enteros (usa normalizado=True si pasas floats 0..1).")
            if validar_bordes:
                size = self.driver.get_window_size()
                if not (0 <= x < size["width"] and 0 <= y < size["height"]):
                    raise ValueError(f"Coordenadas fuera de la pantalla: ({x},{y}) tamaño={size}.")

            try:
                from selenium.webdriver.common.action_chains import ActionChains
                from selenium.webdriver.common.actions.action_builder import ActionBuilder
                from selenium.webdriver.common.actions import interaction
                from selenium.webdriver.common.actions.pointer_input import PointerInput

                actions = ActionChains(self.driver)
                actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "finger"))
                actions.w3c_actions.pointer_action.move_to_location(x, y)
                actions.w3c_actions.pointer_action.pointer_down()
                actions.w3c_actions.pointer_action.pause(0.05)
                actions.w3c_actions.pointer_action.pointer_up()
                actions.perform()
                ok = True
            except Exception as e_w3c:
                print(f"[WARN] W3C Actions falló, probando TouchAction: {e_w3c}")
                ok = False

            if not ok:
                try:
                    from appium.webdriver.common.touch_action import TouchAction
                    TouchAction(self.driver).tap(x=x, y=y).perform()
                    ok = True
                except Exception as e_touch:
                    raise RuntimeError(f"No se pudo realizar el tap por W3C ni TouchAction: {e_touch}")

            if adjuntar_screenshot:
                try:
                    screenshot = self.driver.get_screenshot_as_png()
                    allure.attach(screenshot, name=nombre_screenshot, attachment_type=AttachmentType.PNG)
                except Exception as e_ss:
                    print(f"[WARN] No se pudo adjuntar/guardar screenshot: {e_ss}")

            if sleep_despues > 0:
                time.sleep(float(sleep_despues))

            print(f"[OK] Click realizado en coordenadas: ({x}, {y})")

        except Exception as e:
            print(f"[ERROR] al hacer click por coordenadas: {e}")
            try:
                screenshot_error = self.driver.get_screenshot_as_png()
                allure.attach(screenshot_error, name="error_click_por_coordenadas", attachment_type=AttachmentType.PNG)
            except Exception:
                pass

    def click_random_uia_por_description(self, descriptions, *, persist_key="grupo_sanguineo",
                                         persist_path="datos_generados/random_choices.json",
                                         avoid_repeat=True, avoid_checked=True,
                                         timeout_probe=3, timeout_click=10):
        seen, descs = set(), []
        for d in descriptions:
            if d not in seen:
                descs.append(d); seen.add(d)

        last = None
        store = {}
        try:
            if os.path.exists(persist_path):
                with open(persist_path, "r", encoding="utf-8") as f:
                    store = json.load(f)
                    last = store.get(persist_key)
        except Exception:
            store = {}

        def probe(desc):
            locator = f'new UiSelector().description("{desc}")'
            state = {"desc": desc, "locator": locator, "existe": False, "clickable": False, "checked": False}
            try:
                el = WebDriverWait(self.driver, timeout_probe).until(
                    EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, locator))
                )
                state["existe"] = True
                try:
                    state["checked"] = (el.get_attribute("checked") == "true") or (el.get_attribute("selected") == "true")
                except Exception:
                    pass
                try:
                    WebDriverWait(self.driver, timeout_probe).until(
                        EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, locator))
                    )
                    state["clickable"] = True
                except Exception:
                    state["clickable"] = False
            except Exception:
                pass
            return state

        states = [probe(d) for d in descs]
        print("[DBG] opciones -> " + " | ".join([f'{s["desc"]}: ex={s["existe"]} cl={s["clickable"]} ch={s["checked"]}' for s in states]))

        candidates = [s for s in states if s["existe"]] or states
        if avoid_checked:
            not_checked = [s for s in candidates if not s["checked"]]
            if not_checked:
                candidates = not_checked
        if avoid_repeat and last is not None:
            no_repeat = [s for s in candidates if s["desc"] != last]
            if no_repeat:
                candidates = no_repeat
        clickable = [s for s in candidates if s["clickable"]]
        pool = clickable or candidates
        elegido = random.choice(pool)

        try:
            el = WebDriverWait(self.driver, timeout_click).until(
                EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, elegido["locator"]))
            )
            el.click()
            print(f'[INFO] Click en "{elegido["desc"]}"')
        except TimeoutException:
            for alt in [s for s in states if s is not elegido and s["existe"]]:
                try:
                    el2 = WebDriverWait(self.driver, timeout_click).until(
                        EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, alt["locator"]))
                    )
                    el2.click()
                    elegido = alt
                    print(f'[WARN] Fallback OK: click en "{alt["desc"]}"')
                    break
                except Exception:
                    continue
            else:
                raise

        try:
            os.makedirs(os.path.dirname(persist_path), exist_ok=True)
            store[persist_key] = elegido["desc"]
            with open(persist_path, "w", encoding="utf-8") as f:
                json.dump(store, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[WARN] No se pudo persistir la elección: {e}")

        return elegido["desc"]
