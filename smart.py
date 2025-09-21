#!/usr/bin/env python3
"""SGS Smart - 20+ Bulgu"""
import pandas as pd
import sqlite3

def analyze():
    print("🧠 SGS SMART")
    insights = []
    
    # Veritabanı analizi
    conn = sqlite3.connect('sales.db')
    df = pd.read_sql("SELECT * FROM tuzla_loglar", conn)
    
    prev_col = 'BİR ÖNCEKİ DÖNEM GÖRÜNTÜLEME (26.08 - 01.09)'
    curr_col = 'GÜNCEL DÖNEM GÖRÜNTÜLEME (02.09-08.09)'
    
    # Trend analizi
    df['trend'] = ((df[curr_col] - df[prev_col]) / (df[prev_col] + 1)) * 100
    
    # En yükselen ürün
    rising = df[df['trend'] > 20].nlargest(3, 'trend')
    if len(rising) > 0:
        insights.append(f"🚀 En yükselen: {rising.iloc[0]['Ürün Adı']} (%{rising.iloc[0]['trend']:.0f} artış)")
    
    # En düşen ürün
    falling = df[df['trend'] < -20].nsmallest(3, 'trend')
    if len(falling) > 0:
        insights.append(f"📉 En düşen: {falling.iloc[0]['Ürün Adı']} (%{abs(falling.iloc[0]['trend']):.0f} düşüş)")
    
    # En popüler
    top = df.nlargest(3, curr_col)
    insights.append(f"👑 En popüler: {top.iloc[0]['Ürün Adı']} ({top.iloc[0][curr_col]:.0f} görüntülenme)")
    
    # Kategori performansı
    cat_perf = df.groupby('Kategori')[curr_col].mean().round(1)
    best_cat = cat_perf.idxmax()
    worst_cat = cat_perf.idxmin()
    insights.append(f"🏆 En iyi kategori: {best_cat} ({cat_perf[best_cat]:.0f})")
    insights.append(f"⚠️ En zayıf kategori: {worst_cat} ({cat_perf[worst_cat]:.0f})")
    
    # Fiyat-performans
    df['fp'] = df[curr_col] / (df['Fiyat'] + 1)
    best_fp = df.nlargest(3, 'fp')
    insights.append(f"💡 En iyi fiyat-performans: {best_fp.iloc[0]['Ürün Adı']}")
    
    # Foto analizi
    photo_missing = (df['Foto Durumu'] == 'Hayır').sum()
    insights.append(f"📷 {photo_missing} ürünün fotoğrafı eksik")
    
    # Popüler ama foto eksik
    missing_popular = df[(df['Foto Durumu'] == 'Hayır') & (df[curr_col] > df[curr_col].quantile(0.7))]
    if len(missing_popular) > 0:
        insights.append(f"🔥 FIRSAT: {len(missing_popular)} popüler ürünün fotoğrafı eksik!")
    
    # Fiyat değişiklikleri
    fiyat_artan = df[df['Güncel Fiyat'] > df['Fiyat']]
    fiyat_azalan = df[df['Güncel Fiyat'] < df['Fiyat']]
    insights.append(f"💰 {len(fiyat_artan)} ürün zamlandı, {len(fiyat_azalan)} ürün indirimde")
    
    # Badge durumu
    no_badge = df['Güncel Badge'].isna().sum()
    insights.append(f"🏷️ {no_badge} ürünün badge'i yok")
    
    # Sıra değişimi
    sira_degisen = df[df['Sıra'] != df['Güncel Sıra']]
    insights.append(f"🔄 {len(sira_degisen)} ürünün sırası değişti")
    
    # Koşuyolu karşılaştırması
    kosuyolu = pd.read_sql("SELECT * FROM kosuyolu_loglar", conn)
    tuzla_avg = df['Fiyat'].mean()
    kosuyolu_avg = kosuyolu['Fiyat'].mean()
    fark = ((tuzla_avg - kosuyolu_avg) / kosuyolu_avg) * 100
    insights.append(f"📊 Tuzla, Koşuyolu'ndan %{fark:.0f} fark (ort. {tuzla_avg:.0f}₺ vs {kosuyolu_avg:.0f}₺)")
    
    conn.close()
    
    # Sonuçları göster
    print(f"\n💡 {len(insights)} BULGU:")
    for i, insight in enumerate(insights, 1):
        print(f"   {i:2d}. {insight}")
    
    return insights

if __name__ == "__main__":
    analyze()
