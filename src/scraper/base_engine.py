from abc import ABC, abstractmethod
import logging
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.utils.normalization import decode_bing_redirect

class BaseEngine(ABC):
    def __init__(self, config, limit, min_delay, max_delay):
        self.config = config
        self.limit = limit
        self.min_delay = min_delay
        self.max_delay = max_delay

    @abstractmethod
    def get_links(self, driver, container):
         """Extract links from the container."""
         pass

    def is_valid(self, link, seen_set):
        if not link: return False
        if not link.startswith("http"): return False
        if link in seen_set: return False

        forbidden_terms = [
            "aclick", "login", "signup", "preferences", "settings",
            "privacy", "terms", "cookie", "advertisement", "form=",
            "adurl"
        ]

        if "/search?" in link or "search." in link:
            return False

        if "bing.com/search" in link or "google.com/search" in link:
             return False

        if any(term in link for term in forbidden_terms):
            return False

        return True

    def search(self, query, driver):
        time.sleep(random.randint(self.min_delay, self.max_delay))
        target_url = self.config["url"] + query.replace(" ", "+")
        logging.info(f"Navigating to: {target_url}")

        results = []
        seen = set()

        try:
            driver.get(target_url)
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Captcha check
            page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            if any(x in page_text for x in ["verify you are human", "solve this puzzle", "challenge"]):
                logging.warning(f"!!! BLOCKED. Pausing for manual intervention...")
                print('\a')
                input(f">>> SOLVE CAPTCHA IN BROWSER -> PRESS [ENTER] HERE TO CONTINUE...")
                logging.info("Resuming... Refreshing page...")
                driver.get(target_url)
                time.sleep(5)

            # Scraping Strategy 1: Specific Selector
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.config["container"])))
                container = driver.find_element(By.CSS_SELECTOR, self.config["container"])
                results = self.get_links(driver, container, seen)

            except Exception as e:
                logging.warning(f"Main container not found ({e}). Trying fallback...")

            # Scraping Strategy 2: Fallback
            if len(results) < self.limit:
                 logging.info("Engaging global fallback...")
                 all_links = driver.find_elements(By.TAG_NAME, "a")
                 for a in all_links:
                    try:
                        link = a.get_attribute("href")
                        # Perform specific engine decoding if needed (e.g. Bing)
                        # Ideally this should be handled by a method that can be overridden
                        link = self.process_link(link) 
                        
                        if self.is_valid(link, seen):
                            results.append(link)
                            seen.add(link)
                    except:
                        continue
                    if len(results) >= self.limit: break

        except Exception as e:
            logging.error(f"Error scraping '{query}': {str(e)[:100]}")

        return results

    def process_link(self, link):
        """Hook for processing links (e.g. decoding). Default is identity."""
        return link
