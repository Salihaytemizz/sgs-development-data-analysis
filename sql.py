#!/usr/bin/env python3
"""
SGS SQL - Kısa ve öz
Kullanım: python sql.py dosya.xlsx "SELECT * FROM data"
"""

import sys
import pandas as pd
import duckdb

def query(file_path, sql):
    # Veriyi yükle
    df = pd.read_excel(file_path)
    print(f"📊 {len(df)} satır yüklendi")
    
    # SQL çalıştır
    conn = duckdb.connect()
    conn.register('data', df)
    result = conn.execute(sql).fetchdf()
    
    print(f"✅ {len(result)} sonuç:")
    print(result.head(10))
    return result

if __name__ == "__main__":
    if len(sys.argv) == 3:
        query(sys.argv[1], sys.argv[2])
    else:
        print("Kullanım: python sql.py dosya.xlsx \"SELECT * FROM data\"")
