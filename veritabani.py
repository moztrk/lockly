import psycopg2
from psycopg2 import Error
from cryptography.fernet import Fernet
import os
from datetime import datetime, timedelta
import hashlib
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class VeritabaniYoneticisi:
    def __init__(self):
        self.baglanti = None
        self.imlec = None
        # Şifreleme anahtarı oluşturma veya yükleme
        self.sifreleme_anahtari = self._sifreleme_anahtari_al()
        self.fernet = Fernet(self.sifreleme_anahtari)
        
    def _sifreleme_anahtari_al(self):
        """Şifreleme anahtarını dosyadan okur veya yeni oluşturur"""
        anahtar_dosyasi = "sifreleme_anahtari.key"
        if os.path.exists(anahtar_dosyasi):
            with open(anahtar_dosyasi, "rb") as f:
                return f.read()
        else:
            anahtar = Fernet.generate_key()
            with open(anahtar_dosyasi, "wb") as f:
                f.write(anahtar)
            return anahtar

    def baglan(self):
        """Veritabanına bağlanır ve gerekli tabloları oluşturur"""
        try:
            self.baglanti = psycopg2.connect(
                host="localhost",
                database="lockly",
                user="postgres",
                password="134679"
            )
            self.imlec = self.baglanti.cursor()
            self._tablolari_olustur()
            return True
        except Error as e:
            print(f"Veritabanı bağlantı hatası: {e}")
            return False

    def _tablolari_olustur(self):
        """Gerekli veritabanı tablolarını oluşturur"""
        tablolar = [
            """
            CREATE TABLE IF NOT EXISTS kullanicilar (
                id SERIAL PRIMARY KEY,
                kullanici_adi VARCHAR(50) UNIQUE NOT NULL,
                sifre_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                son_giris_tarihi TIMESTAMP,
                basarisiz_giris_sayisi INTEGER DEFAULT 0,
                hesap_kilitli BOOLEAN DEFAULT FALSE,
                kilit_bitis_tarihi TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sifreler (
                id SERIAL PRIMARY KEY,
                kullanici_id INTEGER REFERENCES kullanicilar(id),
                baslik VARCHAR(100) NOT NULL,
                sifrelenmis_sifre BYTEA NOT NULL,
                website VARCHAR(255),
                aciklama TEXT,
                olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                son_guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS paylasim_baglantilari (
                id SERIAL PRIMARY KEY,
                sifre_id INTEGER REFERENCES sifreler(id),
                paylasim_kodu VARCHAR(100) UNIQUE NOT NULL,
                pin_kodu VARCHAR(6) NOT NULL,
                olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                son_kullanma_tarihi TIMESTAMP NOT NULL,
                kullanildi BOOLEAN DEFAULT FALSE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS guvenlik_sorulari (
                id SERIAL PRIMARY KEY,
                kullanici_id INTEGER REFERENCES kullanicilar(id),
                soru_1 VARCHAR(255) NOT NULL,
                cevap_1 VARCHAR(255) NOT NULL,
                soru_2 VARCHAR(255) NOT NULL,
                cevap_2 VARCHAR(255) NOT NULL,
                soru_3 VARCHAR(255) NOT NULL,
                cevap_3 VARCHAR(255) NOT NULL,
                soru_4 VARCHAR(255) NOT NULL,
                cevap_4 VARCHAR(255) NOT NULL,
                soru_5 VARCHAR(255) NOT NULL,
                cevap_5 VARCHAR(255) NOT NULL,
                kritik_sorular INTEGER[] NOT NULL  -- Kritik soruların indeksleri [1,2,4] gibi
            )
            """,
            """
            ALTER TABLE kullanicilar 
            ADD COLUMN IF NOT EXISTS sifirlama_kodu VARCHAR(6),
            ADD COLUMN IF NOT EXISTS sifirlama_kodu_son_kullanma TIMESTAMP
            """,
            """
            CREATE TABLE IF NOT EXISTS dogrulama_kodlari (
                id SERIAL PRIMARY KEY,
                kullanici_adi TEXT NOT NULL,
                kod TEXT NOT NULL,
                olusturma_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        for tablo in tablolar:
            self.imlec.execute(tablo)
        self.baglanti.commit()

    def sifre_sifrele(self, sifre: str) -> bytes:
        """Şifreyi şifreler"""
        try:
            return self.fernet.encrypt(sifre.encode('utf-8'))
        except Exception as e:
            print(f"Şifreleme hatası: {e}")
            return None

    def sifre_coz(self, sifrelenmis_sifre: bytes) -> str:
        """Şifrelenmiş şifreyi çözer"""
        try:
            if isinstance(sifrelenmis_sifre, memoryview):
                sifrelenmis_sifre = bytes(sifrelenmis_sifre)
            return self.fernet.decrypt(sifrelenmis_sifre).decode('utf-8')
        except Exception as e:
            print(f"Şifre çözme hatası: {e}")
            return None

    def kapat(self):
        """Veritabanı bağlantısını kapatır"""
        if self.imlec:
            self.imlec.close()
        if self.baglanti:
            self.baglanti.close()

    def sifreleri_getir(self, kullanici_id):
        try:
            # Sadece giriş yapan kullanıcının şifrelerini getir
            self.imlec.execute("""
                SELECT id, baslik, sifrelenmis_sifre, website, aciklama, son_guncelleme_tarihi 
                FROM sifreler 
                WHERE kullanici_id = %s
                ORDER BY son_guncelleme_tarihi DESC
            """, (kullanici_id,))
            
            sifreler = self.imlec.fetchall()
            
            sonuclar = []
            for sifre in sifreler:
                try:
                    cozulmus_sifre = self.sifre_coz(sifre[2])
                    if cozulmus_sifre:
                        sonuclar.append((
                            sifre[0],  # id
                            sifre[1],  # baslik
                            cozulmus_sifre,  # sifre
                            sifre[3],  # website
                            sifre[4],  # aciklama
                            sifre[5]   # tarih
                        ))
                except Exception as e:
                    print(f"Şifre çözme hatası: {e}")
                    continue
            
            return sonuclar
        except psycopg2.Error as e:
            print(f"Şifreler getirilirken hata oluştu: {e}")
            return []

    def kullanici_dogrula(self, kullanici_adi, sifre):
        try:
            # Bağlantıyı kontrol et
            self.baglanti_kontrol()
            
            sifre_hash = hashlib.sha256(sifre.encode()).hexdigest()
            
            # Debug için yazdırma
            print(f"Doğrulama deneniyor - Kullanıcı: {kullanici_adi}")
            
            self.imlec.execute("""
                SELECT id, kullanici_adi, sifre_hash FROM kullanicilar 
                WHERE kullanici_adi = %s
            """, (kullanici_adi,))
            
            sonuc = self.imlec.fetchone()
            
            if sonuc:
                print(f"Kullanıcı bulundu - ID: {sonuc[0]}")
                print(f"Hash karşılaştırması: {sifre_hash == sonuc[2]}")
                
                if sifre_hash == sonuc[2]:
                    # Başarılı giriş
                    self.imlec.execute("""
                        UPDATE kullanicilar 
                        SET son_giris_tarihi = CURRENT_TIMESTAMP,
                            basarisiz_giris_sayisi = 0
                        WHERE id = %s
                    """, (sonuc[0],))
                    self.baglanti.commit()
                    return sonuc[0]  # Kullanıcı ID'sini döndür
            
            return None
            
        except Exception as e:
            print(f"Kullanıcı doğrulama hatası: {e}")
            return None

    def sifre_sil(self, sifre_id, kullanici_id):
        try:
            # Önce şifrenin bu kullanıcıya ait olduğunu kontrol et
            self.imlec.execute("""
                DELETE FROM paylasim_baglantilari 
                WHERE sifre_id = %s
            """, (sifre_id,))

            self.imlec.execute("""
                DELETE FROM sifreler 
                WHERE id = %s AND kullanici_id = %s
            """, (sifre_id, kullanici_id))
            
            # Etkilenen satır sayısını kontrol et
            etkilenen = self.imlec.rowcount
            self.baglanti.commit()
            
            print(f"Silme işlemi: Şifre ID={sifre_id}, Kullanıcı ID={kullanici_id}, Başarılı={etkilenen>0}")
            return etkilenen > 0
            
        except psycopg2.Error as e:
            print(f"Şifre silme hatası: {e}")
            self.baglanti.rollback()
            return False

    def baglanti_kontrol(self):
        """Veritabanı bağlantısını kontrol eder ve gerekirse yeniler"""
        try:
            # Bağlantıyı test et
            self.imlec.execute("SELECT 1")
        except (psycopg2.Error, psycopg2.OperationalError):
            # Bağlantı kopmuşsa yeniden bağlan
            self.baglan()

    def kullanici_eposta_getir(self, kullanici_adi):
        """Kullanıcı adına ait e-posta adresini getir"""
        try:
            sorgu = "SELECT email FROM kullanicilar WHERE kullanici_adi = %s"
            self.imlec.execute(sorgu, (kullanici_adi,))
            sonuc = self.imlec.fetchone()
            return sonuc[0] if sonuc else None
        except Exception as e:
            print(f"Hata: {e}")
            return None

    def dogrulama_kodu_olustur(self, kullanici_adi):
        """6 haneli doğrulama kodu oluştur ve sakla"""
        kod = ''.join(random.choices('0123456789', k=6))
        try:
            # Önceki kodları temizle
            self.imlec.execute("DELETE FROM dogrulama_kodlari WHERE kullanici_adi = %s", 
                              (kullanici_adi,))
            
            # Yeni kodu kaydet
            self.imlec.execute("""
                INSERT INTO dogrulama_kodlari (kullanici_adi, kod, olusturma_zamani) 
                VALUES (%s, %s, CURRENT_TIMESTAMP)
            """, (kullanici_adi, kod))
            self.baglanti.commit()
            return kod
        except Exception as e:
            print(f"Hata: {e}")
            return None

    def dogrulama_kodu_gonder(self, email, kod):
        """E-posta ile doğrulama kodunu gönder"""
        # E-posta ayarları
        smtp_ayarlari = {
            'sunucu': 'smtp.gmail.com',
            'port': 587,
            'email': 'mustafa44fbfb@gmail.com',  # Gmail adresiniz
            'sifre': 'mcwt szgs kefs jznq'  # Gmail uygulama şifreniz
        }
        
        # E-posta içeriği
        message = MIMEMultipart()
        message["From"] = smtp_ayarlari['email']
        message["To"] = email
        message["Subject"] = "Lockly - Şifre Sıfırlama Kodu"
        
        body = f"""
        Merhaba,
        
        Şifre sıfırlama talebiniz için doğrulama kodunuz: {kod}
        
        Bu kodu kimseyle paylaşmayın.
        
        Saygılarımızla,
        Lockly Ekibi
        """
        
        message.attach(MIMEText(body, "plain"))
        
        # E-postayı gönder
        try:
            server = smtplib.SMTP(smtp_ayarlari['sunucu'], smtp_ayarlari['port'])
            server.starttls()
            server.login(smtp_ayarlari['email'], smtp_ayarlari['sifre'])
            server.send_message(message)
            server.quit()
        except Exception as e:
            raise Exception(f"E-posta gönderilemedi: {str(e)}")

    def dogrulama_kodu_kontrol_et(self, kullanici_adi, kod):
        """Doğrulama kodunu kontrol et"""
        try:
            self.imlec.execute("""
                SELECT 1 FROM dogrulama_kodlari 
                WHERE kullanici_adi = %s 
                AND kod = %s 
                AND olusturma_zamani > NOW() - INTERVAL '15 minutes'
            """, (kullanici_adi, kod))
            
            return bool(self.imlec.fetchone())
        except Exception as e:
            print(f"Kod kontrol hatası: {e}")
            return False
