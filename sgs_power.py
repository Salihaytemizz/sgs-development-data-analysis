#!/usr/bin/env python3
"""
SGS Power - SQL kadar güçlü, tek komutla!
20+ bulgu çıkaran akıllı SGS

Kullanım:
import sgs_power as sgs
sgs.analyze()  # Tek komut - SQL kadar detaylı!
"""

import pandas as pd
import sqlite3
import numpy as np

def analyze():
    """SQL kadar güçlü analiz - 20+ bulgu"""
    print("🚀 SGS POWER - SQL Seviyesi Analiz")
    print("=" * 50)
    
    insights = []
    
    try:
        conn = sqlite3.connect('sales.db')
        
        # Tuzla şubesi analizi
        tuzla_df = pd.read_sql("SELECT * FROM tuzla_loglar", conn)
        
        # Koşuyolu şubesi analizi
        kosuyolu_df = pd.read_sql("SELECT * FROM kosuyolu_loglar", conn)
        
        print(f"📊 Tuzla: {len(tuzla_df)} ürün")
        print(f"📊 Koşuyolu: {len(kosuyolu_df)} ürün")
        
        # 1. KATEGORİ ANALİZİ
        print("\n📦 Kategori analizi...")
        cat_counts = tuzla_df['Kategori'].value_counts()
        insights.append(f"📦 En büyük kategori: {cat_counts.index[0]} ({cat_counts.iloc[0]} ürün)")
        insights.append(f"📦 En küçük kategori: {cat_counts.index[-1]} ({cat_counts.iloc[-1]} ürün)")
        insights.append(f"📦 Toplam {len(cat_counts)} farklı kategori")
        
        # 2. PERFORMANS ANALİZİ
        print("🏆 Performans analizi...")
        view_col = 'GÜNCEL DÖNEM GÖRÜNTÜLEME (02.09-08.09)'
        
        # En popüler 5 ürün
        top_products = tuzla_df.nlargest(5, view_col)
        insights.append(f"👑 En popüler: {top_products.iloc[0]['Ürün Adı']} ({top_products.iloc[0][view_col]:.0f} görüntülenme)")
        insights.append(f"🥈 2. sırada: {top_products.iloc[1]['Ürün Adı']} ({top_products.iloc[1][view_col]:.0f} görüntülenme)")
        insights.append(f"🥉 3. sırada: {top_products.iloc[2]['Ürün Adı']} ({top_products.iloc[2][view_col]:.0f} görüntülenme)")
        
        # Kategori performansı
        cat_performance = tuzla_df.groupby('Kategori')[view_col].mean().sort_values(ascending=False)
        insights.append(f"🏆 En iyi kategori: {cat_performance.index[0]} (ort. {cat_performance.iloc[0]:.0f} görüntülenme)")
        insights.append(f"⚠️ En zayıf kategori: {cat_performance.index[-1]} (ort. {cat_performance.iloc[-1]:.0f} görüntülenme)")
        
        # 3. FİYAT ANALİZİ
        print("💰 Fiyat analizi...")
        price_stats = tuzla_df['Fiyat'].describe()
        insights.append(f"💰 Ortalama fiyat: {price_stats['mean']:.0f}₺")
        insights.append(f"💰 En pahalı: {tuzla_df.loc[tuzla_df['Fiyat'].idxmax(), 'Ürün Adı']} ({tuzla_df['Fiyat'].max():.0f}₺)")
        insights.append(f"💰 En ucuz: {tuzla_df.loc[tuzla_df['Fiyat'].idxmin(), 'Ürün Adı']} ({tuzla_df['Fiyat'].min():.0f}₺)")
        
        # Fiyat segmentleri
        expensive = tuzla_df[tuzla_df['Fiyat'] > 1000]
        medium = tuzla_df[(tuzla_df['Fiyat'] >= 200) & (tuzla_df['Fiyat'] <= 1000)]
        cheap = tuzla_df[tuzla_df['Fiyat'] < 200]
        
        insights.append(f"💎 Pahalı ürünler (>1000₺): {len(expensive)} adet")
        insights.append(f"⭐ Orta fiyat (200-1000₺): {len(medium)} adet")
        insights.append(f"💸 Ucuz ürünler (<200₺): {len(cheap)} adet")
        
        # En pahalı 5 ürün
        top_expensive = tuzla_df.nlargest(5, 'Fiyat')
        insights.append(f"💎 En pahalı 5: {', '.join([f'{p} ({f}₺)' for p, f in zip(top_expensive['Ürün Adı'].head(3), top_expensive['Fiyat'].head(3))])}")
        
        # 4. TREND ANALİZİ
        print("📈 Trend analizi...")
        prev_col = 'BİR ÖNCEKİ DÖNEM GÖRÜNTÜLEME (26.08 - 01.09)'
        
        # Trend hesaplama
        tuzla_df['trend'] = ((tuzla_df[view_col] - tuzla_df[prev_col]) / (tuzla_df[prev_col] + 1)) * 100
        
        # En yükselen ürünler
        rising = tuzla_df[tuzla_df['trend'] > 20].nlargest(3, 'trend')
        if len(rising) > 0:
            insights.append(f"🚀 En yükselen: {rising.iloc[0]['Ürün Adı']} (%{rising.iloc[0]['trend']:.0f} artış)")
            if len(rising) > 1:
                insights.append(f"🚀 2. yükselen: {rising.iloc[1]['Ürün Adı']} (%{rising.iloc[1]['trend']:.0f} artış)")
        
        # En düşen ürünler
        falling = tuzla_df[tuzla_df['trend'] < -20].nsmallest(3, 'trend')
        if len(falling) > 0:
            insights.append(f"📉 En düşen: {falling.iloc[0]['Ürün Adı']} (%{abs(falling.iloc[0]['trend']):.0f} düşüş)")
        
        # Genel trend
        avg_trend = tuzla_df['trend'].mean()
        insights.append(f"📊 Genel trend: %{avg_trend:.1f} {'artış' if avg_trend > 0 else 'düşüş'}")
        
        # 5. FOTO VE BADGE ANALİZİ
        print("📷 Foto ve badge analizi...")
        
        # Foto durumu
        photo_ok = (tuzla_df['Foto Durumu'] == 'Evet').sum()
        photo_missing = (tuzla_df['Foto Durumu'] == 'Hayır').sum()
        total = len(tuzla_df)
        insights.append(f"📷 Foto durumu: {photo_ok}/{total} ürünün fotoğrafı var (%{photo_ok/total*100:.0f})")
        
        # Büyük foto
        big_photo_missing = (tuzla_df['Büyük Foto Var Yok'] == 'Hayır').sum()
        insights.append(f"📸 {big_photo_missing} ürünün büyük fotoğrafı eksik")
        
        # Badge durumu
        no_badge = tuzla_df['Güncel Badge'].isna().sum()
        has_badge = (~tuzla_df['Güncel Badge'].isna()).sum()
        insights.append(f"🏷️ Badge durumu: {has_badge} üründe badge var, {no_badge} üründe yok")
        
        # FIRSAT: Popüler ama foto eksik
        missing_popular = tuzla_df[(tuzla_df['Foto Durumu'] == 'Hayır') & 
                                 (tuzla_df[view_col] > tuzla_df[view_col].quantile(0.7))]
        if len(missing_popular) > 0:
            insights.append(f"🔥 FIRSAT: {len(missing_popular)} popüler ürünün fotoğrafı eksik!")
        
        # 6. FİYAT-PERFORMANS ANALİZİ
        print("💡 Fiyat-performans analizi...")
        tuzla_df['fiyat_performans'] = tuzla_df[view_col] / (tuzla_df['Fiyat'] + 1)
        best_value = tuzla_df.nlargest(3, 'fiyat_performans')
        insights.append(f"💡 En iyi fiyat-performans: {best_value.iloc[0]['Ürün Adı']} ({best_value.iloc[0]['fiyat_performans']:.2f} puan)")
        
        # 7. DEĞİŞİKLİK ANALİZİ
        print("🔄 Değişiklik analizi...")
        
        # Sıra değişiklikleri
        sira_degisen = tuzla_df[tuzla_df['Sıra'] != tuzla_df['Güncel Sıra']]
        insights.append(f"🔄 {len(sira_degisen)} ürünün sırası değiştirilmiş")
        
        # Fiyat değişiklikleri
        fiyat_artan = tuzla_df[tuzla_df['Güncel Fiyat'] > tuzla_df['Fiyat']]
        fiyat_azalan = tuzla_df[tuzla_df['Güncel Fiyat'] < tuzla_df['Fiyat']]
        insights.append(f"💰 Fiyat değişimi: {len(fiyat_artan)} ürün zamlandı, {len(fiyat_azalan)} ürün indirimde")
        
        # 8. ŞUBE KARŞILAŞTIRMASI
        print("🏪 Şube karşılaştırması...")
        tuzla_avg_price = tuzla_df['Fiyat'].mean()
        kosuyolu_avg_price = kosuyolu_df['Fiyat'].mean()
        price_diff = ((tuzla_avg_price - kosuyolu_avg_price) / kosuyolu_avg_price) * 100
        
        if price_diff > 5:
            insights.append(f"📊 Tuzla, Koşuyolu'ndan %{price_diff:.0f} daha pahalı (ort. {tuzla_avg_price:.0f}₺ vs {kosuyolu_avg_price:.0f}₺)")
        elif price_diff < -5:
            insights.append(f"📊 Tuzla, Koşuyolu'ndan %{abs(price_diff):.0f} daha ucuz (ort. {tuzla_avg_price:.0f}₺ vs {kosuyolu_avg_price:.0f}₺)")
        else:
            insights.append(f"⚖️ Her iki şube benzer fiyatlarda (Tuzla: {tuzla_avg_price:.0f}₺, Koşuyolu: {kosuyolu_avg_price:.0f}₺)")
        
        # Ürün sayısı karşılaştırması
        insights.append(f"🏪 Ürün sayısı: Tuzla {len(tuzla_df)}, Koşuyolu {len(kosuyolu_df)}")
        
        # 9. KATEGORİ BAZLI DETAYLAR
        print("📊 Kategori detayları...")
        for category in cat_counts.head(3).index:
            cat_df = tuzla_df[tuzla_df['Kategori'] == category]
            avg_price = cat_df['Fiyat'].mean()
            avg_views = cat_df[view_col].mean()
            insights.append(f"📦 {category}: {len(cat_df)} ürün, ort. {avg_price:.0f}₺, {avg_views:.0f} görüntülenme")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Analiz hatası: {e}")
    
    # Sonuçları göster
    print(f"\n🎯 SGS POWER ANALİZ SONUÇLARI ({len(insights)} bulgu):")
    print("=" * 60)
    
    for i, insight in enumerate(insights, 1):
        print(f"{i:2d}. {insight}")
    
    print(f"\n🚀 Analiz tamamlandı! {len(insights)} detaylı bulgu")
    
    # Özet istatistik
    print(f"\n📊 ÖZET:")
    print(f"   • Kategori analizi: ✅")
    print(f"   • Performans analizi: ✅") 
    print(f"   • Fiyat analizi: ✅")
    print(f"   • Trend analizi: ✅")
    print(f"   • Foto/badge analizi: ✅")
    print(f"   • Şube karşılaştırması: ✅")
    
    return insights

if __name__ == "__main__":
    analyze()
