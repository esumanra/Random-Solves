from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup

# specify the URL of the archive here
archive_url = "https://robintrajano.com/koenigsegg/"

def get_image_links():
    # create response object
    html = urlopen(archive_url).read()

    # create beautiful-soup object
    soup = BeautifulSoup(html, 'html.parser')
    img_tags = soup('img')
    # find all links on web-page
    links = []
    for tag in img_tags:
        # Look at the parts of a tag
        links.append(tag.get("data-src")+'?format=2500w')
    print(links)

    return links

def download_images(img_links):
    link = 1
    for image_url in img_links:
        img_data = requests.get(image_url).content
        with open(str(link)+'.jpg', 'wb') as handler:
            handler.write(img_data)
        link += 1

if __name__ == "__main__":
    links = get_image_links()
    download_images(links)
