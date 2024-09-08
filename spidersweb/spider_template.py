# spider_template.py

SPIDER_TEMPLATE = """
import scrapy
from scrapy.http import HtmlResponse
from scrapy.exceptions import DropItem, CloseSpider
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from database_utils.database_utils import fetch_website_url, fetch_record_data, update_record

class {spider_class_name}(scrapy.Spider):
    name = "{spider_name}"
    city = "{city}"
    state_id = "{state_id}"

    def __init__(self, *args, **kwargs):
        super({spider_class_name}, self).__init__(*args, **kwargs)
        self.webdriver_path = "/usr/local/bin/chromedriver"
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1920x1080')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36')
        
        self.driver = webdriver.Chrome(service=Service(self.webdriver_path), options=self.options)

        # Define XPaths
        self.xpaths = {xpaths}

    {scrapy_start_requests_function}
    {scrapy_parse_function}
"""

scrapy_start_requests_function =  """def start_requests(self):
        url = fetch_website_url(self.city, self.state_id)
        
        if url:
            self.driver.get(url)
            self.driver.implicitly_wait(30)  # Wait for elements to load

            extracted_data = {}
            for xpath_dict in self.xpaths:
                for field_name, xpath in xpath_dict.items():
                    try:
                        WebDriverWait(self.driver, 30).until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )
                        
                        if "email" in field_name.lower():
                            # Try to extract email using "mailto:" link if available
                            mailto_element = element.get_attribute("href") if element else None
                            if mailto_element and "mailto:" in mailto_element:
                                extracted_data[field_name] = mailto_element.replace("mailto:", "")
                            else:
                                # Fallback to the text if "tel:" link is not available
                                extracted_data[field_name] = element.text if element else None

                        elif any(keyword in field_name.lower() for keyword in ["tel", "phone"]):
                            # Try to extract telephone number using "tel:" link if available
                            tel_element = element.get_attribute("href") if element else None
                            if tel_element and "tel:" in tel_element:
                                extracted_data[field_name] = tel_element.replace("tel:", "")
                            else:
                                # Fallback to the text if "tel:" link is not available
                                extracted_data[field_name] = element.text if element else None

                        else:
                            # Directly extract the text for the name
                            extracted_data[field_name] = element.text if element else None

                    except Exception as e:
                        self.log(f"Element not found for XPath: {xpath}. Error: {e}", level=logging.WARNING)
                        extracted_data[field_name] = None  # Log missing elements as None

            if not any(extracted_data.values()):
                self.log("No elements were extracted.", level=logging.ERROR)
                raise CloseSpider(reason="No elements found with the given XPaths.")

            # Get the page source and create a Scrapy response
            page_source = self.driver.page_source
            scrapy_response = HtmlResponse(url=url, body=page_source, encoding='utf-8')

            # Proceed with parsing if the response is valid
            if scrapy_response is not None:
                self.parse(scrapy_response, extracted_data)
            else:
                self.log("scrapy_response is None, skipping parse.", level=logging.ERROR)
        else:
            self.log(f"No URL found for {self.city}, {self.state_id} in the database.", level=logging.ERROR)
            raise CloseSpider(reason=f"No website URL found for {self.city}, {self.state_id} in the database.")"""

scrapy_parse_function = """def parse(self, response, extracted_data):
        
        for field in list(extracted_data.keys()):  # Convert to list to avoid runtime error due to dict size change
            value = extracted_data[field]
            if not value:
                self.log(f"No {field.replace('_', ' ').title()} found on the page.", level=logging.WARNING)
                del extracted_data[field]  # Remove the key-value pair from the dictionary
        
        # Check if extracted_data is empty after filtering out missing values
        if not extracted_data:
            raise CloseSpider(reason="No valid data found on the page.")
        
        # Log extracted values
        for field, value in extracted_data.items():
            self.log(f"Scraped {field.replace('_', ' ').title()}: {value}", level=logging.INFO)

        # Fetch the current record data from the database
        record = fetch_record_data(response.url)
        if record:
            # Log Current values
            for field, value in record.items():
                self.log(f"Current Record {field.replace('_', ' ').title()}: {value}", level=logging.INFO)
            updates = [(extracted_data[key], key) for key in extracted_data if extracted_data[key] != record.get(key)]

            if updates:
                try:
                    update_record(response.url, updates)
                    for value, field in updates:
                        self.log(f"{field.replace('_', ' ').title()} updated for {response.url}: {value}", level=logging.INFO)
                except Exception as e:
                    self.log(f"Failed to update record: {e}", level=logging.ERROR)
            else:
                self.log(f"No changes detected for {response.url}", level=logging.INFO)
        else:
            self.log("Record not found in the database. Please check the website URL in the database.", level=logging.ERROR)
            raise DropItem("Record not found in the database. Please check the website URL in the database.")"""



PARSE_FUNCTION_STRING = """def parse(self, response, extracted_data):
    print(extracted_data)
    print('***END**')

    for field in list(extracted_data.keys()):
        value = extracted_data[field]
        if not value:
            self.log(f"No {field.replace('_', ' ').title()} found on the page.", level=logging.WARNING)
            del extracted_data[field]
    
    if not extracted_data:
        raise CloseSpider(reason="No valid data found on the page.")
    
    for field, value in extracted_data.items():
        self.log(f"Scraped {field.replace('_', ' ').title()}: {value}", level=logging.INFO)

    record = fetch_record_data(response.url)
    if record:
        for field, value in record.items():
            self.log(f"Current Record {field.replace('_', ' ').title()}: {value}", level=logging.INFO)

        updates = [(extracted_data[key], key) for key in extracted_data if extracted_data[key] != record.get(key)]

        if updates:
            try:
                update_record(response.url, updates)
                for value, field in updates:
                    self.log(f"{field.replace('_', ' ').title()} updated for {response.url}: {value}", level=logging.INFO)
            except Exception as e:
                self.log(f"Failed to update record: {e}", level=logging.ERROR)
        else:
            self.log(f"No changes detected for {response.url}", level=logging.INFO)
    else:
        self.log("Record not found in the database. Please check the website URL in the database.", level=logging.ERROR)
        raise DropItem("Record not found in the database. Please check the website URL in the database.")
"""
