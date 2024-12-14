import psycopg2
from psycopg2 import Error
from cryptography.fernet import Fernet
import os
from datetime import datetime, timedelta
import hashlib

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

    def sifreleri_getir(self, kullanici_id):
        try:
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
            sifre_hash = hashlib.sha256(sifre.encode()).hexdigest()
            self.imlec.execute("""
                SELECT id FROM kullanicilar 
                WHERE kullanici_adi = %s AND sifre_hash = %s
            """, (kullanici_adi, sifre_hash))
            sonuc = self.imlec.fetchone()
            return sonuc[0] if sonuc else None  # Kullanıcı ID'sini döndür
        except psycopg2.Error as e:
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
