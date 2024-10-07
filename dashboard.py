import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')


#HEADER
st.header('**B I C Y C L E** 🚲')
st.markdown("")
st.markdown("")

#MEMANGGIL DATASET
df_hour = pd.read_csv("df_hour.csv")



#######################################################################################
#MEMBUAT FUNGSI
#(0) Fungsi Daily Rental
def daily_rental(df):
    daily_rental_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum",
        "casual": "sum",
        "registered": "sum"
    })
    daily_rental_df = daily_rental_df.reset_index()
    daily_rental_df.rename(columns={
        "cnt": "total_rental"
    }, inplace=True)
    
    return daily_rental_df


#(I) Fungsi 1: Distribution of Casual and Registered Renters by Season & Weather
def distribution_season(df):
    #Menghitung distribusi pengguna casual dan registered berdasarkan musim
    distribution_season_df = df.groupby('season').agg({'casual': 'sum', 'registered': 'sum'}).reset_index()
    return distribution_season_df

def distribution_weather(df):
    #Menghitung distribusi pengguna casual dan registered berdasarkan cuaca
    distribution_weather_df = df.groupby('weathersit_mean').agg({'casual': 'sum', 'registered': 'sum'}).reset_index()
    return distribution_weather_df


#(II) Fungsi 2: Number of Bicycle Rentals Based on Temperature and Season
def temp_on_season(df):
    # Mengelompokkan data berdasarkan musim dan rentang suhu
    df['cnt'] = df['cnt'] * 24
    temperature_summary = df.groupby(by=["season", "temp_category"]).agg({"cnt": "mean"}).unstack(level=0)
    return temperature_summary


#(III) Fungsi 3: Number of Working Days and Holidays
def count_working_days(df):
    #Mengelompokkan berdasarkan tanggal unik dan mengambil nilai 'workingday' tertinggi (1 atau 0) untuk setiap hari
    unique_days_df = df.groupby(['dteday']).agg({'workingday': 'max'}).reset_index()

    #Menghitung jumlah hari kerja (workingday = 1)
    total_working_days = unique_days_df[unique_days_df['workingday'] == 1].shape[0]

    #Menghitung jumlah hari libur (workingday = 0)
    total_holidays = unique_days_df[unique_days_df['workingday'] == 0].shape[0]

    return total_working_days, total_holidays


#(IV) Fungsi 4: Rental Distribution by Month and Factors Influencing Rentals
def monthly_rentals(df):
    #Menghitung rata-rata jumlah penyewaan per bulan dan mengalikan cnt dengan 30
    monthly_rentals_df = df.groupby(by="mnth").agg({"cnt": "mean"}).sort_values(by="mnth")
    monthly_rentals_df["cnt"] = monthly_rentals_df["cnt"] * 30  # Mengalikan dengan 30
    return monthly_rentals_df

def monthly_temp(df):
    #Menghitung rata-rata suhu per bulan
    monthly_temp_df = df.groupby('mnth').agg({
        'temp': 'mean'
    }).sort_index()

    #Denormalisasi suhu (dikali dengan 41 agar dalam bentuk Celcius)
    monthly_temp_df['temp_denorm'] = monthly_temp_df['temp'] * 41
    return monthly_temp_df


#(V) Fungsi 5: Rental Trend Increase from 2011 to 2012
def yearly_rentals(df):
    # Mengelompokkan data berdasarkan tahun dan menghitung total penyewaan
    yearly_rentals_df = df.groupby(by=["yr"]).agg({
        "cnt": "sum"
    })
    return yearly_rentals_df


#(VI) Fungsi 6: Clustering Binning: Number of Rentals Based on Temperature
def rental_by_temp(df):
    #Menghitung rata-rata penyewa berdasarkan kategori suhu (kategori bertipe int)
    rental_count = df.groupby('temp_category')['cnt'].mean().reset_index()

    #Mengalikan rata-rata penyewa per jam dengan 24 untuk mendapatkan estimasi total penyewa per hari
    rental_count['total_rentals'] = rental_count['cnt'] * 24

    #Menghapus kolom cnt yang asli agar hanya total_rentals yang muncul
    rental_count = rental_count.drop(columns=['cnt'])

    return rental_count

def days_by_temp(df):
    #Menghitung jumlah hari berdasarkan kategori suhu (data yang memiliki dteday yang sama akan dihitung satu hari)
    unique_days = df.groupby('dteday')['temp_category'].first().reset_index()
    days_count = unique_days['temp_category'].value_counts().reset_index()
    days_count.columns = ['temp_category', 'unique_days'] 
    
    return days_count


#(VII) Fungsi 7: Clustering Manual: Number of Rentals Based on Season
def rental_by_season(df):
    #Menghitung rata-rata penyewa berdasarkan kategori musim (kategori bertipe int)
    rental_count_season = df.groupby('season')['cnt'].mean().reset_index()

    #Mengalikan rata-rata penyewa per jam dengan 24 untuk mendapatkan estimasi total penyewa per hari
    rental_count_season['total_rentals_season'] = rental_count_season['cnt'] * 24

    #Menghapus kolom cnt yang asli agar hanya total_rentals_season yang muncul
    rental_count_season = rental_count_season.drop(columns=['cnt'])

    return rental_count_season

def days_by_season(df):
    #Menghitung jumlah hari berdasarkan kategori suhu (data yang memiliki dteday yang sama akan dihitung satu hari)
    unique_days = df.groupby('dteday')['season'].first().reset_index()
    days_count = unique_days['season'].value_counts().reset_index()
    days_count.columns = ['season', 'unique_days'] 
    
    return days_count


#(VIII) Fungsi 8: Clustering Manual: Number of Rentals Based on Weather
def rental_by_weather(df):
    #Menghitung rata-rata penyewa berdasarkan kategori musim (kategori bertipe int)
    rental_count_weather = df.groupby('weathersit_mean')['cnt'].mean().reset_index()

    #Mengalikan rata-rata penyewa per jam dengan 24 untuk mendapatkan estimasi total penyewa per hari
    rental_count_weather['total_rentals_weather'] = rental_count_weather['cnt'] * 24

    #Menghapus kolom cnt yang asli agar hanya total_rentals_weather yang muncul
    rental_count_weather = rental_count_weather.drop(columns=['cnt'])

    return rental_count_weather

def days_by_weather(df):
    #Menghitung jumlah hari berdasarkan kategori suhu (data yang memiliki dteday yang sama akan dihitung satu hari)
    unique_days = df.groupby('dteday')['weathersit_mean'].first().reset_index()
    days_count = unique_days['weathersit_mean'].value_counts().reset_index()
    days_count.columns = ['weathersit_mean', 'unique_days'] 
    
    return days_count
#######################################################################################



#######################################################################################
#MEMBUAT FUNGSI INPUT & VISUALISASI DI SISI KIRI
df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])

#Mengambil min dan max tanggal
min_date = df_hour["dteday"].min().date()  # Mengambil tanggal minimum
max_date = df_hour["dteday"].max().date()  # Mengambil tanggal maksimum

with st.sidebar:
    #Menambahkan logo perusahaan
    st.image("https://img.freepik.com/premium-vector/simple-bicycle-logo-template_139869-81.jpg?w=740")
    
    #Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date)  #Ubah value ke tuple
    )

main_df = df_hour[(df_hour["dteday"] >= str(start_date)) & 
                (df_hour["dteday"] <= str(end_date))]
#######################################################################################



#######################################################################################
#APLIKASIKAN FUNGSI YANG TELAH DIBUAT DENGAN INPUT DATE
daily_rental_df = daily_rental(main_df)                             #0
distribution_season_df = distribution_season(main_df)               #1
distribution_weather_df = distribution_weather(main_df)             #1
temp_on_season_df = temp_on_season(main_df)                         #2
total_working_days, total_holidays = count_working_days(main_df)    #3
monthly_rentals_df = monthly_rentals(main_df)                       #4
monthly_temp_df = monthly_temp(df_hour)                             #4
yearly_rentals_df = yearly_rentals(df_hour)                         #5
rental_by_temp_df = rental_by_temp(main_df)                         #6
days_by_temp_df = days_by_temp(main_df)                             #6
rental_by_season_df = rental_by_season(main_df)                     #7
days_by_season_df = days_by_season(main_df)                         #7
rental_by_weather_df = rental_by_weather(main_df)                   #8
days_by_weather_df = days_by_weather(main_df)                       #8
#######################################################################################



#######################################################################################
#FUNGSI 0
st.subheader('Daily Rental')

#Daily Rental
col1, col2 = st.columns(2)
with col1:
    average_rental = daily_rental_df.total_rental.mean()  #Rata-rata sewa per hari
    st.metric("Average Rentals Per Day", value=round(average_rental, 2)) 
with col2:
    total_rental = daily_rental_df.total_rental.sum()  #Total sewa
    st.metric("Total Rentals", value=total_rental)

#User Distribution
#Perhitungan
total_casual = daily_rental_df.casual.sum()
total_registered = daily_rental_df.registered.sum()
total_users = total_casual + total_registered
if total_users > 0:
    percent_casual = (total_casual / total_users) * 100
    percent_registered = (total_registered / total_users) * 100
else:
    percent_casual = 0
    percent_registered = 0

#Tampilan
st.markdown("<h4>User Distribution</h4>", unsafe_allow_html=True)
col3, col4 = st.columns(2)
with col3:
    st.metric(label="Casual Users Percentage", value=f"{round(percent_casual, 2)}%")
with col4:
    st.metric(label="Registered Users Percentage", value=f"{round(percent_registered, 2)}%")
st.markdown("")
#######################################################################################



#######################################################################################
#FUNGSI I
st.subheader("1: Distribution of Casual and Registered Renters by Season and Weather")

#Visualisasi distribusi tipe pengguna berdasarkan musim
distribution_season_df.set_index('season', inplace=True)

fig, ax = plt.subplots(figsize=(10, 6))
distribution_season_df.plot(kind='bar', stacked=True, ax=ax)
plt.title('Distribution of Casual and Registered Renters by Season')
plt.xlabel('Season')
plt.ylabel('Number of Renters')
plt.xticks([0, 1, 2, 3], ['Spring', 'Summer', 'Fall', 'Winter'], rotation=0)
plt.legend(title='Renters Type')
plt.tight_layout()
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', 
    (p.get_x() + p.get_width() / 2, p.get_height()), 
    ha='center', va='bottom', fontsize=10)
st.pyplot(fig)
st.markdown("")

#Visualisasi distribusi tipe pengguna berdasarkan cuaca
distribution_weather_df.set_index('weathersit_mean', inplace=True)

fig, ax = plt.subplots(figsize=(10, 6))
distribution_weather_df.plot(kind='bar', stacked=True, ax=ax)
plt.title('Distribution of Casual and Registered Renters by Weather')
plt.xlabel('Weather')
plt.ylabel('Number of Renters')
plt.xticks([0, 1, 2, 3], ['Clear', 'Cloudy', 'Light Rain', 'Heavy Rain'], rotation=0)
plt.legend(title='Renters Type')
plt.tight_layout()
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', 
    (p.get_x() + p.get_width() / 2, p.get_height()), 
    ha='center', va='bottom', fontsize=10)
st.pyplot(fig)
st.markdown("")
st.markdown("")
st.markdown("")
#######################################################################################



#######################################################################################
#FUNGSI II
st.subheader("2: Number of Bicycle Rentals Based on Temperature and Season")

fig, ax = plt.subplots(figsize=(12, 6))
temp_on_season_df.plot(kind='bar', ax=ax)
plt.title('Average Number of Bicycle Rentals Per Day Based on Temperature and Season')
plt.xlabel('Temperature')
plt.ylabel('Average Rentals Per Day')
plt.xticks(rotation=0)
plt.xticks([0, 1, 2, 3], ['0-10° C', '11-20° C', '21-30° C', '31-41° C'])
plt.legend(title='Season', labels=['Spring', 'Summer', 'Fall', 'Winter'])
plt.tight_layout()
st.pyplot(fig)
st.markdown("")
st.markdown("")
st.markdown("")
#######################################################################################



#######################################################################################
#FUNGSI III
st.subheader("3: Number of Working Days and Holidays")

#Menampilkan jumlah hari kerja dan hari libur
col1, col2 = st.columns(2)

with col1:
    st.metric("Number of Working Days", total_working_days)
with col2:
    st.metric("Number of Holidays", total_holidays)

#Visualisasi persebaran jumlah penyewa sepeda berdasarkan jam
avg_rentals_working_day = df_hour[df_hour['workingday'] == 1].groupby('hr').agg({'cnt': 'mean'}).sort_index()
avg_rentals_holiday = df_hour[df_hour['workingday'] == 0].groupby('hr').agg({'cnt': 'mean'}).sort_index()

fig, ax = plt.subplots(figsize=(10, 5))
plt.plot(avg_rentals_working_day.index, avg_rentals_working_day['cnt'], marker='o', linewidth=2, label='Working Days', color="#72BCD4")
plt.plot(avg_rentals_holiday.index, avg_rentals_holiday['cnt'], marker='o', linewidth=2, label='Holidays', color="#FF6347")
ax.set_title('Average Number of Bicycle Rentals Based on Hours')
ax.set_xlabel('Hours')
ax.set_ylabel('Average Number of Bicycle Rentals')
plt.xticks(avg_rentals_working_day.index)
ax.legend()
plt.xticks(rotation=0)
plt.grid(axis='y')
st.pyplot(fig)
st.markdown("")
st.markdown("")
st.markdown("")
#######################################################################################



#######################################################################################
#FUNGSI IV
st.subheader("4: Rental Distribution by Month and Factors Influencing Rentals")
col1, col2 = st.columns(2)

#Visualisasi penjualan per bulan
with col1:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        monthly_rentals_df.index,
        monthly_rentals_df["cnt"],
        marker='o',
        linewidth=2,
        color="#72BCD4"
    )
    plt.title("Number of Bicycle Rentals by Month", loc="center", fontsize=20)
    plt.xticks(monthly_rentals_df.index, ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], fontsize=10)
    plt.yticks(fontsize=10)
    plt.xlabel("Months", fontsize=12)
    plt.ylabel("Number of Rentals by Month", fontsize=12)
    plt.grid(axis='y')
    st.pyplot(fig)

#Visualisasi rata-rata suhu berdasarkan bulan
with col2:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        monthly_temp_df.index,
        monthly_temp_df['temp_denorm'],
        marker='o',
        linewidth=2,
        color="#72BCD4"
    )
    plt.title("Average Temperature by Month", loc="center", fontsize=20)
    plt.xlabel("Months", fontsize=12)
    plt.ylabel("Average Temperature (°C)", fontsize=12)
    plt.xticks(monthly_temp_df.index, ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], fontsize=10)
    plt.grid(axis='y')
    st.pyplot(fig)
st.markdown("")
st.markdown("")
st.markdown("")
#######################################################################################



#######################################################################################
#FUNGSI V
st.subheader("5: Rental Trend Increase from 2011 to 2012")

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(yearly_rentals_df.index.astype(str), yearly_rentals_df['cnt'], color="#72BCD4")
plt.title("Increase in Bicycle Use from 2011 to 2012", loc="center", fontsize=20)
plt.xlabel("Year", fontsize=12)
plt.ylabel("Total Rental", fontsize=12)
plt.xticks([0, 1], ['2011', '2012'])
plt.grid(axis='y')
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', 
    (p.get_x() + p.get_width() / 2, p.get_height()), 
    ha='center', va='bottom', fontsize=10)
st.pyplot(fig)
st.markdown("")
st.markdown("")
st.markdown("")
#######################################################################################



#######################################################################################
st.title("**Analisis Lanjutan: Clustering**")
st.markdown("")
#######################################################################################



#######################################################################################
#FUNGSI VI
st.subheader("Clustering Binning: Number of Rentals Based on Temperature")
col1, col2 = st.columns(2)

#Visualisasi jumlah penyewa
with col1:
    max_rentals = rental_by_temp_df['total_rentals'].max()
    rental_colors = ['#D3D3D3' if rentals < max_rentals else '#72BCD4' for rentals in rental_by_temp_df['total_rentals']]

    plt.figure(figsize=(8, 5))
    plt.bar(rental_by_temp_df['temp_category'], rental_by_temp_df['total_rentals'], color=rental_colors)
    plt.title('Average Rentals Based on Temperature Per Days')
    plt.xlabel('Temperature')
    plt.ylabel('Average Rentals Per Days')
    plt.xticks([1, 2, 3, 4], ['0-10° C', '11-20° C', '21-30° C', '31-41° C'])
    plt.grid(axis='y')
    plt.tight_layout()
    st.pyplot(plt)

#Visualisasi jumlah hari berdasarkan kategori suhu
with col2:
    max_days = days_by_temp_df['unique_days'].max()
    days_colors = ['#D3D3D3' if days < max_days else '#FFA500' for days in days_by_temp_df['unique_days']]

    plt.figure(figsize=(8, 5))
    plt.bar(days_by_temp_df['temp_category'], days_by_temp_df['unique_days'], color=days_colors)
    plt.title('Number of Days Based on Temperature')
    plt.xlabel('Temperature')
    plt.ylabel('Number of Days')
    plt.xticks([1, 2, 3, 4], ['0-10° C', '11-20° C', '21-30° C', '31-41° C'])
    plt.grid(axis='y')
    plt.tight_layout()
    st.pyplot(plt)
st.markdown("")
st.markdown("")
st.markdown("")
#######################################################################################



#######################################################################################
#FUNGSI VII
st.subheader("Clustering Manual: Number of Rentals Based on Season")
col1, col2 = st.columns(2)

#Visualisasi jumlah penyewa
with col1:
    max_rentals = rental_by_season_df['total_rentals_season'].max()
    rental_colors = ['#D3D3D3' if rentals < max_rentals else '#72BCD4' for rentals in rental_by_season_df['total_rentals_season']] 

    plt.figure(figsize=(8, 5))
    plt.bar(rental_by_season_df['season'], rental_by_season_df['total_rentals_season'], color=rental_colors)
    plt.title('Average Rentals Based on Season Per Days')
    plt.xlabel('Season')
    plt.ylabel('Average Rentals Per Days')
    plt.xticks([1, 2, 3, 4], ['Springer', 'Summer', 'Fall', 'Winter'])
    plt.grid(axis='y')
    plt.tight_layout()
    st.pyplot(plt)

#Visualisasi jumlah hari berdasarkan kategori musim
with col2:
    max_days = days_by_season_df['unique_days'].max()
    days_colors = ['#D3D3D3' if days < max_days else '#FFA500' for days in days_by_season_df['unique_days']] 

    plt.figure(figsize=(8, 5))
    plt.bar(days_by_season_df['season'], days_by_season_df['unique_days'], color=days_colors)
    plt.title('Number of Days Based on Season')
    plt.xlabel('Season')
    plt.ylabel('Number of Days')
    plt.xticks([1, 2, 3, 4], ['Springer', 'Summer', 'Fall', 'Winter'])
    plt.grid(axis='y')
    plt.tight_layout()
    st.pyplot(plt)
st.markdown("")
st.markdown("")
st.markdown("")
#######################################################################################



#######################################################################################
#FUNGSI VIII
st.subheader("Clustering Manual: Number of Rentals Based on Weather")
col1, col2 = st.columns(2)

#Visualisasi jumlah penyewa
with col1:
    max_rentals = rental_by_weather_df['total_rentals_weather'].max()
    rental_colors = ['#D3D3D3' if rentals < max_rentals else '#72BCD4' for rentals in rental_by_weather_df['total_rentals_weather']]   

    plt.figure(figsize=(8, 5))
    plt.bar(rental_by_weather_df['weathersit_mean'], rental_by_weather_df['total_rentals_weather'], color=rental_colors)
    plt.title('Average Rentals Based on Weather Per Days')
    plt.xlabel('Weather')
    plt.ylabel('Average Rentals Per Days')
    plt.xticks([1, 2, 3, 4], ['Clear', 'Cloudy', 'Light Rain', 'Heavy Rain'])
    plt.grid(axis='y')
    plt.tight_layout()
    st.pyplot(plt)

#Visualisasi jumlah hari berdasarkan kategori cuaca
with col2:
    max_days = days_by_weather_df['unique_days'].max()
    days_colors = ['#D3D3D3' if days < max_days else '#FFA500' for days in days_by_weather_df['unique_days']]  

    plt.figure(figsize=(8, 5))
    plt.bar(days_by_weather_df['weathersit_mean'], days_by_weather_df['unique_days'], color=days_colors)
    plt.title('Number of Days Based on Weather')
    plt.xlabel('Weather')
    plt.ylabel('Number of Days')
    plt.xticks([1, 2, 3, 4], ['Clear', 'Cloudy', 'Light Rain', 'Heavy Rain'])
    plt.grid(axis='y')
    plt.tight_layout()
    st.pyplot(plt)
st.markdown("")
st.markdown("")
st.markdown("")
#######################################################################################

















# Menampilkan dataframe jumlah hari
#st.subheader("Jumlah Hari Berdasarkan Kategori Suhu (Int)")
#st.dataframe(rental_by_season_df)

# Menampilkan dataframe jumlah hari
#st.subheader("Jumlah Hari Berdasarkan Kategori Suhu")
#st.dataframe(days_summary)

# Tampilkan DataFrame hasil
st.write("Reference:")
st.dataframe(daily_rental_df)