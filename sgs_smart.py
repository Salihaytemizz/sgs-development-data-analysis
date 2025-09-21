#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SGS - Smart Growth Solutions
Akıllı Evrensel Veri Analiz Motoru

Herhangi bir Excel dosyasını analiz et:
- Restoran verisi → Menü optimizasyonu
- E-ticaret → Ürün performansı  
- Satış → Trend analizi
- Envanter → Stok optimizasyonu

Kullanım:
import sgs_smart as sgs
sgs.analyze('herhangi_veri.xlsx')
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re
from typing import Dict, List, Any, Optional

class SmartSGS:
    def __init__(self):
        self.df = None
        self.data_type = "unknown"
        self.columns_map = {}
        self.insights = []
        self.recommendations = []
        
    def analyze(self, file_path: str, output_name: str = "sgs_smart_report"):
        """
        Akıllı analiz motoru - herhangi veriyi tanır ve analiz eder
        """
        print("🧠 SGS - AKILLI ANALİZ MOTORU")
        print("=" * 50)
        
        # 1. Veriyi yükle
        if not self._load_data(file_path):
            return
            
        # 2. Veri türünü tanı
        self._detect_data_type()
        
        # 3. Sütunları haritalandır
        self._map_columns()
        
        # 4. Uygun analizi gerçekleştir
        self._execute_smart_analysis()
        
        # 5. Rapor oluştur
        self._generate_smart_report(output_name)
        
        print(f"\n✅ SGS AKILLI ANALİZ TAMAMLANDI!")
        print(f"📋 Rapor: {output_name}.html")
    
    def _load_data(self, file_path: str) -> bool:
        """Veri dosyasını yükle"""
        try:
            if file_path.endswith(('.xlsx', '.xls')):
                # Birden fazla sheet kontrol et
                xl_file = pd.ExcelFile(file_path)
                sheets = xl_file.sheet_names
                print(f"📄 {len(sheets)} sayfa bulundu: {', '.join(sheets)}")
                
                # En büyük sheet'i al (genelde ana veri)
                sheet_sizes = {}
                for sheet in sheets:
                    df_temp = pd.read_excel(file_path, sheet_name=sheet)
                    sheet_sizes[sheet] = len(df_temp)
                
                main_sheet = max(sheet_sizes, key=sheet_sizes.get)
                self.df = pd.read_excel(file_path, sheet_name=main_sheet)
                print(f"📊 Ana veri seçildi: '{main_sheet}' ({len(self.df)} satır, {len(self.df.columns)} sütun)")
                
            elif file_path.endswith('.csv'):
                self.df = pd.read_csv(file_path)
                print(f"📊 CSV yüklendi: {len(self.df)} satır, {len(self.df.columns)} sütun")
            else:
                print(f"❌ Desteklenmeyen format. Desteklenen: .xlsx, .xls, .csv")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ Dosya yükleme hatası: {e}")
            return False
    
    def _detect_data_type(self):
        """Veri türünü otomatik tespit et"""
        print(f"\n🔍 VERİ TÜRÜ TESPİTİ...")
        
        columns_lower = [col.lower() for col in self.df.columns]
        columns_text = ' '.join(columns_lower)
        
        # Restoran/Menü verisi tespiti
        restaurant_keywords = [
            'ürün', 'menü', 'kategori', 'fiyat', 'görüntülenme', 'foto', 'badge',
            'yemek', 'içecek', 'pizza', 'burger', 'salata', 'tatlı', 'restoran'
        ]
        restaurant_score = sum(1 for keyword in restaurant_keywords if keyword in columns_text)
        
        # E-ticaret verisi tespiti  
        ecommerce_keywords = [
            'product', 'price', 'stock', 'inventory', 'sales', 'orders', 'customer',
            'sku', 'brand', 'rating', 'review', 'cart', 'checkout'
        ]
        ecommerce_score = sum(1 for keyword in ecommerce_keywords if keyword in columns_text)
        
        # Satış verisi tespiti
        sales_keywords = [
            'satış', 'müşteri', 'tutar', 'tarih', 'date', 'amount', 'quantity',
            'revenue', 'profit', 'commission', 'deal', 'lead'
        ]
        sales_score = sum(1 for keyword in sales_keywords if keyword in columns_text)
        
        # Envanter verisi tespiti
        inventory_keywords = [
            'stok', 'envanter', 'adet', 'miktar', 'depo', 'warehouse', 'stock',
            'inventory', 'supply', 'storage'
        ]
        inventory_score = sum(1 for keyword in inventory_keywords if keyword in columns_text)
        
        # En yüksek skora sahip türü seç
        scores = {
            'restaurant': restaurant_score,
            'ecommerce': ecommerce_score, 
            'sales': sales_score,
            'inventory': inventory_score
        }
        
        self.data_type = max(scores, key=scores.get)
        max_score = scores[self.data_type]
        
        data_type_names = {
            'restaurant': 'Restoran/Menü Verisi',
            'ecommerce': 'E-ticaret Verisi',
            'sales': 'Satış Verisi', 
            'inventory': 'Envanter Verisi'
        }
        
        if max_score > 0:
            print(f"✅ Tespit edilen tür: {data_type_names[self.data_type]} (Güven: {max_score}/10)")
        else:
            self.data_type = 'general'
            print(f"📊 Genel veri olarak analiz edilecek")
    
    def _map_columns(self):
        """Sütunları standart isimlere haritalandır"""
        print(f"🗺️ SÜTUN HARİTALANDIRMA...")
        
        for col in self.df.columns:
            col_lower = col.lower()
            mapped_type = 'other'
            
            # Fiyat sütunları
            if any(word in col_lower for word in ['fiyat', 'price', 'tutar', 'amount', 'cost']):
                mapped_type = 'price'
            
            # Metrik sütunları (görüntülenme, satış, adet)
            elif any(word in col_lower for word in ['görüntülenme', 'view', 'click', 'sales', 'adet', 'quantity']):
                mapped_type = 'metric'
            
            # Kategori sütunları
            elif any(word in col_lower for word in ['kategori', 'category', 'grup', 'type', 'class']):
                mapped_type = 'category'
                
            # İsim sütunları
            elif any(word in col_lower for word in ['ürün', 'product', 'name', 'ad', 'isim', 'title']):
                mapped_type = 'name'
                
            # Tarih sütunları
            elif any(word in col_lower for word in ['tarih', 'date', 'time', 'created']):
                mapped_type = 'date'
                
            # Durum sütunları
            elif any(word in col_lower for word in ['durum', 'status', 'state', 'foto', 'photo']):
                mapped_type = 'status'
            
            # Ek bilgi sütunları
            elif any(word in col_lower for word in ['badge', 'tag', 'label', 'note', 'description']):
                mapped_type = 'meta'
            
            self.columns_map[col] = mapped_type
        
        # Haritalandırma sonuçlarını göster
        type_counts = {}
        for col, col_type in self.columns_map.items():
            if col_type not in type_counts:
                type_counts[col_type] = []
            type_counts[col_type].append(col)
        
        for col_type, cols in type_counts.items():
            if col_type != 'other':
                print(f"  {col_type}: {', '.join(cols)}")
    
    def _execute_smart_analysis(self):
        """Veri türüne göre uygun analizi gerçekleştir"""
        print(f"\n🚀 {self.data_type.upper()} ANALİZİ BAŞLIYOR...")
        
        if self.data_type == 'restaurant':
            self._restaurant_analysis()
        elif self.data_type == 'ecommerce':
            self._ecommerce_analysis()
        elif self.data_type == 'sales':
            self._sales_analysis()
        elif self.data_type == 'inventory':
            self._inventory_analysis()
        else:
            self._general_analysis()
    
    def _restaurant_analysis(self):
        """Restoran özel analizi"""
        # Performans analizi
        price_cols = [col for col, col_type in self.columns_map.items() if col_type == 'price']
        metric_cols = [col for col, col_type in self.columns_map.items() if col_type == 'metric']
        category_cols = [col for col, col_type in self.columns_map.items() if col_type == 'category']
        name_cols = [col for col, col_type in self.columns_map.items() if col_type == 'name']
        
        if price_cols and metric_cols and name_cols:
            price_col = price_cols[0]
            metric_col = metric_cols[0]
            name_col = name_cols[0]
            
            # En popüler ürün
            if not self.df[metric_col].isna().all():
                top_idx = self.df[metric_col].idxmax()
                top_product = self.df.loc[top_idx]
                self.insights.append(f"🏆 En popüler ürün: {top_product[name_col]} ({top_product[metric_col]:.0f} {metric_col.lower()})")
            
            # Karlılık analizi
            self.df['karlılık_skoru'] = self.df[price_col] * self.df[metric_col].fillna(0)
            if not self.df['karlılık_skoru'].isna().all():
                profitable_idx = self.df['karlılık_skoru'].idxmax()
                profitable_product = self.df.loc[profitable_idx]
                self.insights.append(f"💰 En karlı ürün: {profitable_product[name_col]} ({profitable_product['karlılık_skoru']:.0f} puan)")
        
        # Kategori analizi
        if category_cols:
            cat_col = category_cols[0]
            cat_counts = self.df[cat_col].value_counts()
            if len(cat_counts) > 0:
                self.insights.append(f"📦 En büyük kategori: {cat_counts.index[0]} ({cat_counts.iloc[0]} ürün)")
        
        # Foto analizi
        status_cols = [col for col, col_type in self.columns_map.items() if col_type == 'status']
        for status_col in status_cols:
            if 'foto' in status_col.lower():
                missing_photos = (self.df[status_col] == 'Hayır').sum()
                if missing_photos > 0:
                    total = len(self.df)
                    self.insights.append(f"📷 {missing_photos}/{total} ürünün fotoğrafı eksik (%{missing_photos/total*100:.1f})")
                    self.recommendations.append("📸 Öncelik: Fotoğrafı olmayan ürünlere foto ekleyin")
    
    def _ecommerce_analysis(self):
        """E-ticaret analizi"""
        self.insights.append("🛒 E-ticaret verisi tespit edildi")
        # E-ticaret özel analizleri burada olacak
        
    def _sales_analysis(self):
        """Satış analizi"""
        self.insights.append("💼 Satış verisi tespit edildi")
        # Satış özel analizleri burada olacak
        
    def _inventory_analysis(self):
        """Envanter analizi"""
        self.insights.append("📦 Envanter verisi tespit edildi")
        # Envanter özel analizleri burada olacak
        
    def _general_analysis(self):
        """Genel analiz"""
        self.insights.append(f"📊 Genel veri analizi ({len(self.df)} kayıt)")
        
        # Sayısal sütunlar için temel istatistikler
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            self.insights.append(f"🔢 {len(numeric_cols)} sayısal sütun bulundu")
    
    def _generate_smart_report(self, output_name: str):
        """Akıllı HTML rapor oluştur"""
        data_type_names = {
            'restaurant': 'Restoran/Menü',
            'ecommerce': 'E-ticaret', 
            'sales': 'Satış',
            'inventory': 'Envanter',
            'general': 'Genel'
        }
        
        type_name = data_type_names.get(self.data_type, 'Bilinmeyen')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SGS Akıllı Analiz Raporu - {type_name}</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; line-height: 1.6; background: #f5f7fa; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 12px 12px 0 0; }}
                .data-type {{ background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 20px; display: inline-block; margin-top: 10px; }}
                .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px; }}
                .metric {{ background: #f8f9fa; padding: 20px; text-align: center; border-radius: 12px; border-left: 4px solid #667eea; }}
                .insights {{ background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%); padding: 25px; margin: 20px 30px; border-radius: 12px; }}
                .recommendations {{ background: linear-gradient(135deg, #fff3cd 0%, #fef8e6 100%); padding: 25px; margin: 20px 30px; border-radius: 12px; }}
                .footer {{ text-align: center; margin: 30px; color: #666; padding: 20px; }}
                ul {{ list-style-type: none; padding: 0; }}
                li {{ margin: 12px 0; padding: 12px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                h1, h2 {{ margin: 0; }}
                .badge {{ background: #667eea; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 SGS - Akıllı Analiz Raporu</h1>
                    <p>Smart Growth Solutions</p>
                    <div class="data-type">
                        <span class="badge">{type_name} Verisi Tespit Edildi</span>
                    </div>
                </div>
                
                <div class="metrics">
                    <div class="metric">
                        <h3>📊 Toplam Kayıt</h3>
                        <h2>{len(self.df)}</h2>
                    </div>
                    <div class="metric">
                        <h3>📋 Sütun Sayısı</h3>
                        <h2>{len(self.df.columns)}</h2>
                    </div>
                    <div class="metric">
                        <h3>🧠 Veri Türü</h3>
                        <h2>{type_name}</h2>
                    </div>
                    <div class="metric">
                        <h3>⚡ Analiz Süresi</h3>
                        <h2>< 1 saniye</h2>
                    </div>
                </div>
                
                <div class="insights">
                    <h2>💡 Akıllı İçgörüler</h2>
                    <ul>
                        {''.join([f'<li>{insight}</li>' for insight in self.insights])}
                    </ul>
                </div>
                
                <div class="recommendations">
                    <h2>🚀 Aksiyon Önerileri</h2>
                    <ul>
                        {''.join([f'<li>{rec}</li>' for rec in self.recommendations])}
                        <li>📊 SGS ile daha detaylı analiz için premium özellikleri keşfedin</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>📅 Rapor Tarihi: {datetime.now().strftime('%d %B %Y, %H:%M')}</p>
                    <p><strong>Powered by SGS - Smart Growth Solutions</strong></p>
                    <p>🧠 Yapay zeka ile desteklenen akıllı veri analizi</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(f'{output_name}.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

# Ana SGS fonksiyonu
def analyze(file_path: str, output_name: str = "sgs_smart_report"):
    """
    SGS Akıllı Analiz
    
    Kullanım:
    import sgs_smart as sgs
    sgs.analyze('herhangi_veri.xlsx')
    """
    smart_sgs = SmartSGS()
    smart_sgs.analyze(file_path, output_name)

# Test
if __name__ == "__main__":
    print("🧪 SGS AKILLI ANALİZ TESTİ")
    # Test verisi ile deneme
    analyze('image-table-cs.xlsx', 'sgs_smart_test')
