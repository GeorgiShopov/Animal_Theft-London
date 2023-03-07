import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
import streamlit as st
from geopy.geocoders import Nominatim
import time

link="https://data.london.gov.uk/download/mps-stolen-animals-dashboard-data/5831fb56-e29f-467e-a16e-c9bcc6340468/Stolen%20Animals%20December%202023.csv"
data=pd.DataFrame()
data = pd.read_csv(link)

@st.cache
def load_data():
    ###DATA###MANIPULATION
    #converting data types
    data['Count of Stolen Animals'] = data['Count of Stolen Animals'].astype(int)
    data['Year and Month'] = pd.to_datetime(data['Year and Month'], format='%b-%Y')
    data['Type of Animal'] = data['Type of Animal'].astype('category')
    data['Borough'] = data['Borough'].astype('category')
    data['Type Of Offence'] = data['Type Of Offence'].astype('category')
    data['Animal Recovered'] = data['Animal Recovered'].astype('category')
    #renaming
    data.rename(columns={'Count of Stolen Animals':'count',
                        'Year and Month':'date',
                        'Type of Animal':'animal',
                        'Type Of Offence':'offence',
                        'Animal Recovered':'status',
                        'Borough':'borough'}, 
                inplace=True)

    #sorting
    data.sort_values(by='date', ascending=True, inplace=True)

    #more features
    data['year'] = data['date'].dt.year
    data['month_int'] = data['date'].dt.month
    data['month_str'] = data['date'].dt.strftime('%B')

    #cleaning some data
    data['animal'] = data['animal'].str.strip()
    data['animal'] = data['animal'].str.title()
    data['animal'] = data['animal'].replace('Mammal (Exc Cat And Dog)', "Other mammal")

    #reseting index
    data.reset_index(drop=True,inplace=True)
    ### Outlier care
    data.iloc[4807,0] = 100 #to correct the value according the city news
    #or 
    # no_outlier = data["count"] <= 200
    # data[no_outlier]
    return data
data = load_data()

#lists for filters
y=data.year.unique().tolist()
b=data.borough.unique().tolist()
b.append('All')
b.sort()
a=['Dog','Cat','Bird','Fish','Other mammal']
a.append('All')
a.sort()

#generating geolocation data for boroughs
#Table name "geo"
geolocator = Nominatim(user_agent="geoapiExercises")
latitude = []
longitude = []
borough_= []
bb=data['borough'].unique().tolist()
geo=pd.DataFrame(columns=['borough','latitude','longitude'])

@st.cache
def locations():
    for bo in data['borough'].unique().tolist():
        borough_.append(bo)
        latitude.append(geolocator.geocode(bo + ", London, UK").latitude)
        longitude.append(geolocator.geocode(bo + ", London, UK").longitude)
    geo['borough'] = borough_
    geo['latitude'] = latitude
    geo['longitude'] = longitude
    return geo

with st.spinner("Loading..."):
    geo = locations()

# geo[['borough','latitude','longitude']].sample(n=4)
del latitude,longitude

#defining a function to crunch the table
@st.cache(allow_output_mutation=True)
def data_(yr=[2017,2019], borough='All', animal='All', groupby=None, agg=None):
    """
    Filter data based on year range, borough and animal type and group the filtered data by desired columns and aggregations.
    
    Parameters:
    yr (List[int]): List of integers representing the year range to filter the data. Default is [2017,2019].
    borough (str): String representing the desired borough to filter the data. Default is 'All'.
    animal (str): String representing the desired animal type to filter the data. Default is 'All'.
    group_by (List[str]): List of strings representing the columns to group the filtered data by. Default is None.
    aggregation (dict): Dictionary representing the aggregation method for each column. Default is None.
    
    Returns:
    filtered_df (pandas DataFrame): The filtered dataframe based on the provided arguments.
    
    Example:
    filtered_df = filter_data(yr=[2018,2019], borough='Westminster', animal='Dog', group_by=['Borough', 'Year'], aggregation={'count': 'sum'})
    """

    filtered_df = data[(data['year'] >= yr[0]) & (data['year'] <= yr[1])]
    if borough != 'All':
        filtered_df = filtered_df[filtered_df['borough'] == borough]
    if animal != 'All':
        filtered_df = filtered_df[filtered_df['animal'] == animal]
        
    if groupby:
        filtered_df = filtered_df.groupby(groupby).agg(agg)
        filtered_df.reset_index(inplace=True)
    
    return filtered_df

offence_meta = {
"Theft and Handling" : "involves taking property or goods without the owner's consent, or dishonestly receiving or retaining stolen goods.",
"Burglary" : "involves entering a building as a trespasser with the intent to steal.",
"Robbery" : "involves using force or the threat of force to take property from someone.",    
"Violence Against the Person" : "involve acts of violence committed against individuals.",
"Criminal Damage" : "involves intentionally or recklessly damaging property.",
"Other Notifiable Offences" : "are incidents that must be reported to the police.",
"Sexual Offences" : "had 3 incidents, which involves crimes related to sexual assault or exploitation.",
"Fraud or Forgery" : "involves crimes related to deceit, such as counterfeiting or forging documents."
}

###SIDEBAR###

st.sidebar.write('⚙️ **Control Panel**')
#mode
mode=st.sidebar.radio('mode:',('Report','Dashboard'),help="Switch between **Report** and **Dashboard** mode. \n\n **Report** - text and visualization.\n\n **Dashboard** - visualizations only.")

#select borough dropdown :
boro = st.sidebar.selectbox('Borough', (b), help='Filter data by Borough.')

#select animal dropdown
ani = st.sidebar.selectbox('Animal',(a), help='Filter data by animal')

#years slider
from2y = st.sidebar.slider(label = 'Select a range of years',
                    min_value=int(data['year'].min()), 
                    max_value=int(data['year'].max()), 
                    value=(2015, 2023),
                    step=1,
                    help='Filter data by selecting range of years between 2010 and 2023'
                     )

#credits
credits = st.sidebar.checkbox('Credits & Info')
if credits:
    # st.sidebar.write("This is some extra information that is not available yet.")
    
    st.sidebar.write('Data Source:')
    st.sidebar.image('https://data.london.gov.uk/wp-content/themes/bulma-london/img/brand-logo.png.')
    # 'https://data.london.gov.uk/dataset/mps-stolen-animals-dashboard-data'
    st.sidebar.write('')
    st.sidebar.write('Data Author:')
    st.sidebar.image('https://airdrive-images.s3-eu-west-1.amazonaws.com/london/img/publisher/2018-05-25T16%3A53%3A38.77/mps.png')
    st.sidebar.write('')
    
    st.sidebar.write('Analysis & Visualization:')
    # st.sidebar.write('### **Georgi Shopov** for')
    sm1 = "[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/shopovgeorgi/)"
    sm2 = "[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/shopovgeorgii)"

    st.sidebar.write('# **Georgi Shopov**\n\n',sm1,sm2)
    st.sidebar.image('default.png.')
    sm3 = "[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/company/datascigonewild)"
    sm4 = "[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/datascigonewild)"
    st.sidebar.write(sm3,sm4)
    # st.sidebar.title('Data Sciene Gone Wild')

###END###OF###SIDE###BAR###

###VISUALIZATIONS

#bar chart name: m2m
m_totals = data_(yr=[from2y[0],from2y[1]], 
                 borough= boro, 
                 animal= ani,
                 groupby= ['date'], 
                 agg = {'count': ['sum']})

m_totals.columns = ['date', 'count']


m2m = go.Figure()
m2m.add_trace(go.Bar(x=m_totals["date"], 
                     y=m_totals['count'],
                     marker_color=m_totals['count'],
                     marker=dict(colorscale='Cividis'),
                     hovertemplate='<b>%{x}</b><br><b>%{y}</b> stolen animals<extra></extra>'))
m2m.update_layout(title_text="Animal Theft - month to month",
                  template='xgridoff')
m2m.update_traces(hoverlabel=dict(font=dict(size=16)))

#line chart name: time_line
time_line = go.Figure()
time_line.add_trace(go.Scatter(x=m_totals['date'], 
                               y=m_totals['count'],
                               mode="markers+lines" ,
                               marker=dict(size=4,
                                           opacity=1,
                                           color=m_totals['count'],
                                           colorscale='Cividis'),
                               line=dict(shape='spline',color='grey',),
                               hovertemplate='<b>%{x}</b><br><b>%{y}</b> stolen animals<extra></extra>'))
time_line.update_layout(
        title='Timeline',
        showlegend=False,
        template='xgridoff',
        )
time_line.update_traces(hoverlabel=dict(font=dict(size=16)))


#time heatmap
time = data_(yr=[from2y[0],from2y[1]], 
             animal=ani,
             borough=boro,
             groupby= ['date','year','month_str'], 
             agg = {'count': ['sum']})
time.columns = ['date', 'year', 'month', 'count']
time.sort_values(by='date', inplace=True, ascending=True)

times = go.Figure(go.Heatmap(
        x=time['year'],
        y=time['month'],
        z=time['count'],
        xgap=0.05,
        ygap=0.05,
        colorscale='Cividis',
        hovertemplate='%{y}<b> %{x}</b><br><b>%{z}</b> stolen animals<extra></extra>'))

times.update_layout(
    title='Time Heatmap',
    template='xgridoff',
    xaxis=dict(
        range=[min(data['year']), max(data['year'])],  # specify x-axis range
        tickvals=data['year'].unique(),                # specify tick values
        tickmode='array',                              # use array mode for tick values
        ticktext=[str(year) for year in data['year'].unique()]  # specify text labels for tick values
    )
)
times.update_traces(hoverlabel=dict(font=dict(size=16)))


# y2y - Year to year
years = data_(yr=[from2y[0],from2y[1]], 
              borough= boro, 
              animal= ani,
              groupby= ['year'], 
              agg = {'count': ['sum']})
years.columns = ['year', 'sum']

y2y = go.Figure()
y2y.add_trace(go.Bar(x=years["year"], 
                     y=years['sum'],
                     marker_color=years['sum'],
                     marker=dict(colorscale='Cividis'),
                     hovertemplate='<b>%{y}</b> stolen animals in <b>%{x}</b><extra></extra>'))
y2y.update_layout(title_text="Stolen animals - year to year",
                  template='xgridoff')
y2y.update_traces(hoverlabel=dict(font=dict(size=16)))

#by month
months = data_(yr=[from2y[0],from2y[1]], 
               borough= boro, 
               animal= ani,
               groupby= ['month_int','month_str'], 
               agg = {'count': ['sum']})
months.columns = ['m_num', 'month', 'sum']
bymonth = go.Figure()
bymonth.add_trace(go.Bar(x=months["month"], 
                     y=months['sum'],
                     marker_color=months['sum'],
                     marker=dict(colorscale='Cividis'),
                     hovertemplate='<b>%{y}</b> stolen animals in <b>%{x}</b><br><i>(for the selected period)</i><extra></extra>'))
bymonth.update_layout(title_text="Stolen by month.",
                      xaxis=dict(tickangle=-90),
                      template='xgridoff')
bymonth.update_traces(hoverlabel=dict(font=dict(size=16)))

#count by animal type
animal = data_(yr=[from2y[0],from2y[1]], 
               borough= boro, 
               groupby= ['animal'], 
               agg = {'count': ['sum']})
animal.columns = ['animal', 'sum']
animal.sort_values(by='sum', inplace=True, ascending=False)
animals = go.Figure()
animals.add_trace(go.Bar(x=animal["animal"], 
                     y=animal['sum'],
                     text=animal['sum'],
                     orientation='v',
                     marker_color=animal['sum'],
                     marker=dict(colorscale='Cividis'),
                     hovertemplate='<b>%{y}</b> stolen animals type <b>%{x}</b>)<extra></extra>'))
animals.update_layout(title_text="animals by type",
                  template='xgridoff')
animals.update_traces(hoverlabel=dict(font=dict(size=16)))

#pie chart
status = data_(yr=[from2y[0],from2y[1]], 
             groupby= ['status'], 
             borough= boro, 
             animal= ani,
             agg = {'count': ['sum']})
status.columns = ['status', 'sum']
status.sort_values(by='sum', inplace=True, ascending=False)
color_mapping = {'Not Recovered': 'black', 'Recovered': 'yellow'}
pie = px.pie(status, 
             values='sum', 
             names='status',
             color='status',
             color_discrete_map=color_mapping,
             )
            
pie.update_layout(title_text="% of recovered animals", 
                  template='xgridoff',
                  legend=dict(x=0.33, y=-0.1), 
                  legend_title_text="offence")
pie.update_traces(hovertemplate='<b>%{value}</b> stolen animals<br>were <b>%{label}</b><extra></extra>',hoverlabel=dict(font=dict(size=16)))

#sankey rec flow
ani_rec = data_(yr=[from2y[0],from2y[1]], 
                borough= boro, 
                groupby= ['animal','status'], 
                agg = {'count': ['sum']})
source = ani_rec['animal']
target = ani_rec['status']
value = ani_rec['count']
labels = list(set(source) | set(target))

node_color = ['darkblue' if label in source.tolist() else 'yellow' if ani_rec.loc[ani_rec['status'] == label, 'status'].iloc[0] == 'Recovered' else 'black' for label in labels]

node = dict(pad=25, thickness=20, 
            line=dict(color="black", width=0.5), 
            label=labels, color=node_color)
link = dict(source=[labels.index(s) for s in source], target=[labels.index(t) for t in target], value=value)

layout = go.Layout(font=dict(size=16))
rec_flow = go.Figure(data=[go.Sankey(node=node, 
                     link=link)], 
                     layout=layout,
                     )
rec_flow.update_traces(hoverlabel=dict(font=dict(size=16)))


#by offence type
offence = data_(yr=[from2y[0],from2y[1]], 
                borough= boro, 
                animal= ani,
                groupby= ['offence'], 
                agg = {'count': ['sum']})
offence.columns = ['offence', 'count']
offence.sort_values(by='count', inplace=True, ascending=True)

offences = go.Figure()
offences.add_trace(go.Bar(x=offence["count"], 
                     y=offence['offence'],
                     text=offence['offence'],
                     orientation='h',
                     marker_color=offence['count'],
                     marker=dict(colorscale='Cividis'),
                     hovertemplate='<b>%{x}</b> animals were stolen in <b>%{y}</b>)<extra></extra>'))
offences.update_yaxes(showticklabels=False)
offences.update_layout(#title_text="Offence by type",
                  template='xgridoff')

offences.update_layout(
        yaxis=dict(
        tickfont=dict(size=17))
    )

offences.update_traces(hoverlabel=dict(font=dict(size=16)))

#offence-offence split sankey
offence_split= data_([from2y[0],from2y[1]], 
                borough= boro, 
                groupby= ['animal','offence'], 
                agg = {'count': ['sum']})

source = offence_split['animal']
target = offence_split['offence']
value = offence_split['count']
labels = list(set(source) | set(target))
node = dict(pad=25, thickness=20, 
            line=dict(color="black", width=0.5), 
            label=labels, color=node_color)
link = dict(source=[labels.index(s) for s in source], target=[labels.index(t) for t in target], value=value)
layout = go.Layout(font=dict(size=16))
o_split = go.Figure(data=[go.Sankey(node=node, link=link)], layout=layout)
o_split.update_traces(hoverlabel=dict(font=dict(size=16)))

###boroughs
borough = data_(yr=[from2y[0],from2y[1]], 
                animal= ani,
                groupby= ['borough'], 
                agg = {'count': ['sum']})
borough.columns = ['borough', 'count']
borough.sort_values(by='count', inplace=True, ascending=False)
borough = pd.merge(borough, geo, how='left', on='borough')

boroughs = go.Figure()
boroughs.add_trace(go.Bar(x=borough["borough"], 
                     y=borough['count'],
                     text=borough["count"],
                     textfont=dict(size=20),
                     orientation='v',
                     marker_color=borough['count'],
                     marker=dict(colorscale='Cividis'),
                     hovertemplate='<b>%{y}</b> animals were stolen in <b>%{x}</b>)<extra></extra>'))
boroughs.update_yaxes(showticklabels=False)
boroughs.update_layout(#title_text="count by borough",
                  template='xgridoff',
                  height=500,
                  xaxis=dict(tickangle=-90),
                      ) #width=900,
boroughs.update_layout(
    xaxis=dict(
        tickfont=dict(size=17)
    )
)
boroughs.update_traces(hoverlabel=dict(font=dict(size=16)))

###map
map = go.Figure(go.Scattermapbox(
    lat=borough['latitude'],
    lon=borough['longitude'],
    mode='markers',
    marker=dict(size=borough['count']/8, 
#                 color='red',
                color=borough['count'], 
                colorscale='Cividis', 
                opacity=0.9,
                # colorbar=dict(title='Count')
                ),
    text=borough[['borough', 'count']].apply(lambda x: '<br>'.join(x.astype(str)), axis=1),
    
))

map.update_layout(title_text="Theft Map",
                template='xgridoff',
                mapbox=dict(
                    style="stamen-toner",
                    center=dict(lat=51.5074, lon=-0.1278),
                    zoom=9),
                height=600,
               # width=900           
                )
map.update_traces(hoverlabel=dict(font=dict(size=16,color="black")))


###LAYOUT
# st.title('The Stolen Animals of London')
st.markdown("<h1 style='text-align: center;'>The Stolen Animals of London</h1>", unsafe_allow_html=True)

st.image('mapcover2.png')
# st.header('12 Years of Animal Theft Visualized 📊')
# st.markdown("<h3 style='text-align: center;'></h1>", unsafe_allow_html=True)
st.write('')
# st.subheader('Welcome to the Animal Theft Reporting Dashboard!')

if mode == 'Dashboard':
    pass
else:
    with st.expander("**About.**"):
        st.write("This interactive mini report provides a visual representation of the theft of different types"
            " of animals in London over the course of 12 years. \n\nThe dashboard allows you to explore "
            "various aspects of animal theft, including the types of animals that are most frequently "
            "targeted, the boroughs that experience the highest levels of theft, and more.\n\n"
            "The settings in the sidebar allow you to filter the data by different criteria and control the flow of "
            "information that you see and the insights that you gain. \n\nWhether you are a concerned citizen, a "
            "local authority, pet insurer, or an animal welfare organization, this dashboard offers valuable information "
            "and insights into the ongoing problem of animal theft.\n\n"
            "While Animal theft is a global problem, the provided information is at a local level - **London, UK.**")

    # st.info('This is a purely informational message', icon="ℹ️")

    st.write("<span style='font-size: 20px'>💭 **Animal theft**, refers to *the act of illegally taking or removing an animal from its rightful owner or custodian without their permission or consent.* This can include stealing pets from homes, farms or other locations, as well as taking wild animals from their natural habitats. Animal theft is considered a crime in many jurisdictions and can result in legal penalties, including fines and imprisonment.</span>", unsafe_allow_html=True)

    st.write("<span style='font-size: 20px'>This type of crime can be considered a violation of both **animal rights** and **human rights**, depending on "
            "the specific circumstances. \n\n <span style='font-size: 20px'>From an animal rights perspective, the theft of animals can be seen as "
            "a violation of the animal's right to live freely and to be protected from harm. It can also be seen "
            "as a form of exploitation, as the stolen animal is often used for financial gain or personal pleasure"
            " without regard for its well-being.</span>", unsafe_allow_html=True)

    st.write("<span style='font-size: 20px'>From a human rights perspective, the theft of animals can be seen as a violation of the right to "
            "private property, as many animals are considered property under the law. It can also be seen as a "
            "threat to public safety, as stolen animals may be more likely to carry diseases or exhibit aggressive"
            " behavior due to the stress and trauma of the theft.</span>", unsafe_allow_html=True) #, icon="💭"

    st.write("<span style='font-size: 20px'>Animal theft is a serious issue in England and Wales, and it is governed by the *Theft Act 1968*, which makes it an offense to steal an animal. Despite this law, some campaigners have argued that the penalties for animal theft are not severe enough, and have called for tougher sentences. However, it is unclear whether these penalties are enough to deter criminals from committing this crime. To better understand the extent of animal theft and its impact, let's explore some data visualizations.</span>", unsafe_allow_html=True)


# data
yyyy=len(data_(yr=[from2y[0],from2y[1]])['year'].unique().tolist())
st.markdown(f"<h2 style='text-align: center;'>{yyyy} Years of Animal Theft Visualized</h1>", unsafe_allow_html=True)


tab1, tab2 = st.tabs(["📊", "📈"])
tab1.plotly_chart(m2m)
tab2.plotly_chart(time_line)


# st.plotly_chart(m2m)

col0,col1, col2, col3, col4, col5, col6 = st.columns([1,2,2,2,2,2,2])
col1.metric(label="**TOTAL**", value=m_totals['count'].sum())
col2.metric(label="**MINIMUM**", value=m_totals['count'].min())
col3.metric(label="**AVERAGE**", value=int(m_totals['count'].median()))
col4.metric(label="**MAXIMUM**", value=m_totals['count'].max())
col5.metric(label="**LAST MONTH**",value=m_totals['count'][-1:])
col6.metric(label="**LAST 6M**", value=m_totals['count'][-6:].sum())

# st.metric(label="Total", value=m_totals['count'].sum())


col1, col2 = st.columns([1,1])

col1.plotly_chart(y2y,use_container_width=True)
col2.plotly_chart(bymonth,use_container_width=True)

if mode == 'Dashboard':
    pass
else:
    st.write(f"<span style='font-size: 20px'>**{years.sort_values(by='sum', ascending=False).iloc[0]['year']}** and \
    **{years.sort_values(by='sum', ascending=False).iloc[1]['year']}** were the worst years for the period \
    with **{years.iloc[0:2]['sum'].sum()}**.</span>", unsafe_allow_html=True)
    st.write(f"<span style='font-size: 20px'>**{', '.join(months.sort_values(by='sum', ascending=False).iloc[0:4]['month'].tolist())}** seem to be \
    riskiest months for animals and their human friends.</span>", unsafe_allow_html=True)

st.plotly_chart(times)

if mode == 'Dashboard':
    pass
else:
    st.write("<span style='font-size: 20px'>The **stolen pets black market** is a growing illegal industry that involves the theft of pets for "
            "the purpose of selling them for profit. In many cases, stolen pets are resold to unsuspecting "
            "buyers through online marketplaces or even in physical pet stores. The pets may be used for "
            "breeding or other commercial purposes, or they may be kept as pets by the thieves themselves.</span>", unsafe_allow_html=True)


    col1, col2 = st.columns([2,1])
    col1.title('What animals got missing?')
    col2.title('Black market pie')

tab1,tab2 = st.tabs(["📊", "🔀"])
col1, col2 = tab1.columns([2,1])
col2.write('')
col1.plotly_chart(animals,use_container_width=True)
col2.plotly_chart(pie,use_container_width=True)
tab2.plotly_chart(rec_flow,use_container_width=True)

if mode == 'Dashboard':
    pass
else:
    st.write(f"<span style='font-size: 20px'>⚖️ Only **{status.iloc[1]['sum']}** animals found their way home for the past **{len(set(years['year']))}** years. This is **{int(status.iloc[1]['sum']/status['sum'].sum()*100)}%** of **{status['sum'].sum()}** stolen. 🎯 Top targeted animal for the period is **{animal.iloc[0]['animal']}** with **{animal.iloc[0]['sum']}** incidents, followed by **{', '.join(animal.iloc[1:4]['animal'].to_list())}**.</span>", unsafe_allow_html=True)
    # st.title("")


if mode == 'Dashboard':
    pass
else:
    st.write("<span style='font-size: 20px'>The impact of the stolen pets black market can be devastating for pet owners who have had their "
            "beloved animals stolen. The emotional toll of losing a pet can be significant, and the financial " 
            "burden of trying to find and recover a stolen pet can also be considerable. Also, the "
            "conditions in which stolen pets are often kept can be inhumane and potentially dangerous for the "
            "animals or their owners.</span>", unsafe_allow_html=True)
    
    st.write("<span style='font-size: 20px'>Stolen pets may be used in illegal "
        "animal experimentation or as bait animals for training fighting dogs."
        "Animal theft represents a complex and multifaceted issue that involves a range of ethical, legal,"
        " and social considerations. It represents a violation of the sanctity and safety of a home, "
        "and the bond between humans and their pets. \n\n<span style='font-size: 20px'>The theft of animals can also be symbolic of the "
        "power dynamics in society, with the weaker and more vulnerable members being preyed upon by those "
        "with more strength and resources. It can also represent the larger issue of exploitation and "
        "disregard for the welfare of other living beings.</span>", unsafe_allow_html=True)

col1, col2 = st.columns([1,1])
col1.title('How about how?')
col1.plotly_chart(offences,use_container_width=True)

if mode == 'Dashboard':
    col2.title('')
    col2.title('')
    col2.header('')

    col2.plotly_chart(o_split,use_container_width=True)
else:
    col2.title('Top 2 Theft Scenarios')
    col2.write(f"<span style='font-size: 20px'>The most common type of offence is **{offence.iloc[-1]['offence']}** with \
    **{offence.iloc[-1]['count']}** incidents. This type of crime {offence_meta[offence.iloc[-1]['offence']]} </span>", unsafe_allow_html=True)
    col2.write(f"<span style='font-size: 20px'>**{offence.iloc[-2]['offence']}** had the second highest count with \
    **{offence.iloc[-2]['count']}** cases. This type of crime {offence_meta[offence.iloc[-2]['offence']]} </span>", unsafe_allow_html=True)

if mode == 'Dashboard':
    pass
else:
    st.write("<span style='font-size: 20px'>🌟 It is important for pet owners to take steps to protect their pets from theft, such as keeping "
    "them indoors or in a secure area when unattended, ensuring they have proper identification, and being "
    "cautious when interacting with strangers who express interest in their pets. Being informed about the "
    "issue of stolen pets and the existence of the black market can also help pet owners take appropriate "
    "precautions and advocate for stronger laws and enforcement against this illegal activity. </span>", unsafe_allow_html=True)

st.title('Borough cases')
tab1,tab2=st.tabs(['📊','🌐'])
tab1.plotly_chart(boroughs,use_container_width=True)
tab2.plotly_chart(map,use_container_width=True)

if mode == 'Dashboard':
    pass
else:
    st.write(f"<span style='font-size: 20px'>⚠️ **{', '.join(borough.iloc[0:5]['borough'].to_list())}** appear to be the most dangerous boroughs of London \
    with **{borough.iloc[0:5]['count'].sum()}** incidents for the period. </span>", unsafe_allow_html=True)

    st.write(f"<span style='font-size: 20px'>✅ On the other hand, **{', '.join(borough.iloc[-5:-1]['borough'].to_list())}** are the boroughs \
    with lowest count of animal theft cases, leaded by **{borough.iloc[-1]['borough']}** which seems to be the safest. </span>", unsafe_allow_html=True)

    st.write("<span style='font-size: 20px'>Crime is an undeniable truth that affects every part of our society, and regardless of how we approach it, "
             "it remains a daunting challenge. It can be easy to classify London's boroughs into 'safe' and 'dangerous' labels"
             " based on the reported incidents of animal theft, but that approach may miss the subtleties of the issue. We must "
             "delve deeper and gain a profound understanding of the intricate factors that contribute to the incidence of animal "
             "theft in each borough. These factors could include complex socioeconomic factors, such as poverty and unemployment rates, "
             "as well as the availability of resources for law enforcement and community support programs. </span>", unsafe_allow_html=True)
    st.subheader('Aftermath')
    st.write("<span style='font-size: 20px'>Every day **1** or **2** dogs get stolen in London. Only **11%** of all stolen dogs got back home since 2018 "
             "and roughly that much since 2010. And it's not just dogs - **cats**, **birds**, **fish**, and **other animals**.\n\n"
            "<span style='font-size: 20px'>On a broader societal level, pet theft can lead to an increase in crime and a loss of public trust "
            "in law enforcement. It can also contribute to the spread of illegal activities such as dogfighting "
            "and the breeding of animals in inhumane conditions.\n\n"
            "<span style='font-size: 20px'>In order to prevent increasing animal theft in London, new laws and restrictions have been put in place."
            " such as giving harsher sentences to the convicted, and increasing rewards for anyone providing useful information.\n\n"
            "<span style='font-size: 20px'>In October 2020, the UK government announced plans to introduce tougher sentences for animal abusers, "
            "which could include up to **5 years in jail**. It was unclear whether this will also apply to animal theft.\n\n"
            "<span style='font-size: 20px'>The government has also set up a *Pet Theft Taskforce*, which aims to identify ways to tackle the problem "
            "of pet theft and to raise awareness of the issue. The task force is made up of government officials, "
            "police, and representatives from animal welfare organizations.\n\n"
            "<span style='font-size: 20px'>Eventually, the UK government introduced the *Animal Welfare (Sentencing) Act 2021*, which increases "
            "the maximum sentence for animal cruelty from **6 months** to **5 years** in prison. This act could be "
            "relevant in cases where animal theft involves mistreatment or abuse of the stolen animal.\n\n"
            "<span style='font-size: 20px'>The fight against animal theft is ongoing, and progress may be slow, but we must remain committed to the cause. "
             "By raising awareness, advocating for change, and working with law enforcement and animal welfare organizations, "
             "we can make a difference. And while the solution may not be simple or straightforward, we must remember that every "
             "little bit helps. Whether it's reporting suspicious activity or simply choosing not to buy a stolen animal, we can "
             "all do our part to make our communities safer.</span>", unsafe_allow_html=True)
    
    st.write("<span style='font-size: 20px'>If you got your animal lost or stolen, also make sure you visit any of the following organizations who list found animals that were not necessarely stolen.</span>", unsafe_allow_html=True)
    
    with st.expander('**links**'):
        'The RSPCA https://www.rspca.org.uk/'
        'The Blue Cross (https://www.bluecross.org.uk/'
        'The Battersea Dogs and Cats Home https://www.battersea.org.uk/'
        'The Animal Welfare Foundation https://www.animalwelfarefoundation.org.uk/'
        '**extra information**'
        'Stolen Animals data https://data.london.gov.uk/dataset/mps-stolen-animals-dashboard-data'
        'The Metropolitan Police https://www.met.police.uk/'
        'Animal welfare Act 2006 https://www.legislation.gov.uk/ukpga/2006/45/contents'
        'Animal welfare Gov.uk https://www.gov.uk/guidance/animal-welfare'
        'Expenditure incurred and prosecutions taken under the Animal Health Act 1981. https://www.gov.uk/government/publications/section-80-report-for-2021-under-the-animal-health-act-1981'

    st.write('#DataScience #DataAnalysis #DataVisualization #Dashboards #Reports \n\n#Streamlit #Python #Plotly \n\n#London #OpenData #Crime #AnimalTheft #Dashboards #PublicSafety \n\n#DataSciGoneWild')
    
