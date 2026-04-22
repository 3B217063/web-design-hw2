# 簡易會員系統

1132 Web 程式設計 - 第 2 次作業

## 功能

- 首頁（/）：系統介紹與導覽連結
- 會員註冊（/register）：表單驗證並將資料儲存至 users.json
- 會員登入（/login）：比對 JSON 記錄驗證身分
- 歡迎頁面（/welcome/\<username\>）：顯示已登入會員資料
- 會員清單（/users）：列出所有會員（不含密碼）
- 錯誤頁面（/error）：顯示錯誤訊息

## 安裝與執行

```bash
pip install -r requirements.txt
flask --debug run
```

預設管理員帳號：`admin@example.com` / 密碼：`admin123`

## 技術

- Python Flask
- Pico CSS v2（深色主題）
- JSON 檔案儲存（users.json）
