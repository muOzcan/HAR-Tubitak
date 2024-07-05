import asyncio
import websockets
import json
import time
import os

buffer_size = 60  # Her bir sensör için 60 veri noktası
accx_buffer, accy_buffer, accz_buffer = [], [], []
gyrox_buffer, gyroy_buffer, gyroz_buffer = [], [], []
command_file_path = os.path.join(os.path.dirname(__file__), "command.txt")
data_log_file_path = os.path.join(os.path.dirname(__file__), "data_log.json")

# Veriyi anında toplama ve işleme fonksiyonu
async def process_data():
    while True:
        await asyncio.sleep(0.1)  # 100 ms bekle
        if os.path.exists(command_file_path):
            print("Komut dosyası bulundu, veri toplanıyor...")
            start_time = time.time()
            while time.time() - start_time < 3:
                await asyncio.sleep(0.01)  # 10 ms bekle

            if len(accx_buffer) >= buffer_size:
                with open(data_log_file_path, "a") as log_file:
                    for i in range(buffer_size):
                        log_data = {
                            "accX": accx_buffer[i],
                            "accY": accy_buffer[i],
                            "accZ": accz_buffer[i],
                            "gX": gyrox_buffer[i],
                            "gY": gyroy_buffer[i],
                            "gZ": gyroz_buffer[i]
                        }
                        log_file.write(json.dumps(log_data) + "\n")
                
                print(f"Veri kaydedildi. Dosya yolu: {os.path.abspath(data_log_file_path)}")
                os.remove(command_file_path)

async def receive_data():
    uri = "ws://192.168.137.245:81"
    while True:
        try:
            async with websockets.connect(uri, ping_interval=None, close_timeout=10) as websocket:
                while True:
                    data = await websocket.recv()
                    json_data = json.loads(data)
                    accx, accy, accz = json_data['accX'], json_data['accY'], json_data['accZ']
                    gyrox, gyroy, gyroz = json_data['gX'], json_data['gY'], json_data['gZ']
                    
                    # Verileri tamponlara ekle
                    accx_buffer.append(accx)
                    accy_buffer.append(accy)
                    accz_buffer.append(accz)
                    gyrox_buffer.append(gyrox)
                    gyroy_buffer.append(gyroy)
                    gyroz_buffer.append(gyroz)
                    
                    # Tamponları maksimum boyutta tutun
                    if len(accx_buffer) > buffer_size:
                        accx_buffer.pop(0)
                        accy_buffer.pop(0)
                        accz_buffer.pop(0)
                        gyrox_buffer.pop(0)
                        gyroy_buffer.pop(0)
                        gyroz_buffer.pop(0)
                    
                    # Alınan veriyi konsola yazdır
                    print(f"Received data: {json_data}")

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Bağlantı hatası: {e}")
            await asyncio.sleep(5)  # Bağlantı hatası olduğunda 5 saniye bekle ve tekrar dene
        except Exception as e:
            print(f"Bir hata oluştu: {e}")
            await asyncio.sleep(5)  # Genel hata olduğunda 5 saniye bekle ve tekrar dene

# Asenkron döngüyü başlat
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(receive_data())
    loop.create_task(process_data())
    loop.run_forever()
