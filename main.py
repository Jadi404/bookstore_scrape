import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

BASE_URL = "https://books.toscrape.com/"

#Function gets a list of the genre names 
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


# function counts books in genre and the price
def count_books_in_genre(url):
    count = 0
    price = 0

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    books = soup.select("article.product_pod")
    count = len(books)

    for book in books:
        price_text = book.select_one(".price_color").text
        clean_price = float(''.join(c for c in price_text if c.isdigit() or c == '.'))
        price += clean_price

    return count, price


def scrape():
    genres = get_genres()
    data = []

    for genre, link in genres.items():
        total, price = count_books_in_genre(link)

        data.append({
            'Genre': genre,
            'Number of Books': total,
            'Price in Genre': round(price, 2)
        })

    df = pd.DataFrame(data)

    df = df.sort_values('Number of Books', ascending=False)

    most_popular = df.loc[df['Number of Books'].idxmax()]

    summary_row = pd.DataFrame({
        'Genre': [f"Most popular: {most_popular['Genre']}"],
        'Number of Books': [most_popular['Number of Books']],
        'Price in Genre': [most_popular['Price in Genre']]
    })

    df = pd.concat([df, summary_row], ignore_index=True)

    print("Writing to file...")

    df.to_excel(
        '/Users/macbookie/Desktop/output_data.xlsx',
        index=False,
        sheet_name='BookPopularity'
    )

    print("Done :)\n")


if __name__ == "__main__":
    scrape()