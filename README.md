# NBA_ML

### Preparing data
I used player's data from each game for each season since 2012.
Calculated the average statistics for each season.

Stats being used:
- MIN (Minutes played)
- FGM (Field goals made)
- FGA (Field goals attempted)
- FTM (Free throws made)
- FTA (Free throws attempted)
- REB (Total Rebounds)
- DREB (Defensive Rebounds)
- AST (Assists)
- TOV (Turnovers)
- STL (Steals)
- BLK (Blocks)
- PFD (Personal Fouls drawn)
- PTS (Total points scored)
- PLUS_MINUS
- DD2 (Doule-doules)
- TD3 (Triple doubles)
- GW (Game-Winning shots)
- PLAYER_ID 

Also, when picking for ALL_NBA teams, I skip all the rookies, since Its highly unlikely for them to get the reward.
When Predicting the rewards, I skip all the players that had played (on average) less than 20 minutes.

### SMOTE
I'm using SMOTE to deal with highly unbalanced classes.

### Model
For the prediction, I decided to use two different models.
Logistic Regression for predicting top 5 player of ALL_NBA, ALL_ROOKIES, and Ridge for predicting the rest.

As for the output, I treat players who didn't receive any reward as 0, who were in lowest team 1, then 2 and so on...
This way i can use regression to then, choose the top 15 players by my "ALL_NBA_SCORE" value.

### Training
I trained two seperate models for selecting rookies and all nba teams, the one for rookies is trained only on rookies data.

### My predictions
```json
{
  "first all-nba team": [
    "Luka Doncic",
    "Joel Embiid",
    "Shai Gilgeous-Alexander",
    "Giannis Antetokounmpo",
    "Nikola Jokic"
  ],
  "second all-nba team": [
    "Giannis Antetokounmpo",
    "Jalen Brunson",
    "Devin Booker",
    "Joel Embiid",
    "Damian Lillard"
  ],
  "third all-nba team": [
    "LeBron James",
    "Kevin Durant",
    "Domantas Sabonis",
    "Tyrese Haliburton",
    "Donovan Mitchell"
  ],
  "first rookie all-nba team": [
    "Victor Wembanyama",
    "Chet Holmgren",
    "Brandon Miller",
    "GG Jackson",
    "Jaime Jaquez Jr."
  ],
  "second rookie all-nba team": [
    "Keyonte George",
    null,
    null,
    "Brandin Podziemski",
    "Toumani Camara"
  ]
}
```