如果需要資料庫測試，這邊有全家所有商品資訊資料庫可供搬遷，步驟如下:
1. 將backup.sql檔案下載
2. 到C:\Program Files\MySQL\MySQL Server 8.0\bin資料夾輸入CMD
3. 輸入指令：mysql -u [使用者名稱] -p [資料庫名稱] < backup.sql的完整路徑
   Ex. mysql -u root -p project_test2 < "C:\Users\T14 Gen 3\Desktop\AI課程\Project\database\MySQL\backup6.sql"