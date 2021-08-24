# write some code for the API here
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd 
import numpy as np
import json
from urllib.request import urlopen


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
data = pd.read_excel('uwezo_api/data/mapping.xlsx', engine = 'openpyxl', sheet_name = 'Template')

data = data.rename(columns=lambda x: x if not 'Unnamed' in str(x) else '')\
    .dropna(axis = 0, how = 'all').dropna(axis = 1, how = 'all')\
    .dropna(axis = 0, how = 'all').drop(index = 0)

def coord(longitude, latitude):
    location = {
        'type':'Point',
        'coordinates':[longitude, latitude]
    }
    return location
data['location'] = pd.Series(map(lambda lon,lat:coord(lon, lat),
                                          data['longitude'],
                                          data['latitude']
                                    ))
def notNone(s):
    if s is None:
        return ''
    else:
        return s

def transform_in_dict(website, email, phone, facebook, instagram):
    contact = [{'name':'website', 'url':notNone(website)}, 
                {'name':'email', 'url':notNone(email)},
                {'name':'phone', 'url':notNone(phone)},
                {'name':'facebook', 'url':notNone(facebook)},
                {'name':'instagram', 'url':notNone(instagram)}
              ]
    return contact

data['socialMedias'] = pd.Series(map(lambda a,b,c,d,e:transform_in_dict(a,b,c,d,e),
                                          data['website'],
                                          data['email'],
                                          data['phone'],
                                          data['facebook'],
                                          data['instagram']
                                    ))
data = data.fillna('').astype('object')
data = data[['location','_id','socialMedias','country','sectors','name','email','website','classification', 'womenSpecific', 'socialEntrepreneurSpecific', 'yearFounded', 'description', 'supportType', 'fundingType', 'innovationStages']]




boolean = 'qdihcbcn'

@app.get("/")
def index():
    return {'key':boolean}

# define a root `/` endpoint
@app.get("/stakeholder/{stakeholder}/womenspecific/{womenspecific}/socialentrepreneurship/{socialentrepreneurship}")
def predict_genre(stakeholder, womenspecific, socialentrepreneurship):
    # key = track_id spotify de la clé 
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin':'http://127.0.0.1:5000/, http://localhost:3000/'
    }
    stakeholders = ['Incubators, Accelerators & Hubs',
            'Professional Associations & Networks',
            'NGOs',
            'Development Agency',
            'MFIs, Banks, Investors'
            'Local Consultants & Businesses',
            'Public Inititiaves'
    ]

    if stakeholder == 'All':
        stakeholder = stakeholders
    else:
        stakeholder = [stakeholder]
    if womenspecific == 'All':
        womenspecific = ['Yes','No']
    else:
        womenspecific = [womenspecific]
    if socialentrepreneurship == 'All':
        socialentrepreneurship = ['Yes','No']
    else:
        socialentrepreneurship = [socialentrepreneurship]

    df = data[data['classification'].isin(stakeholder) 
     & data['womenSpecific'].isin(womenspecific)
     & data['socialEntrepreneurSpecific'].isin(socialentrepreneurship) 
    ]
    data_dict = {'data':df.to_dict(orient = 'records')}
    # TO DO : appliquer une fonction qui sort les features 
    return JSONResponse(content = data_dict, headers = headers) 
