from selenium import webdriver

# Example using Chrome WebDriver
driver = webdriver.Chrome()
driver.get("https://moddb.com")

# Interact with the page as needed
page_content = driver.page_source
print(page_content)

driver.quit()
