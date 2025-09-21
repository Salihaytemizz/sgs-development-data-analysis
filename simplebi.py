#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SimpleBI - Pandas kadar basit, SQL kadar detaylı
Tek cümle ile veri analizi

Kullanım:
from simplebi import SimpleBI
data = SimpleBI('restaurant.xlsx')
data.ask("En karlı kategoriler neler?")
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Any, Optional

class SimpleBI:
    def __init__(self, file_path: str = None):
        """
        SimpleBI - Tek cümle veri analizi
        """
        self.df = None
        self.file_path = file_path
        self.columns_info = {}
        
        if file_path:
            self.load(file_path)
    
    def load(self, file_path: str):
        """Veri dosyasını yükle"""
        try:
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                self.df = pd.read_excel(file_path)
            elif file_path.endswith('.csv'):
                self.df = pd.read_csv(file_path)
            else:
                raise ValueError("Desteklenen formatlar: .xlsx, .xls, .csv")
            
            self.file_path = file_path
            self._analyze_columns()
            print(f"✅ {len(self.df)} satır, {len(self.df.columns)} sütun yüklendi")
            
        except Exception as e:
            print(f"❌ Dosya yükleme hatası: {e}")
    
    def _analyze_columns(self):
        """Sütunları analiz et ve türlerini belirle"""
        for col in self.df.columns:
            col_lower = col.lower()
            sample_data = self.df[col].dropna().head(10)
            
            # Sütun türünü tahmin et
            col_type = "unknown"
            
            if any(keyword in col_lower for keyword in ['fiyat', 'price', 'tutar', 'amount']):
                col_type = "price"
            elif any(keyword in col_lower for keyword in ['görüntülenme', 'view', 'click', 'tıklama']):
                col_type = "metric"
            elif any(keyword in col_lower for keyword in ['kategori', 'category', 'grup', 'type']):
                col_type = "category"
            elif any(keyword in col_lower for keyword in ['ürün', 'product', 'name', 'ad', 'isim']):
                col_type = "name"
            elif any(keyword in col_lower for keyword in ['tarih', 'date', 'time']):
                col_type = "date"
            elif self.df[col].dtype in ['int64', 'float64']:
                col_type = "numeric"
            else:
                col_type = "text"
            
            self.columns_info[col] = {
                'type': col_type,
                'dtype': str(self.df[col].dtype),
                'sample': sample_data.tolist()
            }
    
    def ask(self, question: str) -> Dict[str, Any]:
        """
        Doğal dilde soru sor, analiz al
        
        Örnekler:
        - "En karlı kategoriler neler?"
        - "Hangi ürünler en çok görüntüleniyor?"
        - "Fiyatı 200'den yüksek ürünler?"
        - "Fotoğrafı olmayan ürünler kaç tane?"
        """
        if self.df is None:
            return {"error": "Önce veri yükleyin: data.load('dosya.xlsx')"}
        
        # Soruyu analiz et
        analysis_type = self._understand_question(question)
        
        # Analizi gerçekleştir
        result = self._execute_analysis(analysis_type, question)
        
        # Sonucu formatla
        return self._format_result(result, question)
    
    def _understand_question(self, question: str) -> Dict[str, Any]:
        """Soruyu anlayıp analiz türünü belirle"""
        q_lower = question.lower()
        
        analysis = {
            'type': 'unknown',
            'target_columns': [],
            'group_by': None,
            'filter_conditions': [],
            'aggregation': None,
            'sort_order': 'desc'
        }
        
        # En/En çok/En az sorular
        if any(word in q_lower for word in ['en ', 'en çok', 'en az', 'en yüksek', 'en düşük']):
            analysis['type'] = 'ranking'
            
            if 'karlı' in q_lower:
                analysis['aggregation'] = 'profitability'
            elif any(word in q_lower for word in ['görüntülen', 'popüler', 'çok']):
                analysis['aggregation'] = 'max'
            elif any(word in q_lower for word in ['az', 'düşük']):
                analysis['sort_order'] = 'asc'
        
        # Sayma soruları
        elif any(word in q_lower for word in ['kaç', 'adet', 'sayı']):
            analysis['type'] = 'count'
        
        # Karşılaştırma soruları
        elif any(word in q_lower for word in ['karşılaştır', 'fark', 'vs']):
            analysis['type'] = 'comparison'
        
        # Filtreleme soruları
        elif any(word in q_lower for word in ['hangi', 'which', 'liste']):
            analysis['type'] = 'filter'
        
        # Kategori belirleme
        if 'kategori' in q_lower:
            cat_cols = [col for col, info in self.columns_info.items() 
                       if info['type'] == 'category']
            if cat_cols:
                analysis['group_by'] = cat_cols[0]
        
        # Hedef sütunları belirle
        for col in self.df.columns:
            if col.lower() in q_lower:
                analysis['target_columns'].append(col)
        
        return analysis
    
    def _execute_analysis(self, analysis_type: Dict, question: str) -> Dict[str, Any]:
        """Analizi gerçekleştir"""
        result = {}
        
        try:
            if analysis_type['type'] == 'ranking':
                result = self._ranking_analysis(analysis_type, question)
            elif analysis_type['type'] == 'count':
                result = self._count_analysis(analysis_type, question)
            elif analysis_type['type'] == 'filter':
                result = self._filter_analysis(analysis_type, question)
            elif analysis_type['type'] == 'comparison':
                result = self._comparison_analysis(analysis_type, question)
            else:
                result = self._general_analysis(question)
                
        except Exception as e:
            result = {"error": f"Analiz hatası: {e}"}
        
        return result
    
    def _ranking_analysis(self, analysis: Dict, question: str) -> Dict:
        """Sıralama analizi (en çok, en az, vb.)"""
        q_lower = question.lower()
        
        if 'karlı' in q_lower and analysis['group_by']:
            # Karlılık analizi = fiyat * görüntülenme
            price_cols = [col for col, info in self.columns_info.items() if info['type'] == 'price']
            metric_cols = [col for col, info in self.columns_info.items() if info['type'] == 'metric']
            
            if price_cols and metric_cols:
                price_col = price_cols[0]
                metric_col = metric_cols[0]
                
                # Karlılık skoru hesapla
                df_copy = self.df.copy()
                df_copy['karlılık_skoru'] = df_copy[price_col] * df_copy[metric_col].fillna(0)
                
                # Kategoriye göre grupla
                result_df = df_copy.groupby(analysis['group_by']).agg({
                    'karlılık_skoru': 'sum',
                    price_col: 'mean',
                    metric_col: 'sum'
                }).round(2)
                
                result_df = result_df.sort_values('karlılık_skoru', ascending=False)
                
                return {
                    'data': result_df,
                    'insight': f"En karlı kategori: {result_df.index[0]} ({result_df.iloc[0]['karlılık_skoru']} puan)",
                    'type': 'ranking_profitability'
                }
        
        # Genel sıralama
        if analysis['group_by'] and analysis['target_columns']:
            target_col = analysis['target_columns'][0]
            result_df = self.df.groupby(analysis['group_by'])[target_col].sum().sort_values(ascending=False)
            
            return {
                'data': result_df,
                'insight': f"En yüksek: {result_df.index[0]} ({result_df.iloc[0]})",
                'type': 'ranking_simple'
            }
        
        return {"error": "Sıralama için uygun sütun bulunamadı"}
    
    def _count_analysis(self, analysis: Dict, question: str) -> Dict:
        """Sayma analizi"""
        q_lower = question.lower()
        
        # Foto eksik olanları say
        if 'foto' in q_lower and 'eksik' in q_lower or 'olmayan' in q_lower:
            photo_cols = [col for col in self.df.columns if 'foto' in col.lower()]
            if photo_cols:
                photo_col = photo_cols[0]
                missing_count = (self.df[photo_col] == 'Hayır').sum()
                total_count = len(self.df)
                
                return {
                    'data': {'eksik': missing_count, 'toplam': total_count},
                    'insight': f"{missing_count}/{total_count} ürünün fotoğrafı eksik (%{missing_count/total_count*100:.1f})",
                    'type': 'count_missing'
                }
        
        # Genel sayma
        if analysis['group_by']:
            counts = self.df[analysis['group_by']].value_counts()
            return {
                'data': counts,
                'insight': f"En çok: {counts.index[0]} ({counts.iloc[0]} adet)",
                'type': 'count_general'
            }
        
        return {"data": {"toplam": len(self.df)}, "insight": f"Toplam {len(self.df)} kayıt", "type": "count_total"}
    
    def _filter_analysis(self, analysis: Dict, question: str) -> Dict:
        """Filtreleme analizi"""
        q_lower = question.lower()
        
        # Fiyat filtreleme
        price_match = re.search(r'(\d+)', q_lower)
        if price_match and any(word in q_lower for word in ['fiyat', 'price']):
            price_threshold = int(price_match.group(1))
            price_cols = [col for col, info in self.columns_info.items() if info['type'] == 'price']
            
            if price_cols:
                price_col = price_cols[0]
                
                if 'yüksek' in q_lower or '>' in q_lower or 'üstü' in q_lower:
                    filtered_df = self.df[self.df[price_col] > price_threshold]
                else:
                    filtered_df = self.df[self.df[price_col] < price_threshold]
                
                return {
                    'data': filtered_df,
                    'insight': f"{len(filtered_df)} ürün bulundu",
                    'type': 'filter_price'
                }
        
        return {"error": "Filtre kriteri anlaşılamadı"}
    
    def _comparison_analysis(self, analysis: Dict, question: str) -> Dict:
        """Karşılaştırma analizi"""
        return {"message": "Karşılaştırma analizi geliştirilmekte..."}
    
    def _general_analysis(self, question: str) -> Dict:
        """Genel analiz"""
        return {
            'data': self.df.describe(),
            'insight': f"Genel istatistikler - {len(self.df)} kayıt",
            'type': 'general'
        }
    
    def _format_result(self, result: Dict, question: str) -> Dict:
        """Sonucu kullanıcı dostu formatta göster"""
        if 'error' in result:
            print(f"❌ {result['error']}")
            return result
        
        print(f"🤔 Soru: {question}")
        
        if 'insight' in result:
            print(f"💡 Sonuç: {result['insight']}")
        
        if 'data' in result:
            data = result['data']
            if isinstance(data, pd.DataFrame):
                print(f"\n📊 Detay:")
                print(data.head(10))
            elif isinstance(data, pd.Series):
                print(f"\n📊 Detay:")
                print(data.head(10))
            elif isinstance(data, dict):
                print(f"\n📊 Detay:")
                for key, value in data.items():
                    print(f"  {key}: {value}")
        
        print("-" * 50)
        return result

# Kullanım kolaylığı için kısa fonksiyon
def analyze(file_path: str):
    """
    Hızlı başlangıç
    
    Kullanım:
    from simplebi import analyze
    data = analyze('restaurant.xlsx')
    data.ask("En karlı kategoriler neler?")
    """
    return SimpleBI(file_path)

# Test
if __name__ == "__main__":
    print("🧪 SimpleBI Test")
    
    # Demo test
    data = SimpleBI()
    if data.df is not None:
        data.ask("En karlı kategoriler neler?")
        data.ask("Fotoğrafı olmayan ürünler kaç tane?")
        data.ask("Fiyatı 200'den yüksek ürünler?")
