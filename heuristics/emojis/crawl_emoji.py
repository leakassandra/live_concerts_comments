"""
Script to crawl data from a github page from a study "Face-Emoji Data" to later be used for analyzing data.
Data stored in `crawled_data.csv`.
"""
import requests
from bs4 import BeautifulSoup
import csv

# request the target website
response = requests.get("https://tscheffler.github.io/2024-Face-Emoji-Norming/ratings.html")

# get the response HTML
if response.status_code != 200:
    print(f"An error occured with status code {response.status_code}")
else:
    content = response.text
    
    # parse the HTML content of the page
    soup = BeautifulSoup(response.content, "html.parser")
    prettified_html = soup.prettify()

    # Find all th tags inside the table header
    ths = soup.select("table#rating-table thead th")

    # Extract text and strip whitespace/newlines
    header_texts = [th.get_text(strip=True) for th in ths]
    # Select all rows inside tbody
    rows = soup.select("table#rating-table tbody tr")
    
    with open("emojis/crawled_data.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(header_texts)

        for row in rows:
        # Extract all td elements
            tds = row.find_all("td")
        
            # For each td, get the text content, stripping whitespace
            # For the first td, the text is inside the <a> tag, but get_text() works anyway
            row_data = [td.get_text(strip=True) for td in tds]
        
            writer.writerow(row_data)
    
    """ with open("emojis/scraped.html", "a") as f:
        f.write(results) """