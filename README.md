# Krischan Score Web-App

Diese Streamlit-Web-App bewertet Aktien, ETFs und Kryptos nach deinem 10-Punkte-System:

- Trend
- EMA20-Richtung
- Kurs im Verhältnis zur EMA20
- RSI14
- Chartbild / Nähe zu Widerständen

Du kannst auf einen Ticker-Button klicken, z. B. `QQQ · 9/10`, und die App zeigt direkt den passenden Chart mit EMA20 und RSI an.

## Online stellen mit Streamlit Community Cloud

1. Kostenloses GitHub-Konto erstellen oder einloggen.
2. Neues Repository erstellen, z. B. `krischan-score`.
3. Diese Dateien ins Repository hochladen:
   - `app.py`
   - `requirements.txt`
   - optional den Ordner `.streamlit`
4. Auf https://share.streamlit.io einloggen.
5. `Create app` bzw. `Deploy an app` wählen.
6. GitHub-Repository auswählen.
7. Main file path: `app.py` eintragen.
8. Auf `Deploy` klicken.

Danach bekommst du einen Link wie:

```text
https://dein-name.streamlit.app
```

## Lokal testen, falls gewünscht

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Beispiel-Ticker

- ETFs: `QQQ`, `SPY`
- Aktien: `AAPL`, `NVDA`, `MU`, `PLD`
- Krypto: `BTC-USD`, `ETH-USD`, `SOL-USD`
- Deutsche Aktien bei Yahoo Finance oft mit `.DE`, z. B. `RHM.DE`

## Wichtig

Das ist ein Lern- und Analyse-Tool, keine Finanzberatung und kein Garant für Gewinne.
