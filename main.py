import requests
from bs4 import BeautifulSoup

url = input("URL: ")

html = requests.get(url).text
soup = BeautifulSoup(html, "html.parser")

for script in soup(["script","style"]):
    script.decompose()

text = soup.get_text()

lines = (line.strip() for line in text.splitlines())
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
text = '\n'.join(chunk for chunk in chunks if chunk)

print(text[:4000])

