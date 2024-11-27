import streamlit as st
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPICallError
import os
import googlemaps
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px
import plotly.graph_objects as go
from geopy.distance import geodesic
import json

st.set_page_config(
    page_title="Machine Learning Application",
    page_icon="🌟",
    layout="wide" 
)
st.title("🌟 Machine Learning Application")

# ---------------- Load JSON file ----------------
# Load JSON google Key
google_service_account_key = st.secrets["google"].get("service_account_key")
if google_service_account_key:
    try:
        # Parse the service account JSON string into a dictionary
        service_account_data = json.loads(st.secrets["google"]["service_account_key"])

        st.success("Google Service Account Key loaded successfully!")
    except json.JSONDecodeError:
        st.error("Failed to parse Google Service Account Key. Ensure it is properly formatted.")
else:
    st.error("Failed to load Google Service Account Key. Please check your secrets.")

# ---------------- Button to run ML ----------------
if "ml_run" not in st.session_state:
    st.session_state.ml_run = False

if st.button("Run ML"):

    # ---------------- Query function ----------------
    # client = bigquery.Client.from_service_account_json(json_file)

    def init_bigquery_client():
        try:
            # Load Google Service Account Key from secrets
            google_service_account_key = st.secrets["google"].get("service_account_key")

            if google_service_account_key:
                # Parse the service account JSON string
                service_account_data = json.loads(google_service_account_key)

                # Initialize BigQuery client using the service account JSON
                client = bigquery.Client.from_service_account_info(service_account_data)
                #st.success("BigQuery client initialized successfully!")
                return client
            else:
                st.error("Google Service Account Key not found in secrets. Please check your configuration.")
                return None

        except json.JSONDecodeError as e:
            st.error(f"Failed to parse Google Service Account Key: {e}")
            return None
        except Exception as e:
            st.error(f"Error initializing BigQuery client: {e}")
            return None


    def run_bigquery_query(query):
        client = init_bigquery_client()
        if client and query:
            query = query
            job_config = bigquery.QueryJobConfig()
            query_job = client.query(query, job_config=job_config)
            results = query_job.result()

            df = results.to_dataframe()
            return df

        
    # ---------------- Customer location dataframe ----------------
    cust_lo_query = """
    SELECT * 
    FROM `madt8102-chatbot-final-project.datasets.customer_branch`
    LEFT JOIN `madt8102-chatbot-final-project.datasets.province`
    USING (provinceId);
    """
    cust_lo = run_bigquery_query(cust_lo_query)
    # st.dataframe(cust_lo)

    # ---------------- Headquater location dataframe ----------------
    hq_lo_query = """
    SELECT *
    FROM `madt8102-chatbot-final-project.datasets.center`;
    """
    hq_lo = run_bigquery_query(hq_lo_query)
    # st.dataframe(hq_lo)

    # ---------------- Sale person dataframe ----------------
    sales_query = """
    SELECT *
    FROM `madt8102-chatbot-final-project.datasets.sales_person`;
    """
    sales_df = run_bigquery_query(sales_query)
    # st.dataframe(sales_df)

    # ---------------- Join cutomer with HQ location dataframe ----------------
    cust_lo_df = cust_lo.merge(hq_lo[['zoneId', 'Latitude', 'Longitude']], on='zoneId', how='left')
    cust_lo_df.rename(columns={'Latitude_x': 'Latitude', 'Longitude_x': 'Longitude', 'Latitude_y': 'HQ_Latitude', 'Longitude_y': 'HQ_Longitude'}, inplace=True)
    # st.dataframe(cust_lo_df)
    
    # ---------------- Googlemap function ----------------
    gmaps = googlemaps.Client(key='AIzaSyDhAZcviLzIYzZBflEjilpTG5wpR15Xf3o')
    def get_distance_and_duration(origin, destination):
        result = gmaps.distance_matrix(origins=[origin], destinations=[destination], mode="driving")
        distance = result["rows"][0]["elements"][0]["distance"]["text"]
        duration = result["rows"][0]["elements"][0]["duration"]["text"]
        return [distance, duration]
    
    # ---------------- Calculate distance and duration ----------------
    cust_lo_df['distance'] = cust_lo_df.apply(lambda row: get_distance_and_duration([row['HQ_Latitude'], row['HQ_Longitude']], [row['Latitude'], row['Longitude']])[0], axis=1)
    cust_lo_df['duration'] = cust_lo_df.apply(lambda row: get_distance_and_duration([row['HQ_Latitude'], row['HQ_Longitude']], [row['Latitude'], row['Longitude']])[1], axis=1)
    # st.dataframe(cust_lo_df)

    # ---------------- Transform datatype function ----------------
    def time_str_to_minutes(time_str):
        if isinstance(time_str, str):
            parts = time_str.split()
            hours = 0
            minutes = 0
            if 'hour' in parts or 'hours' in parts:
                hour_index = parts.index('hour') if 'hour' in parts else parts.index('hours')
                hours = int(parts[hour_index - 1])
            if 'min' in parts or 'mins' in parts:
                min_index = parts.index('min') if 'min' in parts else parts.index('mins')
                minutes = int(parts[min_index - 1])
            return hours * 60 + minutes
        return 0
    
    # ---------------- Transform datatype function ----------------
    cust_lo_df['distance_km'] = cust_lo_df['distance'].str.replace(' km', '').str.replace(',', '').replace('', '0').astype(float)
    cust_lo_df['duration_mins'] = cust_lo_df['duration'].apply(time_str_to_minutes)
    # st.dataframe(cust_lo_df)

    # ---------------- K-Mean function ----------------
    zone_sales_count = sales_df.groupby("zoneId")["sales_id"].count()
    zone_clusters = zone_sales_count.to_dict()

    # Clustering by zoneId
    def cluster_by_zone(df, zone_clusters):
        results = []
        adjustment_logs = []
        cluster_offset = 0

        for zone_id, n_clusters in zone_clusters.items():
            zone_df = df[df['zoneId'] == zone_id].copy()
            if len(zone_df) < n_clusters:  # ตรวจสอบจำนวนข้อมูลน้อยกว่า n_clusters
                adjustment_logs.append(
                    f"Warning: zoneId {zone_id} has less data points ({len(zone_df)}) than n_clusters ({n_clusters})."
                )
                n_clusters = len(zone_df)  # ลด n_clusters ให้เท่ากับจำนวนข้อมูล

            # Normalization
            scaler = MinMaxScaler()
            zone_df[['distance_km', 'duration_mins']] = scaler.fit_transform(zone_df[['distance_km', 'duration_mins']])

            # Clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            zone_df['Cluster'] = kmeans.fit_predict(zone_df[['distance_km', 'duration_mins']])
            zone_df['Cluster'] += cluster_offset
            cluster_offset += n_clusters
            results.append(zone_df)

        return pd.concat(results, ignore_index=True), adjustment_logs
    
    # ---------------- K-Mean and Process Log ----------------
    cust_lo_df, adjustment_logs = cluster_by_zone(cust_lo_df, zone_clusters)
    # st.dataframe(cust_lo_df)

    for log in adjustment_logs:
        st.write(f"Log: {log}")

    # ---------------- Show graph ----------------
    # ฟังก์ชันคำนวณระยะทางระหว่างสองจุด (ใช้ geopy)
    def calculate_distance(center, point):
        return geodesic(center, point).kilometers

    # คำนวณค่า Center และระยะทางที่ไกลที่สุดในแต่ละ Cluster
    def calculate_cluster_info(group):
        center_lat = group['Latitude'].mean()
        center_lon = group['Longitude'].mean()
        center = (center_lat, center_lon)

        # คำนวณระยะทางจาก center ไปยังแต่ละจุดใน Cluster
        distances = group.apply(lambda row: calculate_distance(center, (row['Latitude'], row['Longitude'])), axis=1)
        max_distance = distances.max()

        return pd.Series({'center_lat': center_lat, 'center_lon': center_lon, 'max_distance': max_distance})
    
    # Select zoneId
    df = cust_lo_df.copy()
    cluster_summary = df.groupby('Cluster', group_keys=False).apply(calculate_cluster_info).reset_index()
    
    # สร้าง Scatter Mapbox
    fig = px.scatter_mapbox(
        df, lat='Latitude', lon='Longitude', color='Cluster',
        title="Clusters with Centers and Maximum Distance Radius",
        mapbox_style="carto-positron",
        zoom=5, center={"lat": 13.736717, "lon": 100.523186},
        labels={"Cluster": "Cluster"},
        text=[f"ZoneID: {row['zoneId']}" for _, row in df.iterrows()]
    )

    # Adjusting the size of the graph
    fig.update_layout(
        height=800,  # Height in pixels
        width=1200   # Width in pixels
    )

    # เพิ่ม Centroids
    fig.add_scattermapbox(
        lat=cluster_summary['center_lat'], lon=cluster_summary['center_lon'],
        mode='markers+text',
        marker=dict(size=10, color='red'),
        text=[f"Center {row['Cluster']}" for _, row in cluster_summary.iterrows()],
        textposition='top right',
        name='Centers'
    )

    # เพิ่ม HQ
    fig.add_scattermapbox(
        lat=df['HQ_Latitude'], lon=df['HQ_Longitude'],
        mode='markers+text',
        marker=dict(size=10, color='green'),
        text=[f"HQ of zoneID: {row['zoneId']}" for _, row in df.iterrows()],
        textposition='top right',
        name='HQ'
    )

    # วาดวงกลมรอบ Centroids
    for _, row in cluster_summary.iterrows():
        center_lat = row['center_lat']
        center_lon = row['center_lon']
        radius = row['max_distance']

        # คำนวณจุดของวงกลม
        theta = np.linspace(0, 2 * np.pi, 100)
        circle_lat = center_lat + (radius / 111) * np.cos(theta)
        circle_lon = center_lon + (radius / (111 * np.cos(np.radians(center_lat)))) * np.sin(theta)

        fig.add_trace(go.Scattermapbox(
            lat=circle_lat, lon=circle_lon,
            mode='lines', fill='toself', fillcolor='rgba(135, 206, 250, 0.3)',
            line=dict(color='blue'),
            name=f'Cluster {row["Cluster"]} Area'
        ))
    
    # ปรับตำแหน่งของ Legend
    fig.update_layout(
        legend=dict(
            title="Clusters",
            orientation="v",  # ตั้งให้แสดงในแนวตั้ง
            x=1.00,  # ย้ายไปทางขวา
            y=1.00,  # ตั้งตำแหน่งแนวตั้ง
            bgcolor="rgba(255, 255, 255, 0.8)",  # สีพื้นหลังของ Legend
            borderwidth=1,  # ขอบของ Legend
            bordercolor='black',  # สีขอบของ Legend
        ),
        coloraxis_showscale=False  # ปิดการแสดงผลของ Heatmap
    )

    # แสดงผลใน Streamlit
    st.title("Clusters Visualization with Mapbox")
    st.plotly_chart(fig, use_container_width=True)

    # ---------------- End button session ----------------
    st.session_state.ml_run = True