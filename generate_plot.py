import matplotlib.pyplot as plt
from astral import LocationInfo
from astral.sun import sun
import datetime
import pytz
import matplotlib.ticker as ticker
import sys

# Sett opp lokasjon
city = LocationInfo("Oslo", "Norway", "Europe/Oslo", 59.91, 10.75)

# Lister for datoer og solhendelser
dates = []
sunrises_actual = []
sunsets_actual = []

# Nye lister for de hypotetiske scenariene
sunrises_winter_all_year = [] # UTC+1
sunsets_winter_all_year = []
sunrises_summer_all_year = [] # UTC+2
sunsets_summer_all_year = []

# Funksjon for å konvertere tid til desimaltimer
def time_to_hours(t):
    return t.hour + t.minute / 60 + t.second / 3600

# Definer faste tidssoner
tz_winter = datetime.timezone(datetime.timedelta(hours=1)) 
tz_summer = datetime.timezone(datetime.timedelta(hours=2)) 
tz_oslo = pytz.timezone(city.timezone)

# Bruk inneværende år (slik at scriptet virker neste år også)
current_year = datetime.date.today().year

# Loop gjennom alle dager i året
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

# --- Plotting ---
plt.figure(figsize=(12, 6), dpi=100) # Justert størrelse for skjermer

# Skravering våken tid
plt.axhspan(7, 22, color='gold', alpha=0.15, label='Våken tid (07-22)')

# Natt
plt.fill_between(dates, 0, sunrises_actual, color='gray', alpha=0.4)
plt.fill_between(dates, sunsets_actual, 24, color='gray', alpha=0.4)

# Linjer
plt.plot(dates, sunrises_winter_all_year, color='blue', linestyle=':', linewidth=2.0, alpha=0.9)
plt.plot(dates, sunsets_winter_all_year, color='green', linestyle=':', linewidth=2.0, alpha=0.9)
plt.plot(dates, sunrises_summer_all_year, color='blue', linestyle='--', alpha=0.5)
plt.plot(dates, sunsets_summer_all_year, color='green', linestyle='--', alpha=0.5)
plt.plot(dates, sunrises_actual, label='Soloppgang', color='blue', linewidth=2.5)
plt.plot(dates, sunsets_actual, label='Solnedgang', color='green', linewidth=2.5)

# --- NYTT: Vertikal linje for i dag ---
today = datetime.date.today()
plt.axvline(today, color='red', linewidth=2, linestyle='-', label='I dag')

# Pynting
plt.xlabel('') # Fjerner label for å spare plass
plt.title(f'Solhendelser Oslo {current_year}', fontsize=14)
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4, frameon=False)
plt.grid(True, which='both', linestyle='-', linewidth=0.5)

plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(hours_to_hhmm))
plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(2)) # Hver 2. time for mindre støy
plt.ylim(0, 24)
plt.xlim([datetime.date(current_year, 1, 1), datetime.date(current_year, 12, 31)])
plt.xticks(xticks, xlabels, rotation=45, fontsize=8)

plt.tight_layout()

# Lagre filen i stedet for å vise den
plt.savefig("solgraf.png")
print("Graf lagret som solgraf.png")