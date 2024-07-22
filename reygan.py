import streamlit as st
import pandas as pd
import numpy as np
import paho.mqtt.publish as publish
import time 
import matplotlib.pyplot as plt
from datetime import datetime
from pymongo import MongoClient


MQTT_SERVER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "kualitas/sensor"
url = "mongodb+srv://Reygan:ilham@data.p6svddp.mongodb.net/?retryWrites=true&w=majority&appName=Data" 
mongo_client = MongoClient(url)
db = mongo_client["clara"]  
collection = db["data"]
data = list(collection.find())

timestamp = []
suhu = []
kelembaban = []
udara = []

for record in data:
    timestamp.append(record['timestamp'])
    suhu.append(record['suhu'])
    kelembaban.append(record['kelembaban'])
    udara.append(record['udara'])

df = pd.DataFrame({
    'timestamp' : timestamp,
    'suhu' : suhu,
    'kelembaban' : kelembaban,
    'udara' : udara
})



df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

st.set_page_config(page_title="Clara", page_icon=":tada:", layout="wide")


def pesan(topic, message):
    try:
        publish.single(topic, message, hostname=MQTT_SERVER, port=MQTT_PORT)
    except Exception as e:
        st.error(f"Error: {e}")

st.markdown('''
<style>
    sidebar .sidebar-content {
        background-color: #1e57ff;
    }
    </style>
''', unsafe_allow_html= True)

st.markdown("""
    <style>
    .title {
        color: #1e59ff;
        font-weight: bold;
        font-size: 50px;  
        margin-bottom: 10px;
    }

    .sub-header {
        color: black;  
        font-size: 20px;  
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .stButton > button {
        background-color: white;
        color: #1e90ff;
        padding: 10px 20px;
        text-align: center;
        height: 50px;
        width: 75%;
        text-decoration: none;
        font-size: px;
        cursor: pointer;
        border-radius: 30px;
        border: 2px solid #1e90ff;
        transition-duration: 0.4s;
    }
    .stButton > button:hover {
        color: white;
        background-color: #1e90ff;
        border: 2px solid #1e57ff; 
    }
    .stButton > button:active {
        color: white;
        background-color: #1e57ff;
        border: 2px solid #1e90ff;
    }
    </style>
""", unsafe_allow_html=True)


st.markdown('<p class="title">Air Purifier</p>', unsafe_allow_html=True)


if not df.empty:
    current_suhu = df['suhu'].iloc[-1]
    previous_suhu = df['suhu'].iloc[-2] if len(df) > 1 else current_suhu
    persen_suhu = ((current_suhu - previous_suhu)  / previous_suhu) * 100 if previous_suhu != 0 else 0
    delta_suhu = "inverse" if persen_suhu >  0 else 'normal'
    delta_suhu_ = "" if  persen_suhu < 0 else "+"

    current_lembab = df['kelembaban'].iloc[-1]
    previous_lembab = df['kelembaban'].iloc[-2] if len(df) > 1 else current_lembab
    persen_lembab = ((current_lembab - previous_lembab)  / previous_lembab) * 100 if previous_lembab != 0 else 0
    delta_lembab = "inverse" if persen_lembab >  0 else 'normal'
    delta_lembab_ = "" if  persen_lembab < 0 else "+"

    current_udara = df['udara'].iloc[-1]
    previous_udara = df['udara'].iloc[-2] if len(df) > 1 else current_udara
    persen_udara = ((current_udara - previous_udara)  / previous_udara) * 100 if previous_udara != 0 else 0
    delta_udara = "inverse" if persen_udara >  0 else 'normal'
    delta_udara_ = "" if  persen_udara < 0 else "+"


    st.markdown('<p class="sub-header">Kualitas Ruangan</p>', unsafe_allow_html=True)

    st.metric(label='Suhu', value = f"{df['suhu'].iloc[-1]}°C", delta = f"{delta_suhu_}{persen_suhu:.2f}%", delta_color = delta_suhu)
    st.metric(label='Kelembaban', value = f"{df['kelembaban'].iloc[-1]}%", delta = f"{delta_lembab_}{persen_lembab:.2f}%", delta_color = delta_lembab)
    st.metric(label='Udara', value = f"{df['udara'].iloc[-1]}ppm", delta = f"{delta_udara_}{persen_udara:.2f}%",  delta_color= delta_udara)










st.markdown('<p class="sub-header">Modes</p>', unsafe_allow_html=True)



if st.button("Always ON"):
    pesan("clara/kontrol", "1")
if st.button("OFF"):
    pesan("clara/kontrol", "0")

if st.button("Auto"):
    pesan("clara/kontrol", "2")

st.markdown('<p class="sub-header">Timer Mode(menit)</p>', unsafe_allow_html=True)
timer = st.slider(" ", 0, 1000, 15)
detik = timer * 60
proses = st.progress(0)
if st.button("Setel Timer"):
    pesan("clara/kontrol", "1") 
    for tunggu in range(detik, -1, -1):
        proses.progress((detik - tunggu) / detik)
        time.sleep(1)
    st.success("Timer telah selesai.") 
    pesan("clara/kontrol", "0") 


st.write("")
st.write("")
st.write("")
st.markdown('<p class="sub-header">Data</p>', unsafe_allow_html=True)
tab1, tab2, tab3, tab4= st.tabs(["SUHU", "KELEMBABAN", "KUALITAS UDARA", "BANTUAN"])
with tab1:
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['suhu'], label='suhu', color= '#0000ff')
    plt.xlabel('WAKTU')
    plt.ylabel('NILAI (Celcius)')
    plt.legend()
    st.pyplot(plt)

with tab2:
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['kelembaban'], label='kelembaban', color= '#a52a2a')
    plt.xlabel('WAKTU')
    plt.ylabel('NILAI (%)')
    plt.legend()
    st.pyplot(plt)

with tab3:
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['udara'], label='udara', color= '#800080')
    plt.xlabel('WAKTU')
    plt.ylabel('NILAI (ppm)')
    plt.legend()
    st.pyplot(plt)

with tab4:
    opsi = ['TENTANG', 'INFO MODE','CLARA']
    select = st.selectbox('', opsi)

    if select == 'TENTANG':
        st.subheader("Tujuan Pembuatan")
        st.write("Untuk membersihkan udara di dalam ruangan agar lebih sehat dan nyaman.")

        st.subheader("Spesifikasi")
        st.write("1. ESP 32,")
        st.write("2. Hepa Filter,")
        st.write("3. Fan 12VDC,")
        st.write("4. Sensor Udara MQ135,")
        st.write("5. Sensor DHT11")





    if select == 'INFO MODE':
        st.subheader("Mode Always ON")
        st.write("Mode ini akan membuat air purifier selalu aktif.")

        st.subheader("Mode OFF")
        st.write("Mode ini akan mematikan air purifier selama alat belum di aktifkan.")

        st.subheader("Mode Auto")
        st.write("Mode ini akan mengaktifkan dan mematikan air purifier secara otomatis berdasarkan kualitas udara di sekitar.")

        st.subheader("Timer Mode")
        st.write("Mode ini membuat user dapat mengatur waktu berapa lama alat harus bekerja, dan akan mematikan alat secara otomatis jika waktu selesai.")





@st.cache_data
def convert(df):
    return df.to_csv(index = True, sep = ",").encode('utf-8')

csv = convert(df)
st.download_button(
    label = "Download Data Sensor",
    data = csv,
    file_name = "datasensor",
    mime = "text/csv"
)

on = st.toggle("Create Table")
if on:
    st.table(df)

