import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import plotly.express as px
import plotly.figure_factory as ff

st.set_page_config(page_title="Week 3: Data Visualization", 
                   page_icon="📊",
                   layout="wide",
                   initial_sidebar_state="expanded")

# Hide Streamlit's default menu and footer
st.markdown("""
<style>
    body {
        background-color: #f0f2f6;
    },
    
    .st-emotion-cache-1aplgmp.e1haskxa15 {
        visibility: hidden;
    }
</style> 
""", unsafe_allow_html=True)

movie_ratings_df = pd.read_csv("./data/cleaned_movie_ratings.csv", parse_dates=['timestamp'])
movie_ratings_df['year'] = movie_ratings_df['year'].astype(int)
movie_ratings_df['genre'] = movie_ratings_df['genre'].astype('category')


alt.themes.enable("dark")


with st.sidebar:
    st.title("Movie Ratings Dashboard")
    year_list = sorted(movie_ratings_df['year'].unique().tolist())
    year_list.insert(0, "All")
    selected_year = st.selectbox("Select Year", year_list, index=0)

    genre_list = sorted(movie_ratings_df['genre'].unique().tolist())
    genre_list.insert(0, "All")
    selected_genre = st.selectbox("Select Genre(s)", genre_list, index=0)
    min_rating, max_rating = st.slider("Select Rating Range", 0.0, 10.0, (0.0, 10.0), 1.0)

# Filter the dataframe for use with the sidebar

filtered_df = movie_ratings_df.copy()

if selected_year != 'All':
    filtered_df = filtered_df[filtered_df['year'] == selected_year]

if selected_genre != 'All':
    filtered_df = filtered_df[filtered_df['genre'] == selected_genre]

filtered_df = filtered_df[(filtered_df['rating'] >= min_rating) &
                (filtered_df['rating'] <= max_rating)]

with st.expander("View Raw Data Sample"):
    st.dataframe(filtered_df.head())

col1, col2, col3, col4 = st.columns(4)

# These are my KPIs: 

# KPI 1: Total Rated Movies
total_movies = filtered_df['title'].nunique()
col1.metric("Total Unique Movies: ", f"{total_movies:,}")

# KPI 2: Total Ratings
total_ratings = len(filtered_df)
col2.metric(f"Total Ratings Given: ", f"{total_ratings:,}")

# KPI 3: Overall Mean Rating
overall_mean_rating = filtered_df['rating'].mean()
col3.metric(f"Overall Mean Rating: ", f"{overall_mean_rating:.2f}")

# KPI 4: Most Active Year
active_year = filtered_df.groupby('year')['rating'].count().idxmax()
col4.metric(f"Most Active Year: ",f"{active_year}")

st.divider()

main_col1, main_col2 = st.columns([2, 3])

with main_col1:
    # Question 2: Which genres have the highest viewer satisfaction (highest ratings)?
    st.subheader("Top 3 Genres with the Highest Viewer Satisfaction")

    # Top 3 Genres with the Highest Viewer Satisfaction
    genre_mean_ratings_df = filtered_df.groupby('genre')['rating'].mean().reset_index()
    top_3_genres = genre_mean_ratings_df.sort_values('rating', ascending=False).head(3)

    # Base Bar Chart
    base = alt.Chart(top_3_genres).encode(
        x=alt.X('genre:N', title='Genre', sort='-y'),
        y=alt.Y('rating:Q', title='Mean Rating'), 
        tooltip=['genre', alt.Tooltip('rating', format='.2f')]
    )

    # Bar layer with fixed color
    bar = base.mark_bar().encode(

        color=alt.value("darkred")
    )

    # Text layer for mean rating value
    text = base.mark_text(
        align='center',
        baseline='bottom',
        dy=-5,  # Nudge text up
        color='white' # Better contrast
    ).encode(
        text=alt.Text('rating', format=".2f"),
    )

    chart_final = (bar + text).properties(
        title='3 Genres with the Highest Mean Rating'
    )

    st.altair_chart(chart_final, use_container_width=True)


with main_col2:
    # Question 3: How does mean rating change across movie release years?
    # min_year, max_year = movie_ratings_df['year'].min() - 10, movie_ratings_df['year'].max() + 10
    yearly_mean_ratings = filtered_df.groupby('year')['rating'].mean().reset_index()

    base = alt.Chart(yearly_mean_ratings).encode(
        x=alt.X('year:Q', title='Release Year'),
        y=alt.Y('rating:Q', title='Mean Rating'),
        tooltip=[alt.Tooltip('year', title='year'), alt.Tooltip('rating', format='.2f', title='Mean Rating')]
                 ).properties(title='Mean Rating Trend by Release Year')

    line = base.mark_line(color='green').interactive()
    points = base.mark_point(filled=True, color='green')

    st.altair_chart((line+points).interactive(), use_container_width=True)

st.divider()

detail_col1, detail_col2 = st.columns([4, 6])

with detail_col1:
    # Question 1: What's the breakdown of genres for the movies that were rated?
    genre_counts_df = filtered_df['genre'].value_counts().reset_index()
    genre_counts_df.columns = ['Genre', 'Count']
    st.subheader("Breakdown of Genres for Rated Movies")
    genre_chart = px.bar(
        genre_counts_df.sort_values('Count', ascending=True),
        x='Count', y='Genre', orientation='h',
        title='Total Number of Ratings Per Genre',
        color='Count', color_continuous_scale='Plasma'
    )
    st.plotly_chart(genre_chart, use_container_width=True)


movie_stats = filtered_df.groupby('title').agg(
    mean_rating = ('rating','mean'),
    rating_count = ('rating', 'count'))
    
with detail_col2:
    # What are the 5 best-rated movies that have at least 50 ratings?
    top_movies_50_sorted = movie_stats[movie_stats['rating_count'] >=50].sort_values('mean_rating', ascending=False).head(5).reset_index()

    top_movies_50_chart = px.bar(
        top_movies_50_sorted,
        x='mean_rating',
        y='title',
        orientation='h',
        color='mean_rating',
        color_continuous_scale='Blues',
        title='Top 5 Movies with at least 50 Ratings',
        labels={'mean_rating': 'Mean Rating', 'title': 'Movie Title'},
        text='mean_rating'
    )

    top_movies_50_chart.update_layout(height=400)

    st.plotly_chart(top_movies_50_chart, use_container_width=True)

    st.markdown('---')

    # What are the 5 best-rated movies that have at least 150 ratings?
    top_movies_150_sorted = movie_stats[movie_stats['rating_count'] >= 150].sort_values('mean_rating', ascending=False).head(5).reset_index()

    top_movies_150_chart = px.bar(
        top_movies_150_sorted,
        x='mean_rating',
        y='title',
        orientation='h',
        color='mean_rating',
        color_continuous_scale='Reds',
        title='Top 5 Movies with at least 150 Ratings',
        labels={'mean_rating': 'Mean Rating', 'title': 'Movie Title'},
        text='mean_rating'
    )
    top_movies_150_chart.update_layout(height=400)
    st.plotly_chart(top_movies_150_chart, use_container_width=True)

st.divider()

st.subheader("Rater Demographics")
st.caption('Age Distribution of Users')

# Prepare the data as a clean Series or list for create_distplot
# We only need the actual age values, not a full DataFrame
user_age_values = filtered_df.drop_duplicates(subset=['user_id'])['age'].dropna().tolist()

if user_age_values:
    # Create the figure with the list of age values
    
    fig = ff.create_distplot(
        [user_age_values], 
        group_labels=['Rater Age'], 
        bin_size=2, 
        show_hist=True,
        show_rug=False
    )
    
    # Custom styling
    fig.update_layout(
        xaxis_title="Age",
        yaxis_title="Density / Frequency",
        title='Distribution of Rater Ages',
        template="plotly_white",
        showlegend=False
    )
    
    # Style the histogram (bars)
    fig.data[0].marker.color = '#4CAF50' # Green bars
    fig.data[0].opacity = 0.6
    
    # Style the KDE curve (the smooth line)
    # The KDE trace is fig.data[1]
    fig.data[1].line.color = 'darkred' 
    fig.data[1].line.width = 3

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No user age data available for the current filter selection.")