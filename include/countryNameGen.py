# Run this file for some time if you want some new names for your nations.
# New names will be placed on ../data/kingdomNames.txt

from requests_html import HTMLSession
names = open("../data/kingdomNames.txt", "a")
session = HTMLSession()

def get10CountryNames():

    #define our URL
    url = 'https://www.fantasynamegenerators.com/kingdom-names.php'

    #use the session to get the data
    r = session.get(url)

    #Render the page, up the number on scrolldown to page down multiple times on a page
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

while True:
    print(get10CountryNames())
