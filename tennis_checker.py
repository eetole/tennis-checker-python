"""
Tennis Court Availability Checker for Tampereen Tenniskeskus
Uses Selenium to parse the booking page and find available slots
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
from typing import List, Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env


class TennisSlotChecker:
    def __init__(self, headless: bool = True):
        """
        Initialize the checker with Selenium

        Args:
            headless: Run browser in headless mode (no GUI)
        """
        self.url = "https://tampereentenniskeskus.cintoia.com/"
        self.driver = None
        self.headless = headless

    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # For M1/M2 Macs, we need to ensure we're using the correct architecture
        chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        
        try:
            # First try with the latest ChromeDriver version that matches Chrome 141
            driver_manager = ChromeDriverManager().install()
            service = Service(executable_path=driver_manager)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
        except Exception as e:
            print(f"Error setting up ChromeDriver: {str(e)}")
            print("Trying alternative installation method...")
            try:
                # Fallback to automatic installation
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.implicitly_wait(10)
            except Exception as e2:
                print(f"Alternative method failed: {str(e2)}")
                print("\nTroubleshooting steps:")
                print("1. Make sure Chrome browser is installed at /Applications/Google Chrome.app/")
                print("2. Try running: brew install --cask chromedriver")
                print("3. Or download ChromeDriver manually from: https://chromedriver.chromium.org/downloads")
                print("   - Make sure to download the version that matches your Chrome browser version (141.x.x.x)")
                print("   - Place the chromedriver binary in your PATH or in the project directory")
                raise

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

    def get_available_slots(self, days_ahead: int = 1) -> List[Dict]:
        """
        Get available tennis court slots

        Args:
            days_ahead: Number of days to check ahead

        Returns:
            List of available slots with details
        """
        all_slots = []

        try:
            print("Opening website...")
            self.driver.get(self.url)

            # Wait for page to load
            print("Waiting for page to load...")
            time.sleep(5)

            # Try to find and click booking/calendar button
            self._navigate_to_booking()

            # Check slots for each day
            for day_offset in range(days_ahead):
                check_date = datetime.now() + timedelta(days=day_offset)
                date_str = check_date.strftime('%Y-%m-%d')
                day_name = check_date.strftime('%A')

                print(f"\nChecking {day_name}, {date_str}...")

                try:
                    slots = self._parse_current_view(date_str)
                    all_slots.extend(slots)

                    # Try to navigate to next day
                    if day_offset < days_ahead - 1:
                        self._go_to_next_day()
                        time.sleep(2)

                except Exception as e:
                    print(f"Error checking {date_str}: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error during slot checking: {str(e)}")

        return all_slots

    def _navigate_to_booking(self):
        """Navigate to the booking section"""
        try:
            # Common button texts in Finnish
            possible_buttons = [
                "Varaa", "Varaukset", "Ajanvaraus", "Booking",
                "Varaa kenttä", "Kentänvaraus"
            ]

            for button_text in possible_buttons:
                try:
                    button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{button_text}')]"))
                    )
                    button.click()
                    print(f"Clicked '{button_text}' button")
                    time.sleep(3)
                    return
                except:
                    continue

            print("Could not find booking button, proceeding with current page...")

        except Exception as e:
            print(f"Navigation warning: {str(e)}")

    def _parse_current_view(self, date: str) -> List[Dict]:
        """Parse the current view for available slots"""
        slots = []

        try:
            # Get page source for debugging
            page_source = self.driver.page_source

            #print(page_source)

            # Look for common booking slot indicators
            # These are common patterns in booking systems

            # Try to find time slots
            # time_slots = self.driver.find_elements(By.CSS_SELECTOR,
            #                                        "[class*='slot'], [class*='time'], [class*='available'], [class*='free']")
            #
            # if not time_slots:
            #     # Try alternative selectors
            #     time_slots = self.driver.find_elements(By.CSS_SELECTOR,
            #                                            "button[class*='book'], div[class*='calendar'], td[class*='cell']")
            #
            # if not time_slots:
                # Try alternative selectors
                # time_slots = self.driver.find_elements(By.XPATH,
                #                                        "//b[contains(text(), '19:30')]")

            week_times = [
                "16:00",
                "16:30",
                "17:00",
                "17:30",
                "18:00",
                "18:30",
                "19:00"]
            weekend_times = [
                "10:00",
                "10:30",
                "11:00",
                "11:30",
                "12:00",
                "12:30",
                "13:00",
                "13:30",
                "14:00",
                "14:30",
                "15:00",
                "15:30",
                "16:00",
                "16:30",
                "17:00",
                "17:30",
                "18:00",
                "18:30",
                "19:00"]

            if datetime.now().weekday() < 5:
                times = week_times
            else:
                times = weekend_times

            xpath = " or ".join([f"contains(text(), '{t}')" for t in times])
            # print(xpath)
            time_slots = self.driver.find_elements("xpath", f"//b[{xpath}]")


            for slot_element in time_slots:
                try:
                    # Check if slot appears to be available
                    classes = slot_element.get_attribute('class') or ''
                    is_available = any(word in classes.lower() for word in
                                       ['available', 'free', 'open', 'vapaana'])
                    is_booked = any(word in classes.lower() for word in
                                    ['booked', 'occupied', 'varattu', 'disabled'])

                    if not is_booked and (is_available or not classes):
                        text = slot_element.text.strip()

                        if text and len(text) > 0:
                            slots.append({
                                'date': date,
                                'text': text,
                                'element_type': slot_element.tag_name,
                                'classes': classes
                            })

                except Exception as e:
                    continue

            # Also try to find any table-based calendar structure
            calendar_cells = self.driver.find_elements(By.CSS_SELECTOR,
                                                       "table td, [role='gridcell']")

            for cell in calendar_cells:
                try:
                    text = cell.text.strip()
                    aria_label = cell.get_attribute('aria-label') or ''

                    if text or aria_label:
                        # Check if it looks like a time or available slot
                        if any(char.isdigit() for char in text) or 'available' in aria_label.lower():
                            slots.append({
                                'date': date,
                                'text': text or aria_label,
                                'element_type': 'calendar_cell'
                            })
                except:
                    continue

        except Exception as e:
            print(f"Error parsing view: {str(e)}")

        return slots

    def _go_to_next_day(self):
        """Click next day button"""
        try:
            # Common next/forward button indicators
            next_buttons = [
                "//button[contains(@class, 'next')]",
                "//button[contains(@aria-label, 'next')]",
                "//button[contains(text(), '→')]",
                "//button[contains(text(), '>')]",
                "//*[contains(@class, 'arrow-right')]",
                "//*[contains(@class, 'next-day')]"
            ]

            for xpath in next_buttons:
                try:
                    button = self.driver.find_element(By.XPATH, xpath)
                    button.click()
                    return
                except:
                    continue

        except Exception as e:
            print(f"Could not navigate to next day: {str(e)}")

    def display_slots(self, slots: List[Dict]):
        """Display available slots in a readable format"""
        if not slots:
            print("\n❌ No available slots found.")
            print("\n💡 Tips:")
            print("   - The page structure might have changed")
            print("   - Try running with headless=False to see what's happening")
            print("   - Check if you need to select a specific sport/facility first")
            return

        print(f"\n{'='*70}")
        print(f"Found {len(slots)} potential available slots:")
        print(f"{'='*70}")

        # Group by date
        by_date = {}
        body = ""
        for slot in slots:
            date = slot['date']
            if date not in by_date:
                by_date[date] = []
            by_date[date].append(slot)

        for date in sorted(by_date.keys()):
            try:
                day_name = datetime.strptime(date, '%Y-%m-%d').strftime('%A')
                body += f"\n📅 {date} ({day_name})\n"
            except:
                body += f"\n📅 {date}\n"
            body += "-" * 70 + "\n"

            for slot in by_date[date]:
                text = slot.get('text', 'N/A')
                elem_type = slot.get('element_type', 'unknown')
                body += f"  🎾 {text} [{elem_type}]\n"

        print(body)
        send_email("Tenniskenttä vapaana", body, 'toni.leppakangas@gmail.com')


    def save_page_screenshot(self, filename: str = "booking_page.png"):
        """Save screenshot for debugging"""
        try:
            self.driver.save_screenshot(filename)
            print(f"Screenshot saved to {filename}")
        except Exception as e:
            print(f"Could not save screenshot: {str(e)}")


def send_email(subject, body, to_email):
    # Set up the MIME
    message = MIMEMultipart()
    message['From'] = os.getenv('EMAIL_ADDRESS')
    message['To'] = 'toni.leppakangas@gmail.com'
    message['Subject'] = 'Tenniskenttä vapaana'

    # Add body to email
    message.attach(MIMEText(body, 'plain'))

    # Log in to server and send email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Secure the connection
            server.login(os.getenv('EMAIL_ADDRESS'), os.getenv('EMAIL_PASSWORD'))
            server.send_message(message)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def main():
    """Main function to run the checker"""
    print("🎾 Tennis Court Availability Checker (Selenium)")
    print("=" * 70)

    # Set to False to see the browser window
    checker = TennisSlotChecker(headless=True)

    try:
        checker.setup_driver()

        print("\nSearching for available slots...")
        print("(This may take a minute...)\n")

        slots = checker.get_available_slots(days_ahead=7)
        checker.display_slots(slots)

        # Optionally save screenshot for debugging
        # checker.save_page_screenshot()

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure Chrome browser is installed")
        print("2. Try running with headless=False to see what's happening")
        print("3. The website structure may have changed")

    finally:
        checker.close()
        print("\n✅ Done!")


if __name__ == "__main__":
    main()