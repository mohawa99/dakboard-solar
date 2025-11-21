import matplotlib.pyplot as plt
from astral import LocationInfo
from astral.sun import sun
import datetime
import pytz
import matplotlib.ticker as ticker
import calendar

# --- 1. SETUP AND CALCULATIONS ---

# Setup location
city = LocationInfo("Oslo", "Norway", "Europe/Oslo", 59.91, 10.75)
tz_oslo = pytz.timezone(city.timezone)

# Lists for dates and sun events
dates = []
sunrises_actual = []
sunsets_actual = []
sunrises_winter_all_year = [] # UTC+1
sunsets_winter_all_year = []
sunrises_summer_all_year = [] # UTC+2
sunsets_summer_all_year = []

# Function to convert time to decimal hours
def time_to_hours(t):
    return t.hour + t.minute / 60 + t.second / 3600

# Define fixed timezones
tz_winter = datetime.timezone(datetime.timedelta(hours=1))
tz_summer = datetime.timezone(datetime.timedelta(hours=2))

# Use current year
current_year = datetime.date.today().year
today_date = datetime.date.today()

# --- Calculate exact times for TODAY ---
s_today = sun(city.observer, date=today_date)
sr_today_str = s_today['sunrise'].astimezone(tz_oslo).strftime("%H:%M")
ss_today_str = s_today['sunset'].astimezone(tz_oslo).strftime("%H:%M")
today_info_text = f"I dag ({today_date.strftime('%d.%m')}): Soloppgang {sr_today_str}  |  Solnedgang {ss_today_str}"

# Loop through all days in the year
for month in range(1, 13):
    days_in_month = calendar.monthrange(current_year, month)[1]
    for day in range(1, days_in_month + 1):
        try:
            date = datetime.date(current_year, month, day)
            s = sun(city.observer, date=date)
            dates.append(date)

            # 1. Actual time
            sr_local = s['sunrise'].astimezone(tz_oslo)
            ss_local = s['sunset'].astimezone(tz_oslo)
            sunrises_actual.append(time_to_hours(sr_local.time()))
            sunsets_actual.append(time_to_hours(ss_local.time()))

            # 2. Always winter time
            sr_winter = s['sunrise'].astimezone(tz_winter)
            ss_winter = s['sunset'].astimezone(tz_winter)
            sunrises_winter_all_year.append(time_to_hours(sr_winter.time()))
            sunsets_winter_all_year.append(time_to_hours(ss_winter.time()))

            # 3. Always summer time
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

# --- 2. PLOTTING ---
fig = plt.figure(figsize=(12, 7), dpi=100)
ax = plt.gca()

# --- Background Columns for Months ---
month_centers = []
month_names = ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Des"]

for i in range(1, 13):
    start = datetime.date(current_year, i, 1)
    if i == 12:
        end = datetime.date(current_year + 1, 1, 1)
    else:
        end = datetime.date(current_year, i + 1, 1)
    
    mid = start + (end - start) / 2
    month_centers.append(mid)
    
    # Color every other month
    if i % 2 != 0:
        ax.axvspan(start, end, facecolor='#f2f2f2', alpha=1.0, zorder=0)

# Shading waking hours
ax.axhspan(7, 22, color='gold', alpha=0.15, label='Våken tid (07-22)', zorder=1)

# Night areas
ax.fill_between(dates, 0, sunrises_actual, color='gray', alpha=0.4, zorder=2)
ax.fill_between(dates, sunsets_actual, 24, color='gray', alpha=0.4, zorder=2)

# Lines
ax.plot(dates, sunrises_winter_all_year, color='blue', linestyle=':', linewidth=2.0, alpha=0.7, zorder=3)
ax.plot(dates, sunsets_winter_all_year, color='green', linestyle=':', linewidth=2.0, alpha=0.7, zorder=3)
ax.plot(dates, sunrises_summer_all_year, color='blue', linestyle='--', alpha=0.5, zorder=3)
ax.plot(dates, sunsets_summer_all_year, color='green', linestyle='--', alpha=0.5, zorder=3)
ax.plot(dates, sunrises_actual, label='Soloppgang', color='blue', linewidth=2.5, zorder=4)
ax.plot(dates, sunsets_actual, label='Solnedgang', color='green', linewidth=2.5, zorder=4)

# Vertical line for today
ax.axvline(today_date, color='red', linewidth=2, linestyle='-', label='I dag', zorder=5)

# --- FORMATTING ---
# TITLE: Increased fontsize to 24 and added bold weight
ax.set_title(f'Solhendelser Oslo {current_year}', fontsize=24, fontweight='bold', pad=20)

# X-axis styling
ax.set_xticks(month_centers)
ax.set_xticklabels(month_names, fontsize=10, fontweight='bold', color='#555555')
ax.tick_params(axis='x', length=0) 
ax.set_xlim([datetime.date(current_year, 1, 1), datetime.date(current_year, 12, 31)])

# Y-axis styling
ax.yaxis.set_major_formatter(ticker.FuncFormatter(hours_to_hhmm))
ax.yaxis.set_major_locator(ticker.MultipleLocator(2))
ax.set_ylim(0, 24)

# Grid
ax.grid(True, axis='y', linestyle='-', linewidth=0.5, alpha=0.5)
ax.grid(False, axis='x') 

# Legend
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.06), ncol=4, frameon=False, fontsize=9)

# --- TEXT BOX ---
plt.subplots_adjust(left=0.07, right=0.95, top=0.88, bottom=0.18) # Adjusted top slightly to accommodate larger title

# INFO TEXT: Fontsize set to 14
fig.text(0.5, 0.02, today_info_text, ha='center', fontsize=14, fontweight='bold',
         bbox=dict(facecolor='#ffffff', alpha=1.0, edgecolor='#cccccc', boxstyle='round,pad=0.5'))

# Save file
plt.savefig("solgraf.png")
print(f"Graf lagret med info: {today_info_text}")
