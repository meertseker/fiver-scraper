from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys

# Set up Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Initialize the driver with better error handling
try:
    # Try to use webdriver-manager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
except Exception as e:
    print(f"Error with ChromeDriverManager: {e}")
    print("Trying alternative method...")
    
    try:
        # Try without service parameter (will look for chromedriver in PATH)
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e2:
        print(f"Error: {e2}")
        print("\nPlease ensure Chrome browser is installed and try one of these solutions:")
        print("1. Download ChromeDriver manually from https://chromedriver.chromium.org/")
        print("2. Place chromedriver.exe in the same directory as this script")
        print("3. Add chromedriver.exe to your system PATH")
        sys.exit(1)

url = "https://www.fiverr.com/search/gigs?query=website&source=top-bar&search_in=everywhere"

try:
    driver.get(url)
    
    # Wait for page to load
    print("Loading Fiverr search page...")
    time.sleep(5)
    
    # Accept cookies if the popup appears
    try:
        cookie_accept = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept")]')))
        cookie_accept.click()
        print("Accepted cookies")
    except:
        print("No cookie popup found or already accepted")
    
    # Additional wait for content
    time.sleep(3)
    
    # Debug: Print page title and check if we're on the right page
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
    
    gigs = []
    for selector in gig_selectors:
        try:
            gigs = driver.find_elements(By.CSS_SELECTOR, selector)
            if gigs:
                print(f"Found {len(gigs)} gigs using selector: {selector}")
                break
        except:
            continue
    
    if not gigs:
        print("No gigs found. Checking page source...")
        # Debug: Save page source for inspection
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Page source saved to page_source.html for debugging")
        
        # Try to find any links on the page
        all_links = driver.find_elements(By.TAG_NAME, "a")
        print(f"Total links on page: {len(all_links)}")
    
    # Process gigs if found
    for i, gig in enumerate(gigs[:5]):  # Just get first 5 gigs
        try:
            print(f"\nProcessing gig {i+1}...")
            
            # Try multiple selectors for title
            title = None
            title_selectors = [
                "a.gig-card-title",
                "h3 a",
                "a[class*='title']",
                ".gig-title",
                "h3",
                "a"
            ]
            
            for selector in title_selectors:
                try:
                    title_elem = gig.find_element(By.CSS_SELECTOR, selector)
                    title = title_elem.text
                    if title:
                        break
                except:
                    continue
            
            # Try to find price
            price = None
            price_selectors = [
                "div.price",
                "span.price",
                "[class*='price']",
                "footer span"
            ]
            
            for selector in price_selectors:
                try:
                    price_elem = gig.find_element(By.CSS_SELECTOR, selector)
                    price = price_elem.text
                    if price:
                        break
                except:
                    continue
            
            # Try to find rating
            rating = None
            rating_selectors = [
                "div.rating-wrapper",
                "[class*='rating']",
                "span.rating-score"
            ]
            
            for selector in rating_selectors:
                try:
                    rating_elem = gig.find_element(By.CSS_SELECTOR, selector)
                    rating = rating_elem.text
                    if rating:
                        break
                except:
                    continue
            
            # Try to find link
            link = None
            try:
                link_elem = gig.find_element(By.TAG_NAME, "a")
                link = link_elem.get_attribute("href")
            except:
                pass
            
            # Print whatever we found
            if title or price or rating or link:
                print(f"Title: {title if title else 'Not found'}")
                print(f"Price: {price if price else 'Not found'}")
                print(f"Rating: {rating if rating else 'Not found'}")
                print(f"Link: {link if link else 'Not found'}")
                print("-" * 50)
            else:
                print("Could not extract any information from this gig")
                
        except Exception as e:
            print(f"Error parsing gig {i+1}: {e}")
            continue
            
except Exception as e:
    print(f"Error during scraping: {e}")
    # Save screenshot for debugging
    try:
        driver.save_screenshot("error_screenshot.png")
        print("Screenshot saved as error_screenshot.png")
    except:
        pass
finally:
    driver.quit()