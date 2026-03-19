import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd


BASE_URL = "https://books.toscrape.com/"

#This function collects all the genres on the site then sorts through (strips) the html and returns solely the genre links.
def get_genres():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    genres = soup.select(".nav-list ul li a")

    genre_links = {}

    for genre in genres:
        name = genre.text.strip()
        link = urljoin(BASE_URL, genre["href"])
        genre_links[name] = link

    return genre_links

#This function counts how many books there are in each genre and returns that number. 
def count_books_in_genre(url):
    count = 0
    price = 0 

    while url:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        books = soup.select("article.product_pod")
        count += len(books)
        for book in books:
            price_text = book.select_one(".price_color").text
            clean_price = float(''.join(c for c in price_text if c.isdigit() or c =='.'))
            #HEREEEE

        next_button = soup.select_one("li.next a")

        if next_button:
            url = urljoin(url, next_button["href"])
        else:
            url = None

    return count, price 


def scrape():
    genres = get_genres()

    genre_counts = {}
    data = []

    for genre, link in genres.items():
        total, price = count_books_in_genre(link)
        genre_counts[genre] = total

        data.append({
            'Genre': genre,
            'Number of Books': total,
            'Price in Genre': price

        })

    df = pd.DataFrame(data)
    summary_row = pd.DataFrame({
        'Genre': ['Most popular'],
        'Number of Books': [df['Number of Books'].max()],
        'Price in Genre':['Price in Genre']
    })
    df = df.sort_values('Number of Books', ascending=False)
    df = pd.concat([df,summary_row],ignore_index=True)
    print("Writing to file...")
    df.to_excel(
        '/Users/macbookie/Desktop/output_data.xlsx',
        header=['Genre', 'Number of Books','Total price made in Genre'],
        index=False,
        sheet_name='BookPopularity'
    )
    print("Done :)\n")





if __name__ == "__main__":
    scrape()