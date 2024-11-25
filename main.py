import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def burc_yorumu_uret(burc):
  """Tek bir burç yorumu üretir"""
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
                  "content": f"{burc} burcu için günlük burç yorumu üret. 50-100 kelime arasında olsun."
              }
          ],
          temperature=0.8,
          max_tokens=150
      )
      return response.choices[0].message.content.strip()
  except Exception as e:
      return f"Hata oluştu: {str(e)}"

def main():
  # Burç girişi al
  print("\nBurç seçenekleri: Koç, Boğa, İkizler, Yengeç, Aslan, Başak, Terazi, Akrep, Yay, Oğlak, Kova, Balık")
  burc = input("\nLütfen bir burç giriniz: ").capitalize()
  
  # Burç kontrolü
  gecerli_burclar = ['Koç', 'Boğa', 'İkizler', 'Yengeç', 'Aslan', 'Başak', 
                     'Terazi', 'Akrep', 'Yay', 'Oğlak', 'Kova', 'Balık']
  
  if burc not in gecerli_burclar:
      print("Geçersiz burç adı!")
      return
  
  print(f"\n{burc} burcu için yorum üretiliyor...\n")
  yorum = burc_yorumu_uret(burc)
  print("🌟 GÜNLÜK BURÇ YORUMU 🌟")
  print("-" * 50)
  print(f"Burç: {burc}")
  print("-" * 50)
  print(yorum)
  print("-" * 50)

if __name__ == "__main__":
  main()