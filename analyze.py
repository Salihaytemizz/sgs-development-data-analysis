#!/usr/bin/env python3
"""SGS - Tek söz ile analiz"""
import pandas as pd
import sqlite3
import sys

def analyze():
    """Tek komut - Tüm analiz"""
    print("🧠 SGS ANALİZİ")
    
    # Excel analizi
    try:
        df = pd.read_excel('image-table-cs.xlsx')
        print(f"📊 Excel: {len(df)} ürün")
        
        # Hızlı içgörüler
        for col in df.columns:
            if 'görüntülenme' in col.lower():
                top = df.loc[df[col].idxmax(), 'Ürün Adı']
                print(f"🏆 En popüler: {top}")
                break
    except:
        pass
    
    # SQL analizi  
    try:
        conn = sqlite3.connect('sales.db')
        result = conn.execute("SELECT COUNT(*) FROM tuzla_loglar").fetchone()
        print(f"💾 Veritabanı: {result[0]} kayıt")
        
        # En pahalı ürün
        result = conn.execute("SELECT \"Ürün Adı\", Fiyat FROM tuzla_loglar ORDER BY Fiyat DESC LIMIT 1").fetchone()
        print(f"💰 En pahalı: {result[0]} ({result[1]}₺)")
        
        conn.close()
    except:
        pass
    
    print("✅ Analiz tamam!")

if __name__ == "__main__":
    analyze()
