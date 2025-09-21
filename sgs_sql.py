#!/usr/bin/env python3
"""
SGS SQL - Smart Growth Solutions
Excel dosyalarını SQL ile sorgula

Kullanım:
python sgs_sql.py dosya.xlsx "SELECT * FROM data WHERE fiyat > 200"
"""

import sys
import pandas as pd
import duckdb

def sql_query(file_path, query):
    """Excel dosyasını SQL ile sorgula"""
    print("🐥 SGS SQL Motoru")
    print("=" * 30)
    
    try:
        # Excel dosyasını yükle
        print(f"📄 Dosya yükleniyor: {file_path}")
        df = pd.read_excel(file_path)
        print(f"📊 {len(df)} satır, {len(df.columns)} sütun yüklendi")
        
        # DuckDB bağlantısı oluştur
        conn = duckdb.connect()
        
        # DataFrame'i DuckDB'ye kaydet
        conn.register('data', df)
        
        print(f"\n💾 Tablo 'data' olarak kaydedildi")
        print(f"🔍 SQL Sorgusu: {query}")
        print("-" * 40)
        
        # SQL sorgusunu çalıştır
        result = conn.execute(query).fetchdf()
        
        # Sonucu göster
        if len(result) > 0:
            print(f"✅ {len(result)} sonuç bulundu:")
            print(result.to_string(index=False))
        else:
            print("❌ Sonuç bulunamadı")
            
        return result
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None

def show_schema(file_path):
    """Dosya şemasını göster"""
    try:
        df = pd.read_excel(file_path)
        print("📋 Tablo Şeması:")
        print("-" * 30)
        for i, col in enumerate(df.columns, 1):
            dtype = str(df[col].dtype)
            sample = str(df[col].iloc[0]) if len(df) > 0 else "N/A"
            print(f"{i:2d}. {col:<20} ({dtype}) → {sample}")
        
        print(f"\n💡 Örnek SQL sorguları:")
        print(f"SELECT * FROM data LIMIT 5")
        print(f"SELECT * FROM data WHERE \"{df.columns[0]}\" LIKE '%Pizza%'")
        if any('fiyat' in col.lower() for col in df.columns):
            price_col = next(col for col in df.columns if 'fiyat' in col.lower())
            print(f"SELECT * FROM data WHERE \"{price_col}\" > 200")
        
    except Exception as e:
        print(f"❌ Şema gösterme hatası: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım:")
        print("  python sgs_sql.py dosya.xlsx \"SQL_SORGUSU\"")
        print("  python sgs_sql.py dosya.xlsx --schema  (şemayı göster)")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if len(sys.argv) == 2 or (len(sys.argv) == 3 and sys.argv[2] == "--schema"):
        # Şema göster
        show_schema(file_path)
    else:
        # SQL sorgusu çalıştır
        query = sys.argv[2]
        sql_query(file_path, query)
