import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

from datetime import datetime, timedelta

from src.logger import setup_logger
from src.config import BASE_URL, ENABLE_NOTIFICATIONS
from src.telegram_bot import TelegramBot
from src.database.operations import available_slots_manager

logger = setup_logger(__name__)

class PadelScraper:
    def __init__(self):
        try:
            # Config options for ChromeDriver
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-setuid-sandbox')
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--disable-browser-side-navigation')
            chrome_options.add_argument('--disable-features=TranslateUI')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-popup-blocking')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-default-apps')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')

            # Initialize the driver with error handling
            service = Service()
            self.driver = webdriver.Chrome(
                service=service,
                options=chrome_options
            )
            logger.info("ChromeDriver initialized successfully.")
            
            # Initialize the Telegram notifier
            self.telegram_notifier = TelegramBot()
            
        except Exception as e:
            logger.error(f"Error when initializing ChromeDriver: {str(e)}")
            raise

    def get_available_slots(self):
        """
        Extract available slots from the Padel website.

        Returns:
            list: List of available slots with their information
        """
        try:
            # Load the page
            self.driver.get(BASE_URL)

            # Wait for the calendar to load
            wait = WebDriverWait(self.driver, 10)
            
            # Extra time for all elements to load
            time.sleep(2)
            
            available_slots = []

            # Check the next 5 days
            for day in range(5):
                # Get the HTML after the dynamic content has loaded
                html_content = self.driver.page_source
                soup = BeautifulSoup(html_content, 'html.parser')

                # Find all slot cells
                slots = soup.find_all('span', {'class': 'CalendarioTurnosstyled__Cell-sc-71hh21-2'})
                
                for slot in slots:
                    slot_classes = slot.get('class', [])

                    # Check if the slot is available
                    if 'available' in slot_classes:
                        # Get the slot time
                        slot_time = slot.get('data-cy', '').replace('slot-', '')

                        # Get the court information (the previous div containing the court name and attributes)
                        court_div = slot.find_previous('div', {'class': 'CalendarioTurnosstyled__CourtCell-sc-71hh21-6'})
                        if court_div:
                            court_name = court_div.find('span', {'class': 'CalendarioTurnosstyled__CourtName-sc-71hh21-7'}).text
                            court_attributes = court_div.find('div', {'class': 'CalendarioTurnosstyled__CourtAttributes-sc-71hh21-8'}).text
                            
                            available_slots.append({
                                'day': (datetime.now() + timedelta(days=day)).strftime("%d/%m/%Y"),
                                'hour': slot_time,
                                'court': court_name,
                                'attributes': court_attributes
                            })
                        else:
                            logger.warning(f"Could not find court information for slot {slot_time}")

                # If not the last day, move to the next day
                if day < 4:
                    try:
                        # Find and click the next day button
                        next_day_button = wait.until(
                            EC.element_to_be_clickable((By.CLASS_NAME, "DatePicker___StyledArrowIcon2-sc-aj5dzg-1"))
                        )
                        next_day_button.click()
                        time.sleep(2)  # Wait for the new day to load
                    except Exception as e:
                        logger.error(f"Error when moving to the next day: {str(e)}")
                        break
            
            return available_slots
            
        except Exception as e:
            logger.error(f"Error when getting available slots: {str(e)}")
            return []

    async def check_availability(self):
        """
        Check the availability of slots
        """
        try:
            logger.info("Checking slot availability...")

            # Get available slots
            available_slots = self.get_available_slots()
            
            if available_slots:
                logger.info(f"Found {len(available_slots)} available slots:")
                available_slots_manager.save_slots(available_slots)
            else:
                logger.info("No available slots found.")

            return available_slots
            
        except Exception as e:
            logger.error(f"Error when checking availability: {str(e)}")
            return False
        finally:
            # Close the driver after checking availability
            self.driver.quit()

    async def notify_availability(self, available_slots):
        """
        Notifies about available slots after 17:00 hours
        """
        if not ENABLE_NOTIFICATIONS:
            return

        logger.info("Available slots found:")
        slots_after_17 = []
        
        for slot in available_slots:
            # Convert the slot hour to datetime format for comparison
            hour_slot = datetime.strptime(slot['hour'], '%H:%M').time()
            hour_limit = datetime.strptime('17:00', '%H:%M').time()

            # Only show slots after 17:00
            if hour_slot > hour_limit:
                logger.info(f"{slot['day']} - {slot['court']} at {slot['hour']}")
                slots_after_17.append(slot)

        # Send notification to Telegram if there are slots after 17:00
        if slots_after_17:
            await self.telegram_notifier.notify_available_slots(slots_after_17) 