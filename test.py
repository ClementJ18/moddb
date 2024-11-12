import requests
import ssl

# Define a custom adapter that allows using an SSL context
class MySSLAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        # Create a custom SSL context to limit TLS to 1.2 (and therefore disable TLS 1.3)
        ssl_context = ssl.create_default_context()
        ssl_context.maximum_version = ssl.TLSVersion.TLSv1_2 
        
        kwargs["ssl_context"] = ssl_context
        return super().init_poolmanager(*args, **kwargs)

url = "https://www.moddb.com/members/login"
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:57.0) Gecko/20100101 Firefox/57.0',
}

session = requests.Session()
session.mount("https://", MySSLAdapter())

response = session.get(url, headers=headers)

print("Status Code:", response.status_code)
print("Response Text:", response.text[:500])