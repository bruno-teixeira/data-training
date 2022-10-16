import requests
import pandas as pd
import numpy as np
import datetime 
from datetime import date
import collections
import sys
import config

city = sys.argv[1]
country = sys.argv[2]

data = requests.get(f'http://api.openweathermap.org/data/2.5/forecast/?q={city},{country}&appid={config.OWM_key}&units=metric&lang=en')

def get_weather(data):
    
    forecast_api = data.json()['list']

    weather_info = []

    for forecast_3h in forecast_api: 
        weather_hour = {}
        weather_hour['weather_datetime'] = forecast_3h['dt_txt']
        weather_hour['main_weather'] = forecast_3h['weather'][0]['main']
        weather_hour['weather_detail'] = forecast_3h['weather'][0]['description']
        weather_hour['temperature'] = forecast_3h['main']['temp']
        weather_hour['feels_like'] = forecast_3h['main']['feels_like']
        weather_hour['humidity'] = forecast_3h['main']['humidity']
        weather_hour['wind'] = forecast_3h['wind']['speed']
        try: weather_hour['prob_perc'] = float(forecast_3h['pop'])
        except: weather_hour['prob_perc'] = 0
        try: weather_hour['rain_qty'] = float(forecast_3h['rain']['3h'])
        except: weather_hour['rain_qty'] = 0
        try: weather_hour['snow'] = float(forecast_3h['snow']['3h'])
        except: weather_hour['snow'] = 0
        weather_hour['municipality_iso_country'] = city + ', ' + country
        weather_info.append(weather_hour)
    
    return weather_info
    
df = pd.DataFrame(get_weather(data))
df.weather_datetime = pd.to_datetime(df.weather_datetime)

hour = [
    df['weather_datetime'].dt.hour==0,
    df['weather_datetime'].dt.hour==3,
    df['weather_datetime'].dt.hour==6,
    df['weather_datetime'].dt.hour==9,
    df['weather_datetime'].dt.hour==12,
    df['weather_datetime'].dt.hour==15,
    df['weather_datetime'].dt.hour==18,
    df['weather_datetime'].dt.hour==21
]

time_of_day = ['12am', '3am', '6am', '9am', '12pm', '3pm', '6pm', '9pm']
df['time_of_day'] = np.select(hour, time_of_day)

df_tomorrow = df[df['weather_datetime'].dt.date == date.today() + datetime.timedelta(days=1)].reset_index(drop=True)
date_tomorrow = df_tomorrow['weather_datetime'].dt.date.iloc[1]

min_temp = df_tomorrow.temperature.min()
max_temp = df_tomorrow.temperature.max()

v_snow = df_tomorrow.snow.sum()

if v_snow > 0:
  snow = 'snow with a '
else: snow = ''

min_temp_hr = df_tomorrow[df_tomorrow['temperature'] == min_temp].time_of_day.values[0]
max_temp_hr = df_tomorrow[df_tomorrow['temperature'] == max_temp].time_of_day.values[0]

most_weather = pd.DataFrame(collections.Counter(df_tomorrow.weather_detail).items(), columns=['weather', 'qt']).sort_values(by='qt', ascending=False)['weather'].values[0]

v_rain = df_tomorrow['prob_perc'].sort_values(ascending=False).iloc[0]

if v_rain <= 0.2: 
    chance = 'very low'
if 0.2 < v_rain <= 0.4:  
    chance = 'low'
if 0.4 < v_rain <= 0.6:  
    chance = 'medium'
if 0.6 < v_rain <= 0.8:  
    chance = 'high'  
if 0.8 < v_rain <= 1:  
    chance = 'very high'   

print('''
City: {}, {}
Date: {}      

Most of tomorrow weather will be {}{}, with a {} chance of rain.

Temperatures tomorrow may rise from a low of {} degrees at {} to a high of {} degrees at {}.
'''.format(city, country, date_tomorrow, snow, most_weather, chance, min_temp, min_temp_hr, max_temp, max_temp_hr)
     )

