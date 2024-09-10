import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
from .spider_template import SPIDER_TEMPLATE, scrapy_parse_function,scrapy_start_requests_function
import os
import re
from .utils import extract_phone_numbers, extract_email


class ScrapingService:
    def __init__(self, city, state_id, website, xpaths):
        self.city = city
        self.state_id = state_id
        self.website = website
        self.xpaths = xpaths  # List of dictionaries containing XPaths and field names

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def getData(self):
        # Set up Selenium WebDriver
        webdriver_path = "/usr/local/bin/chromedriver"  # Update path if needed
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run Chrome in headless mode (without a GUI)
        options.add_argument('--disable-gpu')  # Disable GPU acceleration
        options.add_argument('--window-size=1920x1080')  # Set a window size
        options.add_argument('--no-sandbox')  # Bypass OS security model
        options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36')  # Set user agent
        
        driver = webdriver.Chrome(service=Service(webdriver_path), options=options)

        # Fetch the URL
        self.logger.info(f"Fetching URL: {self.website}")
        driver.get(self.website)
        driver.implicitly_wait(30)
        page_source = driver.page_source
        scrapy_response = HtmlResponse(url=self.website, body=page_source, encoding='utf-8')

        extracted_data = {}
        for xpath_dict in self.xpaths:
            for field_name, xpath in xpath_dict.items():
                try:
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    element = driver.find_element(By.XPATH, xpath)
                    extracted_data[field_name] = element.text if element else None

                    if "email" in field_name.lower():
                        
                        # Try to extract email using "mailto:" link if available
                        mailto_element = element.get_attribute("href") if element else None
                        if mailto_element and "mailto:" in mailto_element:
                            extracted_data[field_name] = mailto_element.replace("mailto:", "")
                        else:
                            # Fallback to the text if "tel:" link is not available
                            extracted_data[field_name] = element.text if element else None
                            
                        
                        if extracted_data[field_name] :
                            email_addresses = extract_email(extracted_data[field_name])

                            if email_addresses:
                                    extracted_data[field_name] = email_addresses[0]


                    elif any(keyword in field_name.lower() for keyword in ["tel", "phone"]):
                        # Try to extract telephone number using "tel:" link if available
                        tel_element = element.get_attribute("href") if element else None
                        if tel_element and "tel:" in tel_element:
                            extracted_data[field_name] = tel_element.replace("tel:", "")
                        else:
                            # Fallback to the text if "tel:" link is not available
                            extracted_data[field_name] = element.text if element else None


                            phone_numbers = extract_phone_numbers(extracted_data[field_name])

                            if extracted_data[field_name]:
                                phone_numbers = extract_phone_numbers(extracted_data[field_name])

                                if phone_numbers:
                                        extracted_data[field_name] = phone_numbers[0]


                    else:
                        # Directly extract the text for the name
                        extracted_data[field_name] = element.text if element else None

                except Exception as e:
                    self.logger.warning(f"Element not found for XPath: {xpath}. Error: {e}")
                    extracted_data[field_name] = None  # Log missing elements as None

        driver.quit()

        # Print the extracted data
        self.logger.info("Extracted Data:")
        self.logger.info(extracted_data)
        return extracted_data






class SpiderFileService:
    def __init__(self, city, state_id, website_url, xpaths):
        self.city = city
        self.state_id = state_id
        self.website_url = website_url
        self.xpaths = xpaths
        self.spider_class_name, self.spider_name = self.generate_spider_names(self.city, self.state_id)

        self.spider_dir = os.path.join('spiders','generated_spiders')
        os.makedirs(self.spider_dir, exist_ok=True)

    def spider_file_path(self):
        return os.path.join(self.spider_dir, f'{self.spider_name}.py')

    def spider_exists(self):
        return os.path.exists(self.spider_file_path())

    def generate_spider_content(self):

        xpath_dict = [
            {"building_department_main_phone": self.xpaths['building_department_main_phone']},
            {"building_department_main_email":self.xpaths['building_department_main_email']},
            {"municipality_main_tel":self.xpaths['municipality_main_tel']},
            {"chief_building_official_name":self.xpaths['chief_building_official_name']}
        ]


        
        return SPIDER_TEMPLATE.format(city=self.city,
                                      state_id=self.state_id, 
                                      xpaths=xpath_dict,
                                      scrapy_start_requests_function = scrapy_start_requests_function,
                                      scrapy_parse_function = scrapy_parse_function,
                                      spider_class_name = self.spider_class_name,
                                      spider_name = self.spider_name
                                      )

    def save_spider_file(self):
        spider_content = self.generate_spider_content()
        with open(self.spider_file_path(), 'w') as file:
            file.write(spider_content)

    def create_or_update_spider(self):
        if self.spider_exists():
            print(f'Spider for {self.city}, {self.state_id} already exists. Updating the file...')
        else:
            print(f'Creating new spider for {self.city}, {self.state_id}...')
        
        self.save_spider_file()
        print(f'Spider file for {self.city}, {self.state_id} has been generated/updated at {self.spider_file_path()}.')

    def to_upper_camel_case(self, s):
        # Capitalize each word and remove spaces
        return ''.join(word.capitalize() for word in s.split())

    def to_snake_case(self,s):
        # Replace spaces with underscores and convert to uppercase
        return re.sub(r'\s+', '_', s).upper()

    def generate_spider_names(self, city, state_id):
        # Convert to proper case
        city_ucwords = self.to_upper_camel_case(city)
        state_ucwords = self.to_upper_camel_case(state_id)
        
        # Generate spider class name
        spider_class_name = f"{city_ucwords}{state_ucwords}Spider"
        
        # Generate spider name
        city_snake = self.to_snake_case(city)
        state_snake = self.to_snake_case(state_id)
        spider_name = f"{city_snake}_{state_snake}_SPIDER"
        
        return spider_class_name, spider_name

