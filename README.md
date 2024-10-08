# Runners insights

## Description

This project extracts the information about Zurich marathon runners from Datasport and provides a dashboard visualization split per age group and marathon year.
It features:
- a web parsing agent ```./webparser/parser.py``` 
which scrapes the data for Zurich marathon runners for 2014-2018
- a dashboard ```./visualization/app.py``` which visulizes runners per age group and marathon year

![Alt text](./figures/dashboard.jpg)
### Setting Up Your Environment

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Evgeniy-Ponomarev/runners-insights.git
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run data parsing**:
   ```bash
   cd webparser
   python3 parser.py
   ```

4. **Lauch the dashboard**:
   ```bash
   cd ..
   cd visualization
   python3 app.py
   ```