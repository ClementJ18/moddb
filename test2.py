import cloudscraper
scraper = cloudscraper.create_scraper()
r = scraper.get("https://www.moddb.com/members/login")
print(r.status_code)
