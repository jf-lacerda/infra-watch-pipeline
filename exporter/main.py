from fastapi import FastAPI, Response
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST
import speedtest
import threading
import time

app = FastAPI()

download_gauge = Gauge("internet_download_speed_mbps", "Download speed in Mbps")
upload_gauge = Gauge("internet_upload_speed_mbps", "Upload speed in Mbps")
ping_gauge = Gauge("internet_ping_ms", "Ping in ms")

def run_speedtest():
    while True:
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            download = st.download() / 1_000_000
            upload = st.upload() / 1_000_000
            ping = st.results.ping

            download_gauge.set(round(download, 2))
            upload_gauge.set(round(upload, 2))
            ping_gauge.set(round(ping, 2))

            print("Métricas atualizadas.")
        except Exception as e:
            print(f"Erro no speedtest: {e}")
        time.sleep(600)  # a cada 10 minutos

@app.on_event("startup")
def start_background_task():
    threading.Thread(target=run_speedtest, daemon=True).start()

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
