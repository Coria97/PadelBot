import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from .logger import setup_logger
from .config import BASE_URL, ENABLE_NOTIFICATIONS
from .telegram_notifier import TelegramNotifier

logger = setup_logger(__name__)

class PadelScraper:
    def __init__(self):
        try:
            # Configurar opciones de Chrome
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Ejecutar en modo headless
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Inicializar el driver con manejo de errores
            service = Service()
            self.driver = webdriver.Chrome(
                service=service,
                options=chrome_options
            )
            logger.info("ChromeDriver inicializado correctamente")
            
            # Inicializar el notificador de Telegram
            self.telegram_notifier = TelegramNotifier()
            
        except Exception as e:
            logger.error(f"Error al inicializar ChromeDriver: {str(e)}")
            raise

    def get_available_slots(self):
        """
        Extrae los turnos disponibles del HTML
        
        Returns:
            list: Lista de turnos disponibles con su información
        """
        try:
            # Cargar la página
            self.driver.get(BASE_URL)
            
            # Esperar a que el calendario se cargue
            wait = WebDriverWait(self.driver, 10)
            calendar = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "CalendarioTurnosstyled__Grid-sc-71hh21-1"))
            )
            
            # Tiempo extra para que se carguen todos los elementos
            time.sleep(2)
            
            available_slots = []
            
            # Revisar los próximos 5 días
            for day in range(5):                
                # Obtener el HTML después de que se haya cargado el contenido dinámico
                html_content = self.driver.page_source
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Encontrar todas las celdas de turnos
                slots = soup.find_all('span', {'class': 'CalendarioTurnosstyled__Cell-sc-71hh21-2'})
                
                for slot in slots:
                    # Log para depuración
                    slot_classes = slot.get('class', [])
                    
                    # Verificar si el turno está disponible
                    if 'available' in slot_classes:
                        # Obtener la hora del turno
                        slot_time = slot.get('data-cy', '').replace('slot-', '')
                        
                        # Obtener la cancha (el div anterior que contiene el nombre de la cancha)
                        court_div = slot.find_previous('div', {'class': 'CalendarioTurnosstyled__CourtCell-sc-71hh21-6'})
                        if court_div:
                            court_name = court_div.find('span', {'class': 'CalendarioTurnosstyled__CourtName-sc-71hh21-7'}).text
                            court_attributes = court_div.find('div', {'class': 'CalendarioTurnosstyled__CourtAttributes-sc-71hh21-8'}).text
                            
                            available_slots.append({
                                'fecha': (datetime.now() + timedelta(days=day)).strftime("%d/%m/%Y"),
                                'hora': slot_time,
                                'cancha': court_name,
                                'caracteristicas': court_attributes
                            })
                        else:
                            logger.warning(f"No se encontró la información de la cancha para el slot {slot_time}")
                
                # Si no es el último día, avanzar al siguiente día
                if day < 4:
                    try:
                        # Encontrar y hacer clic en el botón de siguiente día
                        next_day_button = wait.until(
                            EC.element_to_be_clickable((By.CLASS_NAME, "DatePicker___StyledArrowIcon2-sc-aj5dzg-1"))
                        )
                        next_day_button.click()
                        time.sleep(2)  # Esperar a que cargue el nuevo día
                    except Exception as e:
                        logger.error(f"Error al avanzar al siguiente día: {str(e)}")
                        break
            
            return available_slots
            
        except Exception as e:
            logger.error(f"Error al obtener slots disponibles: {str(e)}")
            return []

    async def check_availability(self):
        """
        Verifica la disponibilidad de turnos
        """
        try:
            logger.info("Verificando disponibilidad de turnos...")
            
            # Obtener turnos disponibles
            available_slots = self.get_available_slots()
            
            if available_slots:
                logger.info(f"Se encontraron {len(available_slots)} turnos disponibles:")
                await self.notify_availability(available_slots)
            else:
                logger.info("No se encontraron turnos disponibles")
            
            return available_slots
            
        except Exception as e:
            logger.error(f"Error al verificar disponibilidad: {str(e)}")
            return False
        finally:
            # Cerrar el navegador
            self.driver.quit()

    async def notify_availability(self, available_slots):
        """
        Notifica sobre los turnos disponibles después de las 17:00 horas
        """
        if not ENABLE_NOTIFICATIONS:
            return

        logger.info("Turnos disponibles encontrados:")
        slots_after_17 = []
        
        for slot in available_slots:
            # Convertir la hora del slot a formato datetime para comparar
            hour_slot = datetime.strptime(slot['hora'], '%H:%M').time()
            hour_limite = datetime.strptime('17:00', '%H:%M').time()
            
            # Solo mostrar turnos después de las 17:00
            if hour_slot > hour_limite:
                logger.info(f"{slot['fecha']} - {slot['cancha']} a las {slot['hora']}")
                slots_after_17.append(slot)
        
        # Enviar notificación a Telegram si hay slots después de las 17:00
        if slots_after_17:
            await self.telegram_notifier.notify_available_slots(slots_after_17) 