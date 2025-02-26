from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

def setup_driver():
    """Thiết lập và khởi tạo trình duyệt Chrome."""
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--headless")  # Chạy ở chế độ nền
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def get_tiktok_user_info(username):
    """Lấy thông tin người dùng từ trang TikTok."""
    driver = setup_driver()
    url = f"https://www.tiktok.com/@{username}"
    driver.get(url)
    time.sleep(5)  # Đợi trang tải

    try:
        user_page_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-e2e="user-page"]'))
        )
        
        for element in user_page_elements:
            if "Couldn't find this account" in element.text:
                driver.quit()
                return {"status": "error", "message": "Không tìm thấy tài khoản này."}

        user_info = [element.text for element in user_page_elements]
        driver.quit()
        return {"status": "success", "data": user_info}
    
    except Exception as e:
        driver.quit()
        return {"status": "error", "message": str(e)}

@app.route("/get_user_info", methods=["GET"])
def get_user_info():
    username = request.args.get("username")
    if not username:
        return jsonify({"status": "error", "message": "Thiếu username."}), 400
    
    result = get_tiktok_user_info(username)
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)