import pandas as pd
import panel as pn
from panel.interact import interact
import numpy as np
import holoviews as hv
import squarify
from functools import reduce
import seaborn as sb

hv.extension('bokeh')
pn.extension(template='bootstrap')

#load data for dataframe
def get_data_from_pickle():
    df = pd.read_pickle('loop.pkl')
    return df

df=get_data_from_pickle()
df.sort_values(by='datetime', inplace=True)
df['Year'] = df['datetime'].dt.year

#find the min and max of the years in the dataframe to populate the sliders
startYear = df['datetime'].min().year
endYear = df['datetime'].max().year

ticket_type = pn.widgets.CheckBoxGroup(
    name = 'Ticket Type',
    value=list(df['ticket_type'].unique()),
    options=list(df['ticket_type'].unique()),
    inline=True
)

day_of_week = pn.widgets.CheckBoxGroup(
    name = 'Travel Day',
    value=list(df['day_type'].unique()),
    options = list(df['day_type'].unique()),
    inline=True
)

range_slider = pn.widgets.RangeSlider(
    name='Ridership for Years 2',
    start=startYear, end=endYear,
    value=(startYear,endYear),
    step=1
)

def get_selection(*range_slider, thetickettypes, thedaytypes):
   #get a list of years from the slider values
    if len(range_slider) == 2:
        thestart=range_slider[0][0]
        theend=range_slider[0][1]
        #print(thestart)
        #print(theend)
        yearlist = list(range(thestart, theend+1))
    if len(range_slider) ==1:
        yearlist = list(range_slider[0][0])
        
    #these are switches to determine if the user has selected any value for day_type and ticket_type
    #(there will always be years)
    days=False
    ticket=False
   
    #check for ticket_types        
    if len(thetickettypes) !=0:
        ticket=True
    #check for day_types    
    if len(thedaytypes) !=0:
        days=True
    if days and ticket:
        #all three have values
        the_df_selection=df[df['Year'].isin(yearlist) & df['ticket_type'].isin(thetickettypes) & df['day_type'].isin(thedaytypes)]
    elif days:
        #only days chosen
        the_df_selection=df[df['Year'].isin(yearlist) & df['day_type'].isin(thedaytypes)]
    elif ticket:
        #only days chosen
        the_df_selection=df[df['Year'].isin(yearlist) & df['ticket_type'].isin(thetickettypes)]
    else:
        #only years chosen
        the_df_selection=df[df['Year'].isin(yearlist)]
        
    return the_df_selection

get_selection=pn.bind(get_selection, range_slider.value, thetickettypes=ticket_type.value,
                            thedaytypes=day_of_week.value)
							
#pn.Column(freq, phase, range_slider).servable(area='sidebar')
pn.Column(
    range_slider,
    "",
    pn.layout.Divider(margin=(-20, 0, 0, 0)),
    'Day of Travel:',
    day_of_week,
    "",
    pn.layout.Divider(margin=(-20, 0, 0, 0)),
    'Ticket Types:',
    ticket_type,
    "",
    background='#989897', width=400
).servable(area='sidebar')

df_selection=get_selection(range_slider.value, thetickettypes=ticket_type.value, thedaytypes=day_of_week.value)

def calc_percentages(colname, df):
    #calculate the percentages for the values in the given column (colname)
    #looks in df_selection
    df2=df.groupby([colname])\
    .agg({'total_number':'sum'})[['total_number']]\
    .apply(lambda x:round(100*x/x.sum(),1))\
    .sort_values(by='total_number', ascending=False)
    theoutcome = df2.to_dict('split') 
    thevalues = [reduce(lambda x, y: x + y, inner_list) for inner_list in theoutcome['data']]
    labelswithvalues = []                                                                                
    for i,j in zip(theoutcome['index'], thevalues):
        listvalue=f'{i} ({j}%)'
        labelswithvalues.append(listvalue)
    return (theoutcome['index'], thevalues, labelswithvalues)
	
yearly_ridership_bars = hv.Bars(df_selection.groupby('Year')['total_number'].sum(),
                                hv.Dimension('Year'), 'total_number').opts(width=500)

total_ridership_num = int(df_selection['total_number'].sum())

day_of_travel_percentages = calc_percentages('day_type', df_selection)

day_type_square = squarify.plot(day_of_travel_percentages[1],
                                label=day_of_travel_percentages[2],
                                pad=2, color=sb.color_palette('Spectral',len(day_of_travel_percentages[0])),
                               )
day_type_square.set_title('Ridership Day of Travel')
day_type_square.axis('off')

#f1 = hv.DynamicMap(yearly_ridership_bars)
f2 = pn.indicators.Number(value=total_ridership_num, name='Total Ridership', format='{value} rides',font_size='24')
f3 = day_type_square

pn.Row(
    pn.Card(yearly_ridership_bars, title='Ridership by Year', collapsible=False),
    pn.Card(f2,background='lightgray', hide_header=True, width=200),    
).servable(area='main')

