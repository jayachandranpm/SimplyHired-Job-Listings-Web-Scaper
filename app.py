import csv
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from time import sleep

# Initialize the Chrome WebDriver using ChromeDriverManager
service = Service(ChromeDriverManager().install())
driver = Chrome(service=service)

# URL of the webpage to scrape
url = "https://www.simplyhired.com/search?q=data+scientist&l="

# Open the URL in the WebDriver
driver.get(url)

# Wait for job listings to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@class='chakra-button css-1djbb1k']")))

# Create a CSV file and write headers
csv_file = open('Job_Postings.csv', 'w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Job Title', 'Company', 'Location', 'Job Posting Time', 'Preferred Qualifications', 'Company Logo', 'Job Description', 'Application Link'])

# Scrape job listings from multiple pages
total_listings = 100  # Total number of job listings to scrape
listings_per_page = 20  # Number of listings per page
pages_to_scrape = total_listings // listings_per_page  # Calculate number of pages to scrape

for page in range(2, pages_to_scrape + 2):  # Start from 2 because the first page is already loaded
    # Click the pagination block for the current page
    pagination_block = driver.find_element(By.XPATH, f"//a[contains(@data-testid,'paginationBlock{page}')]") 
    pagination_block.click()
    sleep(3)  # Wait for the new page to load

    # Get all job title links on the current page
    job_title_links = driver.find_elements(By.XPATH, "//a[@class='chakra-button css-1djbb1k']")

    # Extract details for the job listings on the current page
    for idx, job_title_link in enumerate(job_title_links, start=1):
        # Get the URL of the job listing
        job_url = job_title_link.get_attribute('href')
        
        # Get the application link
        application_link = job_title_link.get_attribute('href')
        
        # Open the job listing URL in a new tab using JavaScript
        driver.execute_script(f"window.open('{job_url}', '_blank');")
        
        # Switch to the newly opened tab by iterating through window handles
        driver.switch_to.window(driver.window_handles[-1])
        
        # Wait for the new page to load
        sleep(3)  # Adjust the sleep duration as needed or use WebDriverWait
        
        try:
            # Refresh the element references to handle StaleElementReferenceException
            job_title_link = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//h1")))
            
            # Extract job details
            company_name_element = driver.find_element(By.XPATH, "//span[@data-testid='detailText']")
            location_element = driver.find_element(By.XPATH, "//span[@data-testid='viewJobQualificationItem']")
            job_description_element = driver.find_element(By.XPATH, "//div[@class='css-cxpe4v']")
            posting_time_element = driver.find_element(By.XPATH, "//span[contains(@data-testid,'viewJobBodyJobPostingTimestamp')]")
            
            company_name = company_name_element.text.strip() if company_name_element else "N/A"
            location = location_element.text.strip() if location_element else "N/A"
            job_description = job_description_element.text.strip() if job_description_element else "N/A"
            posting_time = posting_time_element.text.strip() if posting_time_element else "N/A"
            
            # Extract preferred qualifications
            preferred_qualifications_elements = driver.find_elements(By.XPATH, "//ul[@class='chakra-wrap__list css-19lo6pj']//li[@class='chakra-wrap__listitem css-1yp4ln']")
            preferred_qualifications = [element.text.strip() for element in preferred_qualifications_elements]
            
            # Extract company logo or set to "NA" if not available
            company_logo_elements = driver.find_elements(By.XPATH, "//img[@class='chakra-image css-sm43lu']")
            company_logo = company_logo_elements[0].get_attribute('src') if company_logo_elements else "NA"
            
            # Write the details to the CSV file
            csv_writer.writerow([job_title_link.text.strip(), company_name, location, posting_time, ', '.join(preferred_qualifications), company_logo, job_description, application_link])
            
        except StaleElementReferenceException:
            print(f"Error processing job {idx + (page - 2) * listings_per_page}: StaleElementReferenceException occurred. Refreshing element references.")
            # You can add code here to refresh element references or handle this exception as needed
        except Exception as e:
            print(f"Error processing job {idx + (page - 2) * listings_per_page}: {str(e)}")
        
        # Close the tab
        driver.close()
        
        # Switch back to the main tab
        driver.switch_to.window(driver.window_handles[0])

# Close the CSV file
csv_file.close()

# Close the WebDriver
driver.quit()
