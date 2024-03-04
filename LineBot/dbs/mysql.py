import pymysql
import json
# import time
# from dbutils.pooled_db import PooledDB


with open('./config/config.json', 'r') as file:
    config = json.load(file)
    
class Sql():
    def connectSql(self):
        conn = pymysql.connect(
            host = config["SQLhost"],
            user = config["SQLuser"],
            password = config["SQLpassword"],
            database = config["SQLdatabase"],
            port = config["SQLport"] # MySQL 服務器的端口號，默認是 3306
        )
        print('SQL Succesful connect!')
        return conn

    #重新連線
    def  sqlConnError(self, conn) :
        while not conn.open :
            print('Attempting to reconnect...')
            try:
                conn = self.connectSql()
                if conn.open:
                    return conn
            except ConnectionError as e:
                print(f"ConnectionError: {e}")
        return conn

    def sqlData(self, conn, table="products", PRODNAME=None, CMNO=None, BARCODE=None, limit=None, searchAll=False):
        """(prodname, searchAll = False, table="products") -> List[dict]"""
        conn = self.sqlConnError(conn)
        cursor = conn.cursor()
        try:
            # 更改隔離級別，可以使用到新加入的資料
            conn.begin()
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
            # 查詢數據
            # 參數化查詢 %s 要傳入List/Tuple
            if searchAll: # 查整表
                select_query = f'SELECT * FROM {table}'
                cursor.execute(select_query)
            elif CMNO: # 查編號
                if limit: # 查前幾筆
                    select_query = f'SELECT * FROM {table} WHERE CMNO = %s LIMIT %s, %s'
                    cursor.execute(select_query, (CMNO, limit[0], limit[0]+limit[1]))
                else:
                    select_query = f'SELECT * FROM {table} WHERE CMNO = %s'
                    cursor.execute(select_query, (CMNO, ))
            elif PRODNAME: # 查產品名稱
                name = '%'
                for text in PRODNAME:
                    name = name + text + '%'
                if limit:
                    select_query = f'SELECT * FROM {table} WHERE prodname LIKE %s LIMIT %s, %s'
                    cursor.execute(select_query, (name, limit[0], limit[0]+limit[1]))
                else:
                    select_query = f'SELECT * FROM {table} WHERE prodname LIKE %s'
                    cursor.execute(select_query, (name, ))
            elif BARCODE: # 查BARCODE
                if limit:
                    select_query = f'SELECT * FROM {table} WHERE barcode = %s LIMIT %s, %s'
                    cursor.execute(select_query, (BARCODE, limit[0], limit[0]+limit[1]))
                else:
                    select_query = f'SELECT * FROM {table} WHERE barcode = %s'
                    cursor.execute(select_query, (BARCODE, ))

            # 獲取查詢結果
            result = cursor.fetchall()
            # print(result)
            prodList = []
            for i in range(len(result)):
                prod = {
                    # 資料庫資料不為 None 時，將資訊轉為 string。
                    'CMNO': str(result[i][0]), 
                    'PRODNAME': str(result[i][1]),
                    'LEVEL': str(result[i][2]) if result[i][2] else None,
                    'G_ML_NUM': str(result[i][3]) if result[i][3] else None,
                    'G_ML': str(result[i][4]) if result[i][4] else None,
                    'UNIT': str(result[i][5]) if result[i][5] else None,
                    'HEAT': str(result[i][6]) if result[i][6] else None,
                    'PROTEIN': str(result[i][7]) if result[i][7] else None,
                    'TOTALFAT': str(result[i][8]) if result[i][8] else None,
                    'SATFAT': str(result[i][9]) if result[i][9] else None,
                    'TRANSFAT': str(result[i][10]) if result[i][10] else None,
                    'CARBOHYDRATE': str(result[i][11]) if result[i][11] else None,
                    'SUGAR': str(result[i][12]) if result[i][12] else None,
                    'SODIUM': str(result[i][13]) if result[i][13] else None,
                    'BARCODE': str(result[i][14]) if result[i][14] else None,
                    'URL': str(result[i][15]) if result[i][15] else None, # 無資料(None)時，保持原狀，儲存為 None
                    'NAME': str(result[i][16]) if result[i][16] else None
                }
                prodList.append(prod)
            conn.commit()
            return prodList
        except Exception as e:
            # 事務回滾
            conn.rollback()
            print(f"SQL Search Error: {e}")
    def updateBarcode(self, conn, table="products", CMNO=None, barcodeValue=None, personNAME=None):
        """更新Barcode資料"""
        conn = self.sqlConnError(conn)
        cursor = conn.cursor()
        try:
            # 更改隔離級別，可以使用到新加入的資料
            conn.begin()
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
            update_query = f"UPDATE {table} SET barcode = %s, name = %s WHERE CMNO = %s"
            cursor.execute(update_query, (barcodeValue, personNAME, CMNO))   
            conn.commit() # 寫入

            # 檢查是否插入
            select_query = f'SELECT * FROM {table} WHERE barcode = %s'
            cursor.execute(select_query, (barcodeValue, ))
            result = cursor.fetchall()
        
            # if len(result) > 0:
            #     print ("Barcode inserted successfully.")
        except Exception as e:
            # 事務回滾
            conn.rollback()
            print(f"SQL updateBarcode Error: {e}")
    def insertProduct(self, conn, data, table="products"):
        conn = self.sqlConnError(conn)
        cursor = conn.cursor()
        try:
            # 更改隔離級別
            conn.begin()
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
            # 定義加入的資料
            PRODNAME, G_ML_NUM, UNIT, HEAT, PROTEIN, TOTALFAT, SATFAT, TRANSFAT, CARBOHYDRATE, SUGAR, SODIUM, G_ML, BARCODE, CMNO, LEVEL = data
            G_ML_NUM = round(float(G_ML_NUM), 1)
            UNIT = round(float(UNIT), 1)
            HEAT = round(float(HEAT), 1)
            PROTEIN = round(float(PROTEIN), 1)
            TOTALFAT = round(float(TOTALFAT), 1)
            SATFAT = round(float(SATFAT), 1)
            TRANSFAT = round(float(TRANSFAT), 1)
            CARBOHYDRATE = round(float(CARBOHYDRATE), 1)
            SUGAR = round(float(SUGAR), 1)
            SODIUM = round(float(SODIUM), 1)
            # 加入資料
            insert_query = f'INSERT INTO {table} (CMNO, PRODNAME, G_ML, G_ML_NUM, UNIT, HEAT, PROTEIN, TOTALFAT, SATFAT, TRANSFAT, CARBOHYDRATE, SUGAR, SODIUM, BARCODE, LEVEL) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
            cursor.execute(insert_query, (CMNO, PRODNAME, G_ML, G_ML_NUM, UNIT, HEAT, PROTEIN, TOTALFAT, SATFAT, TRANSFAT, CARBOHYDRATE, SUGAR, SODIUM, BARCODE, LEVEL))
            # 提交對數據庫的更改
            conn.commit()
        except Exception as e:
            print(f"SQL Insert data Error: {e}")
        finally:
            # # 關閉游標和連接
            cursor.close()
            conn.close()

    def searchNullBarcode(self, conn, table="products"):
        """查詢Barcode為空的資料"""
        conn = self.sqlConnError(conn)
        cursor = conn.cursor()
        try:
            # 更改隔離級別，可以使用到新加入的資料
            conn.begin()
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
            select_query = f'SELECT * FROM {table} WHERE barcode IS NULL'
            cursor.execute(select_query)
            result = cursor.fetchall()

            prodList = []
            for i in range(len(result)):
                prod = {
                    # 資料庫資料不為 None 時，將資訊轉為 string。
                    'PRODNAME': str(result[i][1])
                }
                prodList.append(prod)
            # 提交對數據庫的更改
            conn.commit()
            return prodList
        except Exception as e:
            print(f"SQL searchNullBarcode Error: {e}")
    def searchNums(self, conn, table="products"):
        """查詢Barcode為空的資料"""
        conn = self.sqlConnError(conn)
        cursor = conn.cursor()
        try:
            # 更改隔離級別，可以使用到新加入的資料
            conn.begin()
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
            select_query = f'SELECT name, COUNT(barcode) FROM {table} GROUP BY name'
            cursor.execute(select_query)
            result = cursor.fetchall()
            text = ""
            for res in result:
                text += f"{res[0]}: {res[1]}\n"
            # 提交對數據庫的更改
            conn.commit()
            return str(text)
        except Exception as e:
            print(f"SQL searchNums Error: {e}")
        
if __name__ == "__main__":
    sqlConn = Sql()
    conn = sqlConn.connectSql()
    # prods = sqlConn.sqlData(conn, PRODNAME="CACAO", table='products')
    # prods = sqlConn.sqlData(conn, BARCODE="2012202120248", table='products')

    # if len(prods) == 0:
    #     print('x')
    # print(prods)

    data = ['1', '1', '2', '154.7', '3', '1.5', '0.8', '0', '28.5', '23.6', '3', '毫升', '4710063337802', 'C481055'] 
    sqlConn.insertProduct(conn, data)