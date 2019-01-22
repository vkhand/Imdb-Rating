import requests
import bs4
from lxml import html
import pandas as pd

url = 'https://www.imdb.com/chart/top?ref_=nv_mv_250'
headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'}
req = requests.get(url)
soup = bs4.BeautifulSoup(req.text,"html.parser")
containers = soup.find_all('td', class_ = 'titleColumn')
total_movies = len(containers)

genre = []
index = 0

df = pd.read_csv('draft_result.csv')
for i in range(total_movies):
    budget = ""
    gross_usa= ""
    cu_wo_gr = ""
    pro = ""
    reviewers = ""
    movie_url = 'https://www.imdb.com' + containers[i].find('a').get('href')
    req1 = requests.get(movie_url)
    soup1 = bs4.BeautifulSoup(req1.text,"html.parser")
    containers1 = soup1.find('div', class_ = 'titleBar')
    header = containers1.find('h1').text
    movie_name = header[:-8]
    movie_year = header[-6:-2]
    imdb_rating = soup1.find('div', class_ = 'imdbRating').find('span').text
    number_rating = soup1.find('div', class_ = 'imdbRating').find('a').text
#     movie_duration =  containers1.find('div', class_ = 'subtext').find('time').text.strip()
#     genre_plus_rel = containers1.find('div', class_ = 'subtext').find_all('a')
#     all_genre = genre_plus_rel[0:-1]
#     movie_release_date = genre_plus_rel[-1].text
    
    subtext = containers1.find('div', class_ = 'subtext').text.replace('\n','').replace(' ','')
    #contains rating, duratiion, genre and release year
    subtext_list = subtext.split('|')
    
    #subtext_list[0] = rate
    #subtext_list[1] = movie duration
    #subtext_list[2] = genre list
    #subtext_list[3] = release date
    
    #if rate is not defined, subtext_list is of length 3
    
    #all genre
    if(len(subtext_list) == 4):
        reviewers = subtext_list[0]
        movie_duration = subtext_list[1]
        genre_list = subtext_list[2].split(',')
        movie_release_date = subtext_list[3]
    if(len(subtext_list) == 3):
        movie_duration = subtext_list[0]
        genre_list = subtext_list[1].split(',')
        movie_release_date = subtext_list[2]   
    
    for i in range(len(genre_list), 4):
        genre_list.append("")
    
    story_summary = soup1.find('div', class_ = 'plot_summary').find('div',class_ = 'summary_text').text.strip()

    #crawl director name
    credit_summary = soup1.find('div', class_ = 'plot_summary').find_all('div', class_ = 'credit_summary_item')
    director = credit_summary[0].find('a').text

    #crawl writers list
    un_writers = soup1.find('div', class_ = 'plot_summary').find_all('div', class_ = 'credit_summary_item')[1].text.strip()[9:]
    index_extra = un_writers.find('|')
    writers_list = un_writers[:index_extra].strip().split(',')
    
    for i in range(len(writers_list),3):
        writers_list.append("")
    
    
    #crawl star list
    un_stars = soup1.find('div', class_ = 'plot_summary').find_all('div', class_ = 'credit_summary_item')[2].text.strip('\n')[7:]
    index_extra = un_stars.find('|')
    stars_list = un_stars[:index_extra].strip().split(',')
    
    for i in range(len(stars_list), 5):
        stars_list.append("")

    # to crawl plot_list
    all_plot_div = soup1.find("div",attrs={"class":"article","id":"titleStoryLine"}).find('div', class_ = "see-more inline canwrap").text.replace('\n','')
    index_extra = all_plot_div.find('\xa0See')
    plot_list = all_plot_div[15:index_extra-1]

    box_office_div = soup1.find("div",attrs={"class":"article","id":"titleDetails"}).find_all('div', class_='txt-block')
#     for i in range(len(all_genre)):
#         genre.append(all_genre[i].text)
        
    for i in range(len(box_office_div)):
        test_text = box_office_div[i].find('h4')
        if (test_text is not None):
            if(test_text.text=='Budget:'):
                budget = box_office_div[i].text[8:].replace(' ','').replace('\n', ' ')
            if(test_text.text == 'Gross USA:'):
                gross_usa = box_office_div[i].text.replace('\n','')[11:].replace(' ','')
            if(test_text.text == 'Cumulative Worldwide Gross:'):
                cu_wo_gr = box_office_div[i].text.replace('\n','').strip()[28:] 
            if(test_text.text == 'Production Co:'):
                pro = box_office_div[i].text.replace('\n','').strip()
                index_extra = pro.find(' See more\xa0')
                pro = pro[15:index_extra]

    df.loc[index] = [movie_name,movie_url,movie_year,imdb_rating,number_rating,reviewers,movie_duration,genre_list[0],genre_list[1],genre_list[2],genre_list[3],movie_release_date,story_summary,director,writers_list[0],writers_list[1],writers_list[2],stars_list[0],stars_list[1],stars_list[2],stars_list[3],stars_list[4],plot_list,budget,gross_usa,cu_wo_gr,pro]
    index += 1
#     print(movie_url,movie_name,genre,movie_release_date, imdb_rating,number_rating, director, writers_list,stars_list,plot_list)
    # containers_new = soup.find_all('td')

df.to_csv('imdb_rating.csv',index=False)
