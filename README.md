本專案是一個整合爬蟲與後端 API 的應用程式，
用於從中華職棒(https://www.cpbl.com.tw/)爬取最新棒球比賽數據，並儲存至 PostgreSQL 資料庫，通過 FastAPI 提供前端應用所需的 RESTful API。



已布署到 render (https://cpbl-crawler-1.onrender.com/docs)
若要程式開發才需要安裝。

## Installation

```base
git clone https://github.com/Sean12344321/CPBL-crawler.git
cd app/api
```

執行下面指令

```bash
 pip install -r requirements.txt
 uvicorn main:app --reload
```

執行以後去 localhost:8000 即可使用 api
