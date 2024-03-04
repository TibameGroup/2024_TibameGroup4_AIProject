# -*- coding: utf-8 -*-
"""
Created on Tue Dec 26 20:58:43 2023

@author: T14 Gen 3
"""
import sqlalchemy 
from sqlalchemy import create_engine,Integer,MetaData,Table,Column,insert,update,delete
from sqlalchemy import Integer ,VARCHAR ,DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker,Mapped,mapped_column
from typing_extensions import Annotated
#設定引擎,初始化資料庫連接，使用pymysql模組
#http://172.22.0.1:3306/
engine1=create_engine("mysql+pymysql://root:propro124579@127.0.0.1:3306/demo1",echo=True)
engine2=create_engine("mysql+pymysql://root:propro124579@127.0.0.1:3306/testdb",echo=True)


#容器對象，將描述的資料庫（或多個資料庫）的許多不同功能放在一起

#創建sqlTable 

Base1=declarative_base()
Base2=declarative_base()

decimal_default=Annotated[float,mapped_column(DECIMAL(5,1),default=0,nullable=True)]
class Official(Base1) :
    __tablename__="products"
    id :Mapped[int] =mapped_column(primary_key=True,autoincrement=True)
    level:Mapped[str]=mapped_column(VARCHAR(20),nullable=True)
    PRODNAME:Mapped[str]=mapped_column(VARCHAR(20),unique=True)
    G_ML:Mapped[decimal_default]
    UNIT:Mapped[decimal_default]
    HEAT:Mapped[decimal_default]
    PROTEIN:Mapped[decimal_default]
    TOTALFAT:Mapped[decimal_default]
    SATFAT:Mapped[decimal_default]
    TRANSFAT:Mapped[decimal_default]
    CARBOHYDRATE:Mapped[decimal_default]
    SUGAR:Mapped[decimal_default]
    SODIUM:Mapped[decimal_default]
    barcode:Mapped[int]=mapped_column(Integer,unique=True,nullable=True)
    
class Client(Base2) :
    __tablename__="products"
    id :Mapped[int] =mapped_column(primary_key=True,autoincrement=True)
    level:Mapped[str]=mapped_column(VARCHAR(20),nullable=True)
    PRODNAME:Mapped[str]=mapped_column(VARCHAR(20),unique=True)
    G_ML:Mapped[decimal_default]
    UNIT:Mapped[decimal_default]
    HEAT:Mapped[decimal_default]
    PROTEIN:Mapped[decimal_default]
    TOTALFAT:Mapped[decimal_default]
    SATFAT:Mapped[decimal_default]
    TRANSFAT:Mapped[decimal_default]
    CARBOHYDRATE:Mapped[decimal_default]
    SUGAR:Mapped[decimal_default]
    SODIUM:Mapped[decimal_default]
    barcode:Mapped[int]=mapped_column(Integer,unique=True,nullable=True)
    
Base1.metadata.create_all(engine1)
Base2.metadata.create_all(engine2)
Session=sessionmaker(bind=engine1)
session=Session()
Session2=sessionmaker(bind=engine2)
session2=Session2()

#official 增加數據
def officialInsert(datas) :
    #批量增加
    with session as se :
        se.execute(
            insert(Official).values(
                datas
                )
            )
        se.commit()
        
#Client 端增加數據
def ClientInsert(datas) :
     #批量增加
     with session2 as se2 :
         se2.execute(
             insert(Client).values(
                 datas
                 )
             )
         se2.commit()       

#select 兩個數據庫
def selectALL(barcode) :
    with session as se1,se1.begin() ,session2 as se2,se2.begin() :
        official=se1.query(Official).filter(Official.barcode==9).first()
        if official==None :
            client=se2.query(Client).filter(Client.barcode==9).first()
            return client
            if client==None :
               return None
        return official

#official 更新    
def officialupdate(datas) :
    #批量更新
   # datas =[{"id":1,"HEAT":7.0},{"id":2,"HEAT":8.0}]
    with session as se :
        se.execute(update(Official),datas)
        se.commit()
    

def clientupdate(datas) :
    #批量更新
   # datas =[{"id":1,"HEAT":7.0},{"id":2,"HEAT":8.0}]
    with session2 as se2 :
        se2.execute(update(Client),datas)
        se2.commit()
    
def officialdelete() :
#批量刪除
    with session as se :
        se.execute(
        delete(Official).where(Official.PRODNAME.in_(["5","3"]))
        )
        session.commit()


# selectALL()
#officialInsert(datas)


# # with open("dict.txt","r",encoding="utf-8") as f:
# #     data=f.read()
# #     print(data)
# #     data_list=[]
# #     data_list.append(data)
    
# data_list=[{"PRODNAME":"1","barcode":2},{"PRODNAME":"2","barcode":2},{"PRODNAME":"3","barcode":1}]
# insertClientTable(data_list) 

# select(2)
if __name__ ==' __main__' :
    print("ok")
