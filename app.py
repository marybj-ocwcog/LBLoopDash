import dash
from dash import Dash, dcc, html, Input, Output
# from dash.dependencies import Input, Output
# import dash_core_components as dcc
# import dash_html_components as html
import dash_leaflet as dl
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import numpy as np
import dash_bootstrap_components as dbc
import geopandas as gpd
import json
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
from gtfs_functions import Feed, map_gdf


# Load ridership data
df = pd.read_csv('loop.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
df['Year-Month'] = df['datetime'].dt.to_period('M')

# load notes on LB Loop service
notes_df = pd.read_csv('LBLoop_Notes.csv')
notes_df.sort_values(by=['Year'], inplace=True)

dfCC = df.loc[df['service'].isin(['Campus Connector 1', 'Campus Connector 2'])]

# Load shapefiles using Geopandas
shapefile1 = gpd.read_file('LocalBus_LB_Loop.shp')
shapefile2 = gpd.read_file('GTFS_oregon_stops COG LB Loop.shp')

# Convert geopandas dataframe to json
shapefile1_json = json.loads(shapefile1.to_json())
shapefile2_json = json.loads(shapefile2.to_json())


# ------------------------------------------------------ APP ------------------------------------------------------
dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css")
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN, dbc_css])
app.title = "Linn-Benton Loop Ridership"

# define pieces of the app

# title header
main_title_header = html.Div([
	html.Br(),
	html.Br(),
	dbc.Row([
		dbc.Col([
			html.Img(src=app.get_asset_url("loop-logo-flat.jpg"),
                style={"width": "100px", "height": "100px", "margin-right": "10px", 'align': 'left'}),
			html.Br(),
			], width='auto'),
		dbc.Col([
			html.H1(children="Linn-Benton Loop Ridership",
			        style={"color": "rgb(33 36 35)"}),
			html.Label(
					"Use this interface to explore the ridership of the Linn-Benton Loop transit system over the years.",
					style={"color": "rgb(33 36 35)"},
			),
			html.Br(),
			html.Br(),
		])
	])
], style={'margin-left': '10px', 'align': 'left', 'width': '100vw'})

# data selectors for overview tab
overview_data_selectors = html.Div([
	html.Br(),
    html.Label('Use these filter options to explore the data.', style={
               "color": "rgb(33 36 35)", "margin-left": "10px"}),
    html.Br(),
    html.Br(),
	dbc.Row([
		dbc.Col([
			dcc.RadioItems(
				id='year-type',
				options=[
					{'label': '	 Calendar Year', 'value': 'calendar'},
					{'label': '	 Financial Year (Jul-Jun)', 'value': 'financial'}],
				value='calendar',
				inline=False,
				inputStyle={"margin-left": "10px"}
				)
		], width=2),
		dbc.Col([
			html.Label('Select a year range:', htmlFor='year-slider',
			           style={"color": "rgb(33 36 35)", "margin-left": "10px"}),
			dcc.RangeSlider(
				id='year-slider',
				marks={str(year): str(year) for year in df['Year'].unique()},
				min=df['Year'].min(),
				max=df['Year'].max(),
				value=[df['Year'].max()-3, df['Year'].max()],
				step=1
			)
		])
	]),
    html.Br()
], style={'backgroundColor': 'beige', 'marginTop': 22, 'margin-left': '10px', 'align': 'left', 'width': '90vw'}, className='dbc')

# data selectors for overview tab - by month (it is exactly the same as the previous one)
overview_data_selectors2 = html.Div([
	html.Br(),
    html.Label('Use these filter options to explore the month-by-month data.',
               style={"color": "rgb(33 36 35)", "margin-left": "10px"}),
    html.Br(),
    html.Br(),
	dbc.Row([
		dbc.Col([
			dcc.RadioItems(
				id='year-type2',
				options=[
					{'label': '	 Calendar Year', 'value': 'calendar'},
					{'label': '	 Financial Year (Jul-Jun)', 'value': 'financial'}],
				value='calendar',
				inline=False,
				inputStyle={"margin-left": "10px"}
				)
		], width=2),
		dbc.Col([
			html.Label('Select a year range:', htmlFor='year-slider2',
			           style={"color": "rgb(33 36 35)", "margin-left": "10px"}),
			dcc.RangeSlider(
				id='year-slider2',
				marks={str(year): str(year) for year in df['Year'].unique()},
				min=df['Year'].min(),
				max=df['Year'].max(),
				value=[df['Year'].max()-3, df['Year'].max()],
				step=1
			)
		])
	]),
    html.Br()
], style={'backgroundColor': 'beige', 'marginTop': 22, 'margin-left': '10px', 'align': 'left', 'width': '90vw'}, className='dbc')


# tabs for the app
tabs = html.Div([
		dcc.Tabs(
			value="tab-1",
			children=[
				dcc.Tab(
					label="Overview",
					value="tab-1",
					children=html.Div([overview_data_selectors, dcc.Graph(id='subplot',
                        style={'width': '90vw', 'margin-left': '15px', 'align': 'left'})])
				),
                dcc.Tab(
					label="Overview - by Month",
					value="tab-2",
					children=html.Div([overview_data_selectors2, dcc.Graph(id='month_table',
                        style={'width': '90vw', 'margin-left': '15px', 'align': 'left'})])
				),
				dcc.Tab(
					label="Route:  Campus Connector",
					value="tab-3",
					children=([
							dl.Map(center=[44.6365, -123.1059], zoom=10, children=[
								dl.TileLayer()
								],
							id="map", style={'width': '1000px', 'height': '500px'})
							])
				),
				dcc.Tab(
					label='Route:  Heart-to-Hub Uniter',
					value="tab-4",
					children=[
						html.Div([html.H3('Heart-to-Hub Uniter Page Content Goes Here')
							])
							]
				),
				dcc.Tab(label='Route:  US 20 Commuter',
					value="tab-5",
					children=[
							html.Div([
								html.H3('US 20 Commuter Page Content Goes Here')
							])
							]
				),
				dcc.Tab(label='Route:  Saturday Service',
					value="tab-6",
					children=[
							html.Div([
								html.H3('Saturday Service Page Content Goes Here')
							])
							]
				)
			],
		),
	], className='dbc')


# Define the layout
app.layout = dbc.Container([main_title_header, tabs], style={'margin-left': 1})

# ------------------------------------------------------ Callbacks - Overview Tab ------------------------------------------------------


# Define the callback for the bar chart
@app.callback(
	Output('subplot', 'figure'),
	[Input('year-type', 'value'),
	Input('year-slider', 'value')]
)
def update_subplot(year_type, year_range):

	if year_type == 'financial':
		year_column = 'Fiscal Year'
		plot_title = 'Ridership by Financial Year (July to June)'
		table_headers = ['Fiscal Year', 'Note', 'Service']  # for table fig
	else:
		year_column = 'Year'
		plot_title = 'Ridership by Calendar Year'
		table_headers = ['Year', 'Note', 'Service']  # for table fig

	filtered_df = df[(df[year_column] >= year_range[0]) &
	                  (df[year_column] <= year_range[1])]
	rides_per_year = filtered_df.groupby(
	    [year_column])['total_number'].sum().reset_index(name='Count')

	fig = make_subplots(
		rows=3, cols=3,
		subplot_titles=(plot_title,
                        'Notes',
						"by Ticket Type (grouped by Ticket Group)",
						"by Ticket Group",
						'by Route'),
		specs=[
        [{"colspan": 2}, None, {"type": "table"}],
		[{'type': 'xy'}, {'type': 'pie'}, {'type': 'xy'}]
		]
        )
    # _____________________________________________________
    # bar chart of ridership by selected year type
    # _____________________________________________________
	fig.add_trace(
		go.Bar(
			x=rides_per_year[year_column],
			y=rides_per_year['Count'],
			showlegend=False,
			orientation='v',
			hovertemplate="Year: %{x}" +
			"<br>Count: %{y:,.0f}</br><extra></extra>"
		),
		row=1, col=1
	)
	fig.update_layout(
		hoverlabel=dict(
			bgcolor="white")
	)
    # _____________________________________________________
	# notes for the years selected
    # _____________________________________________________
	filtered_notesTest = notes_df[(notes_df[year_column] >= year_range[0]) & (
	    notes_df[year_column] <= year_range[1])]

	if filtered_notesTest.empty:
		no_data_dict = {'Year': [''], 'Fiscal Year': [''], 'Note': [
		    'No notes for this time period.'], 'Service': ['']}
		filtered_notes = pd.DataFrame.from_dict(no_data_dict)
	else:
		filtered_notes = filtered_notesTest.copy(deep=True)

	fig.add_trace(
		go.Table(
		columnorder=[1, 2, 3],
		columnwidth=[10, 50, 15],
			header=dict(values=table_headers, align='left'),
			cells=dict(values=[filtered_notes[year_column],
			           filtered_notes.Note, filtered_notes.Service], align='left')
		),
		row=1, col=3
	)

    # _____________________________________________________
	# Process and aggregate the dataframes for second row of charts
    # ____________________________________________________
	df_agg_type = filtered_df.groupby(['ticket_group', 'ticket_type'])[
	                                  'total_number'].sum().reset_index()
	df_agg_group = filtered_df.groupby('ticket_group')[
	                                   'total_number'].sum().reset_index()
	df_agg_route = filtered_df.groupby(
	    'service')['total_number'].sum().reset_index()

	# Create a list to store traces
	data_type = []
	data_group = []
	data_route = []

	# Define a color map for the groups
	group_colors = {group: color for group, color in zip(df_agg_group['ticket_group'].unique(),
														 px.colors.qualitative.Plotly)}

    # _____________________________________________________
	# Create a trace for each group (for the 'by type, by group' bar chart)
    # _____________________________________________________
	for group, color in group_colors.items():
		df_group = df_agg_type[df_agg_type['ticket_group'] == group]
		data_type.append(go.Bar(name=group,
								y=df_group['ticket_type'],
								x=df_group['total_number'],
								legendgroup=group,
								hovertemplate='Ticket Type: %{y}<br>Tickets Sold: %{x:,.0f}<extra></extra>',
								showlegend=False,
								orientation='h',
								marker_color=color)
						)
    # _____________________________________________________
	# Create a trace for the 'by group' pie chart
    # _____________________________________________________
	data_group.append(go.Pie(labels=df_agg_group['ticket_group'],
							values=df_agg_group['total_number'],
							hovertemplate='Ticket Group: %{label} <br> Tickets Sold: %{value:,.0f}<extra></extra>',
							showlegend=False,
							marker_colors=[group_colors[group] for group in df_agg_group['ticket_group']])
						)
    # _____________________________________________________
	# Create a trace for the 'by route' chart
    # _____________________________________________________
	data_route.append(go.Bar(name='Total',
							y=df_agg_route['service'],
							x=df_agg_route['total_number'],
							showlegend=False,
							orientation='h',
							hovertemplate='Route: %{y}<br>Tickets Sold: %{x:,.0f}<extra></extra>')
						)

	# Add second row traces to the subplot
	for trace in data_type:
		fig.add_trace(trace, row=2, col=1)

	for trace in data_group:
		fig.add_trace(trace, row=2, col=2)

	fig.update_layout(
		height=800,
		uniformtext=dict(minsize=10, mode='hide'),
		margin=dict(t=50, l=25, r=25, b=25),
		showlegend=False
)

	for trace in data_route:
		fig.add_trace(trace, row=2, col=3)

	# Update layout
	fig.update_layout(barmode='group')

	return fig

# ------------------------------------------------------ Callbacks - Overview by Month Tab ------------------------------------------------------


# Define the callback for the table
@app.callback(
	Output('month_table'),
	[Input('year-type2', 'value'),
	Input('year-slider2', 'value')]
)
def update_table(year_type2, year_range2):

	if year_type2 == 'financial':
		year_column = 'Fiscal Year'
		plot_title = 'Ridership by Financial Year (July to June)'
		table_headers = ['Fiscal Year', 'Note', 'Service']  # for table fig
	else:
		year_column = 'Year'
		plot_title = 'Ridership by Calendar Year'
		table_headers = ['Year', 'Note', 'Service']  # for table fig

	filtered_df = df[(df[year_column] >= year_range[0]) &
	                  (df[year_column] <= year_range[1])]

    # create a pivot table of the data
    table_df = filtered_df.groupby(['Year-Month', 'ticket_group','ticket_type'], sort=True)['total_number'].sum().reset_index()
    table_df_pivot = table_df.pivot_table(index='Year-Month', columns=['ticket_group','ticket_type'], values='total_number', sort=True, fill_value=0)
    table_df_pivot['Month Total']=table_df_pivot.sum(axis=1)
    table_df_pivot.index = table_df_pivot.index.astype(str)
    table_df_pivot.reset_index(inplace=True)
    table_df_pivot=table_df_pivot.rename(columns={'index':'Year-Month'})
    
    #Create table figure
    #fig.add_trace(
    #.Table(
    #eader=dict(values=list(table_df_pivot.columns)),
    #ells=dict(values=[table_df_pivot.iloc[:,num] for num in range(len(table_df_pivot.columns))],
    #align=['right']*len(table_df_pivot.columns))
    #),
    #=3, col=1
	
	
	return fig




# Run the app
if __name__ == '__main__':
	app.run_server(debug=True)
