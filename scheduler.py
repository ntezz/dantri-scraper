import schedule
import time
from scraper import DantriScraper
import datetime

def daily_scraping_job():
    now = datetime.datetime.now()
    print(f"Bắt đầu thu thập dữ liệu vào lúc {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    scraper = DantriScraper()
    scraper.scrape_all_pages(max_pages=5)
    scraper.save_to_csv(f"dantri_news_{now.strftime('%Y%m%d')}.csv")

    print(f"✅ Đã thực hiện xong thu thập lúc {now.strftime('%H:%M')}")

def run_scheduler():
    # Lên lịch chạy mỗi ngày lúc 6h sáng
    schedule.every().day.at("06:00").do(daily_scraping_job)
    
    print("🕒 Trình lập lịch đã khởi động. Đang chờ thực thi lúc 06:00 mỗi ngày...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Kiểm tra mỗi phút

if __name__ == "__main__":
    run_scheduler()
