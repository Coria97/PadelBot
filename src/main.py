import time
import asyncio
import schedule

from src.config import CHECK_INTERVAL 
from src.logger import setup_logger
from src.scraper import PadelScraper

logger = setup_logger(__name__)

async def run_check():
    """
    Ejecuta una verificación de disponibilidad
    """
    logger.info("Iniciando verificación de disponibilidad...")
    scraper = PadelScraper()
    await scraper.check_availability()

async def main():
    """
    Función principal que programa y ejecuta las verificaciones
    """
    logger.info("Iniciando PadelBot...")
    
    # Programar la verificación inicial
    await run_check()
    
    # Programar verificaciones periódicas
    schedule.every(CHECK_INTERVAL).minutes.do(lambda: asyncio.run(run_check()))
    
    # Mantener el programa en ejecución
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main()) 