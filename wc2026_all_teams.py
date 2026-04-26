"""
FIFA WC 2026 — All 48 Teams Match Data
=======================================
Runs all teams at once using verified ESPN IDs.
Saves results to wc2026_master.csv and wc2026_master.json

Install:  pip3 install requests pandas
Run:      python3 wc2026_all_teams.py
"""

import json
import os
import re
import time
import calendar
from datetime import datetime

import pandas as pd
import requests

# ─────────────────────────────────────────────────────────────────────────────

GAMES_NEEDED = 20
OUTPUT_DIR   = "/Users/mealfa482/Desktop/WorldCupGames"
MASTER_CSV   = os.path.join(OUTPUT_DIR, "wc2026_master.csv")
MASTER_JSON  = os.path.join(OUTPUT_DIR, "wc2026_master.json")
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.espn.com/",
}

# ── ALL 48 TEAMS — (name, ESPN_ID, confederation, WC_group) ──────────────────
# IDs verified from ID_Selecciones.pdf

TEAMS = [
    # CONCACAF Hosts
    ("Canadá",              206,   "CONCACAF", "B"),
    ("México",              203,   "CONCACAF", "A"),
    ("Estados Unidos",      660,   "CONCACAF", "D"),
    # AFC
    ("Australia",           628,   "AFC",           "D"),
    ("Irak",               4375,   "AFC",           "I"),
    ("Irán",                469,   "AFC",           "G"),
    ("Japón",               627,   "AFC",           "F"),
    ("Jordania",           2917,   "AFC",           "J"),
    ("Qatar",              4398,   "AFC",           "B"),
    ("Arabia Saudita",      655,   "AFC",           "H"),
    ("Corea del Sur",       451,   "AFC",           "A"),
    ("Uzbekistán",         2570,   "AFC",           "K"),
    # CAF
    ("Argelia",             624,   "CAF",           "J"),
    ("Cabo Verde",         2597,   "CAF",           "H"),
    ("RD Congo",           2850,   "CAF",           "K"),
    ("Costa de Marfil",    4789,   "CAF",           "E"),
    ("Egipto",             2620,   "CAF",           "G"),
    ("Ghana",              4469,   "CAF",           "L"),
    ("Marruecos",          2869,   "CAF",           "C"),
    ("Senegal",             654,   "CAF",           "I"),
    ("Sudáfrica",           467,   "CAF",           "A"),
    ("Túnez",               659,   "CAF",           "F"),
    # CONCACAF
    ("Curazao",           11678,   "CONCACAF",      "E"),
    ("Haití",              2654,   "CONCACAF",      "C"),
    ("Panamá",             2659,   "CONCACAF",      "L"),
    # CONMEBOL
    ("Argentina",           202,   "CONMEBOL",      "J"),
    ("Brasil",              205,   "CONMEBOL",      "C"),
    ("Colombia",            208,   "CONMEBOL",      "K"),
    ("Ecuador",             209,   "CONMEBOL",      "E"),
    ("Paraguay",            210,   "CONMEBOL",      "D"),
    ("Uruguay",             212,   "CONMEBOL",      "H"),
    # OFC
    ("Nueva Zelanda",      2666,   "OFC",           "G"),
    # UEFA
    ("Austria",             474,   "UEFA",          "J"),
    ("Bélgica",             459,   "UEFA",          "G"),
    ("Bosnia y Herzegovina",452,   "UEFA",          "B"),
    ("Croacia",             477,   "UEFA",          "L"),
    ("República Checa",     450,   "UEFA",          "A"),
    ("Inglaterra",          448,   "UEFA",          "L"),
    ("Francia",             478,   "UEFA",          "I"),
    ("Alemania",            481,   "UEFA",          "E"),
    ("Países Bajos",        449,   "UEFA",          "F"),
    ("Noruega",             464,   "UEFA",          "I"),
    ("Portugal",            482,   "UEFA",          "K"),
    ("Escocia",             580,   "UEFA",          "C"),
    ("España",              164,   "UEFA",          "H"),
    ("Suecia",              466,   "UEFA",          "F"),
    ("Suiza",               475,   "UEFA",          "B"),
    ("Turquía",             465,   "UEFA",          "D"),
]

# ── QUALIFICATION DATES ───────────────────────────────────────────────────────
# Date each nation officially qualified for WC 2026
QUAL_DATES = {
    "México":               "Anfitrión",
    "Estados Unidos":       "Anfitrión",
    "Canadá":               "Anfitrión",
    "Sudáfrica":            "2025-10-14",
    "Paraguay":             "2025-09-04",
    "Corea del Sur":        "2025-06-05",
    "Australia":            "2025-06-10",
    "República Checa":      "2026-03-31",
    "Turquía":              "2026-03-31",
    "Alemania":             "2025-11-17",
    "Curazao":              "2025-11-18",
    "Qatar":                "2025-10-14",
    "Costa de Marfil":      "2025-10-14",
    "Suiza":                "2025-11-18",
    "Ecuador":              "2025-06-10",
    "Brasil":               "2025-06-10",
    "Escocia":              "2025-11-18",
    "Países Bajos":         "2025-11-17",
    "Marruecos":            "2025-09-05",
    "Japón":                "2025-03-20",
    "Haití":                "2025-11-18",
    "Suecia":               "2026-03-31",
    "España":               "2025-11-18",
    "Túnez":                "2025-09-08",
    "Bélgica":              "2025-11-18",
    "Egipto":               "2025-10-08",
    "Irán":                 "2025-03-25",
    "Nueva Zelanda":        "2025-03-24",
    "Cabo Verde":           "2025-10-13",
    "Arabia Saudita":       "2025-10-14",
    "Uruguay":              "2025-09-04",
    "Francia":              "2025-11-13",
    "Senegal":              "2025-10-14",
    "Irak":                 "2026-03-31",
    "Noruega":              "2025-11-16",
    "Argentina":            "2025-03-25",
    "Argelia":              "2025-10-09",
    "Austria":              "2025-11-18",
    "Jordania":             "2025-06-05",
    "Portugal":             "2025-11-16",
    "RD Congo":             "2026-03-31",
    "Uzbekistán":           "2025-06-05",
    "Colombia":             "2025-09-04",
    "Inglaterra":           "2025-10-14",
    "Croacia":              "2025-11-14",
    "Ghana":                "2025-10-12",
    "Panamá":               "2025-11-18",
    "Bosnia y Herzegovina": None,
}

# ── TEAM NAME TRANSLATIONS (English → Spanish) ────────────────────────────────
TEAM_NAMES = {
    "Algeria":"Argelia","Argentina":"Argentina","Australia":"Australia",
    "Austria":"Austria","Bahrain":"Baréin","Belgium":"Bélgica",
    "Bolivia":"Bolivia","Bosnia-Herzegovina":"Bosnia y Herzegovina",
    "Bosnia and Herzegovina":"Bosnia y Herzegovina","Brazil":"Brasil",
    "Bulgaria":"Bulgaria","Cameroon":"Camerún","Canada":"Canadá",
    "Cape Verde":"Cabo Verde","Chile":"Chile","China":"China",
    "Colombia":"Colombia","Congo DR":"RD Congo","Costa Rica":"Costa Rica",
    "Croatia":"Croacia","Curacao":"Curazao","Curaçao":"Curazao",
    "Czechia":"República Checa","Czech Republic":"República Checa",
    "Denmark":"Dinamarca","Ecuador":"Ecuador","Egypt":"Egipto",
    "El Salvador":"El Salvador","England":"Inglaterra","Estonia":"Estonia",
    "Faroe Islands":"Islas Feroe","Finland":"Finlandia","France":"Francia",
    "Gabon":"Gabón","Gambia":"Gambia","Georgia":"Georgia",
    "Germany":"Alemania","Ghana":"Ghana","Greece":"Grecia",
    "Guatemala":"Guatemala","Guinea":"Guinea","Haiti":"Haití",
    "Honduras":"Honduras","Hungary":"Hungría","Iceland":"Islandia",
    "Indonesia":"Indonesia","Iran":"Irán","Iraq":"Irak",
    "Ireland":"Irlanda","Israel":"Israel","Italy":"Italia",
    "Ivory Coast":"Costa de Marfil","Jamaica":"Jamaica","Japan":"Japón",
    "Jordan":"Jordania","Kazakhstan":"Kazajistán","Kenya":"Kenia",
    "Kosovo":"Kosovo","Kuwait":"Kuwait","Latvia":"Letonia",
    "Lebanon":"Líbano","Liberia":"Liberia","Libya":"Libia",
    "Luxembourg":"Luxemburgo","Malaysia":"Malasia","Mali":"Malí",
    "Malta":"Malta","Mauritania":"Mauritania","Mexico":"México",
    "Moldova":"Moldavia","Montenegro":"Montenegro","Morocco":"Marruecos",
    "Mozambique":"Mozambique","Netherlands":"Países Bajos",
    "New Caledonia":"Nueva Caledonia","New Zealand":"Nueva Zelanda",
    "Nicaragua":"Nicaragua","Niger":"Níger","Nigeria":"Nigeria",
    "North Korea":"Corea del Norte","North Macedonia":"Macedonia del Norte",
    "Northern Ireland":"Irlanda del Norte","Norway":"Noruega",
    "Oman":"Omán","Pakistan":"Pakistán","Palestine":"Palestina",
    "Panama":"Panamá","Papua New Guinea":"Papúa Nueva Guinea",
    "Paraguay":"Paraguay","Peru":"Perú","Philippines":"Filipinas",
    "Poland":"Polonia","Portugal":"Portugal","Qatar":"Qatar",
    "Republic of Ireland":"República de Irlanda","Romania":"Rumanía",
    "Russia":"Rusia","Rwanda":"Ruanda","Saudi Arabia":"Arabia Saudita",
    "Scotland":"Escocia","Senegal":"Senegal","Serbia":"Serbia",
    "Sierra Leone":"Sierra Leona","Singapore":"Singapur",
    "Slovakia":"Eslovaquia","Slovenia":"Eslovenia",
    "Solomon Islands":"Islas Salomón","South Africa":"Sudáfrica",
    "South Korea":"Corea del Sur","Spain":"España","Sudan":"Sudán",
    "Sweden":"Suecia","Switzerland":"Suiza","Syria":"Siria",
    "Tajikistan":"Tayikistán","Tanzania":"Tanzania","Thailand":"Tailandia",
    "Togo":"Togo","Trinidad and Tobago":"Trinidad y Tobago",
    "Tunisia":"Túnez","Turkiye":"Turquía","Turkey":"Turquía",
    "Türkiye":"Turquía","Uganda":"Uganda","Ukraine":"Ucrania",
    "United Arab Emirates":"Emiratos Árabes Unidos",
    "United States":"Estados Unidos","Uruguay":"Uruguay",
    "Uzbekistan":"Uzbekistán","Venezuela":"Venezuela","Vietnam":"Vietnam",
    "Wales":"Gales","Yemen":"Yemen","Zambia":"Zambia","Zimbabwe":"Zimbabue",
    "Cuba":"Cuba","Guyana":"Guyana","Suriname":"Surinam",
    "Barbados":"Barbados","Bahamas":"Bahamas","Kosovo":"Kosovo",
    "Bolivia":"Bolivia","Dominican Republic":"República Dominicana",
    "Puerto Rico":"Puerto Rico",
}

def translate(name):
    return TEAM_NAMES.get(str(name).strip(), name)


# ── COMPETITION SLUGS ─────────────────────────────────────────────────────────

LEAGUE_NAMES = {
    "fifa.friendly":           "Amistoso Internacional",
    "fifa.world":              "Copa del Mundo FIFA",
    "fifa.worldq.uefa":        "Clasificación Mundial - UEFA",
    "fifa.worldq.concacaf":    "Clasificación Mundial - CONCACAF",
    "fifa.worldq.afc":         "Clasificación Mundial - AFC",
    "fifa.worldq.conmebol":    "Clasificación Mundial - CONMEBOL",
    "fifa.worldq.caf":         "Clasificación Mundial - CAF",
    "fifa.worldq.ofc":         "Clasificación Mundial - OFC",
    "fifa.worldq.intercont":   "Clasificación Mundial - Playoff Intercontinental",
    "uefa.nations":            "UEFA Nations League",
    "uefa.nations.league":     "UEFA Nations League",
    "concacaf.nations.league": "CONCACAF Nations League",
    "concacaf.nations":        "CONCACAF Nations League",
    "afc.asian.cup":           "Copa Asiática AFC",
    "afc.asian":               "Clasificación Copa Asiática",
    "caf.nations":             "Copa Africa de Naciones",
    "conmebol.america":        "Copa América",
    "ofc.nations":             "Copa de Naciones OFC",
    "fifa.arabcup":            "Copa Árabe FIFA",
    "concacaf.gold":           "Copa Oro CONCACAF",
    "concacaf.gold.cup":       "Copa Oro CONCACAF",
    "fifa.confed":             "Copa Confederaciones FIFA",
}

LEAGUES = list(LEAGUE_NAMES.keys())
BASE    = "https://site.api.espn.com/apis/site/v2/sports/soccer"

# ── FETCH ─────────────────────────────────────────────────────────────────────

def fetch_team_matches(team_name: str, team_id: int) -> list:
    found     = {}
    today     = datetime.today()
    year, mon = today.year, today.month

    for _ in range(48):
        if len(found) >= GAMES_NEEDED:
            break

        last_day  = calendar.monthrange(year, mon)[1]
        start     = f"{year}{mon:02d}01"
        end       = f"{year}{mon:02d}{last_day:02d}"
        label     = f"{year}-{mon:02d}"
        month_new = 0

        for slug in LEAGUES:
            url = f"{BASE}/{slug}/scoreboard?dates={start}-{end}&limit=1000"
            try:
                r = requests.get(url, headers=HEADERS, timeout=12)
                if r.status_code != 200:
                    continue
                for ev in r.json().get("events", []):
                    eid  = ev.get("id", "")
                    if not eid or eid in found:
                        continue
                    if not ev.get("status", {}).get("type", {}).get("completed"):
                        continue
                    comp           = (ev.get("competitions") or [{}])[0]
                    competitor_ids = [
                        str(c.get("team", {}).get("id", ""))
                        for c in comp.get("competitors", [])
                    ]
                    if str(team_id) in competitor_ids:
                        found[eid] = (ev, slug)
                        month_new += 1
            except Exception:
                continue
            time.sleep(0.05)

        print(f"    {label}: {month_new:2d} new  (total: {len(found)})")

        mon -= 1
        if mon == 0:
            mon, year = 12, year - 1
        time.sleep(0.2)

    return list(found.values())


# ── PARSE ─────────────────────────────────────────────────────────────────────

def parse_event(ev: dict, slug: str) -> dict:
    comp = (ev.get("competitions") or [{}])[0]

    home_team = away_team = home_score = away_score = ""
    for c in comp.get("competitors", []):
        name  = c.get("team", {}).get("displayName", "")
        score = c.get("score", "")
        if c.get("homeAway") == "home":
            home_team, home_score = name, score
        else:
            away_team, away_score = name, score

    raw = ev.get("date", "")
    try:
        date_out = datetime.fromisoformat(
            raw.replace("Z", "+00:00")
        ).strftime("%Y-%m-%d")
    except Exception:
        date_out = ""

    # Penalty detection
    home_pens = away_pens = ""
    went_to_pens = False

    for c in comp.get("competitors", []):
        for ls in c.get("linescores", []):
            period_type = ls.get("period", {})
            ptype = period_type.get("type", "").lower() if isinstance(period_type, dict) else ""
            if "shootout" in ptype or "penalt" in ptype:
                went_to_pens = True
                val = str(ls.get("displayValue", ""))
                if c.get("homeAway") == "home":
                    home_pens = val
                else:
                    away_pens = val

    status_desc   = ev.get("status", {}).get("type", {}).get("description", "").lower()
    status_detail = ev.get("status", {}).get("type", {}).get("detail", "").lower()
    if not went_to_pens:
        if any(x in status_desc or x in status_detail
               for x in ["penalt", "pks", "shootout"]):
            went_to_pens = True

    if not went_to_pens:
        for note in comp.get("notes", []):
            headline = note.get("headline", "").lower()
            if "penalt" in headline or "pks" in headline or "shootout" in headline:
                went_to_pens = True
                pen_match = re.search(r'(\d+)\s*[-–]\s*(\d+)\s*on\s*penalt', headline)
                if pen_match and not home_pens:
                    home_pens = pen_match.group(1)
                    away_pens = pen_match.group(2)
                break

    # Result
    try:
        h, a = int(home_score), int(away_score)
        if h > a:
            result = "Victoria Local"
        elif h < a:
            result = "Victoria Visitante"
        else:
            if went_to_pens and home_pens and away_pens:
                hp, ap     = int(home_pens), int(away_pens)
                pen_winner = "Victoria Local" if hp > ap else "Victoria Visitante"
                result     = f"{pen_winner} - {home_pens}-{away_pens} en penales ({h}-{a} al final)"
            elif went_to_pens:
                result = "Empate (fue a penales)"
            else:
                result = "Empate"
    except (ValueError, TypeError):
        result = ""

    competition = LEAGUE_NAMES.get(slug, slug)

    venue_obj = comp.get("venue", {}) or {}
    stadium   = venue_obj.get("fullName", "")
    address   = venue_obj.get("address", {}) or {}
    city      = address.get("city", "") or venue_obj.get("location", "")
    state     = address.get("state", "")
    country   = address.get("country", "")
    location  = ", ".join([p for p in [city, state, country] if p])

    return {
        "match_id":         ev.get("id", ""),
        "fecha":            date_out,
        "competicion":      competition,
        "equipo_local":     translate(home_team),
        "goles_local":      home_score,
        "goles_visitante":  away_score,
        "equipo_visitante": translate(away_team),
        "resultado":        result,
        "estadio":          stadium,
        "ciudad":           location,
    }


# ── SAVE ──────────────────────────────────────────────────────────────────────

def save_all(all_team_data: dict):
    all_rows = []
    for team_name, (conf, group, matches) in all_team_data.items():
        for i, m in enumerate(matches, 1):
            all_rows.append({
                "seleccion":        team_name,
                "confederacion":    conf,
                "grupo_wc2026":     group,
                "fecha_clasif":     QUAL_DATES.get(team_name, ""),
                "numero_partido":   i,
                "fecha":            m.get("fecha", ""),
                "competicion":      m.get("competicion", ""),
                "equipo_local":     m.get("equipo_local", ""),
                "goles_local":      m.get("goles_local", ""),
                "goles_visitante":  m.get("goles_visitante", ""),
                "equipo_visitante": m.get("equipo_visitante", ""),
                "resultado":        m.get("resultado", ""),
                "estadio":          m.get("estadio", ""),
                "ciudad":           m.get("ciudad", ""),
            })

    if all_rows:
        df = pd.DataFrame(all_rows)
        df = df.sort_values(["grupo_wc2026", "seleccion", "fecha"]).reset_index(drop=True)
        df.to_csv(MASTER_CSV, index=False, encoding="utf-8-sig")

    # JSON
    teams_dict = {}
    for team_name, (conf, group, matches) in all_team_data.items():
        qual_date = QUAL_DATES.get(team_name, "")
        enriched = []
        for m in matches:
            row = {
                "seleccion":        team_name,
                "confederacion":    conf,
                "grupo_wc2026":     group,
                "fecha_clasif":     qual_date,
                **m,
            }
            # Mark the qualification match
            if qual_date and qual_date != "Anfitrión" and m.get("fecha") == qual_date:
                row["es_clasif"] = True
            enriched.append(row)
        teams_dict[team_name] = enriched

    with open(MASTER_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "generado":     datetime.today().strftime("%Y-%m-%d %H:%M"),
            "equipos_done": len(teams_dict),
            "equipos_total":48,
            "equipos":      teams_dict,
        }, f, ensure_ascii=False, indent=2)


# ── MAIN ──────────────────────────────────────────────────────────────────────

def run():
    print("\n" + "="*65)
    print("  FIFA WC 2026 — Todos los equipos (48)")
    print("="*65 + "\n")

    all_team_data = {}
    total         = len(TEAMS)

    for idx, (team_name, team_id, conf, group) in enumerate(TEAMS, 1):
        print(f"\n[{idx:2d}/{total}] {team_name}  (ESPN ID: {team_id})")
        print(f"  {'─'*50}")

        events_slugs = fetch_team_matches(team_name, team_id)

        if not events_slugs:
            print(f"  ⚠️  Sin resultados para {team_name}")
            all_team_data[team_name] = (conf, group, [])
            continue

        matches = [parse_event(ev, slug) for ev, slug in events_slugs]
        matches = [m for m in matches if m.get("fecha")]
        matches = sorted(matches, key=lambda x: x["fecha"], reverse=True)[:GAMES_NEEDED]
        matches = sorted(matches, key=lambda x: x["fecha"])

        all_team_data[team_name] = (conf, group, matches)

        print(f"\n  ✅  {len(matches)} partidos encontrados")
        for i, m in enumerate(matches, 1):
            score = f"{m['goles_local']}-{m['goles_visitante']}"
            clasif = " ⭐ CLASIFICÓ" if m.get("fecha") == QUAL_DATES.get(team_name) else ""
            print(f"  {i:2d}. {m['fecha']}  {m['equipo_local']:<22} {score:<5} "
                  f"{m['equipo_visitante']:<22}  {m['competicion']}{clasif}")

        # Save after every team so progress is never lost
        save_all(all_team_data)
        print(f"  💾  Guardado ({idx}/{total} equipos)")

    # Final summary
    print(f"\n{'='*65}")
    print("  RESUMEN FINAL:")
    complete   = sum(1 for _, (_, _, m) in all_team_data.items() if len(m) >= GAMES_NEEDED)
    incomplete = [(t, len(m)) for t, (_, _, m) in all_team_data.items() if len(m) < GAMES_NEEDED]
    print(f"  ✅  {complete}/48 equipos con 20 partidos")
    if incomplete:
        print(f"  ⚠️  Equipos incompletos:")
        for t, c in sorted(incomplete, key=lambda x: x[1]):
            print(f"     {t:<30} {c}/20")
    print(f"\n  💾  {MASTER_CSV}")
    print(f"  💾  {MASTER_JSON}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    run()
