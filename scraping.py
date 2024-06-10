import time
import json
import gzip
import requests
import multiprocessing
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class GrabFoodScraper:
    def __init__(self, url, location):
        self.url = url
        self.location = location
        self.driver = self.setup_driver()
        self.restaurant_data = []

    def setup_driver(self):
        chrome_options = webdriver.ChromeOptions()
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3112.50 Safari/537.36"
        chrome_options.add_argument(f'user-agent={user_agent}')
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def load_url(self):
        self.driver.get(self.url)

    def accept_cookies(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept")]'))
            ).click()
        except TimeoutException:
            pass

    def fill_location(self):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-layout")))
        location_input = self.driver.find_element(By.ID, 'location-input')
        location_input.click()
        time.sleep(2)
        location_input.clear()
        location_input.send_keys(self.location)
        submit_button = self.driver.find_element(By.CSS_SELECTOR, '.ant-btn.submitBtn___2roqB.ant-btn-primary')
        submit_button.click()
        WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-layout")))
        time.sleep(5)

    def extract_restaurant_data(self, max_restaurants=2):
        count = 0
        for _ in range(20):
            restaurant_elements = WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.RestaurantListCol___1FZ8V"))
            )
            last_restaurant_element = restaurant_elements[-1]
            self.driver.execute_script("arguments[0].scrollIntoView();", last_restaurant_element)
            time.sleep(5)
            if count >= max_restaurants:
                break

            for restaurant_element in restaurant_elements[count:]:
                if count >= max_restaurants:
                    break
                count += 1
                try:
                    restaurant_info = self.get_restaurant_info(restaurant_element)
                    if restaurant_info:
                        self.restaurant_data.append(restaurant_info)
                except NoSuchElementException:
                    continue

    def get_restaurant_info(self, restaurant_element):
        restaurant_cuisine = restaurant_element.find_element(By.CSS_SELECTOR, "div.basicInfoRow___UZM8d").text
        restaurant_name = restaurant_element.find_element(By.CSS_SELECTOR, "p.name___2epcT").text
        rating = restaurant_element.find_element(By.CSS_SELECTOR, "div.numbersChild___2qKMV:nth-child(1)").text
        duration_distance = restaurant_element.find_element(By.CSS_SELECTOR, "div.numbersChild___2qKMV:nth-child(2)").text
        image_element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img.show___3oA6B"))
        )
        image_url = image_element.get_attribute("src")
        restaurant_id = restaurant_element.find_element(By.CSS_SELECTOR, "a").get_attribute("href").split('/')[-1][:-1]
        time.sleep(5)
        lat, lon, est_delivery_fee, est_at = self.get_additional_info(restaurant_id)
        promo_available = "True" if restaurant_element.find_elements(By.CSS_SELECTOR, "p.promoText___2LmzI") else "False"
        offers = restaurant_element.find_element(By.CSS_SELECTOR, "span.discountText___GQCkj").text if restaurant_element.find_elements(By.CSS_SELECTOR, "span.discountText___GQCkj") else "No discount"
        notice = restaurant_element.find_element(By.CSS_SELECTOR, "p.closeSoon___1eGf8").text if restaurant_element.find_elements(By.CSS_SELECTOR, "p.closeSoon___1eGf8") else "No promo"

        restaurant_dict = {
            "Restaurant Id": restaurant_id,
            "Restaurant Name": restaurant_name,
            "Cuisine": restaurant_cuisine,
            "Rating": rating,
            "Duration & Distance": duration_distance,
            "Promo": promo_available,
            "Offers": offers,
            "Notice": notice,
            "Image URL": image_url,
            "Latitude": lat,
            "Longitude": lon,
            "Estimate Time of Delivery": est_at,
            "Estimated Delivery Fee": est_delivery_fee
        }
        print(restaurant_name)
        return restaurant_dict

    def get_additional_info(self, restaurant_id):
        response = requests.get(f"https://portal.grab.com/foodweb/v2/merchants/{restaurant_id}?latlng=1.396364,103.747462")
        if response.status_code == 200:
            info = json.loads(response.text)['merchant']
            latitude = info['latlng']['latitude']
            longitude = info['latlng']['longitude']
            est_delivery_fee = info['estimatedDeliveryFee']["priceDisplay"]
            est_at = info['ETA']
        else:
            latitude = "can't find"
            longitude = "can't find"
            est_delivery_fee = "N/A"
            est_at = "N/A"
        return latitude, longitude, est_delivery_fee, est_at

    def save_data(self, filename_prefix):
        filename_json = f"{filename_prefix}_restaurants_data.json"
        filename_ndjson_gz = f"{filename_prefix}_restaurant_data.ndjson.gz"
        
        with open(filename_json, 'w', encoding='utf-8') as file:
            json.dump(self.restaurant_data, file, ensure_ascii=False, indent=4)

        with gzip.open(filename_ndjson_gz, "wt", encoding="utf-8") as f:
            for data in self.restaurant_data:
                json.dump(data, f)
                f.write('\n')

    def close(self):
        self.driver.quit()

def scrape_location(location, filename_prefix):
    url = "https://food.grab.com/sg/en/"
    scraper = GrabFoodScraper(url, location)
    scraper.load_url()
    scraper.accept_cookies()
    scraper.fill_location()
    scraper.extract_restaurant_data()
    scraper.save_data(filename_prefix)
    scraper.close()

if __name__ == "__main__":
    locations = [
        ("PT Singapore - Choa Chu Kang North 6, Singapore, 689577", "choa_chu_kang"),
        ("Chong Boon Dental Surgery - Block 456 Ang Mo Kio Avenue 10, #01-1574, Singapore, 560456", "ang_mo_kio")
    ]
    
    processes = []
    for location, filename_prefix in locations:
        process = multiprocessing.Process(target=scrape_location, args=(location, filename_prefix))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()
