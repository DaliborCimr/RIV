import numpy as np
import pandas as pd
import urllib

#parsing of page source to get a files
r = urllib.request.urlopen("http://hodnoceni15.rvvi.cz/www")
bytecode = r.read().decode().split('\n')
#splitText = bytecode.split('\n')
nameOfInstitutions = []
references = []
for line in bytecode:
    if 'xlsx' in line:
        newRef = (line.split('xlsx',1)[0].rsplit('/',1)[1] + 'xlsx')#.replace(' ', '_')
        newInstitution = (line.split('</b>',1)[1].rsplit('</div>',1)[0])#.replace(' ', '_')
        nameOfInstitutions = np.append(nameOfInstitutions,newInstitution)
        references = np.append(references,newRef)
        #schools=np.append(schools,[(ref,name)])
institutions = np.vstack((list(range(len(references))), references,nameOfInstitutions)).T

#download excel files
inputData = []
for index, row in enumerate(institutions):
    dls = "http://hodnoceni15.rvvi.cz/public/" + row[1]
    urllib.request.urlretrieve(dls, 'data/' + row[1])
    #delete unnecessary data
    institutionArticles = pd.ExcelFile('data/' + row[1]).parse('Tab3_Pil1').rename({3:''})
    institutionArticles.columns = institutionArticles.iloc[3]
    institutionArticles = institutionArticles[4:]
    #reindexing (optional)
    institutionArticles.index = range(len(institutionArticles))
    inputData.append(institutionArticles)