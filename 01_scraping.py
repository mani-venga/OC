import requests
from bs4 import BeautifulSoup
import csv

# Page a scrapper
url = "http://books.toscrape.com/catalogue/category/books/travel_2/index.html"
url_debut = "http://books.toscrape.com/catalogue"
csvFile = "fichier.csv"

# Recuperation des donnees de la page (url)
page = requests.get(url)
driver = BeautifulSoup(page.content, 'html.parser')

#<p class="price_color">£45.17</p>
# data[1].find('span', attrs={'class':'company-name'}).getText()
# data_soup.find_all(attrs={"data-foo": "value"})

pagesA = driver.find_all("h3")
url_fin = pagesA[0].find("a").get("href").split("..")[-1]
urlProduit = url_debut + url_fin

# Boucle qui va recuperer les donnees de chaque url
ma_liste = []
for link in pagesA :

    url_fin = link.find("a").get("href").split("..")[-1]
    urlProduit = url_debut + url_fin
    pageProduit = requests.get(urlProduit)
    driverProduit = BeautifulSoup(pageProduit.content, 'html.parser')

    ## donnees pour l'entete du csv -- Product Information 
    product_page_url = urlProduit
    upc =  driverProduit.table.find_all("td")[0].text
    price_excluding_tax = driverProduit.table.find_all("td")[2].text
    price_including_tax = driverProduit.table.find_all("td")[3].text

    title = driverProduit.h1.text
    lineDebut = driverProduit.find(attrs={'class':"instock availability"}).text.find("(") + 1 # Identifie ou se touve '(' 
    number_available = driverProduit.find(attrs={'class':"instock availability"}).text[lineDebut:].split(" ")[0] # Permet de recuprer le nombre de dispo


    # description du livre
    product_description = driverProduit.find(attrs={"id":"product_description"}).find_next_siblings("p")[0].text

    # Categorie
    category = driverProduit.find("ul").find_all("a")[-1].text

    # review star
    review_rating = driverProduit.find("p", attrs={"class":"star-rating"}).get("class")[1]

    # image_url
    image_url = driverProduit.find("img").get("src")

    # Ajout dans la liste, les donnees recoltes
    ma_liste.append([product_page_url, upc, title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, image_url] )


# Export en csv dans le dossier courant
with open(csvFile, "w", newline='',  ) as csvfile :
    entete = ['product_page_url', 'upc', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description', 'category', 'review_rating', 'image_url']
    ecrit = csv.DictWriter(csvfile, fieldnames=entete, delimiter=';')
    ecrit.writeheader()
    
    for liste in ma_liste :
        ecrit.writerow({"product_page_url" : liste[0], "upc" : liste[1], "title" : liste[2], "price_including_tax" : liste[3], "price_excluding_tax": liste[4], "number_available": liste[5], "product_description": liste[6], "category":liste[7], "review_rating":liste[8], "image_url":liste[9]})
    
    csvfile.close()


