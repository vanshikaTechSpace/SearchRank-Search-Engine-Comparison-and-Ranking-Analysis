from .base_engine import BaseEngine
from selenium.webdriver.common.by import By
import logging

class GoogleEngine(BaseEngine):
    def get_links(self, driver, container, seen):
        results = []
        potential_links = container.find_elements(By.CSS_SELECTOR, "a")
        logging.info(f"Scanning {len(potential_links)} raw links in main container...")

        for elem in potential_links:
            try:
                link = elem.get_attribute("href")
                if self.is_valid(link, seen):
                    results.append(link)
                    seen.add(link)
                elif link and "http" in link:
                    logging.debug(f"Rejected: {link}")
            except:
                continue
            if len(results) >= self.limit: break
        return results
