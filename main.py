import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import dash_bootstrap_components as dbc
import numpy as np

agriculture_data = pd.read_csv('./data/agriculture_data.csv')
data_science_job_salaries = pd.read_csv('./data/data_science_job_salaries.csv')
disaster_data = pd.read_csv('./data/disaster_data.csv', encoding='ISO-8859-1')

agriculture_data['year'] = pd.to_datetime(agriculture_data['sale_date']).dt.year
disaster_data['year'] = disaster_data['Start Year']

disaster_data['Total Affected'] = disaster_data['Total Affected'].fillna(0).astype(int)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def create_graphs(start_year, end_year):
    filtered_disaster_data = disaster_data[(disaster_data['year'] >= start_year) & (disaster_data['year'] <= end_year)]
    filtered_agriculture_data = agriculture_data[(agriculture_data['year'] >= start_year) & (agriculture_data['year'] <= end_year)]
    filtered_salary_data = data_science_job_salaries[(data_science_job_salaries['work_year'] >= start_year) & (data_science_job_salaries['work_year'] <= end_year)]

    disaster_data_agg = filtered_disaster_data.groupby('ISO').agg({
        'Total Affected': 'sum',
        'Disaster Type': lambda x: x.value_counts().index[0]
    }).reset_index()

    agriculture_data_agg = filtered_agriculture_data.groupby('farm_location').agg({
        'units_shipped_kg': 'sum',
        'product_name': lambda x: x.value_counts().index[0]
    }).reset_index()

    combined_data = pd.merge(disaster_data_agg, agriculture_data_agg, left_on='ISO', right_on='farm_location', how='outer')

    world_map_fig = px.scatter_geo(combined_data, 
                                   locations="ISO", 
                                   color="Disaster Type",
                                   size="Total Affected",
                                   hover_name="ISO",
                                   hover_data={
                                       "Producto principal": combined_data['product_name'],
                                       "Producción agrícola (kg)": combined_data['units_shipped_kg'],
                                       "Afectados por desastres": combined_data['Total Affected']
                                   },
                                   projection="natural earth",
                                   title=f"Impacto de Desastres Naturales y Producción Agrícola Global ({start_year}-{end_year})")

    world_map_fig.update_geos(showcountries=True, showcoastlines=True, showland=True, fitbounds="locations")
    world_map_fig.update_layout(height=600, margin={"r":0,"t":50,"l":0,"b":0})

    data_science_avg = filtered_salary_data.groupby('work_year')['salary_in_usd'].mean().reset_index()

    filtered_agriculture_data['year'] = pd.to_datetime(filtered_agriculture_data['sale_date']).dt.year

    agriculture_production = filtered_agriculture_data.groupby('year')['units_shipped_kg'].sum().reset_index()

    combined_data = pd.merge(data_science_avg, agriculture_production, left_on='work_year', right_on='year')

    salary_production_fig = go.Figure()

    salary_production_fig.add_trace(go.Scatter(
        x=combined_data['work_year'],
        y=combined_data['salary_in_usd'],
        name='Salario promedio en Ciencia de Datos',
        line=dict(color='blue')
    ))

    salary_production_fig.add_trace(go.Scatter(
        x=combined_data['work_year'],
        y=combined_data['units_shipped_kg'],
        name='Producción agrícola',
        yaxis='y2',
        line=dict(color='green')
    ))

    salary_production_fig.update_layout(
        title=f"Relación entre Salarios de Ciencia de Datos y Producción Agrícola ({start_year}-{end_year})",
        xaxis_title="Año",
        yaxis_title="Salario promedio en Ciencia de Datos (USD)",
        yaxis2=dict(
            title="Producción agrícola (kg)",
            overlaying='y',
            side='right'
        ),
        legend_title="Métricas",
        hovermode="x unified"
    )

    correlation = combined_data['salary_in_usd'].corr(combined_data['units_shipped_kg'])

    salary_production_fig.add_annotation(
        x=0.95,
        y=0.95,
        xref="paper",
        yref="paper",
        text=f"Correlación: {correlation:.2f}",
        showarrow=False,
        font=dict(size=12),
        align="right",
        bgcolor="rgba(255, 255, 255, 0.8)"
    )

    tech_impact_fig = px.scatter(filtered_salary_data, 
                                 x='salary_in_usd', 
                                 y='experience_level', 
                                 size='salary_in_usd', 
                                 color='job_title',
                                 hover_name='job_title',
                                 title=f"Impacto de la Inversión en Tecnología en la Producción Agrícola ({start_year}-{end_year})")

    job_distribution = filtered_salary_data['job_title'].value_counts()
    top_6_jobs = job_distribution.nlargest(6)
    otros = pd.Series({'Otros': job_distribution.iloc[6:].sum()})
    job_distribution_final = pd.concat([top_6_jobs, otros])
    
    job_distribution_fig = px.pie(values=job_distribution_final.values, 
                                  names=job_distribution_final.index, 
                                  title=f"Distribución de Empleos en Agro-Tech y Ciencia de Datos ({start_year}-{end_year})")
    
    return world_map_fig, salary_production_fig, tech_impact_fig, job_distribution_fig

app.layout = html.Div([
    html.Div([
        html.H1("El Amanecer del Agro-Tech y la Ciencia de Datos: Salvando al Mundo del Colapso Climático",
                style={'textAlign': 'center', 'color': '#2C3E50', 'fontFamily': 'Arial, sans-serif'}),
    ], style={'backgroundColor': '#ECF0F1', 'padding': '20px', 'marginBottom': '20px'}),
    
    dcc.RangeSlider(
        id='year-slider',
        min=2020,
        max=2024,
        step=1,
        marks={i: str(i) for i in range(2020, 2025)},
        value=[2020, 2024]
    ),
    
    html.Div([
        html.Div([
            html.H2("Capítulo 1: El Colapso de los Sistemas Tradicionales de Agricultura",
                    style={'color': '#34495E', 'fontFamily': 'Arial, sans-serif'}),
            dcc.Graph(id='world-map')
        ], className='six columns'),
        
        html.Div([
            html.H2("Capítulo 2: La Rebelión de la Agro-Tech y la Ciencia de Datos",
                    style={'color': '#34495E', 'fontFamily': 'Arial, sans-serif'}),
            dcc.Graph(id='salary-production')
        ], className='six columns'),
    ], className='row'),
    
    html.Div([
        html.Div([
            html.H2("Capítulo 3: La Fusión de Inteligencias: Humanos y Máquinas al Rescate de la Agricultura",
                    style={'color': '#34495E', 'fontFamily': 'Arial, sans-serif'}),
            dcc.Graph(id='tech-impact')
        ], className='six columns'),
        
        html.Div([
            html.H2("Capítulo 4: El Futuro de la Alimentación: Granjas Inteligentes y la Conquista del Hambre Global",
                    style={'color': '#34495E', 'fontFamily': 'Arial, sans-serif'}),
            dcc.Graph(id='job-distribution')
        ], className='six columns'),
    ], className='row'),
], style={'backgroundColor': '#F7F9F9', 'padding': '20px'})

@app.callback(
    [Output('world-map', 'figure'),
     Output('salary-production', 'figure'),
     Output('tech-impact', 'figure'),
     Output('job-distribution', 'figure')],
    [Input('year-slider', 'value')]
)
def update_graphs(years):
    start_year, end_year = years
    return create_graphs(start_year, end_year)

if __name__ == '__main__':
    app.run_server(debug=True)
