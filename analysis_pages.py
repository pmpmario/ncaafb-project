# analysis_pages.py
import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# ----------------------------------------
# DB connection helper
# ----------------------------------------
def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Alys@003!",
        database="ncaafb_db"
    )


# =========================================================
# 1️⃣ TEAMS MAINTAINING TOP 5 RANKINGS ACROSS SEASONS
# =========================================================
def analysis_top5_consistency():
    st.header("🏆 Teams Maintaining Top 5 Rankings Across Seasons")

    conn = get_conn()
    query = """
        SELECT 
            r.team_id,
            t.name AS team_name,
            r.season_id,
            s.year,
            COUNT(*) AS top5_weeks
        FROM rankings r
        JOIN teams t ON r.team_id = t.team_id
        JOIN seasons s ON r.season_id = s.season_id
        WHERE r.rank <= 5
        GROUP BY r.team_id, r.season_id
        ORDER BY top5_weeks DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    st.dataframe(df)

    if not df.empty:
        fig = px.bar(df, x="team_name", y="top5_weeks", color="year", barmode="group")
        st.plotly_chart(fig)


# =========================================================
# 2️⃣ AVERAGE RANKING POINTS PER TEAM / SEASON
# =========================================================
def analysis_avg_points_per_season():
    st.header("📊 Average Ranking Points per Team by Season")

    conn = get_conn()
    query = """
        SELECT 
            r.team_id,
            t.name AS team_name,
            s.year,
            AVG(r.points) AS avg_points
        FROM rankings r
        JOIN teams t ON r.team_id = t.team_id
        JOIN seasons s ON r.season_id = s.season_id
        GROUP BY r.team_id, s.year
        ORDER BY avg_points DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    st.dataframe(df)
    fig = px.line(df, x="year", y="avg_points", color="team_name", markers=True)
    st.plotly_chart(fig)


# =========================================================
# 3️⃣ FIRST-PLACE VOTES SUMMARY
# =========================================================
def analysis_first_place_votes():
    st.header("🥇 First-Place Votes by Team Across All Weeks")

    conn = get_conn()
    query = """
        SELECT 
            t.name AS team_name,
            SUM(r.fp_votes) AS total_fp_votes
        FROM rankings r
        JOIN teams t ON r.team_id = t.team_id
        GROUP BY t.name
        HAVING total_fp_votes > 0
        ORDER BY total_fp_votes DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    st.dataframe(df)
    fig = px.bar(df, x="team_name", y="total_fp_votes")
    st.plotly_chart(fig)


# =========================================================
# 4️⃣ PLAYERS APPEARING IN MULTIPLE SEASONS
# =========================================================
def analysis_multi_season_players():
    st.header("👥 Players Appearing in Multiple Seasons")

    conn = get_conn()
    query = """
        SELECT 
            p.player_id,
            p.first_name,
            p.last_name,
            COUNT(DISTINCT ps.season_id) AS seasons_played
        FROM player_statistics ps
        JOIN players p ON ps.player_id = p.player_id
        GROUP BY p.player_id
        HAVING seasons_played > 1
        ORDER BY seasons_played DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    st.dataframe(df)


# =========================================================
# 5️⃣ PLAYER POSITION DISTRIBUTION ACROSS TEAMS
# =========================================================
def analysis_position_distribution():
    st.header("🧩 Player Position Distribution Across Teams")

    conn = get_conn()
    query = """
        SELECT 
            p.position,
            t.name AS team_name,
            COUNT(*) AS player_count
        FROM players p
        JOIN teams t ON p.team_id = t.team_id
        GROUP BY p.position, t.name
        ORDER BY p.position;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    st.dataframe(df)
    fig = px.bar(df, x="position", y="player_count", color="team_name")
    st.plotly_chart(fig)


# =========================================================
# 6️⃣ HOME vs AWAY GAME COUNTS (requires season_schedule table)
# =========================================================
def analysis_home_vs_away():
    st.header("🏟️ Home vs Away Games Per Team")

    conn = get_conn()

    query = """
        SELECT
            team_id,
            team_name,
            SUM(CASE WHEN is_home = 1 THEN 1 ELSE 0 END) AS home_games,
            SUM(CASE WHEN is_home = 0 THEN 1 ELSE 0 END) AS away_games
        FROM team_game_counts
        GROUP BY team_id, team_name
        ORDER BY home_games DESC;
    """

    df = pd.read_sql(query, conn)
    conn.close()

    st.subheader("📊 Home vs Away Game Counts")
    st.dataframe(df, use_container_width=True)

    st.subheader("📈 Visualization")
    if not df.empty:
        df_chart = df.set_index("team_name")[["home_games", "away_games"]]
        st.bar_chart(df_chart)
    else:
        st.info("No data in team_game_counts table.")



# =========================================================
# 7️⃣ MOST ACTIVE VENUES
# =========================================================
def analysis_most_used_venues():
    st.header("🏟️ Most Used Venues")

    conn = get_conn()
    df = pd.read_sql("SELECT * FROM most_used_venues ORDER BY games_hosted DESC", conn)
    conn.close()

    st.dataframe(df, use_container_width=True)
    st.bar_chart(df.set_index("venue_name")["games_hosted"])



# =========================================================
# 8️⃣ RANKING IMPROVEMENT vs GAME PERFORMANCE
# =========================================================
def analysis_rank_vs_performance():
    st.header("📈 Ranking Improvement vs Game Performance")

    conn = get_conn()
    query = """
        SELECT 
            r.team_id,
            t.name AS team_name,
            r.week,
            r.rank,
            gs.points_scored
        FROM rankings r
        JOIN teams t ON r.team_id = t.team_id
        LEFT JOIN game_scores gs
            ON gs.team_id = r.team_id
            AND gs.season_id = r.season_id
            AND gs.week = r.week
        ORDER BY r.team_id, r.week;
    """

    df = pd.read_sql(query, conn)
    conn.close()

    st.subheader("📊 Combined Ranking & Performance Data")
    st.dataframe(df, use_container_width=True)

    if df.empty:
        st.warning("No ranking or game data available.")
        return

    st.subheader("📈 Ranking vs Points Scored (Scatter Plot)")
    fig = px.scatter(
        df,
        x="points_scored",
        y="rank",
        color="team_name",
        trendline="ols",
        title="Points Scored vs Team Rank"
    )

    st.plotly_chart(fig, use_container_width=True)
