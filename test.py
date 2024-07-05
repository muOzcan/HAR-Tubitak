import time
import json
import numpy as np
import joblib
import tensorflow as tf
import os
import keyboard
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Modeli ve gerekli bileşenleri yükleme
model = tf.keras.models.load_model('C:/Users/musta/OneDrive/Masaüstü/HAR Updates/HAR_Data/har_model.keras')
model.load_weights('C:/Users/musta/OneDrive/Masaüstü/HAR Updates/HAR_Data/har_model_weights.weights.h5')
label_encoder = joblib.load('C:/Users/musta/OneDrive/Masaüstü/HAR Updates/HAR_Data/label_encoder.pkl')
scaler = joblib.load('C:/Users/musta/OneDrive/Masaüstü/HAR Updates/HAR_Data/scaler.pkl')

buffer_size = 60  # Her bir sensör için 60 veri noktası
command_file_path = os.path.join(os.path.dirname(__file__), "command.txt")
data_log_file_path = os.path.join(os.path.dirname(__file__), "data_log.json")

def start_recording():
    # Komut dosyasına yaz
    with open(command_file_path, "w") as file:
        file.write("start_recording")
    print(f"Komut dosyasina 'start_recording' yazildi. Dosya yolu: {os.path.abspath(command_file_path)}")
    
    # Kayıt tamamlanana kadar bekle
    while os.path.exists(command_file_path):
        time.sleep(0.1)
    
    time.sleep(3)  # Ekstra bekleme süresi, veri kaydının tamamlanması için
    print("Kayit tamamlandi, veri işleniyor...")

def process_data():
    print(f"Veri günlüğü dosyasindan okuma. Dosya yolu: {os.path.abspath(data_log_file_path)}")
    with open(data_log_file_path, "r") as log_file:
        lines = log_file.readlines()

    if len(lines) < buffer_size:
        print("Yeterli veri yok")
        return

    # En son buffer_size kadar veriyi al
    recent_data = lines[-buffer_size:]
    combined_buffer = []

    for line in recent_data:
        json_data = json.loads(line)
        combined_buffer.extend([
            json_data['accX'], json_data['accY'], json_data['accZ'], 
            json_data['gX'], json_data['gY'], json_data['gZ']
        ])


    # Veriyi flatten ederek tek bir satırda birleştirme
    input_data = np.array(combined_buffer).reshape(1, -1)

    # Veriyi ölçeklendirme
    input_data = scaler.transform(input_data)

    # Veriyi kontrol etmek için print
    print(f"Flattened and scaled input data: {input_data}")

    # Tahmin yap
    prediction = model.predict(input_data)
    predicted_label = label_encoder.inverse_transform([np.argmax(prediction)])
    
    print(prediction)
    print(f"Tahmin edilen aktivite: {predicted_label[0]}")

    # Data log dosyasını temizleme
    with open(data_log_file_path, "w") as log_file:
        log_file.write("")  # Dosyayı tamamen temizle

if __name__ == "__main__":
    while True:
        if keyboard.is_pressed("1"):
            start_recording()
            process_data()
            time.sleep(1)
