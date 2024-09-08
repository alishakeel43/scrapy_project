# Web Scraping Project with Django and Scrapy
Overview
This project is designed to provide a comprehensive web scraping solution using Django, Scrapy, and Selenium. It features a user-friendly interface for filling out a form to generate and manage Scrapy spiders dynamically. The solution fetches data from websites, allows users to confirm the data before storing it, and keeps track of XPaths and other configurations in the database.

# Features
1. **Dynamic Spider Creation**: Generate or update Scrapy spider files based on user-provided city and state IDs. The spiders are created from a template with dynamic XPath definitions.

2. **Interactive Data Confirmation**: After scraping data using Selenium, display the data on a webpage for user confirmation. If the user confirms the data, it is stored in the database.

3. **Form-Based Scraping:** Users can input details such as city, state ID, website URL, and XPaths through a form. The data is then fetched, confirmed, and stored as needed.

4. **Database Integration**: Store the scraped data and XPaths in the database for future reference and updates.

5. **Error Handling and Logging**: Includes robust logging and error handling to manage issues during the scraping process.

# Installation 

1. **Clone the Repository**

   git clone <repository-url>
   cd <repository-directory>

2. **Install Dependencies**

   pip install -r requirements.txt
   
3. **Setup Django Project**

   Configure settings.py for your database and other settings.
   Apply migrations:
   python manage.py migrate

4. **Configure Scrapy and Selenium**
   Install Scrapy and Selenium.
   Ensure Chromedriver is installed and properly configured. according to insatlled googlechrome version.
5. **Run the Django Development Server**
   python manage.py runserver

# Usage
# Create or Update a Spider
1. **Fill Out the Form**

   Navigate to the form page in your Django application. Enter the city, state ID, website URL, and XPaths.

   
2. **Data Scraping and Confirmation**

   **Fetch Data:** The system uses Selenium to scrape data from the provided URL based on the specified XPaths.
   **Confirm Data:** Review the scraped data on a confirmation page. Confirm if the data is correct.

3. **Submit Data**
   After confirming the data, submit the form to store it in the database. The system will generate or update the spider file according to the provided city and state ID.
