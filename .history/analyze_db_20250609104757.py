import sqlite3
import json
from datetime import datetime

def analyze_database():
    conn = sqlite3.connect('aurawell.db')
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("数据库表结构分析：")
    print("=" * 50)
    
    for table in tables:
        table_name = table[0]
        print(f"\n表名: {table_name}")
        print("-" * 30)
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print("列信息：")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # 获取记录数
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        print(f"\n记录数: {count}")
        
        # 获取示例数据
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1;")
            sample = cursor.fetchone()
            print("\n示例数据：")
            for col, val in zip(columns, sample):
                print(f"  - {col[1]}: {val}")
    
    conn.close()

if __name__ == "__main__":
    analyze_database() 