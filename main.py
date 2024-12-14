import hashlib
import secrets
import string
import re
from datetime import datetime, timedelta
from veritabani import VeritabaniYoneticisi
import uuid

class SifreYoneticisi:
    def __init__(self):
        self.vt = VeritabaniYoneticisi()
        self.vt.baglan()
        self.mevcut_kullanici = None
        self.maksimum_giris_denemesi = 3
        self.kilit_suresi_dakika = 30

    def sifre_gucunu_degerlendir(self, sifre: str) -> tuple:
        puan = 0
        geri_bildirim = []

        if len(sifre) >= 12:
            puan += 2
        elif len(sifre) >= 8:
            puan += 1
        else:
            geri_bildirim.append("Şifre en az 8 karakter olmalıdır.")

        if re.search(r"[A-Z]", sifre):
            puan += 1
        else:
            geri_bildirim.append("Büyük harf ekleyin.")

        if re.search(r"[a-z]", sifre):
            puan += 1
        else:
            geri_bildirim.append("Küçük harf ekleyin.")

        if re.search(r"\d", sifre):
            puan += 1
        else:
            geri_bildirim.append("Sayı ekleyin.")

        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", sifre):
            puan += 1
        else:
            geri_bildirim.append("Özel karakter ekleyin.")

        guc = "Zayıf"
        if puan >= 5:
            guc = "Güçlü"
        elif puan >= 3:
            guc = "Orta"

        return guc, geri_bildirim

    def guvenli_sifre_olustur(self, uzunluk=16, ozel_karakterler=True, sayilar=True) -> str:
        karakterler = string.ascii_letters
        if sayilar:
            karakterler += string.digits
        if ozel_karakterler:
            karakterler += "!@#$%^&*(),.?\":{}|<>"
        
        while True:
            sifre = ''.join(secrets.choice(karakterler) for _ in range(uzunluk))
            guc, _ = self.sifre_gucunu_degerlendir(sifre)
            if guc == "Güçlü":
                return sifre

    def kullanici_kayit(self, kullanici_adi: str, sifre: str, email: str) -> bool:
        try:
            sifre_hash = hashlib.sha256(sifre.encode()).hexdigest()
            sorgu = """
            INSERT INTO kullanicilar (kullanici_adi, sifre_hash, email)
            VALUES (%s, %s, %s)
            """
            self.vt.imlec.execute(sorgu, (kullanici_adi, sifre_hash, email))
            self.vt.baglanti.commit()
            return True
        except Exception as e:
            print(f"Kayıt hatası: {e}")
            return False

    def kullanici_giris(self, kullanici_adi: str, sifre: str) -> bool:
        try:
            sorgu = "SELECT * FROM kullanicilar WHERE kullanici_adi = %s"
            self.vt.imlec.execute(sorgu, (kullanici_adi,))
            kullanici = self.vt.imlec.fetchone()

            if not kullanici:
                return False

            if kullanici[7]:  # hesap_kilitli
                kilit_bitis = kullanici[8]  # kilit_bitis_tarihi
                if kilit_bitis and datetime.now() < kilit_bitis:
                    kalan_sure = (kilit_bitis - datetime.now()).minutes
                    print(f"Hesabınız kilitli. Kalan süre: {kalan_sure} dakika")
                    return False

            sifre_hash = hashlib.sha256(sifre.encode()).hexdigest()
            if sifre_hash == kullanici[2]:  # sifre_hash
                self.mevcut_kullanici = kullanici[0]  # kullanici_id
                self.vt.imlec.execute("""
                    UPDATE kullanicilar 
                    SET basarisiz_giris_sayisi = 0, 
                        hesap_kilitli = FALSE, 
                        son_giris_tarihi = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (self.mevcut_kullanici,))
                self.vt.baglanti.commit()
                return True
            else:
                yeni_deneme_sayisi = kullanici[6] + 1
                if yeni_deneme_sayisi >= self.maksimum_giris_denemesi:
                    kilit_bitis = datetime.now() + timedelta(minutes=self.kilit_suresi_dakika)
                    self.vt.imlec.execute("""
                        UPDATE kullanicilar 
                        SET basarisiz_giris_sayisi = %s,
                            hesap_kilitli = TRUE,
                            kilit_bitis_tarihi = %s
                        WHERE id = %s
                    """, (yeni_deneme_sayisi, kilit_bitis, kullanici[0]))
                else:
                    self.vt.imlec.execute("""
                        UPDATE kullanicilar 
                        SET basarisiz_giris_sayisi = %s
                        WHERE id = %s
                    """, (yeni_deneme_sayisi, kullanici[0]))
                self.vt.baglanti.commit()
                return False
        except Exception as e:
            print(f"Giriş hatası: {e}")
            return False

    def sifre_paylas(self, sifre_id: int, gecerlilik_suresi: int = 10) -> tuple:
        try:
            self.vt.imlec.execute("""
                SELECT id FROM sifreler 
                WHERE id = %s AND kullanici_id = %s
            """, (sifre_id, self.mevcut_kullanici))
            
            if not self.vt.imlec.fetchone():
                return None, None

            paylasim_kodu = str(uuid.uuid4())
            pin_kodu = ''.join(secrets.choice(string.digits) for _ in range(6))
            son_kullanma = datetime.now() + timedelta(minutes=gecerlilik_suresi)

            self.vt.imlec.execute("""
                INSERT INTO paylasim_baglantilari 
                (sifre_id, paylasim_kodu, pin_kodu, son_kullanma_tarihi)
                VALUES (%s, %s, %s, %s)
            """, (sifre_id, paylasim_kodu, pin_kodu, son_kullanma))
            
            self.vt.baglanti.commit()
            return paylasim_kodu, pin_kodu
        except Exception as e:
            print(f"Paylaşım hatası: {e}")
            return None, None

    def paylasilan_sifreyi_al(self, paylasim_kodu: str, pin_kodu: str) -> str:
        try:
            self.vt.imlec.execute("""
                SELECT s.sifrelenmis_sifre, p.kullanildi, p.son_kullanma_tarihi
                FROM paylasim_baglantilari p
                JOIN sifreler s ON p.sifre_id = s.id
                WHERE p.paylasim_kodu = %s AND p.pin_kodu = %s
            """, (paylasim_kodu, pin_kodu))
            
            sonuc = self.vt.imlec.fetchone()
            if not sonuc:
                return None

            sifrelenmis_sifre, kullanildi, son_kullanma = sonuc

            if kullanildi or datetime.now() > son_kullanma:
                return None

            self.vt.imlec.execute("""
                UPDATE paylasim_baglantilari
                SET kullanildi = TRUE
                WHERE paylasim_kodu = %s
            """, (paylasim_kodu,))
            
            self.vt.baglanti.commit()
            return self.vt.sifre_coz(sifrelenmis_sifre)
        except Exception as e:
            print(f"Paylaşılan şifre alma hatası: {e}")
            return None

    def kapat(self):
        self.vt.kapat()

    def sifre_ekle(self, baslik: str, sifre: str, website: str = "", aciklama: str = "") -> bool:
        try:
            sifrelenmis_sifre = self.vt.sifre_sifrele(sifre)
            sorgu = """
            INSERT INTO sifreler (kullanici_id, baslik, sifrelenmis_sifre, website, aciklama)
            VALUES (%s, %s, %s, %s, %s)
            """
            self.vt.imlec.execute(sorgu, (self.mevcut_kullanici, baslik, sifrelenmis_sifre, website, aciklama))
            self.vt.baglanti.commit()
            return True
        except Exception as e:
            print(f"Şifre ekleme hatası: {e}")
            return False

    def sifreleri_getir(self) -> list:
        try:
            sorgu = """
            SELECT id, baslik, sifrelenmis_sifre, website, aciklama, son_guncelleme_tarihi
            FROM sifreler
            WHERE kullanici_id = %s
            ORDER BY son_guncelleme_tarihi DESC
            """
            self.vt.imlec.execute(sorgu, (self.mevcut_kullanici,))
            sifreler = self.vt.imlec.fetchall()
            
            sonuclar = []
            for sifre in sifreler:
                try:
                    cozulmus_sifre = self.vt.sifre_coz(sifre[2])
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
        except Exception as e:
            print(f"Şifre getirme hatası: {e}")
            return []

    def sifre_guncelle(self, sifre_id: int, baslik: str, sifre: str, website: str, aciklama: str) -> bool:
        try:
            sifrelenmis_sifre = self.vt.sifre_sifrele(sifre)
            sorgu = """
            UPDATE sifreler
            SET baslik = %s, sifrelenmis_sifre = %s, website = %s, aciklama = %s,
                son_guncelleme_tarihi = CURRENT_TIMESTAMP
            WHERE id = %s AND kullanici_id = %s
            """
            self.vt.imlec.execute(sorgu, (baslik, sifrelenmis_sifre, website, aciklama, sifre_id, self.mevcut_kullanici))
            self.vt.baglanti.commit()
            return True
        except Exception as e:
            print(f"Şifre güncelleme hatası: {e}")
            return False

    def sifre_sil(self, sifre_id: int) -> bool:
        try:
            sorgu = "DELETE FROM sifreler WHERE id = %s AND kullanici_id = %s"
            self.vt.imlec.execute(sorgu, (sifre_id, self.mevcut_kullanici))
            self.vt.baglanti.commit()
            return True
        except Exception as e:
            print(f"Şifre silme hatası: {e}")
            return False