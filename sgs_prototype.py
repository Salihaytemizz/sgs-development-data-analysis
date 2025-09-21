#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SGS - Smart Growth Solutions
Restoran sahipleri için otomatik Excel analizi

Kullanım:
import sgs
sgs.analyze('restaurant_data.xlsx')
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

class SGS:
    def __init__(self):
        self.insights = []
        self.recommendations = []
        self.report_data = {}
        
    def analyze(self, file_path, output_name="sgs_report"):
        """
        Ana fonksiyon: Excel dosyasını analiz et
        """
        print("🍽️ SGS - RESTORAN ANALİZİ BAŞLIYOR")
        print("=" * 50)
        
        # Excel dosyasını oku
        try:
            # Birden fazla sheet var mı kontrol et
            xl_file = pd.ExcelFile(file_path)
            sheets = xl_file.sheet_names
            
            print(f"📄 {len(sheets)} sayfa bulundu: {', '.join(sheets)}")
            
            # İlk sheet'i ana veri olarak al
            df = pd.read_excel(file_path, sheet_name=sheets[0])
            print(f"📊 Ana veri: {len(df)} ürün, {len(df.columns)} özellik")
            
        except Exception as e:
            print(f"❌ Dosya okuma hatası: {e}")
            return
        
        # Restoran-specific analiz
        self._restaurant_analysis(df)
        
        # Rapor oluştur
        self._generate_restaurant_report(df, output_name)
        
        print(f"\n✅ SGS ANALİZİ TAMAMLANDI!")
        print(f"📋 Rapor: {output_name}.html")
        
    def _restaurant_analysis(self, df):
        """Restoran özel analizi"""
        
        print("\n🔍 RESTORAN ANALİZ MOTORU ÇALIŞIYOR...")
        
        # 1. Ürün performans analizi
        self._analyze_product_performance(df)
        
        # 2. Kategori analizi  
        self._analyze_categories(df)
        
        # 3. Fiyat stratejisi
        self._analyze_pricing(df)
        
        # 4. Görsel/foto analizi
        self._analyze_visuals(df)
        
        # 5. Aksiyon önerileri
        self._generate_action_items(df)
        
    def _analyze_product_performance(self, df):
        """Ürün performans analizi"""
        
        # Görüntülenme sütununu bul
        view_cols = [col for col in df.columns if 'görüntülenme' in col.lower() or 'görüntüleme' in col.lower()]
        price_cols = [col for col in df.columns if 'fiyat' in col.lower() or 'price' in col.lower()]
        name_cols = [col for col in df.columns if 'ürün' in col.lower() or 'name' in col.lower() or 'ad' in col.lower()]
        
        if view_cols and price_cols and name_cols:
            view_col = view_cols[0]
            price_col = price_cols[0] 
            name_col = name_cols[0]
            
            # En popüler ürün
            top_product_idx = df[view_col].idxmax()
            top_product = df.loc[top_product_idx]
            
            self.insights.append(f"🏆 En popüler ürün: {top_product[name_col]} ({top_product[view_col]} görüntülenme)")
            
            # En karlı ürün potansiyeli
            df['karlılık_skoru'] = df[price_col] * df[view_col].fillna(0)
            top_profitable_idx = df['karlılık_skoru'].idxmax()
            top_profitable = df.loc[top_profitable_idx]
            
            self.insights.append(f"💰 En karlı ürün: {top_profitable[name_col]} (${top_profitable['karlılık_skoru']:.0f} puan)")
            
            # Düşük performanslı pahalı ürünler
            expensive_threshold = df[price_col].quantile(0.75)
            low_view_threshold = df[view_col].quantile(0.25)
            
            missed_opportunities = df[
                (df[price_col] > expensive_threshold) & 
                (df[view_col] <= low_view_threshold)
            ]
            
            if len(missed_opportunities) > 0:
                self.insights.append(f"⚠️ {len(missed_opportunities)} pahalı ürün az görülüyor (FIRSAT!)")
                
    def _analyze_categories(self, df):
        """Kategori analizi"""
        
        cat_cols = [col for col in df.columns if 'kategori' in col.lower() or 'category' in col.lower()]
        
        if cat_cols:
            cat_col = cat_cols[0]
            
            # En büyük kategori
            cat_counts = df[cat_col].value_counts()
            biggest_cat = cat_counts.index[0]
            
            self.insights.append(f"📦 En büyük kategori: {biggest_cat} ({cat_counts.iloc[0]} ürün)")
            
            # Kategori performansı
            view_cols = [col for col in df.columns if 'görüntülenme' in col.lower()]
            price_cols = [col for col in df.columns if 'fiyat' in col.lower()]
            
            if view_cols and price_cols:
                view_col = view_cols[0]
                price_col = price_cols[0]
                
                cat_performance = df.groupby(cat_col).agg({
                    view_col: 'mean',
                    price_col: 'mean',
                    cat_col: 'count'
                }).round(2)
                
                cat_performance['karlılık'] = cat_performance[view_col] * cat_performance[price_col]
                best_cat = cat_performance['karlılık'].idxmax()
                
                self.insights.append(f"🎯 En karlı kategori: {best_cat}")
                
    def _analyze_pricing(self, df):
        """Fiyat stratejisi analizi"""
        
        price_cols = [col for col in df.columns if 'fiyat' in col.lower()]
        
        if price_cols:
            price_col = price_cols[0]
            
            # Fiyat segmentleri
            df['fiyat_segmenti'] = pd.cut(df[price_col], 
                                        bins=[0, 200, 500, 1000, float('inf')], 
                                        labels=['Ekonomik', 'Orta', 'Premium', 'Lüks'])
            
            # En popüler fiyat segmenti
            segment_counts = df['fiyat_segmenti'].value_counts()
            top_segment = segment_counts.index[0]
            
            self.insights.append(f"💵 En popüler fiyat segmenti: {top_segment} ({segment_counts.iloc[0]} ürün)")
            
    def _analyze_visuals(self, df):
        """Görsel/foto analizi"""
        
        photo_cols = [col for col in df.columns if 'foto' in col.lower() or 'görsel' in col.lower()]
        
        if photo_cols:
            for photo_col in photo_cols:
                if 'durumu' in photo_col.lower():
                    no_photo_count = (df[photo_col] == 'Hayır').sum()
                    total = len(df)
                    
                    if no_photo_count > 0:
                        self.insights.append(f"📷 {no_photo_count}/{total} ürünün fotoğrafı eksik (%{no_photo_count/total*100:.1f})")
                        
    def _generate_action_items(self, df):
        """Aksiyon önerileri"""
        
        print("\n💡 AKSİYON ÖNERİLERİ OLUŞTURULUYOR...")
        
        # Foto eksikliği
        photo_cols = [col for col in df.columns if 'foto' in col.lower()]
        if photo_cols:
            photo_col = photo_cols[0]
            if 'durumu' in photo_col.lower():
                missing_photos = df[df[photo_col] == 'Hayır']
                if len(missing_photos) > 0:
                    self.recommendations.append("📸 Öncelik 1: Fotoğrafı olmayan ürünlere foto ekleyin")
        
        # Badge eksikliği
        badge_cols = [col for col in df.columns if 'badge' in col.lower()]
        if badge_cols:
            badge_col = badge_cols[0]
            no_badge = df[df[badge_col].isna()]
            if len(no_badge) > 0:
                self.recommendations.append("🏷️ Öncelik 2: Popüler ürünlere badge ekleyin")
        
        # Fiyat optimizasyonu
        price_cols = [col for col in df.columns if 'fiyat' in col.lower()]
        view_cols = [col for col in df.columns if 'görüntülenme' in col.lower()]
        
        if price_cols and view_cols:
            price_col = price_cols[0]
            view_col = view_cols[0]
            
            # Pahalı ama az görülen ürünler
            expensive = df[price_col] > df[price_col].quantile(0.75)
            low_views = df[view_col] <= df[view_col].quantile(0.25)
            
            missed_opps = df[expensive & low_views]
            if len(missed_opps) > 0:
                self.recommendations.append(f"🎯 Öncelik 3: {len(missed_opps)} pahalı ürünü öne çıkarın")
        
        # Kategori optimizasyonu
        self.recommendations.append("📊 Öncelik 4: En karlı kategoriye daha fazla ürün ekleyin")
        
    def _generate_restaurant_report(self, df, output_name):
        """HTML rapor oluştur"""
        
        # Temel istatistikler
        total_products = len(df)
        
        price_cols = [col for col in df.columns if 'fiyat' in col.lower()]
        avg_price = df[price_cols[0]].mean() if price_cols else 0
        
        view_cols = [col for col in df.columns if 'görüntülenme' in col.lower()]
        total_views = df[view_cols[0]].sum() if view_cols else 0
        
        # HTML içeriği
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SGS Restoran Analiz Raporu</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .metrics {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .metric {{ background: #f8f9fa; padding: 15px; text-align: center; border-radius: 8px; }}
                .insights {{ background: #e8f5e8; padding: 15px; margin: 20px 0; border-radius: 8px; }}
                .recommendations {{ background: #fff3cd; padding: 15px; margin: 20px 0; border-radius: 8px; }}
                .footer {{ text-align: center; margin-top: 40px; color: #666; }}
                ul {{ list-style-type: none; padding: 0; }}
                li {{ margin: 10px 0; padding: 8px; background: white; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🍽️ SGS - Restoran Analiz Raporu</h1>
                <p>Smart Growth Solutions</p>
            </div>
            
            <div class="metrics">
                <div class="metric">
                    <h3>📊 Toplam Ürün</h3>
                    <h2>{total_products}</h2>
                </div>
                <div class="metric">
                    <h3>💰 Ortalama Fiyat</h3>
                    <h2>${avg_price:.0f}</h2>
                </div>
                <div class="metric">
                    <h3>👀 Toplam Görüntülenme</h3>
                    <h2>{total_views:.0f}</h2>
                </div>
            </div>
            
            <div class="insights">
                <h2>🔍 Ana İçgörüler</h2>
                <ul>
                    {''.join([f'<li>{insight}</li>' for insight in self.insights])}
                </ul>
            </div>
            
            <div class="recommendations">
                <h2>🚀 Aksiyon Önerileri</h2>
                <ul>
                    {''.join([f'<li>{rec}</li>' for rec in self.recommendations])}
                </ul>
            </div>
            
            <div class="footer">
                <p>📅 Rapor Tarihi: {datetime.now().strftime('%d %B %Y, %H:%M')}</p>
                <p>Powered by SGS - Smart Growth Solutions</p>
            </div>
        </body>
        </html>
        """
        
        # HTML dosyasını kaydet
        with open(f'{output_name}.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

# Ana SGS fonksiyonu - tek satır kullanım
def analyze(file_path, output_name="sgs_report"):
    """
    SGS Ana Fonksiyonu
    
    Kullanım:
    import sgs
    sgs.analyze('restaurant_data.xlsx')
    """
    sgs = SGS()
    sgs.analyze(file_path, output_name)

# Test
if __name__ == "__main__":
    # Mevcut Excel dosyanızla test
    print("🧪 SGS PROTOTİP TESTİ")
    analyze('image-table-cs.xlsx', 'sgs_restaurant_report')
