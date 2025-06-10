import sqlite3
import os
from datetime import datetime

def analyze_database():
    db_path = 'aurawell.db'
    
    # 检查数据库文件
    print("数据库文件信息：")
    print("=" * 50)
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"数据库文件大小: {size} 字节")
        print(f"最后修改时间: {datetime.fromtimestamp(os.path.getmtime(db_path))}")
    else:
        print("错误：数据库文件不存在！")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查数据库版本
        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()
        print(f"\nSQLite 版本: {version[0]}")
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("\n警告：数据库中没有表！")
            return
            
        print("\n数据库表结构分析：")
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
                col_id, name, type_, notnull, default_value, pk = col
                print(f"  - {name} ({type_})")
                if pk:
                    print("    * 主键")
                if notnull:
                    print("    * 非空")
                if default_value:
                    print(f"    * 默认值: {default_value}")
            
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
                
                # 获取索引信息
                cursor.execute(f"PRAGMA index_list({table_name});")
                indexes = cursor.fetchall()
                if indexes:
                    print("\n索引信息：")
                    for idx in indexes:
                        idx_name = idx[1]
                        print(f"  - 索引名: {idx_name}")
                        cursor.execute(f"PRAGMA index_info({idx_name});")
                        idx_columns = cursor.fetchall()
                        for idx_col in idx_columns:
                            col_id = idx_col[1]
                            col_name = columns[col_id][1]
                            print(f"    * 列: {col_name}")
        
        # 检查外键约束
        cursor.execute("PRAGMA foreign_key_list;")
        foreign_keys = cursor.fetchall()
        if foreign_keys:
            print("\n外键约束：")
            for fk in foreign_keys:
                print(f"  - 从 {fk[2]} 到 {fk[3]}")
        
    except sqlite3.Error as e:
        print(f"\n数据库错误: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    analyze_database() 