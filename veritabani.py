import psycopg2
from psycopg2 import Error
from cryptography.fernet import Fernet
import os
from datetime import datetime, timedelta

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
