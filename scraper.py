import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime
import time
import random

class DantriScraper:
    def __init__(self):
        self.base_url = "https://dantri.com.vn"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://dantri.com.vn/'
        }
        self.data = []
        self.session = requests.Session()
        self.max_articles = 5  # Chỉ thu thập tối đa 5 bài viết
        
    def get_soup(self, url):
        try:
            print(f"Đang truy cập URL: {url}")
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            if "access-denied" in response.url:
                raise Exception("Bị chặn truy cập bởi website")
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Lỗi khi truy cập URL {url}: {str(e)}")
            return None

    def extract_article_data(self, article_url):
        print(f"Đang xử lý bài viết: {article_url}")
        soup = self.get_soup(article_url)
        if not soup:
            return None
        try:
            title = soup.find('h1', class_='title-page').get_text(strip=True) if soup.find('h1', class_='title-page') else ''
            excerpt = soup.find('h2', class_='singular-excerpt').get_text(strip=True) if soup.find('h2', class_='singular-excerpt') else ''
            image_tag = soup.find('div', class_='singular-content').find('img') if soup.find('div', class_='singular-content') else None
            image_url = image_tag['src'] if image_tag else ''
            content_div = soup.find('div', class_='singular-content')
            if content_div:
                for element in content_div(['script', 'style', 'div', 'a']):
                    element.decompose()
                content = ' '.join(content_div.stripped_strings)
            else:
                content = ''
            print(f"Đã thu thập bài viết: {title[:50]}...")
            return {
                'title': title,
                'excerpt': excerpt,
                'image_url': image_url,
                'content': content,
                'article_url': article_url,
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"Lỗi khi trích xuất bài viết: {str(e)}")
            return None

    def scrape_page(self, page_num=1):
        url = f"{self.base_url}/trang-{page_num}.htm" if page_num > 1 else self.base_url
        print(f"\nBắt đầu thu thập trang {page_num}: {url}")
        soup = self.get_soup(url)
        if not soup:
            print(f"Không thể lấy nội dung trang {page_num}")
            return False
        articles = soup.find_all('article', class_='article-item')
        if not articles:
            print(f"Không tìm thấy bài viết nào ở trang {page_num}")
            return False
        print(f"Tìm thấy {len(articles)} bài viết trên trang {page_num}")
        for i, article in enumerate(articles, 1):
            if len(self.data) >= self.max_articles:
                print("Đã thu thập đủ số lượng bài viết yêu cầu.")
                return False
            try:
                link = article.find('a', href=True)
                if link and '/chu-de/' not in link['href']:
                    article_url = self.base_url + link['href'] if not link['href'].startswith('http') else link['href']
                    print(f"\n[{len(self.data)+1}/{self.max_articles}] Đang xử lý: {article_url}")
                    article_data = self.extract_article_data(article_url)
                    if article_data:
                        self.data.append(article_data)
                    delay = random.uniform(1, 3)
                    print(f"Đợi {delay:.1f} giây trước khi tiếp tục...")
                    time.sleep(delay)
            except Exception as e:
                print(f"Lỗi khi xử lý bài viết {i}: {str(e)}")
                continue
        return True

    def scrape_first_5_pages(self):
        for page_num in range(1, 6):
            print(f"\n{'='*50}")
            print(f"Đang thu thập trang {page_num}/5")
            print(f"{'='*50}")
            if len(self.data) >= self.max_articles:
                print("Đã đủ 5 bài viết, dừng lại.")
                break
            success = self.scrape_page(page_num)
            if not success:
                break

    def save_to_csv(self, filename='dantri_news.csv'):
        if not self.data:
            print("Không có dữ liệu để lưu")
            return
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)
        df = pd.DataFrame(self.data)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"\nĐã lưu {len(df)} bài viết vào {filepath}")

if __name__ == "__main__":
    print("Bắt đầu thu thập dữ liệu từ Dantri.com.vn (chỉ 5 bài viết đầu tiên)")
    scraper = DantriScraper()
    try:
        scraper.scrape_first_5_pages()
        scraper.save_to_csv()
    except KeyboardInterrupt:
        print("\nDừng chương trình do người dùng yêu cầu")
        if scraper.data:
            scraper.save_to_csv('dantri_news_partial.csv')
    except Exception as e:
        print(f"\nLỗi không mong muốn: {str(e)}")
        if scraper.data:
            scraper.save_to_csv('dantri_news_partial.csv')
    print("Kết thúc chương trình")
