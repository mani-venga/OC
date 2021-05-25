import requests
import csv
from os import path, mkdir
from bs4 import BeautifulSoup


# Page a scrapper
url = "http://books.toscrape.com/catalogue/category/books_1/index.html"
url_debut = "http://books.toscrape.com/catalogue"
urlImage_debut = "http://books.toscrape.com"


# Verifie qu'un dossier img est present, si oui le créé 
dossierImg = "dossierImg"
if path.isdir(dossierImg) :
    print("Le repertoire d'image existe deja, pas besoin de le creer.")
else :
    mkdir(dossierImg)
    print("Le repertoire image vient d'etre cree.")


# Recuperation des donnees de la page (url)
page = requests.get(url)
driver = BeautifulSoup(page.content, 'html.parser')



# cree un dict contenant pour chaque categorie, son emplacement url
dict_cat = {}
for categorie in driver.find_all("ul")[1].find_all("a") :
    
    cat_lien = categorie.get("href").replace("..",'')
    cat_lien = url_debut + "/category" + cat_lien
    cat_nom = categorie.text.split("\n")[2].strip()

    # si aucun nom n'est renseigne, on passe (generalement pour la 1er etape qui contient un vide)
    if cat_nom == '' :
        continue

    dict_cat[cat_nom] = cat_lien


for dictName, dictUrl in dict_cat.items() :
    print("Voici le nom : " + dictName + " et son Url : " + dictUrl)

    # On se connecte a la nouvelle page
    dictPage = requests.get(dictUrl)
    dictDriver = BeautifulSoup(dictPage.content, 'html.parser')
    csvFile = dictName + ".csv"

    # On recupere toutes les infos (url ) de chaque livre
    pagesA = dictDriver.find_all("h3")

    # Verification si plusieurs page d'une meme categorie existe
    nextPage = dictDriver.find_all("a")[-1]
    while nextPage.text == "next" :
        print("il existe une page supplemntaire")        
        # nextPage.get("href") => 'next'
        # remplace le dernier mot par le lien next
        dictUrl2 = dictUrl.replace(dictUrl.split("/")[-1],nextPage.get("href"))
        dictPage = requests.get(dictUrl2)
        dictDriver = BeautifulSoup(dictPage.content, 'html.parser')
        pagesA.extend(dictDriver.find_all("h3"))

        # reverification d'une page supplementaire
        nextPage = dictDriver.find_all("a")[-1]

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
        try : 
            product_description = driverProduit.find(attrs={"id":"product_description"}).find_next_siblings("p")[0].text
        except AttributeError :
            print("Pas de description")
            product_description = "..."


        # Categorie
        category = driverProduit.find("ul").find_all("a")[-1].text

        # review star
        review_rating = driverProduit.find("p", attrs={"class":"star-rating"}).get("class")[1]

        # image_url
        image_url = driverProduit.find("img").get("src").split("..")[-1]
        image_url = urlImage_debut + image_url
        

        # Ajout dans la liste, les donnees recoltes
        ma_liste.append([product_page_url, upc, title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, image_url, photo] )


    # Export en csv dans le dossier courant
    with open(csvFile, "w", newline='', encoding="utf-8" ) as csvfile :
        entete = ['product_page_url', 'upc', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description', 'category', 'review_rating', 'image_url',]
        ecrit = csv.DictWriter(csvfile, fieldnames=entete, delimiter=';')
        ecrit.writeheader()
        
        for liste in ma_liste :
            ecrit.writerow({"product_page_url" : liste[0], "upc" : liste[1], "title" : liste[2], "price_including_tax" : liste[3], "price_excluding_tax": liste[4], "number_available": liste[5], "product_description": liste[6], "category":liste[7], "review_rating":liste[8], "image_url":liste[9]})

            # cree un repertoire de categorie dans image
            catDossier = dossierImg + "/" + dictName.replace(" ","_")[:10]
            if not path.isdir(catDossier)    :
                mkdir(catDossier)
            # Telecharge les images par categorie
            titreFichier = liste[2].replace('[A-Za-z0-9]+', '')
            titreFichier = titreFichier.replace("?","")
            titreFichier = titreFichier.replace(":",".")
            titreFichier = titreFichier.replace("!",".")
            titreFichier = titreFichier.replace(";",".")
            titreFichier = titreFichier.replace(",",".")
            titreFichier = titreFichier.replace("/",".")
            titreFichier = titreFichier.replace('"',".")
            titreFichier = titreFichier.replace("'",".")
            with open( catDossier + "/" + titreFichier[:10] + ".jpg", "wb") as f :
                photo = requests.get(liste[9])
                f.write(photo.content)
                f.close()
        
        csvfile.close()

# ajouter le module dans requirements
# Ajouter dans le GIT HUB
# Tester dans un nouvel environnement
# Renommer le package pour OCR
