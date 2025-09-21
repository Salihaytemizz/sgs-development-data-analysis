#!/usr/bin/env python3
"""
SGS - Smart Growth Solutions
Ultra basit veri analizi

Kullanım:
import sgs
sgs.read_csv("data.csv")     # Tek satır - tüm analiz!
sgs.read_excel("data.xlsx")  # Excel için
"""

import pandas as pd
import numpy as np
from datetime import datetime

class SGS:
    def __init__(self):
        self.data = None
        self.insights = []
    
    def read_csv(self, file_path):
        """CSV oku ve otomatik analiz et"""
        print("🧠 SGS - Akıllı Analiz")
        
        # Veriyi yükle
        self.data = pd.read_csv(file_path)
        print(f"📊 {len(self.data)} satır, {len(self.data.columns)} sütun")
        
        # Otomatik analiz
        self._auto_analyze()
        
        # Sonuçları göster
        self._show_results()
        
        return self.data
    
    def read_excel(self, file_path):
        """Excel oku ve otomatik analiz et"""
        print("🧠 SGS - Akıllı Analiz")
        
        # Veriyi yükle
        self.data = pd.read_excel(file_path)
        print(f"📊 {len(self.data)} satır, {len(self.data.columns)} sütun")
        
        # Otomatik analiz
        self._auto_analyze()
        
        # Sonuçları göster
        self._show_results()
        
        return self.data
    
    def _auto_analyze(self):
        """Otomatik akıllı analiz"""
        if self.data is None:
            return
        
        # Sütun türlerini tanı
        for col in self.data.columns:
            col_lower = col.lower()
            
            # En popüler ürün/öğe
            if any(word in col_lower for word in ['görüntülenme', 'view', 'click']):
                if not self.data[col].isna().all():
                    max_idx = self.data[col].idxmax()
                    name_col = self._find_name_column()
                    if name_col:
                        product = self.data.loc[max_idx, name_col]
                        value = self.data.loc[max_idx, col]
                        self.insights.append(f"🏆 En popüler: {product} ({value:,.0f})")
            
            # En pahalı
            if any(word in col_lower for word in ['fiyat', 'price', 'tutar']):
                if not self.data[col].isna().all():
                    max_idx = self.data[col].idxmax()
                    name_col = self._find_name_column()
                    if name_col:
                        product = self.data.loc[max_idx, name_col]
                        value = self.data.loc[max_idx, col]
                        self.insights.append(f"💰 En pahalı: {product} ({value:,.0f}₺)")
        
        # Kategori analizi
        cat_col = self._find_category_column()
        if cat_col:
            top_category = self.data[cat_col].value_counts().index[0]
            count = self.data[cat_col].value_counts().iloc[0]
            self.insights.append(f"📦 En büyük kategori: {top_category} ({count} ürün)")
        
        # Eksik veriler
        for col in self.data.columns:
            if 'foto' in col.lower() and 'durum' in col.lower():
                missing = (self.data[col] == 'Hayır').sum()
                if missing > 0:
                    self.insights.append(f"📷 {missing} ürünün fotoğrafı eksik")
    
    def _find_name_column(self):
        """İsim sütununu bul"""
        for col in self.data.columns:
            if any(word in col.lower() for word in ['ürün', 'product', 'name', 'ad', 'isim']):
                return col
        return None
    
    def _find_category_column(self):
        """Kategori sütununu bul"""
        for col in self.data.columns:
            if any(word in col.lower() for word in ['kategori', 'category', 'grup']):
                return col
        return None
    
    def _show_results(self):
        """Sonuçları göster"""
        if self.insights:
            print("\n💡 Bulgular:")
            for insight in self.insights:
                print(f"   {insight}")
        
        print(f"\n✅ Analiz tamamlandı! {len(self.insights)} bulgu")
    
    def compare(self, col1, col2):
        """İki sütunu karşılaştır"""
        if self.data is None:
            print("❌ Önce veri yükleyin")
            return
        
        if col1 in self.data.columns and col2 in self.data.columns:
            correlation = self.data[col1].corr(self.data[col2])
            print(f"🔗 {col1} vs {col2}: {correlation:.2f} korelasyon")
        else:
            print("❌ Sütunlar bulunamadı")
    
    def trend(self, column, period="daily"):
        """Trend analizi"""
        if self.data is None:
            print("❌ Önce veri yükleyin")
            return
        
        if column in self.data.columns:
            print(f"📈 {column} trend analizi yapılıyor...")
            # Basit trend hesaplama
            values = self.data[column].dropna()
            if len(values) > 1:
                trend_direction = "yükselişte" if values.iloc[-1] > values.iloc[0] else "düşüşte"
                print(f"📊 Trend: {trend_direction}")
        else:
            print("❌ Sütun bulunamadı")

# Global fonksiyon - daha da basit kullanım
_sgs_instance = SGS()

def read_csv(file_path):
    """Ultra basit CSV okuma"""
    return _sgs_instance.read_csv(file_path)

def read_excel(file_path):
    """Ultra basit Excel okuma"""
    return _sgs_instance.read_excel(file_path)

def compare(col1, col2):
    """Ultra basit karşılaştırma"""
    return _sgs_instance.compare(col1, col2)

def trend(column, period="daily"):
    """Ultra basit trend"""
    return _sgs_instance.trend(column, period)

# Test
if __name__ == "__main__":
    print("🧪 SGS Test")
    # Test için mevcut Excel dosyasını kullan
    read_excel("image-table-cs.xlsx")