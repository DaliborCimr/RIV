import numpy as np
import pandas as pd
import urllib


def check_author_or_article(object_id, df, item_id):
    """ Testing of existence of author or article
     
     Args:
         object_id: id of author or article
         df: DataFrame of authors or articles
         item_id: column name to comparison
         
    """
    for index, existAuthor in df.iterrows():
        if object_id == int(existAuthor[item_id]):
            return False
    return True

""" parsing of page source to get a files"""
r = urllib.request.urlopen("http://hodnoceni15.rvvi.cz/www")
bytecode = r.read().decode().split('\n')

nameOfInstitutions = []
references = []
for line in bytecode:
    if 'xlsx' in line:
        newRef = (line.split('xlsx', 1)[0].rsplit('/', 1)[1] + 'xlsx')  # .replace(' ', '_')
        newInstitution = (line.split('</b>', 1)[1].rsplit('</div>', 1)[0])  # .replace(' ', '_')
        nameOfInstitutions = np.append(nameOfInstitutions, newInstitution)
        references = np.append(references, newRef)
institutions = np.vstack((list(range(len(references))), references, nameOfInstitutions)).T

"""download excel files"""
inputData = []
for indexOfArt, row in enumerate(institutions):
    dls = "http://hodnoceni15.rvvi.cz/public/" + row[1]
    urllib.request.urlretrieve(dls, 'data/' + row[1])
    # delete unnecessary data
    institutionArticles = pd.ExcelFile('data/' + row[1]).parse('Tab3_Pil1').rename({3: ''})
    institutionArticles.columns = institutionArticles.iloc[3]
    institutionArticles = institutionArticles[4:]
    # reindexing (optional)
    institutionArticles.index = range(len(institutionArticles))
    inputData.append(institutionArticles)

""" Testing data for developing of algorithm with different names of columns. All is set to quick debug and 
not finished yet.

affiliations is number mark of cooperation of institutions and can be one of following numbers:
    0: article is only from one czech institution
    1: article is from one czech institution in cooperation with non-czech institutions
    2: article is from more czech institutions
    3: article is from more czech institutions in cooperation with non-czech institutions
"""
skola1 = pd.read_excel('skola1.xlsx')
skola2 = pd.read_excel('skola2.xlsx')
instArticles = [skola1, skola2]

articles = pd.DataFrame(columns=['articleId', 'articleName', 'eval', 'czechEval', 'affiliations'])
authors = pd.DataFrame(columns=['authorId', 'authorName'])
institutions = pd.DataFrame({'instId': pd.Series([0.0, 1.0]), 'instName': pd.Series(['skola1', 'skola2'])})
articlesOfAuthors = pd.DataFrame(columns=['authorId', 'articleId', 'instId', 'contribution'])

for indexOfInst, inst in enumerate(instArticles):
    for indexOfArt, row in inst.iterrows():
        # If an article already exists, change affiliations. Otherwise, add article.
        affiliations = -1
        if check_author_or_article(int(row['ID']), articles, 'articleId'):
            if row['podílCelkem'] == row['podílŠkoly']:
                affiliations = 0
            else:
                affiliations = 2
            articles = articles.append({'articleId': int(row['ID']), 'articleName': row['Článek'],
                                        'eval': row['podílCelkem'], 'czechEval': row['podílŠkoly'],
                                        'affiliations': affiliations}, ignore_index=True)
        else:
            i = articles[articles['articleId'] == int(row['ID'])].index[0]
            articles.set_value(i, 'czechEval', articles.loc[i]['czechEval'] + row['podílŠkoly'])
            articles.set_value(i, ['affiliations'], 1)

        # If an article already exists, change affiliations. Otherwise, add article.
        authorRow = row['Autor'].split(';')
        for newAuthor in authorRow:
            authorDetail = newAuthor.split(',')
            if check_author_or_article(int(authorDetail[1]), authors, 'authorId'):
                authors = authors.append({'authorId': int(authorDetail[1]), 'authorName': authorDetail[0]},
                                         ignore_index=True)

            articlesOfAuthors = articlesOfAuthors.append({'authorId': int(authorDetail[1]), 'articleId': int(row['ID']),
                                                          'instId': int(indexOfInst),
                                                          'contribution': (row['podílŠkoly'] / len(authorRow))},
                                                         ignore_index=True)
for indexOfArt, row in articles.iterrows():
    if articles.loc[indexOfArt]['czechEval'] != articles.loc[indexOfArt]['eval']:
        if articles.loc[indexOfArt]['affiliations'] == 1:
            articles.set_value(indexOfArt, ['affiliations'], 3)
