from __future__ import print_function
__author__ = 'zem232'

if __name__ == '__main__':
    """Outputs a dataframe of the bus waits.

    Arguments: 
        Input file (bus oncalls .csv)

    """

import pandas as pd
import numpy as np
import sys
from datetime import datetime, timedelta
import seaborn
from matplotlib import pyplot
import matplotlib
matplotlib.rcParams.update({'font.size': 15})
pyplot.figure(figsize=(15, 15))

# Look at all intervals between subway arrivals
def next_whole_minute(t):
    return t+59 - (t+59)%60

## GLOBAL VARIABLES FOR ALL BUSES
LGAstops = ['LGA/TERMINAL B', 'LGA/TERMINAL D','LGA/TERMINAL C','sbs60-q48-geo', 'lga/circle','LGA M60 E.B. (does not stop)']
dropcols = (['Timestamp',' Latitude', 'Longitude'])

if not len(sys.argv) == 2:
    print('''USAGE:
    $python bus_waits.py <infile.csv>''')
    sys.exit()

file = sys.argv[1]
name = file[:-4]
line = file[:3]
print(file)

BUS = pd.read_csv(file)
BUS.dropna(axis=0,inplace=True)
BUS['Date']=pd.to_datetime(BUS['Timestamp'])
BUS.drop(dropcols,axis=1,inplace=True)
BUSID = BUS[' BusID'].unique()

if file.startswith('Q72'):
    for x in range(len(BUSID)):
        if BUS[BUS[' BusID'] == BUSID[x]].reset_index()['Stop Name'][0] == 'LGA/TERMINAL D':
            BUS = BUS[BUS[' BusID'] != BUSID[x]]
            
if file.startswith('M60'):
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

LGABUS = BUS[(BUS['Stop Name'] == LGASTOP) & 
    ((BUS['Stop Status'] == 'at stop') | 
     (BUS['Stop Status'] == 'approaching') | 
     (BUS['Stop Status'] == '< 1 stop away'))]
BUSID = LGABUS[' BusID'].unique()
BUS_df = pd.DataFrame(index=range(len(BUSID)))

time = []
for x in range(0,len(BUSID)):
    time.append(LGABUS[LGABUS[' BusID'] == BUSID[x]].tail(1).reset_index()['Date'][0])
BUS_df['Arrival Time'] = time

BUS_df = BUS_df.sort_values(['Arrival Time'], ascending=False).reset_index()
wait = []
wait.append(0)
for x in range(1,len(BUS_df.index)):
    wait.append(BUS_df['Arrival Time'][x-1]-BUS_df['Arrival Time'][x])
BUS_df['Wait'] = wait
BUS_df.drop(['index'],axis=1,inplace=True)

print(BUS_df)
dfname = 'bus_frequency_' + name + '.csv'
BUS_df.to_csv(dfname, index=False)



next_bus = []
next_bus_by_line_ts = []
next_bus_by_line_ls = []
time_ = []
deltas = []
for x in range(1, len(BUS_df)):
    deltas.append(BUS_df['Wait'][x].total_seconds())

deltas = np.round(deltas).astype(int)
    
for i in range(2, len(deltas)):
    last_value, value = deltas[i-1], deltas[i]
    for t in range(next_whole_minute(last_value), value, 60):
        x = (t // 60 + 19 * 60) % (24 * 60) # 19 from UTC offset
        waiting_time = 1. / 60 * (value - t)
        time_.append(t)
        next_bus.append(waiting_time)
        next_bus_by_line_ts.append(waiting_time)
        next_bus_by_line_ls.append(line)
    
data=np.array(deltas)/60
fn='time_between_arrivals'+name+'.png'
title='Distribution of Bus Frequency (' +line +') \n'
color='blue'
print('got', len(data), 'points')
pyplot.clf()
lm = seaborn.distplot(data, color=color, kde_kws={'gridsize': 2000})
pyplot.title(title, fontsize = 23)
pyplot.xticks(fontsize = 15)
pyplot.yticks(fontsize = 15)
pyplot.xlabel('Time (min)', fontsize = 20)
pyplot.ylabel('Probability distribution', fontsize = 20)
pyplot.savefig(fn)
print('mean', np.mean(data), 'median', np.median(data))
pyplot.show()


# Violin Plot
matplotlib.rcParams.update({'font.size': 15})
pyplot.figure(figsize=(15, 10))
pyplot.clf()
seaborn.violinplot(orient='h',
                   x=next_bus_by_line_ts,
                   y=next_bus_by_line_ls,
                   order=[line],
                   scale='width',
                   palette=['#EE352E']*3 + ['#00933C']*3 + 
                   ['#808183', '#A7A9AC', '#555555'],
                   bw=0.03, cut=0, gridsize=2000)
#pyplot.xlim([-1, 40])
pyplot.title('Time Until the Next Bus ' , fontsize = 20 )
pyplot.xlabel('Time (min)' , fontsize = 15 )
pyplot.xticks(fontsize = 15)
pyplot.yticks(fontsize = 15)
fq = 'time_to_arrival_by_bus_' + name 
pyplot.savefig(fq)
    
#make dataframe
x = next_bus_by_line_ts
y = next_bus_by_line_ls
z = time_

df = pd.DataFrame({'line':line, 'time':z, 'time_to_next_bus':x, })
csvname = 'bus_waits_' + name + '.csv'
df.to_csv(csvname, index=False)



