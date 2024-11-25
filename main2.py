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

def burc_yorumu_uret(burc, tarih):
  """Belirli bir tarih için burç yorumu üretir"""
  try:
      response = client.chat.completions.create(
          model="gpt-4",
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
      time.sleep(5)  # Hata durumunda 5 saniye bekle
      return None

def yillik_yorumlar_uret(burc):
  """365 günlük yorum üretir"""
  baslangic_tarihi = datetime.now()
  yorumlar = []
  
  for i in range(365):
      guncel_tarih = baslangic_tarihi + timedelta(days=i)
      print(f"İşleniyor: {i+1}/365 - Tarih: {guncel_tarih.strftime('%d-%m-%Y')}")
      
      yorum = None
      deneme = 0
      while yorum is None and deneme < 3:  # Her tarih için en fazla 3 deneme
          deneme += 1
          yorum = burc_yorumu_uret(burc, guncel_tarih)
          if yorum is None and deneme < 3:
              print(f"Yeniden deneniyor... ({deneme}/3)")
      
      if yorum:
          yorumlar.append({
              'Tarih': guncel_tarih.strftime('%d-%m-%Y'),
              'Burç': burc,
              'Yorum': yorum
          })
          # Her 10 yorumda bir kaydet
          if (i + 1) % 10 == 0:
              ara_kaydet(yorumlar, burc, "temp")
      
      # Her 5 yorumda bir 2 saniye bekle (rate limit için)
      if (i + 1) % 5 == 0:
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
  
  print(f"\n{burc} burcu için 365 günlük yorumlar üretiliyor...")
  print("Bu işlem uzun sürebilir. Lütfen bekleyin...\n")
  
  baslangic = time.time()
  yorumlar = yillik_yorumlar_uret(burc)
  bitis = time.time()
  
  excel_kaydet(yorumlar, burc)
  
  print(f"\nToplam üretilen yorum sayısı: {len(yorumlar)}")
  print(f"Geçen süre: {(bitis-baslangic)/60:.2f} dakika")

if __name__ == "__main__":
  main()