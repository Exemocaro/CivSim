# run this file for some time if you want some new names for your nations.
# run this file on this directory or it won't find the kingdomNames.txt file
# new names will be placed on ../data/kingdomNames.txt

from requests_html import HTMLSession
import os

def get10CountryNames(names, session):

    #define our URL
    url = 'https://www.fantasynamegenerators.com/kingdom-names.php'

    #use the session to get the data
    r = session.get(url)

    #render the page, up the number on scrolldown to page down multiple times on a page
    r.html.render(sleep=0.5, keep_page=True, scrolldown=1)

    #take the rendered html and find the element that we are interested in
    kingdomsWeird = r.html.find('#result')

    kingdoms = []

    #loop through those elements extracting the text and link
    for item in kingdomsWeird:
        kingdom = {
            'name': item.text,
            #'link': item.absolute_links
        }
        kingdoms = kingdom["name"]

    for k in kingdoms:
        #names.write(f"{k[0]}{k[1:]}")
        k = ''.join(k)
        names.write(k)
        #print(k[0])
    
    names.write('\n')

    return kingdoms

def main():

    namesDir = ["../data/kingdomNames.txt", "kingdomNames.txt"]
    fileOpening = ["a", "w"]
    selection = 0

    # check if the file exists before opening it, and changing the file location if it doesn't exist
    if not os.path.isfile(namesDir[selection]):
        print(f"\n{namesDir[selection]} not found! Will create a new file and change the directory from {namesDir[selection]} to {namesDir[selection + 1]}...")
        selection = 1
    with open(namesDir[selection], fileOpening[selection]) as names:
        session = HTMLSession()

        while True:
            print(get10CountryNames(names, session))

if __name__ == "__main__":
    main()
