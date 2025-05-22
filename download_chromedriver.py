import requests
import zipfile
import os
import platform

def download_chromedriver():
    """Download ChromeDriver for Windows"""
    
    # Get the latest stable version
    version_url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
    response = requests.get(version_url)
    version = response.text.strip()
    
    print(f"Downloading ChromeDriver version: {version}")
    
    # Determine the correct file based on system
    system = platform.system()
    if system == "Windows":
        filename = "chromedriver_win32.zip"
    else:
        print("This script is designed for Windows. Please modify for other systems.")
        return
    
    # Download URL
    download_url = f"https://chromedriver.storage.googleapis.com/{version}/{filename}"
    
    # Download the file
    print(f"Downloading from: {download_url}")
    response = requests.get(download_url)
    
    # Save the zip file
    with open(filename, "wb") as f:
        f.write(response.content)
    
    # Extract the zip file
    print("Extracting ChromeDriver...")
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(".")
    
    # Remove the zip file
    os.remove(filename)
    
    print("ChromeDriver downloaded successfully!")
    print("chromedriver.exe is now in the current directory")
    print("You can now run your Selenium script.")

if __name__ == "__main__":
    try:
        download_chromedriver()
    except Exception as e:
        print(f"Error downloading ChromeDriver: {e}")
        print("Please download manually from https://chromedriver.chromium.org/") 