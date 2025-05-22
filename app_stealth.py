from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import os
import sys

# Set up Chrome options with better anti-detection
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--start-maximized")

# Initialize the driver
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
except Exception as e:
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except:
        print("Failed to initialize Chrome driver")
        sys.exit(1)

# Execute script to remove webdriver property
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

def human_like_delay(min_seconds=1, max_seconds=3):
    """Add random delay to simulate human behavior"""
    time.sleep(random.uniform(min_seconds, max_seconds))

url = "https://www.fiverr.com/search/gigs?query=website&source=top-bar&search_in=everywhere"

try:
    print("Opening Fiverr...")
    driver.get(url)
    
    # Wait for initial page load
    human_like_delay(3, 5)
    
    # Check if we need to handle any popups or captchas
    print(f"Page title: {driver.title}")
    
    # Handle cookie consent
    try:
        cookie_buttons = driver.find_elements(By.XPATH, "//button[contains(translate(., 'ACCEPT', 'accept'), 'accept')]")
        if cookie_buttons:
            cookie_buttons[0].click()
            print("Accepted cookies")
            human_like_delay()
    except:
        pass
    
    # Scroll down to trigger lazy loading
    print("Scrolling to load content...")
    driver.execute_script("window.scrollTo(0, 500);")
    human_like_delay(2, 3)
    
    # Wait for any dynamic content to load
    try:
        WebDriverWait(driver, 15).until(
            lambda driver: len(driver.find_elements(By.TAG_NAME, "article")) > 0 or
                         len(driver.find_elements(By.CSS_SELECTOR, "[class*='gig']")) > 0
        )
    except:
        print("Timeout waiting for content to load")
    
    # Try to find gigs with broader search
    print("Searching for gigs...")
    
    # Method 1: Find by article tags
    gigs = driver.find_elements(By.TAG_NAME, "article")
    
    # Method 2: If no articles, try divs with gig in class
    if not gigs:
        gigs = driver.find_elements(By.CSS_SELECTOR, "div[class*='gig-wrapper'], div[class*='gig-card']")
    
    # Method 3: Find by data attributes
    if not gigs:
        gigs = driver.find_elements(By.CSS_SELECTOR, "[data-gig-id], [data-impression-collected]")
    
    print(f"Found {len(gigs)} potential gig elements")
    
    if not gigs:
        # Save page source and screenshot for debugging
        with open("debug_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.save_screenshot("debug_screenshot.png")
        print("No gigs found. Debug files saved.")
        
        # Check if we're blocked
        if "captcha" in driver.page_source.lower() or "are you a robot" in driver.page_source.lower():
            print("Possible CAPTCHA detected. Manual intervention may be required.")
    
    # Process found gigs
    scraped_data = []
    for i, gig in enumerate(gigs[:10]):  # Process up to 10 gigs
        try:
            gig_data = {}
            
            # Scroll element into view
            driver.execute_script("arguments[0].scrollIntoView(true);", gig)
            human_like_delay(0.5, 1)
            
            # Extract text content
            gig_text = gig.text
            lines = gig_text.split('\n')
            
            # Try to parse the text content
            for line in lines:
                if line and len(line) > 10 and not line.startswith('From'):
                    if 'title' not in gig_data:
                        gig_data['title'] = line
                elif line.startswith('$') or line.startswith('From $'):
                    gig_data['price'] = line
                elif '(' in line and ')' in line and any(char.isdigit() for char in line):
                    gig_data['rating'] = line
            
            # Try to find link
            links = gig.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and "/gigs/" in href:
                    gig_data['link'] = href
                    break
            
            if gig_data:
                scraped_data.append(gig_data)
                print(f"\nGig {i+1}:")
                for key, value in gig_data.items():
                    print(f"  {key}: {value}")
                
        except Exception as e:
            print(f"Error processing gig {i+1}: {str(e)}")
            continue
    
    print(f"\nTotal gigs scraped: {len(scraped_data)}")
    
    # Save results to file
    if scraped_data:
        with open("fiverr_gigs.txt", "w", encoding="utf-8") as f:
            for i, gig in enumerate(scraped_data):
                f.write(f"Gig {i+1}:\n")
                for key, value in gig.items():
                    f.write(f"  {key}: {value}\n")
                f.write("-" * 50 + "\n")
        print("Results saved to fiverr_gigs.txt")
    
except Exception as e:
    print(f"Error during scraping: {e}")
    driver.save_screenshot("error_screenshot.png")
    print("Error screenshot saved")
finally:
    print("Closing browser...")
    driver.quit()