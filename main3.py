import os
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
from datetime import datetime, timedelta
import time

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def mevcut_yorumlari_kontrol_et(burc):
  """Mevcut Excel dosyasını kontrol eder ve kayıtlı yorumları yükler"""
  dosya_adi = f"{burc}_yillik_yorumlar_FINAL.xlsx"
  temp_dosya = f"{burc}_yorumlar_temp.xlsx"
  
  if os.path.exists(dosya_adi):
      df = pd.read_excel(dosya_adi)
      return df.to_dict('records')
  elif os.path.exists(temp_dosya):
      df = pd.read_excel(temp_dosya)
      return df.to_dict('records')
  return []

def burc_yorumu_uret(burc, tarih):
  """Belirli bir tarih için burç yorumu üretir"""
  try:
      response = client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
              {
                  "role": "system",
                  "content": "Sen uzman bir astrologsun. Türkçe olarak özgün ve özel günlük burç yorumları üretiyorsun."
              },
              {
                  "role": "user",
                  "content": f"{burc} burcu için {tarih.strftime('%d-%m-%Y')} tarihli özgün bir günlük burç yorumu üret. 50-100 kelime arasında olsun."
              }
          ],
          temperature=0.8,
          max_tokens=150
      )
      return response.choices[0].message.content.strip()
  except Exception as e:
      print(f"Hata oluştu: {str(e)}")
      time.sleep(5)
      return None

def yillik_yorumlar_uret(burc):
  """365 günlük yorum üretir"""
  # Mevcut yorumları yükle
  yorumlar = mevcut_yorumlari_kontrol_et(burc)
  mevcut_tarihler = set(yorum['Tarih'] for yorum in yorumlar)
  
  baslangic_tarihi = datetime.now()
  
  for i in range(365):
      guncel_tarih = baslangic_tarihi + timedelta(days=i)
      tarih_str = guncel_tarih.strftime('%d-%m-%Y')
      
      # Eğer bu tarih için yorum zaten varsa, atla
      if tarih_str in mevcut_tarihler:
          print(f"Atlandi: {tarih_str} - Zaten mevcut")
          continue
          
      print(f"İşleniyor: {len(yorumlar)+1}/365 - Tarih: {tarih_str}")
      
      yorum = None
      deneme = 0
      while yorum is None and deneme < 3:
          deneme += 1
          yorum = burc_yorumu_uret(burc, guncel_tarih)
          if yorum is None and deneme < 3:
              print(f"Yeniden deneniyor... ({deneme}/3)")
      
      if yorum:
          yorumlar.append({
              'Tarih': tarih_str,
              'Burç': burc,
              'Yorum': yorum
          })
          # Her 10 yorumda bir kaydet
          if len(yorumlar) % 10 == 0:
              ara_kaydet(yorumlar, burc, "temp")
      
      # Her 5 yorumda bir 2 saniye bekle
      if len(yorumlar) % 5 == 0:
          time.sleep(2)
  
  return yorumlar

def ara_kaydet(yorumlar, burc, suffix="temp"):
  """Ara kayıt yapar"""
  df = pd.DataFrame(yorumlar)
  df.to_excel(f"{burc}_yorumlar_{suffix}.xlsx", index=False)
  print(f"Ara kayıt yapıldı: {len(yorumlar)} yorum kaydedildi.")

def excel_kaydet(yorumlar, burc):
  """Final Excel dosyasını oluşturur"""
  if not yorumlar:
      print("Kaydedilecek yorum bulunamadı!")
      return
  
  df = pd.DataFrame(yorumlar)
  dosya_adi = f"{burc}_yillik_yorumlar_FINAL.xlsx"
  df.to_excel(dosya_adi, index=False)
  print(f"\nTüm yorumlar {dosya_adi} dosyasına kaydedildi")
  return dosya_adi

def main():
  print("\nBurç seçenekleri: Koç, Boğa, İkizler, Yengeç, Aslan, Başak, Terazi, Akrep, Yay, Oğlak, Kova, Balık")
  burc = input("\nLütfen bir burç giriniz: ").capitalize()
  
  gecerli_burclar = ['Koç', 'Boğa', 'İkizler', 'Yengeç', 'Aslan', 'Başak', 
                     'Terazi', 'Akrep', 'Yay', 'Oğlak', 'Kova', 'Balık']
  
  if burc not in gecerli_burclar:
      print("Geçersiz burç adı!")
      return
  
  # Mevcut yorumları kontrol et
  mevcut_yorumlar = mevcut_yorumlari_kontrol_et(burc)
  if mevcut_yorumlar:
      print(f"\nMevcut {len(mevcut_yorumlar)} yorum bulundu. Kaldığı yerden devam edilecek.")
  
  print(f"\n{burc} burcu için yorumlar üretiliyor...")
  print("Bu işlem uzun sürebilir. Lütfen bekleyin...\n")
  
  baslangic = time.time()
  yorumlar = yillik_yorumlar_uret(burc)
  bitis = time.time()
  
  excel_kaydet(yorumlar, burc)
  
  print(f"\nToplam üretilen yorum sayısı: {len(yorumlar)}")
  print(f"Geçen süre: {(bitis-baslangic)/60:.2f} dakika")

if __name__ == "__main__":
  main()