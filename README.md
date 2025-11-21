
# NCAAFB MySQL + Streamlit Explorer

A complete NCAA Football (NCAAFB) data analytics dashboard built using:

- **Python**
- **Pandas**
- **MySQL**
- **Streamlit**
- **Plotly**
- **Sportradar JSON API data**

This tool lets you explore teams, players, seasons, weekly rankings, venues, and advanced analytics.

---

## 📌 Features

### ✅ 1. Home Dashboard  
- Overview of teams  
- Active players  
- Season summaries  

### 🧩 2. Teams Explorer  
- Filter by conference, division, venue state  
- Search teams  
- View roster per team  

### 👥 3. Players Explorer  
- Filter by position, status, eligibility  
- Search across teams  
- Detailed player listings  

### 📅 4. Seasons & Rankings Viewer  
- Season list  
- Filter by year or status  
- Weekly AP rankings with team metadata  

### 🏆 5. Rankings Table  
- Week-by-week ranking view  
- Rank range filter  
- Team search  

### 🏟️ 6. Venue Directory  
- Venues list with filters  
- Turf/roof/state filter  

### 🧑‍🏫 7. Coaches Directory  
- Search by coach or team  
- Linked to team data  

---

## 📊 Analytics Dashboards (SQL-powered)

Eight ready-made dashboards:

1. **Top 5 Ranking Consistency**  
2. **Average Ranking Points by Season**  
3. **First-Place Votes Summary**  
4. **Multi-Season Player Presence**  
5. **Player Position Distribution**  
6. **Home vs Away Game Counts**  
7. **Most Used Venues**  
8. **Rank vs Performance (Scatter Plot)**  

---

## 🗄 Database Schema (MySQL)

### Core tables:
- `teams`
- `venues`
- `conferences`
- `divisions`
- `seasons`
- `players`
- `player_statistics`
- `rankings`
- `coaches`

---

## 🛠 Installation & Setup

### 1. Install Python dependencies
```
pip install -r requirements.txt
```

### 2. Install MySQL & create database
```sql
CREATE DATABASE ncaafb_db;
```

### 3. Update DB credentials in `app_streamlit.py`
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_PASSWORD",
    "database": "ncaafb_db",
}
```

### 4. Run Streamlit app
```
streamlit run app_streamlit.py
```

---

## 📁 Project Structure

```
project/
│── app_streamlit.py
│── analysis_pages.py
│── README.md
```

---

## 📡 API Data Sources

Loaded manually via JSON files:

- `/seasons`
- `/season/{year}/schedule`
- `/players/{id}/profile`
- `/teams/{team_id}/roster`
- `/rankings/weekly`

---

## 🧪 Testing

You can test queries using:

```python
import pandas as pd
pd.read_sql("SELECT * FROM teams", conn)
```

---

## 🚀 Future Enhancements

- Add comparison charts  
- Add predictive analytics  
- Add player career statistics  
- Add win/loss seasonal breakdown  

---

## 📬 Contact

For questions, enhancements, or collaboration — feel free to reach out!

---

Enjoy exploring NCAA Football data! 🏈📊
