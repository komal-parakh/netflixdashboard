import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Netflix Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data # means the file is only loaded once — not on every user interaction
def load_data():
    df = pd.read_csv("netflix_titles.csv")
    df["country"] = df["country"].fillna("Unknown")
    df["listed_in"] = df["listed_in"].fillna("Unknown")
    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
    return df

df = load_data()

# ---------------- UI ----------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #FAFAFA;
    color: black;
}
[data-testid="stSidebar"] {
    background-color: #F0F0F0;
}
h1, h2, h3 {
    color: #E50914;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("Netflix Dashboard")

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Data Explorer", "Visualizations", "Insights", "Recommendation"]
)

st.sidebar.header("Filters")

year_range = st.sidebar.slider(
    "Year Range",
    int(df["release_year"].min()),
    int(df["release_year"].max()),
    (2010, 2020)
)

type_filter = st.sidebar.multiselect(
    "Type",
    df["type"].unique(),
    default=df["type"].unique()
)

genres = ["All"] + list(df["listed_in"].str.split(", ").explode().unique())
genre_filter = st.sidebar.selectbox("Genre", genres)

countries = ["All"] + list(df["country"].unique())
country_filter = st.sidebar.selectbox("Country", countries)

# ---------------- FILTER LOGIC ----------------
filtered_df = df[
    (df["release_year"].between(year_range[0], year_range[1])) &
    (df["type"].isin(type_filter))
]

if genre_filter != "All":
    filtered_df = filtered_df[
        filtered_df["listed_in"].str.contains(genre_filter)
    ]

if country_filter != "All":
    filtered_df = filtered_df[
        filtered_df["country"].str.contains(country_filter)
    ]

# ---------------- COMMON PLOT FUNCTION ----------------
def show_plot(fig):
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

# =========================================================
# 🏠 HOME
# =========================================================
if page == "Home":
    st.title("🎬 Netflix Dashboard")

    total = filtered_df.shape[0]
    movies = filtered_df[filtered_df["type"] == "Movie"].shape[0]
    tv = filtered_df[filtered_df["type"] == "TV Show"].shape[0]
    countries = filtered_df["country"].nunique()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Titles", total)
    col2.metric("Movies", movies)
    col3.metric("TV Shows", tv)
    col4.metric("Countries", countries)

    st.markdown("---")

    st.subheader("📈 Content Growth")

    growth = filtered_df.groupby("release_year").size()

    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(growth.index, growth.values, color = "red")
    ax.xlabel("Year")
    ax.ylabel("Titles")
    show_plot(fig)

# =========================================================
# 🔍 DATA EXPLORER
# =========================================================
elif page == "Data Explorer":
    st.title("🔍 Explore Data")

    search = st.text_input("Search Title")

    display_df = filtered_df.copy()

    if search:
        display_df = display_df[
            display_df["title"].str.contains(search, case=False, na=False)
        ]

    st.write("Results:", display_df.shape[0])
    st.dataframe(display_df, use_container_width=True)

# =========================================================
# 📊 VISUALIZATIONS
# =========================================================
elif page == "Visualizations":
    st.title("📊 Visualizations")

    col1, col2 = st.columns(2)

    # ---------- TOP GENRES ----------
    with col1:
        genres = filtered_df["listed_in"].str.split(", ").explode()
        top_genres = genres.value_counts().head(10)

        fig, ax = plt.subplots(figsize=(6,4))
        ax.barh(top_genres.index, top_genres.values, color = "#e67076") # horizontal bar chart
        ax.set_title("Top 10 Genres on Netflix")
        ax.set_xlabel("Number of Titles")
        ax.set_ylabel("Genres")
        ax.grid(True, linestyle="--", alpha=0.5)
        show_plot(fig)

    # ---------- RATINGS ----------
    with col2:
        ratings = filtered_df["rating"].value_counts()

        fig, ax = plt.subplots(figsize=(6,4))
        ax.bar(ratings.index, ratings.values, color = "#e67076")
        ax.set_title("Content Ratings Distribution")
        ax.set_xlabel("Ratings")
        ax.set_ylabel("Count")
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, linestyle="--", alpha=0.5)
        show_plot(fig)

    col3, col4 = st.columns(2)

    # ---------- MOVIES vs TV ----------
    with col3:
        movies = filtered_df[filtered_df["type"] == "Movie"].groupby("release_year").size()
        tv = filtered_df[filtered_df["type"] == "TV Show"].groupby("release_year").size()

        fig, ax = plt.subplots(figsize=(6,4))
        ax.plot(movies.index, movies.values, label="Movies", color = "#e67076")
        ax.plot(tv.index, tv.values, label="TV Shows", color = "#e67076")
        ax.set_title("Movies vs TV Shows Over Time")
        ax.set_xlabel("Release Year")
        ax.set_ylabel("Number of Titles")
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.5)
        show_plot(fig)

    # ---------- TOP COUNTRIES ----------
    with col4:
        countries = filtered_df["country"].value_counts().head(10)

        fig, ax = plt.subplots(figsize=(6,4))
        ax.barh(countries.index, countries.values, color = "#e67076")
        ax.set_title("Top 10 Content Producing Countries")
        ax.set_xlabel("Number of Titles")
        ax.set_ylabel("Countries")
        ax.grid(True, linestyle="--", alpha=0.5)
        show_plot(fig)

    col5, col6 = st.columns(2)

    # ---------- MONTHLY CONTENT ----------
    with col5:
        monthly = filtered_df["date_added"].dt.month.value_counts().sort_index()

        fig, ax = plt.subplots(figsize=(6,4))
        ax.plot(monthly.index, monthly.values, marker="o", label="Content Added", color = "#e67076")
        ax.set_title("Content Added Per Month")
        ax.set_xlabel("Month")
        ax.set_ylabel("Number of Titles")
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.5)
        show_plot(fig)

    # ---------- DURATION ----------
    with col6:
        temp_df = filtered_df.copy()  # FIX WARNING
        temp_df["duration_int"] = temp_df["duration"].str.extract("(\d+)").astype(float)

        fig, ax = plt.subplots(figsize=(6,4))
        ax.hist(temp_df["duration_int"].dropna(), bins=20, color = "#e67076")
        ax.set_title("Distribution of Content Duration")
        ax.set_xlabel("Duration (Minutes/Seasons)")
        ax.set_ylabel("Frequency")
        ax.grid(True, linestyle="--", alpha=0.5)
        show_plot(fig)
# =========================================================
# 🧠 INSIGHTS
# =========================================================
elif page == "Insights":
    st.title("🧠 Insights")

    if not filtered_df.empty:
        year = filtered_df["release_year"].mode()[0]
        country = filtered_df["country"].value_counts().idxmax()
        genre = filtered_df["listed_in"].str.split(",").explode().mode()[0]

        growth = df.groupby("release_year").size()
        percent = (growth.loc[2015:].sum() / len(df)) * 100

        st.write(f"🔥 Most common release year: {year}")
        st.write(f"🌍 Top country: {country}")
        st.write(f"🎭 Most popular genre: {genre}")
        st.write(f"📈 {percent:.1f}% of content added after 2015")

# =========================================================
# 🤖 RECOMMENDATION
# =========================================================
elif page == "Recommendation":
    st.title("🤖 Smart Recommendation")

    genre_choice = st.selectbox("Choose a genre", genres[1:])

    if st.button("Recommend 🎬"):
        recs = df[df["listed_in"].str.contains(genre_choice)].sample(5)

        st.subheader("🎬 You may like:")

        for _, row in recs.iterrows():
            st.markdown(f"""
            <div style="
                background-color:white;
                padding:12px;
                border-radius:10px;
                margin-bottom:10px;
                box-shadow:0 2px 8px rgba(0,0,0,0.1);
            ">
            <b>🎬 {row['title']}</b><br>
            🌍 {row['country']} | 📅 {row['release_year']}<br>
            🎭 {row['listed_in']}<br>
            ⭐ {row['rating']} | ⏱️ {row['duration']}
            </div>
            """, unsafe_allow_html=True)
            
