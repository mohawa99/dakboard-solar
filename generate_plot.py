import matplotlib.pyplot as plt
from astral import LocationInfo
from astral.sun import sun
import datetime
import pytz
import matplotlib.ticker as ticker
import sys

# --- 1. OPPSETT OG BEREGNINGER ---

# Sett opp lokasjon
city = LocationInfo("Oslo", "Norway", "Europe/Oslo", 59.91, 10.75)
tz_oslo = pytz.timezone(city.timezone)

# Lister for datoer og solhendelser (for hele året)
dates = []
sunrises_actual = []
sunsets_actual = []
sunrises_winter_all_year = [] # UTC+1
sunsets_winter_all_year = []
sunrises_summer_all_year = [] # UTC+2
sunsets_summer_all_year = []

# Funksjon for å konvertere tid til desimaltimer (for plotting)
def time_to_hours(t):
    return t.hour + t.minute / 60 + t.second / 3600

# Definer faste tidssoner
tz_winter = datetime.timezone(datetime.timedelta(hours=1))
tz_summer = datetime.timezone(datetime.timedelta(hours=2))

# Bruk inneværende år
current_year = datetime.date.today().year
today_date = datetime.date.today()

# --- NYTT: Beregn nøyaktige tider for I DAG for tekstboksen ---
s_today = sun(city.observer, date=today_date)
# Konverter til Oslo-tid og formater som HH:MM streng
sr_today_str = s_today['sunrise'].astimezone(tz_oslo).strftime("%H:%M")
ss_today_str = s_today['sunset'].astimezone(tz_oslo).strftime("%H:%M")
# Lag teksten som skal vises
today_info_text = f"I dag ({today_date.strftime('%d.%m')}): Soloppgang {sr_today_str}  |  Solnedgang {ss_today_str}"


# Loop gjennom alle dager i året for grafene
for month in range(1, 13):
    for day in range(1, 32):
        try:
            date = datetime.date(current_year, month, day)
            s = sun(city.observer, date=date)
            dates.append(date)

            # 1. Faktisk tid
            sr_local = s['sunrise'].astimezone(tz_oslo)
            ss_local = s['sunset'].astimezone(tz_oslo)
            sunrises_actual.append(time_to_hours(sr_local.time()))
            sunsets_actual.append(time_to_hours(ss_local.time()))

            # 2. Alltid vintertid
            sr_winter = s['sunrise'].astimezone(tz_winter)
            ss_winter = s['sunset'].astimezone(tz_winter)
            sunrises_winter_all_year.append(time_to_hours(sr_winter.time()))
            sunsets_winter_all_year.append(time_to_hours(ss_winter.time()))

            # 3. Alltid sommertid
            sr_summer = s['sunrise'].astimezone(tz_summer)
            ss_summer = s['sunset'].astimezone(tz_summer)
            sunrises_summer_all_year.append(time_to_hours(sr_summer.time()))
            sunsets_summer_all_year.append(time_to_hours(ss_summer.time()))

        except ValueError:
            continue

def hours_to_hhmm(x, pos):
    h = int(x)
    m = int((x - h) * 60)
    return f"{h:02d}:{m:02d}"

norske_mnd = ["", "jan", "feb", "mar", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "des"]

xticks = []
xlabels = []
for month in range(1, 13):
    for day in [1, 15]:
        try:
            d = datetime.date(current_year, month, day)
            xticks.append(d)
            xlabels.append(f"{day}. {norske_mnd[month]}")
        except ValueError:
            continue

# --- 2. PLOTTING ---
# Øker høyden litt (fra 6 til 7) for å gi plass til tekst nederst
fig = plt.figure(figsize=(12, 7), dpi=100)
ax = plt.gca() # Hent gjeldende akse

# Skravering våken tid
ax.axhspan(7, 22, color='gold', alpha=0.15, label='Våken tid (07-22)')

# Natt
ax.fill_between(dates, 0, sunrises_actual, color='gray', alpha=0.4)
ax.fill_between(dates, sunsets_actual, 24, color='gray', alpha=0.4)

# Linjer
ax.plot(dates, sunrises_winter_all_year, color='blue', linestyle=':', linewidth=2.0, alpha=0.9)
ax.plot(dates, sunsets_winter_all_year, color='green', linestyle=':', linewidth=2.0, alpha=0.9)
ax.plot(dates, sunrises_summer_all_year, color='blue', linestyle='--', alpha=0.5)
ax.plot(dates, sunsets_summer_all_year, color='green', linestyle='--', alpha=0.5)
ax.plot(dates, sunrises_actual, label='Soloppgang', color='blue', linewidth=2.5)
ax.plot(dates, sunsets_actual, label='Solnedgang', color='green', linewidth=2.5)

# Vertikal linje for i dag
ax.axvline(today_date, color='red', linewidth=2, linestyle='-', label='I dag')

# Pynting av graf
ax.set_title(f'Solhendelser Oslo {current_year}', fontsize=14)
# Flytter legenden litt opp for å gi plass til tekstboksen under
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=4, frameon=False, fontsize=9)
ax.grid(True, which='both', linestyle='-', linewidth=0.5)

ax.yaxis.set_major_formatter(ticker.FuncFormatter(hours_to_hhmm))
ax.yaxis.set_major_locator(ticker.MultipleLocator(2))
ax.set_ylim(0, 24)
ax.set_xlim([datetime.date(current_year, 1, 1), datetime.date(current_year, 12, 31)])
plt.xticks(xticks, xlabels, rotation=45, fontsize=8)


# --- 3. JUSTERING OG TEKSTBOKS ---

# Juster margene manuelt for å lage plass nederst.
# 'bottom=0.2' betyr at grafen slutter 20% fra bunnen av bildet.
plt.subplots_adjust(left=0.08, right=0.95, top=0.93, bottom=0.2)

# Legg til tekstboksen. Koordinatene (0.5, 0.05) er relative til hele bildet.
# 0.5 er midt på horisontalt, 0.05 er helt nederst vertikalt.
fig.text(0.5, 0.05, today_info_text, ha='center', fontsize=13, fontweight='bold',
         bbox=dict(facecolor='#f0f0f0', alpha=1.0, edgecolor='gray', boxstyle='round,pad=0.6'))

# Lagre filen
plt.savefig("solgraf.png")
print(f"Graf lagret med info: {today_info_text}")
