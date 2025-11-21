import streamlit as st
import pandas as pd
import mysql.connector

from analysis_pages import (
    analysis_top5_consistency,
    analysis_avg_points_per_season,
    analysis_first_place_votes,
    analysis_multi_season_players,
    analysis_position_distribution,
    analysis_home_vs_away,
    analysis_most_used_venues,
    analysis_rank_vs_performance
)

# =====================================================================
# DB CONFIG  🔑  (EDIT IF NEEDED)
# =====================================================================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Alys@003!",   # <- change if needed
    "database": "ncaafb_db",
}

# =====================================================================
# BASIC HELPERS
# =====================================================================
def get_connection():
    """Create a new MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)

def run_query(query: str, params=None) -> pd.DataFrame:
    """Run a SELECT query and return a DataFrame."""
    conn = get_connection()
    try:
        df = pd.read_sql(query, conn, params=params)
    finally:
        conn.close()
    return df


# =====================================================================
# PAGE RENDER FUNCTIONS
# =====================================================================

# 1. 🏠 HOME DASHBOARD
def page_home_dashboard():
    st.header("🏠 NCAAFB Data Explorer – Home Dashboard")

    st.subheader("📌 Teams & Conferences Overview")
    teams_query = """
        SELECT 
            t.team_id,
            t.market,
            t.name AS team_name,
            t.alias,
            c.name AS conference,
            d.name AS division
        FROM teams t
        LEFT JOIN conferences c ON t.conference_id = c.conference_id
        LEFT JOIN divisions d   ON t.division_id   = d.division_id
        ORDER BY c.name, d.name, t.market, t.name;
    """
    df_teams = run_query(teams_query)
    st.dataframe(df_teams, use_container_width=True)

    st.subheader("👥 Active Players")
    players_query = """
        SELECT 
            p.player_id,
            p.first_name,
            p.last_name,
            p.position,
            p.status,
            p.eligibility,
            t.market,
            t.name AS team_name
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.team_id
        WHERE p.status = 'ACT'
        ORDER BY t.market, t.name, p.last_name, p.first_name;
    """
    df_active_players = run_query(players_query)
    st.dataframe(df_active_players, use_container_width=True)

    st.subheader("📅 Seasons Summary")
    seasons_query = """
        SELECT
            season_id,
            year,
            status,
            type_code,
            start_date,
            end_date
        FROM seasons
        ORDER BY year DESC;
    """
    df_seasons = run_query(seasons_query)
    st.dataframe(df_seasons, use_container_width=True)


# 2. 🧩 TEAMS EXPLORER
def page_teams_explorer():
    st.header("🧩 Teams Explorer")

    # --- Filters sidebar-ish controls (but on main page) ---
    st.subheader("🔍 Filters")

    # Conferences
    conf_df = run_query("SELECT conference_id, name FROM conferences ORDER BY name;")
    conf_options = ["All"] + conf_df["name"].tolist()
    selected_conf = st.selectbox("Conference", conf_options)

    # Divisions (optional if table exists)
    try:
        div_df = run_query("SELECT division_id, name FROM divisions ORDER BY name;")
        div_options = ["All"] + div_df["name"].tolist()
        selected_div = st.selectbox("Division", div_options)
    except Exception:
        div_df = pd.DataFrame(columns=["division_id", "name"])
        selected_div = "All"

    # States from venues
    state_df = run_query("SELECT DISTINCT state FROM venues ORDER BY state;")
    state_options = ["All"] + state_df["state"].dropna().tolist()
    selected_state = st.selectbox("State (Venue)", state_options)

    # Search by team or alias
    search_text = st.text_input("Search by team name / market / alias")

    # --- Build query dynamically ---
    base_query = """
        SELECT
            t.team_id,
            t.market,
            t.name AS team_name,
            t.alias,
            c.name AS conference,
            d.name AS division,
            v.name AS venue,
            v.city,
            v.state,
            v.capacity
        FROM teams t
        LEFT JOIN conferences c ON t.conference_id = c.conference_id
        LEFT JOIN divisions d   ON t.division_id   = d.division_id
        LEFT JOIN venues v      ON t.venue_id      = v.venue_id
    """

    conditions = []
    params = []

    # Map selected conference/division names to IDs
    if selected_conf != "All":
        conf_id = conf_df.loc[conf_df["name"] == selected_conf, "conference_id"].iloc[0]
        conditions.append("t.conference_id = %s")
        params.append(conf_id)

    if selected_div != "All" and not div_df.empty:
        div_id = div_df.loc[div_df["name"] == selected_div, "division_id"].iloc[0]
        conditions.append("t.division_id = %s")
        params.append(div_id)

    if selected_state != "All":
        conditions.append("v.state = %s")
        params.append(selected_state)

    if search_text:
        conditions.append("(t.name LIKE %s OR t.market LIKE %s OR t.alias LIKE %s)")
        like = f"%{search_text}%"
        params.extend([like, like, like])

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    base_query += " ORDER BY conference, division, market, team_name;"

    df_teams = run_query(base_query, params=params)
    st.subheader("📋 Teams")
    st.dataframe(df_teams, use_container_width=True)

    # --- Team roster viewer ---
    st.subheader("👥 View Team Roster")

    if not df_teams.empty:
        team_display = df_teams["team_name"] + " (" + df_teams["market"] + ")"
        team_choice = st.selectbox("Select a team", team_display)
        if team_choice:
            chosen_team_id = df_teams.loc[team_display == team_choice, "team_id"].iloc[0]
            roster_query = """
                SELECT
                    p.player_id,
                    p.first_name,
                    p.last_name,
                    p.position,
                    p.eligibility,
                    p.status,
                    p.height,
                    p.weight
                FROM players p
                WHERE p.team_id = %s
                ORDER BY p.position, p.last_name, p.first_name;
            """
            df_roster = run_query(roster_query, params=[chosen_team_id])
            st.dataframe(df_roster, use_container_width=True)
    else:
        st.info("No teams found with the selected filters.")


# 3. 👥 PLAYERS EXPLORER
def page_players_explorer():
    st.header("👥 Players Explorer")

    # Filters metadata
    pos_df = run_query("SELECT DISTINCT position FROM players ORDER BY position;")
    pos_opts = ["All"] + pos_df["position"].dropna().tolist()
    sel_pos = st.selectbox("Position", pos_opts)

    status_df = run_query("SELECT DISTINCT status FROM players ORDER BY status;")
    status_opts = ["All"] + status_df["status"].dropna().tolist()
    sel_status = st.selectbox("Status", status_opts)

    elig_df = run_query("SELECT DISTINCT eligibility FROM players ORDER BY eligibility;")
    elig_opts = ["All"] + elig_df["eligibility"].dropna().tolist()
    sel_elig = st.selectbox("Eligibility (Class)", elig_opts)

    search_text = st.text_input("Search by player name or team name")

    base_query = """
        SELECT
            p.player_id,
            p.first_name,
            p.last_name,
            p.position,
            p.status,
            p.eligibility,
            p.height,
            p.weight,
            t.market,
            t.name AS team_name
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.team_id
    """

    conditions = []
    params = []

    if sel_pos != "All":
        conditions.append("p.position = %s")
        params.append(sel_pos)

    if sel_status != "All":
        conditions.append("p.status = %s")
        params.append(sel_status)

    if sel_elig != "All":
        conditions.append("p.eligibility = %s")
        params.append(sel_elig)

    if search_text:
        conditions.append("(CONCAT(p.first_name, ' ', p.last_name) LIKE %s OR t.name LIKE %s OR t.market LIKE %s)")
        like = f"%{search_text}%"
        params.extend([like, like, like])

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    base_query += """
        ORDER BY t.market, t.name, p.last_name, p.first_name;
    """

    df_players = run_query(base_query, params=params)
    st.dataframe(df_players, use_container_width=True)


# 4. 📅 SEASON & (RANKINGS) VIEWER
def page_season_schedule_viewer():
    st.header("📅 Season & Rankings Viewer")

    seasons_df = run_query("SELECT season_id, year, status, type_code, start_date, end_date FROM seasons ORDER BY year DESC;")
    st.subheader("📋 Seasons")
    st.dataframe(seasons_df, use_container_width=True)

    if seasons_df.empty:
        st.info("No seasons found in the database.")
        return

    # Filter by year/status
    years = ["All"] + seasons_df["year"].astype(str).tolist()
    sel_year = st.selectbox("Filter by year", years)

    status_vals = ["All"] + seasons_df["status"].dropna().unique().tolist()
    sel_status = st.selectbox("Filter by status", status_vals)

    filt_df = seasons_df.copy()
    if sel_year != "All":
        filt_df = filt_df[filt_df["year"] == int(sel_year)]
    if sel_status != "All":
        filt_df = filt_df[filt_df["status"] == sel_status]

    st.subheader("🎯 Filtered Seasons")
    st.dataframe(filt_df, use_container_width=True)

    # --- Rankings by season & week ---
    st.subheader("🏆 Rankings for Selected Season")

    # Season selector
    season_display = filt_df["year"].astype(str) + " (" + filt_df["type_code"] + ")"
    selected = st.selectbox("Choose a season to view rankings", season_display)

    if selected:
        chosen_season_id = filt_df.loc[season_display == selected, "season_id"].iloc[0]

        # Get weeks available for that season
        weeks_df = run_query(
            "SELECT DISTINCT week FROM rankings WHERE season_id = %s ORDER BY week;",
            params=[chosen_season_id]
        )
        if weeks_df.empty:
            st.info("No rankings for this season.")
        else:
            week_opts = ["All"] + weeks_df["week"].tolist()
            sel_week = st.selectbox("Week", week_opts)

            rank_query = """
                SELECT
                    r.week,
                    r.effective_time,
                    t.market,
                    t.name AS team_name,
                    r.rank,
                    r.points,
                    r.fp_votes,
                    r.wins,
                    r.losses,
                    r.ties
                FROM rankings r
                JOIN teams t ON r.team_id = t.team_id
                WHERE r.season_id = %s
            """
            params = [chosen_season_id]

            if sel_week != "All":
                rank_query += " AND r.week = %s"
                params.append(sel_week)

            rank_query += " ORDER BY r.week, r.rank;"

            df_rank = run_query(rank_query, params=params)
            st.dataframe(df_rank, use_container_width=True)

    st.info("ℹ️ You can later extend this page to include a full game schedule table if you store `season_schedule` in MySQL.")


# 5. 🏆 RANKINGS TABLE
def page_rankings_table():
    st.header("🏆 Rankings – AP Poll Viewer")

    # Load seasons for filter
    seasons_df = run_query("SELECT season_id, year FROM seasons ORDER BY year DESC;")
    if seasons_df.empty:
        st.info("No seasons found – cannot show rankings.")
        return

    year_display = seasons_df["year"].astype(str).tolist()
    sel_year = st.selectbox("Season Year", year_display)
    chosen_season_id = seasons_df.loc[seasons_df["year"] == int(sel_year), "season_id"].iloc[0]

    # Weeks for selected season
    weeks_df = run_query(
        "SELECT DISTINCT week FROM rankings WHERE season_id = %s ORDER BY week;",
        params=[chosen_season_id]
    )
    week_opts = ["All"] + weeks_df["week"].tolist() if not weeks_df.empty else ["All"]
    sel_week = st.selectbox("Week", week_opts)

    # Rank range
    min_rank = st.number_input("Min rank", min_value=1, max_value=25, value=1)
    max_rank = st.number_input("Max rank", min_value=min_rank, max_value=25, value=25)

    # Optional team search
    search_team = st.text_input("Search by team name / market")

    base_query = """
        SELECT
            r.week,
            r.effective_time,
            t.market,
            t.name AS team_name,
            r.rank,
            r.points,
            r.fp_votes,
            r.wins,
            r.losses,
            r.ties
        FROM rankings r
        JOIN teams t ON r.team_id = t.team_id
        WHERE r.season_id = %s
          AND r.rank BETWEEN %s AND %s
    """
    params = [chosen_season_id, int(min_rank), int(max_rank)]

    if sel_week != "All":
        base_query += " AND r.week = %s"
        params.append(sel_week)

    if search_team:
        base_query += " AND (t.name LIKE %s OR t.market LIKE %s)"
        like = f"%{search_team}%"
        params.extend([like, like])

    base_query += " ORDER BY r.week, r.rank;"

    df = run_query(base_query, params=params)
    st.dataframe(df, use_container_width=True)


# 6. 🏟️ VENUE DIRECTORY
def page_venue_directory():
    st.header("🏟️ Venue Directory")

    state_df = run_query("SELECT DISTINCT state FROM venues ORDER BY state;")
    states = ["All"] + state_df["state"].dropna().tolist()
    sel_state = st.selectbox("Filter by state", states)

    roof_df = run_query("SELECT DISTINCT roof_type FROM venues ORDER BY roof_type;")
    roofs = ["All"] + roof_df["roof_type"].dropna().tolist()
    sel_roof = st.selectbox("Filter by roof type", roofs)

    base_query = """
        SELECT
            venue_id,
            name,
            city,
            state,
            country,
            capacity,
            surface,
            roof_type,
            latitude,
            longitude
        FROM venues
    """
    conditions = []
    params = []

    if sel_state != "All":
        conditions.append("state = %s")
        params.append(sel_state)

    if sel_roof != "All":
        conditions.append("roof_type = %s")
        params.append(sel_roof)

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    base_query += " ORDER BY state, city, name;"

    df = run_query(base_query, params=params)
    st.dataframe(df, use_container_width=True)


# 7. 🧑‍🏫 COACHES TABLE
def page_coaches_table():
    st.header("🧑‍🏫 Coaches")

    search_text = st.text_input("Search by coach name or team name")

    base_query = """
        SELECT
            c.coach_id,
            c.full_name,
            c.position,
            t.market,
            t.name AS team_name,
            t.alias
        FROM coaches c
        LEFT JOIN teams t ON c.team_id = t.team_id
    """
    conditions = []
    params = []

    if search_text:
        conditions.append("(c.full_name LIKE %s OR t.name LIKE %s OR t.market LIKE %s)")
        like = f"%{search_text}%"
        params.extend([like, like, like])

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    base_query += " ORDER BY c.full_name;"

    df = run_query(base_query, params=params)
    st.dataframe(df, use_container_width=True)


# =====================================================================
# MAIN APP
# =====================================================================
def main():
    st.set_page_config(
        page_title="NCAAFB MySQL Explorer",
        page_icon="🏈",
        layout="wide"
    )

    st.sidebar.title("🏈 NCAAFB Explorer")
    st.sidebar.caption("MySQL: ncaafb_db")

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Home Dashboard",
            "🧩 Teams Explorer",
            "👥 Players Explorer",
            "📅 Season & Rankings Viewer",
            "🏆 Rankings Table",
            "🏟️ Venue Directory",
            "🧑‍🏫 Coaches Table",
            "📊 Analysis Dashboards",

        ],
    )

    if page == "🏠 Home Dashboard":
        page_home_dashboard()
    elif page == "🧩 Teams Explorer":
        page_teams_explorer()
    elif page == "👥 Players Explorer":
        page_players_explorer()
    elif page == "📅 Season & Rankings Viewer":
        page_season_schedule_viewer()
    elif page == "🏆 Rankings Table":
        page_rankings_table()
    elif page == "🏟️ Venue Directory":
        page_venue_directory()
    elif page == "🧑‍🏫 Coaches Table":
        page_coaches_table()
    elif page == "📊 Analysis Dashboards":
        analysis_page = st.sidebar.selectbox(
            "Select Analysis",
            [
                "1. Top 5 Consistency",
                "2. Avg Points per Season",
                "3. First Place Votes",
                "4. Multi-Season Players",
                "5. Position Distribution",
                "6. Home vs Away Games",
                "7. Most Used Venues",
                "8. Rank vs Performance"
            ]
        )

        if analysis_page == "1. Top 5 Consistency":
            analysis_top5_consistency()
        elif analysis_page == "2. Avg Points per Season":
            analysis_avg_points_per_season()
        elif analysis_page == "3. First Place Votes":
            analysis_first_place_votes()
        elif analysis_page == "4. Multi-Season Players":
            analysis_multi_season_players()
        elif analysis_page == "5. Position Distribution":
            analysis_position_distribution()
        elif analysis_page == "6. Home vs Away Games":
            analysis_home_vs_away()
        elif analysis_page == "7. Most Used Venues":
            analysis_most_used_venues()
        elif analysis_page == "8. Rank vs Performance":
            analysis_rank_vs_performance()



if __name__ == "__main__":
    main()
