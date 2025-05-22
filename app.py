from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys
import random
from fake_useragent import UserAgent

# Initialize fake user-agent
ua = UserAgent()

# Set up Chrome options to avoid bot detection
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
# Set random user-agent
chrome_options.add_argument(f"user-agent={ua.random}")
# Additional anti-detection options
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-gpu")  # Sometimes helps with detection
chrome_options.add_argument("--log-level=3")  # Suppress verbose logs

# Initialize the driver with error handling
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    # Hide automation flags
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
except Exception as e:
    print(f"Error with ChromeDriverManager: {e}")
    print("Trying alternative method...")
    try:
        chromedriver_path = os.path.join(os.getcwd(), "chromedriver.exe")
        if os.path.exists(chromedriver_path):
            driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        else:
            raise FileNotFoundError("chromedriver.exe not found in script directory")
    except Exception as e2:
        print(f"Error: {e2}")
        print("\nPlease ensure Chrome browser is installed and try one of these solutions:")
        print("1. Download ChromeDriver manually from https://chromedriver.chromium.org/")
        print("2. Place chromedriver.exe in the same directory as this script (C:\\Users\\meert\\Desktop\\fiver)")
        print("3. Ensure Chrome and ChromeDriver versions match your system (64-bit/32-bit)")
        print("4. Current Chrome version: Check via chrome://version")
        sys.exit(1)

def scrape_gig_details(driver, link):
    """Visit a gig link and scrape title, rating, and price."""
    try:
        driver.get(link)
        print(f"\nVisiting gig page: {link}")
        # Random delay to mimic human behavior
        time.sleep(random.uniform(2, 4))
        # Scroll to mimic human interaction
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        time.sleep(random.uniform(0.5, 1.5))

        # Check for bot detection page
        try:
            if "human touch" in driver.page_source.lower():
                print("Bot detection triggered. Saving page source for debugging...")
                with open("bot_detection.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                return {
                    "link": link,
                    "title": "Bot detection triggered",
                    "price": "Not found",
                    "rating": "Not found"
                }
        except:
            pass

        # Try multiple selectors for title
        title = None
        title_selectors = [
            "h1.gig-title",
            "h1[class*='title']",
            "h1",
            "[class*='gig-header'] h1",
            "h1[data-testid='gig-title']",
            "h1[class*='headline']"
        ]
        for selector in title_selectors:
            try:
                title_elem = driver.find_element(By.CSS_SELECTOR, selector)
                title = title_elem.text.strip()
                if title and "human touch" not in title.lower():
                    break
            except:
                continue

        # Try multiple selectors for price
        price = None
        price_selectors = [
            "div.package-price",
            "[class*='price']",
            "span[class*='price']",
            "div[class*='pricing']",
            "[data-test-id='package-price']",
            "div[data-testid='package-price'] span",
            "div[class*='package-content'] [class*='price']"
        ]
        for selector in price_selectors:
            try:
                price_elem = driver.find_element(By.CSS_SELECTOR, selector)
                price = price_elem.text.strip()
                if price and "$" in price:
                    break
            except:
                continue

        # Try multiple selectors for rating
        rating = None
        rating_selectors = [
            "span.rating-score",
            "[class*='rating']",
            "div[class*='rating'] span",
            "[data-test-id='rating']",
            "span[data-testid='rating']",
            "div[class*='reviews'] span[class*='rating']"
        ]
        for selector in rating_selectors:
            try:
                rating_elem = driver.find_element(By.CSS_SELECTOR, selector)
                rating = rating_elem.text.strip()
                if rating and rating.replace(".", "").isdigit():
                    break
            except:
                continue

        # Return scraped details
        return {
            "link": link,
            "title": title if title and "human touch" not in title.lower() else "Not found",
            "price": price if price else "Not found",
            "rating": rating if rating else "Not found"
        }

    except Exception as e:
        print(f"Error scraping gig details from {link}: {e}")
        return {
            "link": link,
            "title": "Error",
            "price": "Error",
            "rating": "Error"
        }

url = "https://www.fiverr.com/search/gigs?query=website&source=top-bar&search_in=everywhere"

try:
    driver.get(url)
    print("Loading Fiverr search page...")
    time.sleep(random.uniform(4, 6))  # Random delay

    # Scroll to mimic human behavior
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(random.uniform(1, 2))

    # Accept cookies if popup appears
    try:
        cookie_accept = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept") or contains(text(), "Agree ")]')))
        cookie_accept.click()
        print("Accepted cookies")
    except:
        print("No cookie popup found or already accepted")

    time.sleep(random.uniform(2, 4))
    print(f"Page title: {driver.title}")

    # Try multiple selectors for gig cards
    gig_selectors = [
        "div.gig-card-layout",
        "div[class*='gig-card']",
        "article.gig-card",
        "div[data-testid='gig-card']",
        "div.gigs-grid > div",
        "div[class*='services-col']"
    ]

    links = []
    for selector in gig_selectors:
        try:
            gigs = driver.find_elements(By.CSS_SELECTOR, selector)
            if gigs:
                print(f"Found {len(gigs)} gigs using selector: {selector}")
                for i, gig in enumerate(gigs[:5]):  # Limit to first 5 gigs
                    try:
                        link_elem = gig.find_element(By.TAG_NAME, "a")
                        link = link_elem.get_attribute("href")
                        if link:
                            links.append(link)
                            print(f"Found gig {i+1} link: {link}")
                    except:
                        print(f"No link found for gig {i+1}")
                break
        except:
            continue

    if not links:
        print("No gigs found. Checking page source...")
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Page source saved to page_source.html for debugging")
        all_links = driver.find_elements(By.TAG_NAME, "a")
        print(f"Total links on page: {len(all_links)}")
        for i, link_elem in enumerate(all_links[:5]):
            link = link_elem.get_attribute("href")
            if link:
                links.append(link)
                print(f"Found link {i+1}: {link}")

    # Scrape details for each link
    for i, link in enumerate(links):
        print(f"\nProcessing gig {i+1}...")
        details = scrape_gig_details(driver, link)
        print(f"Title: {details['title']}")
        print(f"Price: {details['price']}")
        print(f"Rating: {details['rating']}")
        print(f"Link: {details['link']}")
        print("-" * 50)

except Exception as e:
    print(f"Error during scraping: {e}")
    try:
        driver.save_screenshot("error_screenshot.png")
        print("Screenshot saved as error_screenshot.png")
    except:
        pass
finally:
    driver.quit()