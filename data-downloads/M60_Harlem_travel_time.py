from __future__ import print_function
__author__ = 'zem232'

if __name__ == '__main__':
    """Outputs a dataframe of the bus travel time from select stops.

    Arguments: 
        Input file (bus oncalls .csv)

    """

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys

if not len(sys.argv) == 2:
    print('''USAGE:
    $python bus_waits.py <infile.csv>''')
    sys.exit()

file = sys.argv[1]
name = file[:-4]
line = file[:3]
print(file)

## GLOBAL VARIABLES FOR ALL BUSES
LGAstops = ['LGA/TERMINAL B', 'LGA/TERMINAL D','LGA/TERMINAL C','sbs60-q48-geo', 'lga/circle','LGA M60 E.B. (does not stop)']
dropcols = (['Timestamp',' Latitude', 'Longitude'])

BUS = pd.read_csv(file)
BUS.dropna(axis=0,inplace=True)
BUS['Date']=pd.to_datetime(BUS['Timestamp'])
BUS.drop(dropcols,axis=1,inplace=True)
BUSID = BUS[' BusID'].unique()

if 'Direction' in BUS.columns:
    BUS = BUS[BUS['Direction'] ==0]
else:
    for x in BUSID:
        if ('LGA/TERMINAL A' in BUS[BUS[' BusID']==x]['Stop Name'].unique()):
            BUS = BUS[BUS[' BusID'] != x]
BUSID = BUS[' BusID'].unique()

df=pd.DataFrame(index=LGAstops)
for x in range(len(BUSID)):
    df[x] = 3
    for y in range(len(df.index)):
        df[x][y] = df.index[y] in BUS[BUS[' BusID'] == BUSID[x]]['Stop Name'].unique()
df = df.astype(int)
df['Total']= df.T.sum()
df.loc[df.Total == df.Total.max()]

LGASTOP = df.loc[df.Total == df.Total.max()].index[0]
for x in range(len(BUSID)):
    if df[x][LGASTOP] == 0:
        BUS = BUS[BUS[' BusID'] != BUSID[x]]

if line == 'M60':
    BUSID = BUS[' BusID'].unique()
    for x in BUSID:
        if ('E 125 ST/LEXINGTON AV' in BUS[BUS[' BusID']==x]['Stop Name'].unique()) or ('E 125 ST/MADISON AV' in BUS[BUS[' BusID']==x]['Stop Name'].unique()):
            a='continue'
        else:
            print('delete +'+ x)
            BUS = BUS[BUS[' BusID'] != x]
      
    BUSID = BUS[' BusID'].unique()
    BUS_df = pd.DataFrame(index=range(len(BUSID)))
    
    a = []
    b = []
    for x in BUSID:
        try:
            a.append(BUS[(BUS[' BusID'] == x) & 
                 ((BUS['Stop Name'] == LGASTOP) | 
                  (BUS['Stop Name'] == LGASTOP)) & 
                 ((BUS['Stop Status'] == 'at stop') | 
                  (BUS['Stop Status'] == 'approaching') | 
                  (BUS['Stop Status'] == '< 1 stop away'))].head(1).reset_index()['Date'][0])
        except IndexError:
            a.append(BUS[(BUS[' BusID'] == x) & 
                         ((BUS['Stop Name'] == LGASTOP) | 
                          (BUS['Stop Name'] == LGASTOP))
                        ].tail(1).reset_index()['Date'][0])
    
        try:
            b.append(BUS[(BUS[' BusID'] == x) & 
                         ((BUS['Stop Name'] == 'E 125 ST/LEXINGTON AV') | 
                          (BUS['Stop Name'] == 'E 125 ST/MADISON AV')) &
                         ((BUS['Stop Status'] == 'at stop') | 
                          (BUS['Stop Status'] == 'approaching') | 
                          (BUS['Stop Status'] == '< 1 stop away'))
                        ].tail(1).reset_index()['Date'][0])
        except IndexError:
            b.append(BUS[(BUS[' BusID'] == x) & 
                         ((BUS['Stop Name'] == 'E 125 ST/LEXINGTON AV') | 
                          (BUS['Stop Name'] == 'E 125 ST/MADISON AV'))
                        ].tail(1).reset_index()['Date'][0])

else:
    print('''USAGE:
    Valid for 'M60' bus line only. ''')
          

BUS_df['LGA_Arrival'] = a
BUS_df['Departure'] = b
BUS_df['travel_time_seconds'] = BUS_df['LGA_Arrival'] - BUS_df['Departure']
BUS_df['travel_time_seconds'] = BUS_df['travel_time_seconds'].map(lambda x: round(x.total_seconds()))
BUS_df = BUS_df[BUS_df['travel_time_seconds']>0]
BUS_df['LGA_Arrival'] = BUS_df['LGA_Arrival'].astype(str)
BUS_df['Departure'] = BUS_df['Departure'].astype(str)

csvname = name +'_Harlem_travel_time.csv'
BUS_df.to_csv(csvname, index=False)

