import random
import time
import requests
import os
import pickle
import json
import hashlib
import datetime
import base64
from requests_toolbelt.multipart.encoder import MultipartEncoder
from faker import Faker
from fake_useragent import UserAgent
from seleniumwire import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, \
    ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


class Codashop:
    def __init__(self):
        pass

    def start_request(self, user_id: str) -> str:
        url = "https://order-sg.codashop.com/initPayment.action"

        payload = {
            "voucherPricePoint.id": 8159,
            "voucherPricePoint.price": 300000.0,
            "voucherPricePoint.variablePrice": 0,
            "n": "12/7/2022-208",
            "email": "",
            "userVariablePrice": 0,
            "order.data.profile": "eyJuYW1lIjoiICIsImRhdGVvZmJpcnRoIjoiIiwiaWRfbm8iOiIifQ==",
            "user.userId": user_id,
            "user.zoneId": "",
            "msisdn": "",
            "voucherTypeName": "FREEFIRE",
            "shopLang": "id_ID",
            "voucherTypeId": 5,
            "gvtId": 19,
            "checkoutId": "",
            "affiliateTrackingId": "",
            "impactClickId": "",
            "anonymousId": ""

        }

        response = requests.post(url=url, data=payload)
        if response.status_code == 200:
            status = response.json().get("success")

            if not status:
                print(response.text)
                return response.text
            elif status:
                nickname = response.json().get("confirmationFields").get("roles")[0].get("role")
                if nickname:
                    print(f"Nickname: {nickname} - Codashop")
                    return f"Nickname={nickname}"
                else:
                    print(f"{response.text} - Codashop")
                    return response.text
        else:
            print(f"{response.status_code} - {response.text} - Codashop")
            return f"{response.status_code} - {response.text}"


class DuniaGames:  # Delay 6 detik untuk per 1 request
    def __init__(self):
        self.cred_path = os.path.join(os.getcwd(), "cred", "duniagames_cred.pkl")

        if not os.path.exists(self.cred_path):
            self.get_cred()

    def check_url(self, driver) -> str:
        max_retries = 0
        is_page_loaded = False
        while not is_page_loaded and max_retries < 3:
            try:
                driver.set_page_load_timeout(6)
                driver.get("https://duniagames.co.id/top-up/item/freefire")
                if driver.current_url == "https://duniagames.co.id/top-up/item/freefire":
                    WebDriverWait(driver, 6).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[formcontrolname="userid"]')))
                    is_page_loaded = True
                    print("Page Loaded")
                    return "Page Loaded"
            except TimeoutException as e:
                print(f"Timeout loading page ({max_retries + 1}/3 retries)")
                max_retries += 1
        else:
            print("Timeout contacting https://duniagames.co.id/top-up/item/freefire")
            return "Timeout contacting https://duniagames.co.id/top-up/item/freefire"

    def get_cred(self) -> str:
        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument("--window-size=1920,1080")
        driver_options.add_argument('--headless')
        driver_options.add_argument('--no-sandbox')
        driver_options.add_argument('--ignore-certificate-errors-spki-list')
        driver_options.add_argument('--ignore-ssl-errors')

        with webdriver.Chrome(options=driver_options) as driver:
            url = self.check_url(driver)
            if url == "Page Loaded":
                max_retries = 0
                is_api_intercepted = False
                while not is_api_intercepted and max_retries < 3:
                    try:
                        time.sleep(5)
                        # Fill in user ID
                        userid_form = driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="userid"]')
                        userid_form.send_keys(str(random.randint(1000000000, 9999999999)))

                        # Select denomination
                        denom_spinner = driver.find_element(By.CSS_SELECTOR,
                                                            'mat-form-field.mat-form-field-type-mat-select')
                        denom_spinner.click()
                        time.sleep(1)

                        denoms = driver.find_elements(By.CSS_SELECTOR, 'mat-option.mat-focus-indicator')
                        denoms_index = random.randint(4, 12)
                        driver.execute_script("arguments[0].scrollIntoView(true);", denoms[denoms_index])
                        denoms[denoms_index].click()
                        time.sleep(1)

                        # Select payment method (QRIS)
                        payment_method = driver.find_element(By.XPATH,
                                                             "//div[contains(@class, "
                                                             "'section-payment-product')]//mat-form-field[contains("
                                                             "@class, 'mat-form-field')]")
                        payment_method.click()
                        time.sleep(1)

                        qris = driver.find_element(By.XPATH,
                                                   "//mat-option[@aria-disabled='false']//span[contains(@class, "
                                                   "'mat-option-text') and contains(., 'QRIS')]/ancestor::mat-option")
                        qris.click()
                        time.sleep(1)

                        prefix = ["083", "087", "085", "081", "0881"]
                        index = random.randint(0, len(prefix) - 1)
                        phone_number = f"{prefix[index]}{random.randint(1000000000, 9999999999)}"
                        phone_number_form = driver.find_element(By.CSS_SELECTOR,
                                                                'input[data-test-id="phonenumber-payment"]')
                        phone_number_form.send_keys(phone_number)

                        email = Faker().email(domain='gmail.com')
                        email_form = driver.find_element(By.CSS_SELECTOR, 'input[data-test-id="email-input"]')
                        email_form.send_keys(email)
                        time.sleep(1)

                        buy_product = driver.find_element(By.CSS_SELECTOR, 'div[data-test-id="buy-product"]')
                        buy_product.click()

                        api_request = driver.wait_for_request(
                            "https://api.duniagames.co.id/api/transaction/v1/top-up/inquiry/store", 30)

                        if api_request:
                            request_body = json.loads(api_request.body.decode('utf-8'))
                            cred = {
                                "productId": request_body.get("productId"),
                                "itemId": request_body.get("itemId"),
                                "catalogId": request_body.get("catalogId"),
                                "paymentId": request_body.get("paymentId"),
                            }
                            with open(self.cred_path, "wb") as f:
                                pickle.dump(cred, f)

                            is_api_intercepted = True
                            print(
                                "Successfully intercepting https://api.duniagames.co.id/api/transaction/v1/top-up/inquiry/store")
                            return f"Successfully intercepting https://api.duniagames.co.id/api/transaction/v1/top-up/inquiry/store"
                        else:
                            print(f"api request not found")
                            max_retries += 1
                            driver.refresh()

                    except TimeoutException as e:
                        print(
                            f"Timeout intercepting https://api.duniagames.co.id/api/transaction/v1/top-up/inquiry/store ({max_retries + 1}/3 retries)")
                        max_retries += 1
                        driver.refresh()

                    except NoSuchElementException as e:
                        print("Element not found:", e)
                        max_retries += 1
                        driver.refresh()

                    except ElementNotInteractableException as e:
                        print("Element not interactable:", e)
                        max_retries += 1
                        driver.refresh()

                    except ElementClickInterceptedException as e:
                        print("Element click intercepted:", e)
                        max_retries += 1
                        driver.refresh()

                    except Exception as e:
                        print("Unexpected error:", e)
                        max_retries += 1
                        driver.refresh()
                else:
                    print(
                        "Failed to intercept https://api.duniagames.co.id/api/transaction/v1/top-up/inquiry/store due to maximum retries")
                    return "Failed to intercept https://api.duniagames.co.id/api/transaction/v1/top-up/inquiry/store due to maximum retries"

            return "Timeout contacting https://duniagames.co.id/top-up/item/freefire"

    def request(self, user_id: str) -> requests.Response:
        with open(self.cred_path, "rb") as f:
            cred = pickle.load(f)

        url = "https://api.duniagames.co.id/api/transaction/v1/top-up/inquiry/store"

        headers = {
            'Accept': 'application / json, text / plain, * / *',
            'User-Agent': UserAgent().random,
            'Content-Type': 'application/json',
        }
        payload = {
            "productId": 3,
            "itemId": cred.get("itemId"),
            "product_ref": "REG",
            "product_ref_denom": "REG",
            "catalogId": cred.get("catalogId"),
            "paymentId": cred.get("paymentId"),
            "gameId": user_id
        }

        response = requests.post(url=url, headers=headers, json=payload)
        return response

    def start_request(self, user_id: str) -> str:
        response = self.request(user_id)

        if response.status_code == 200:
            response_data = response.json()
            nickname = response_data["data"].get("userNameGame")

            print(f"Nickname: {nickname} - Duniagames")
            return nickname

        elif response.status_code == 429:
            print(f"Too Many Request - Duniagames")
            print(response.headers)

        else:
            print(f"Failed. {response.status_code} - {response.content} - Duniagames")


class UniPin:
    def __init__(self):
        pass

    def start_request(self, user_id: str) -> str:
        start_url = "https://www.unipin.com/id/garena/free-fire"
        get_cred = requests.get(url=start_url)

        if get_cred.status_code == 200:
            soup = BeautifulSoup(get_cred.content, "html.parser")
            csrf_token = soup.find("meta", {"name": "csrf-token"})["content"]
            cookies = get_cred.cookies
            xrsf_token = cookies.get("XSRF-TOKEN")
            session = cookies.get("unipin_session")

            inquiry_url = "https://www.unipin.com/id/garena/inquiry"
            inquiry_headers = {
                "Accept": "application/json, text/javascript, */*;",
                "Content-Type": "application/x-www-form-urlencoded;",
                "Cookie": f"region=ID; free-fire_rgid=RURnL3R2RzNhYkZ3VzdDTkNCTVZwQT09; free-fire_game=free-fire; "
                          f"free-fire_playerid={user_id}; XSRF-TOKEN={xrsf_token}; unipin_session={session}",
                "User-Agent": UserAgent().random,
                "X-Csrf-Token": f"{csrf_token}",
                "X-Requested-With": "XMLHttpRequest"
            }
            inquiry_payload = (
                f"rgid=RURnL3R2RzNhYkZ3VzdDTkNCTVZwQT09&playerid={user_id}&game=free-fire&did=242&pid"
                f"=103&influencer=&cust_email=")

            post_inquiry = requests.post(url=inquiry_url, headers=inquiry_headers, data=inquiry_payload)

            if post_inquiry.status_code == 200:
                data = post_inquiry.json()
                status = data.get("status")

                if status == "1":
                    inquiry_id = data.get("message")

                    checkout_url = f"https://www.unipin.com/id/garena/checkout/{inquiry_id}"
                    info = requests.get(url=checkout_url)

                    if info.status_code == 200:
                        info_html = BeautifulSoup(info.content, "html.parser")
                        details_rows = info_html.find_all('div', class_='details-row')

                        if len(details_rows) >= 2:
                            nickname = details_rows[1].find('div', class_='details-value')
                            if nickname:
                                print(f"Nickname: {nickname.get_text(strip=True)} - Unipin")
                                return f"Nickname={nickname.get_text(strip=True)}"
                    else:
                        print(f"{info.text} - Unipin")
                        return info.text
                else:
                    print(f"{post_inquiry.text} - Unipin")
                    return post_inquiry.text
        else:
            print(f"{get_cred.text} - Unipin")
            return get_cred.text


class VogAon:
    def __init__(self):
        pass

    def start_request(self, user_id: str) -> str:
        url = "https://back-fe.vogaon.com/api/v1/apigames/cek/freefire"

        payload = {
            "game_code": "freefire",
            "all_fields": {
                "User ID": user_id
            }
        }

        response = requests.post(url=url, json=payload)
        if response.status_code == 200:
            nickname = response.json()["data"]["username"]
            print(f"Nickname: {nickname} - VogAon")
            return f"Nickname={nickname}"
        else:
            print(f"{response.text} - VogAon")
            return response.text


class DiamondStore:
    def __init__(self):
        self.payment_method = [3, 6, 7, 8, 9, 17, 32, 33, 34]
        self.price_code = [4127, 4128, 4714, 4209, 4210, 4211, 4212, 4213, 4214, 4215, 4216, 4217, 4218, 4219, 4220,
                           4219, 4221, 4222, 4223, 4224, 4225, 4226, 4227, 4228, 4229, 4230, 4231, 4232, 4233, 4234,
                           4235, 4236, 4237, 4238, 4239, 4240, 4241, 4242, 4243, 4244, 4245, 4246, 4247, 4248, 4249,
                           4250, 4251, 4252, 4253, 4254, 4255]

    def start_request(self, user_id: str) -> str:
        pm_index = random.randint(0, (len(self.payment_method) - 1))
        pc_index = random.randint(0, (len(self.price_code) - 1))

        url = "https://storediamond.id//ajax/order_confirm.php"
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded;",
            "User-Agent": UserAgent().random,
            "X-Requested-With": "XMLHttpRequest"
        }

        payload = f"kategori=11&id={user_id}&layanan={self.price_code[pc_index]}&metode={self.payment_method[pm_index]}&rek_ovo=&kontak=&g-recaptcha-response="

        response = requests.post(url=url, headers=headers, data=payload)
        if response.status_code == 200:
            status = response.json().get("status")
            if status:
                msg = response.json().get("msg")
                lines = msg.split("\n")
                nickname = None
                for line in lines:
                    if line.strip().startswith("Nickname : "):
                        nickname = line.strip().replace('Nickname : ', '')
                        break

                if nickname:
                    print(f"Nickname: {nickname} - Diamondstore")
                    return f"Nickname={nickname}"
                else:
                    print(f"{response.text} - Diamondstore")
                    return response.text
            else:
                print(f"{response.text} - Diamondstore")
                return response.text
        else:
            print(f"{response.status_code} - {response.text} - Diamondstore")
            return f"{response.status_code} - {response.text}"


class MvStore:
    def __init__(self):
        pass

    def start_request(self, user_id: str) -> str:
        url = "https://mvstore.id/api/ign"

        payload = {
            "id": user_id,
            "serverGame": "",
            "gameCode": "FF"
        }

        response = requests.post(url=url, data=payload)

        if response.status_code == 200:
            nickname = response.json().get("nickName")
            if nickname:
                print(f"Nickname: {nickname} - MvStore")
                return f"Nickname={nickname}"
            else:
                print(f"Tujuan Salah - MvStore")
                return "Tujuan Salah"
        else:
            print(f"{response.status_code} - {response.text}")


class TopUpYok:
    def __init__(self):
        pass

    def start_request(self, user_id: str) -> str:
        url = "https://topupyok.com//ajax/order_confirm.php"

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded;",
            "User-Agent": UserAgent().random,
            "X-Requested-With": "XMLHttpRequest"
        }

        payload = f"kategori=11&id={user_id}&layanan=1761&metode=7&rek=&rek=&rek=&rek=&promo_voucher=&kontak="

        response = requests.post(url=url, headers=headers, data=payload)
        if response.status_code == 200:
            status = response.json().get("status")
            if status:
                msg = response.json().get("msg")
                lines = msg.split("\n")
                nickname = None
                for line in lines:
                    if line.strip().startswith("Nickname : "):
                        nickname = line.strip().replace('Nickname : ', '')
                        break

                if nickname:
                    print(f"Nickname: {nickname} - TopUpYok")
                    return f"Nickname={nickname}"
                else:
                    print(f"{response.text} - TopUpYok")
                    return response.text
            else:
                print(f"{response.text} - TopUpYok")
                return response.text
        else:
            print(f"{response.status_code} - {response.text} - TopUpYok")
            return f"{response.status_code} - {response.text}"


class IsiGameStore:
    def __init__(self):
        pass

    def start_request(self, user_id: str) -> str:
        url = f"https://isigame.store/api/v1/order/prepare/FREEFIRE?userId={user_id}&zoneId=undefined"
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": UserAgent().random
        }

        response = requests.get(url=url, headers=headers)

        if response.status_code == 200:
            msg = response.json().get("message")
            if msg == "Success":
                nickname = response.json().get("data")
                print(f"Nickname: {nickname} - IsiGameStore")
                return f"Nickname={nickname}"
            else:
                print(f"{response.text} - IsiGameStore")
                return response.text
        else:
            print(f"{response.text} - IsiGameStore")
            return response.text


class LatomStore:
    def __init__(self):
        self.p_id = ["FF5-S24", "FF5", "FF10", "FF10-S24", "FF12-S888", "FF12-S97", "FF20", "FF50", "FF50-S24",
                     "FF55-S24", "FF60", "FF70-S888", "FF70", "FF70-S97", "FF80-S24", "FF100", "FF100-S24", "FF120-S24",
                     "FF130-S24", "FF140-S888", "FF140", "FF140-S97", "FF145-S24", "FF150-S24", "FF190-S24",
                     "FF200-S24", "FF210-S888", "FF210", "FF210-S97", "FFMINGGUAN-S24", "FFMM", "FF280-S888", "FF280",
                     "FF280-S97", "FF355", "FF355-S888", "FF355-S97", "FF400", "FF420-S888", "FF420-S97",
                     "FF500-S24", "FF500", "FF510-S24", "FF565-S888", "FF565-S97", "FF600", "FF635-S888", "FF635-S97",
                     "FFBULANAN-S24", "FFMB", "FF720-S888", "FF720", "FF720-S97", "FF800-S24", "FF800", "FF860-S888",
                     "FF860", "FF860-S97", "FF930-S888", "FF930-S97", "FF1000-S888", "FF1000", "FF1000-S97",
                     "FF1075-S888", "FF1050-S24", "FF1075", "FF1075-S97", "FF1080", "FF1080-S24", "FF1450-S888",
                     "FF1440", "FF1450-S97", "FF1450", "FF1800", "FF2000", "FF2140", "FF2180-S97", "FF2200-S24",
                     "FF3640-S97", "FF7290", "FF7290-S24", "FF36500-S24", "FF73100-S24"]

    def generate_xgorgon(self) -> str:
        o = "ORDERCONFIRMGUEST"
        x = "latomReactdd"
        d = datetime.date.today().strftime('%Y-%m-%d')

        A = o + x + d

        gorgon = hashlib.sha256(A.encode()).hexdigest()
        return gorgon

    def start_request(self, user_id: str) -> str:
        p_index = random.randint(0, (len(self.p_id) - 1))
        url = "https://a-api.latomstore.id/v3/user/orderConfirmGuest"
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://latomstore.id",
            "Priority": "u=1, i",
            "Referer": "https://latomstore.id/",
            "User-Agent": UserAgent().random,
            "Xgorgon": self.generate_xgorgon(),
        }

        x = random.randint(1234567890, 9999999999)
        index = random.randint(0, 4)
        prefix = ["083", "087", "085", "081", "0881"]

        payload = f"layanan={self.p_id[p_index]}&metode=3&id={user_id}&kontak={prefix[index]}{x}&api_key=undefined"

        response = requests.post(url=url, headers=headers, data=payload)
        if response.status_code == 200:
            nickname = response.json().get("data").get("nick")
            if nickname:
                print(f"Nickname: {nickname} - LatomStore")
                return f"Nickname={nickname}"
            else:
                print(f"{response.status_code} - {response.reason} - {response.json()} - LatomStore")
                return f"{response.status_code} - {response.reason} - {response.json()}"

        elif response.status_code == 400:
            msg = response.json().get("msg")
            if msg == "ID anda salah":
                print("Tujuan Salah - LatomStore")
                return "Tujuan Salah"
            else:
                print(f"{response.status_code} - {response.reason} - {response.json()} - LatomStore")
                return f"{response.status_code} - {response.reason} - {response.json()}"
        else:
            print(f"{response.status_code} - {response.reason} - {response.text} - LatomStore")
            return f"{response.status_code} - {response.reason} - {response.text}"


class YoggStore:
    def __init__(self):
        self.denom = ["FF20P", "FF25P", "FF40P", "FF50P", "FF70P", "FF100P", "FF140P", "FF210P",
                      "FF280P", "FF355P", "FF425P", "FF720P", "FF1000P", "FF2000P", "FF7290P"]

    def generate_xgorgon(self) -> str:
        o = "ORDERCONFIRMGUEST"
        x = "YoggstoreKey"
        d = datetime.date.today().strftime('%Y-%m-%d')

        A = o + x + d

        gorgon = hashlib.sha256(A.encode()).hexdigest()
        return gorgon

    def start_request(self, user_id: str) -> str:
        d_index = random.randint(0, (len(self.denom) - 1))
        url = "https://a-api.yoggstore.id/v3/user/orderConfirmGuest"

        x = random.randint(1234567890, 9999999999)
        index = random.randint(0, 4)
        prefix = ["083", "087", "085", "081", "0881"]

        payload = {
            "layanan": self.denom[d_index],
            "jumlah": "1",
            "metode": "40",
            "promo_voucher": "",
            "kontak": f"{prefix[index]}{x}",
            "rek": "",
            "pintrx": "",
            "id": user_id
        }

        multipart_data = MultipartEncoder(
            fields=payload,
            boundary='----WebKitFormBoundaryMAR4kG7ZO72IBnbF'
        )

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": multipart_data.content_type,
            "Origin": "https://yoggstore.id",
            "Priority": "u=1, i",
            "Referer": "https://yoggstore.id/",
            "User-Agent": UserAgent().random,
            "Xgorgon": self.generate_xgorgon(),
        }

        response = requests.post(url=url, headers=headers, data=multipart_data)
        if response.status_code == 200:
            nickname = response.json().get("data").get("nick")
            if nickname:
                print(f"Nickname: {nickname} - YoggStore")
                return f"Nickname={nickname}"
            else:
                print(f"{response.status_code} - {response.reason} - {response.json()} - YoggStore")
                return f"{response.status_code} - {response.reason} - {response.json()}"

        elif response.status_code == 400:
            msg = response.json().get("msg")
            if msg == "ID anda salah":
                print("Tujuan Salah - YoggStore")
                return "Tujuan Salah"
            else:
                print(f"{response.status_code} - {response.reason} - {response.json()} - YoggStore")
                return f"{response.status_code} - {response.reason} - {response.json()}"
        else:
            print(f"{response.status_code} - {response.reason} - {response.text} - YoggStore")
            return f"{response.status_code} - {response.reason} - {response.text}"


class IndoFlazz:
    def __init__(self):
        self.p_id = ["FF10-S9", "FF20-S9", "FF30-S9", "FF40-S9", "FF50-S9", "FF70-S9", "FF100-S9",
                     "FF120-S9", "FF140-S9", "FF150-S9", "FF190-S9", "FF210-S9", "FF280-S9",
                     "FF350-S9", "FF425-S9", "FF500-S9", "FF545-S9", "FF720-S9", "FF860-S9", "FF1000-S9"]

    def generate_xgorgon(self) -> str:
        o = "ORDERCONFIRMGUEST"
        x = "IndoflazzMaju"
        d = datetime.date.today().strftime('%Y-%m-%d')

        A = o + x + d

        gorgon = hashlib.sha256(A.encode()).hexdigest()
        return gorgon

    def start_request(self, user_id: str) -> str:
        p_index = random.randint(0, (len(self.p_id) - 1))
        url = "https://a-api.indoflazz.com/v3/user/orderConfirmGuest"
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://indoflazz.com",
            "Priority": "u=1, i",
            "Referer": "https://indoflazz.com/",
            "User-Agent": UserAgent().random,
            "Xgorgon": self.generate_xgorgon(),
        }

        x = random.randint(1234567890, 9999999999)
        index = random.randint(0, 4)
        prefix = ["083", "087", "085", "081", "0881"]

        payload = f"layanan={self.p_id[p_index]}&metode=3&id={user_id}&kontak={prefix[index]}{x}&api_key=undefined"

        response = requests.post(url=url, headers=headers, data=payload)
        if response.status_code == 200:
            nickname = response.json().get("data").get("nick")
            if nickname:
                print(f"Nickname: {nickname} - IndoFlazz - {int(time.time())}")
                return f"Nickname={nickname}"
            else:
                print(f"{response.status_code} - {response.reason} - {response.json()} - IndoFlazz - {int(time.time())}")
                return f"{response.status_code} - {response.reason} - {response.json()}"

        elif response.status_code == 400:
            msg = response.json().get("msg")
            if msg == "ID anda salah":
                print("Tujuan Salah - IndoFlazz")
                return "Tujuan Salah"
            else:
                print(f"{response.status_code} - {response.reason} - {response.json()} - IndoFlazz - {int(time.time())}")
                return f"{response.status_code} - {response.reason} - {response.json()}"
        else:
            print(f"{response.status_code} - {response.reason} - {response.text} - IndoFlazz - {int(time.time())}")
            return f"{response.status_code} - {response.reason} - {response.text}"


class TopupGim:
    def __init__(self):
        pass

    def decrypt_data(self, data: str):
        # Extract padding count from the end of the data string
        padding_count_str = data[-1]
        padding_count = int(padding_count_str)  # Convert string to integer

        # Extract the modified string (n) without the padding count
        modified_string = data[:-1]

        # Reverse the modification of the modified string (n)
        original_base64_bytes = []
        for i in range(len(modified_string)):
            if i % 2 == 0:
                original_base64_bytes.append(chr(ord(modified_string[i]) - 1))
            else:
                original_base64_bytes.append(chr(ord(modified_string[i]) + 1))

        # Join the characters to form the original base64 encoded bytes
        original_base64_string = ''.join(original_base64_bytes)

        # Add back the appropriate number of padding characters
        original_base64_string += '=' * padding_count

        return original_base64_string

    def parse_data(self, user_id: str):
        # input string
        e = '{"property-user_id":"' + user_id + '","productCode":"1528555434"}'

        # encrypt ke base64
        t = base64.b64encode(e.encode()).decode()

        # hitung char "="
        padding_count = t.count('=')

        # hapus char "="
        r = t.replace('=', '')

        # teuing teu ngarti. hasil refactor dari codingan web javascript
        # ke python
        n = ''.join(
            chr(ord(r[i]) + 1) if i % 2 == 0 else chr(ord(r[i]) - 1)
            for i in range(len(r))
        )

        # gabungin n sama total char "="
        data = n + str(padding_count)
        return data

    def start_request(self, user_id: str) -> str:
        data = self.parse_data(user_id)
        start_url = "https://topupgim.com/product/free-fire/1528555434"
        get_cred = requests.get(url=start_url)

        if get_cred.status_code == 200:
            soup = BeautifulSoup(get_cred.content, "html.parser")
            csrf_token = soup.find("meta", {"name": "csrf-token"})["content"]
            cookies = get_cred.cookies
            cookies_csrf = cookies.get("_csrf")
            session = cookies.get("topupgim.sid")

            api_url = "https://topupgim.com/t/prepare/check-uid"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Cookie": f"topupgim.sid={session}; _csrf={cookies_csrf}",
                "User-Agent": UserAgent().random
            }

            payload = {
                "_csrf": csrf_token,
                "data": data
            }

            check_uid = requests.post(url=api_url, headers=headers, json=payload)
            if check_uid.status_code == 200:
                status = check_uid.json().get("data").get("is_valid")
                if status:
                    nickname = check_uid.json().get("data").get("player_name")
                    print(f"Nickname: {nickname} - TopupGim")
                    return f"Nickname={nickname}"
                else:
                    end = time.time()
                    print(f"Tujuan Salah - TopupGim")
                    return "Tujuan Salah"
            else:
                print(f"{check_uid.status_code} - {check_uid.text} - TopupGim")
        else:
            print(f"{get_cred.status_code} - {get_cred.text} - TopupGim")


class DigiPlay:
    def __init__(self):
        self.cred_path = os.path.join(os.getcwd(), "cred", "digiplay.pkl")

        if not os.path.exists(self.cred_path):
            self.get_cred()

    def get_cred(self):
        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument('--headless')
        driver_options.add_argument('--no-sandbox')
        driver_options.add_argument('--ignore-certificate-errors-spki-list')
        driver_options.add_argument('--ignore-ssl-errors')
        driver = webdriver.Chrome(options=driver_options)

        is_cred_intercepted = False
        max_retries = 0
        while not is_cred_intercepted and max_retries < 3:
            try:
                driver.set_page_load_timeout(10)
                driver.get("https://digiplay.id/produk/free-fire")
                cred = {
                    "ci_session": driver.get_cookie("ci_session").get("value"),
                    "csrf_digiplay_cookie": driver.get_cookie("csrf_digiplay_cookie").get("value")
                }

                with open(self.cred_path, "wb") as f:
                    pickle.dump(cred, f)

                print("Successfully intercepting https://digiplay.id/produk/free-fire")
                driver.quit()
                return f"Successfully intercepting https://digiplay.id/produk/free-fire"

            except TimeoutException as e:
                print(f"Timeout intercepting https://digiplay.id/produk/free-fire ({max_retries + 1}/3 retries)")
                max_retries += 1
                driver.refresh()
        else:
            driver.quit()
            return "Timeout contacting https://digiplay.id/produk/free-fire"

    def start_request(self, user_id: str) -> str:
        with open(self.cred_path, "rb") as f:
            cred = pickle.load(f)

        url = "https://digiplay.id/api/check_username"
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": f"ci_session={cred.get('ci_session')}; "
                      f"csrf_digiplay_cookie={cred.get('csrf_digiplay_cookie')};",
            "User-Agent": UserAgent().random,
            "X-Requested-With": "XMLHttpRequest"
        }
        payload = f"game=FF&type=check_username&user_id={user_id}&csrf_digiplay_token={cred.get('csrf_digiplay_cookie')}"

        response = requests.post(url=url, headers=headers, data=payload)

        if response.status_code == 200:
            code = response.json().get("code")
            if code == 200:
                nickname = response.json().get("username")
                print(f"Nickname: {nickname} - Digiplay")
                return f"Nickname={nickname}"
            else:
                print(f"{response.text} - Tujuan Salah - Digiplay")
                return "Tujuan Salah"
        else:
            print(f"{response.status_code} - {response.reason} - Digiplay")


class VocaGame:
    def __init__(self):
        pass

    def start_request(self, user_id: str) -> str:
        url = f"https://api.vocagame.com/v1/order/prepare/FREEFIRE?userId={user_id}&zoneId=undefined"
        response = requests.get(url=url)

        if response.status_code == 200:
            nickname = response.json().get("data")
            print(f"Nickname: {nickname} - VocaGame")
            return f"Nickname={nickname}"

        else:
            print(f"{response.status_code} - {response.text} - VocaGame")
            return response.text


class FsGameshop:
    def __init__(self):
        self.payment_method = [3, 5, 6, 8, 9, 10, 11, 12, 13, 17, 18, 19, 31, 32, 33]
        self.price_code = [4487, 4496, 4507, 4510, 4517, 4528, 4538, 4546, 4556, 4568, 4572, 4585, 4591, 4602, 4613,
                           4612, 4628, 4641, 4652, 4666, 4671, 4680, 4689, 4703, 4714, 4718, 4727, 4736, 4748, 4754,
                           4760, 4776, 4791, 4788, 4798, 4802, 4810, 4818]

    def start_request(self, user_id: str) -> str:
        pm_index = random.randint(0, (len(self.payment_method) - 1))
        pc_index = random.randint(0, (len(self.price_code) - 1))

        url = "https://fsgameshop.com//ajax/order_confirm.php"
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded;",
            "User-Agent": UserAgent().random,
            "X-Requested-With": "XMLHttpRequest"
        }
        payload = f"kategori=11&id={user_id}&layanan={self.price_code[pc_index]}&metode={self.payment_method[pm_index]}&rek_ovo=&kontak=&g-recaptcha-response="

        response = requests.post(url=url, headers=headers, data=payload)
        if response.status_code == 200:
            status = response.json().get("status")
            if status:
                msg = response.json().get("msg")
                lines = msg.split("\n")
                nickname = None
                for line in lines:
                    if line.strip().startswith("Nickname : "):
                        nickname = line.strip().replace('Nickname : ', '')
                        break

                if nickname:
                    print(f"Nickname: {nickname} - FsGameShop")
                    return f"Nickname={nickname}"
                else:
                    print(f"{response.text} - FsGameShop")
                    return response.text
            else:
                print(f"{response.text} - FsGameShop")
                return response.text
        else:
            print(f"{response.status_code} - {response.text} - FsGameShop")
            return f"{response.status_code} - {response.text}"


class SungSaja:
    def __init__(self):
        pass

    def start_request(self, user_id: str) -> str:
        url = "https://sungsaja.com//ajax/order_confirm.php"
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded;",
            "User-Agent": UserAgent().random,
            "X-Requested-With": "XMLHttpRequest"
        }
        payload = f"kategori=11&id={user_id}&layanan=2405&jumlah=1&metode=3&promo_voucher=&kontak=&g-recaptcha-response="

        response = requests.post(url=url, headers=headers, data=payload)
        if response.status_code == 200:
            status = response.json().get("status")
            if status:
                msg = response.json().get("msg")
                lines = msg.split("\n")
                nickname = None
                for line in lines:
                    if line.strip().startswith("Nickname : "):
                        nickname = line.strip().replace('Nickname : ', '')
                        break

                if nickname:
                    print(f"Nickname: {nickname} - SungSaja")
                    return f"Nickname={nickname}"
                else:
                    print(f"{response.text} - SungSaja")
                    return response.text
            else:
                print(f"{response.text} - SungSaja")
                return response.text
        else:
            print(f"{response.status_code} - {response.text} - SungSaja")
            return f"{response.status_code} - {response.text}"


class MatchaShop:
    def __init__(self):
        pass

    def start_request(self, user_id: str) -> str:
        url = "https://matchashop.id//ajax/order_confirm.php"
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded;",
            "User-Agent": UserAgent().random,
            "X-Requested-With": "XMLHttpRequest"
        }
        payload = f"kategori=11&id={user_id}&layanan=85&metode=3&rek_ovo=&kontak=&g-recaptcha-response="

        response = requests.post(url=url, headers=headers, data=payload)
        if response.status_code == 200:
            status = response.json().get("status")
            if status:
                msg = response.json().get("msg")
                lines = msg.split("\n")
                nickname = None
                for line in lines:
                    if line.strip().startswith("Nickname : "):
                        nickname = line.strip().replace('Nickname : ', '')
                        break

                if nickname:
                    print(f"Nickname: {nickname} - MatchaShop")
                    return f"Nickname={nickname}"
                else:
                    print(f"{response.text} - MatchaShop")
                    return response.text
            else:
                print(f"{response.text} - MatchaShop")
                return response.text
        else:
            print(f"{response.status_code} - {response.text} - MatchaShop")
            return f"{response.status_code} - {response.text}"


class TopUp:
    def __init__(self):
        self.cred_path = os.path.join(os.getcwd(), "cred", "topup_cred.pkl")

        if not os.path.exists(self.cred_path):
            self.get_cred(str(random.randint(1000000000, 9999999999)))

    def check_url(self, driver) -> str:
        max_retries = 0
        is_page_loaded = False
        while not is_page_loaded and max_retries < 3:
            try:
                driver.set_page_load_timeout(10)
                driver.get("https://topup.co.id/id/free-fire")
                if driver.current_url == "https://topup.co.id/id/free-fire":
                    is_page_loaded = True
                    print("Page Loaded")
                    return "Page Loaded"
            except TimeoutException as e:
                print(f"Timeout loading page ({max_retries + 1}/3 retries)")
                max_retries += 1
                driver.refresh()
        else:
            print("Timeout contacting topup.co.id/id/free-fire")
            return "Timeout contacting topup.co.id/id/free-fire"

    def get_cred(self, user_id: str) -> str:
        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument('--headless')
        driver_options.add_argument('--no-sandbox')
        driver_options.add_argument('--ignore-certificate-errors-spki-list')
        driver_options.add_argument('--ignore-ssl-errors')

        with webdriver.Chrome(options=driver_options) as driver:
            url = self.check_url(driver)

            if url == "Page Loaded":
                max_retries = 0
                is_api_intercepted = False
                while not is_api_intercepted and max_retries < 3:
                    try:
                        username_form = driver.find_element(
                            By.CSS_SELECTOR, "input[type='number'].w-full.block.border.p-2.rounded-md"
                        )
                        username_form.send_keys(user_id)

                        denoms = driver.find_elements(
                            By.XPATH,
                            "//div[@class='relative cursor-pointer flex items-center hover:bg-gray-100 border rounded-lg' "
                            "and not(.//span[@class='text-xs font-bold text-red-500' and contains(text(), 'Gangguan')])]"
                        )

                        index = random.randint(0, 49)
                        denom = denoms[index]

                        driver.execute_script("arguments[0].scrollIntoView(true);", denom)
                        time.sleep(2)
                        denom.click()

                        emoney = driver.find_element(
                            By.XPATH, "//div[contains(@class, 'py-2')] //span[text()='Emoney']"
                        )

                        driver.execute_script("arguments[0].scrollIntoView(true);", emoney)
                        time.sleep(3)
                        emoney.click()

                        brands = driver.find_elements(
                            By.XPATH,
                            "//div[contains(@class, 'p-3') and contains(@class, "
                            "'w-full') and contains(@class, 'relative') and contains("
                            "@class, 'rounded-lg') and contains(@class, 'border') and "
                            ".//span[text()='DANA' or text()='Shopee Pay' or text("
                            ")='LINKAJA' or text()='GOPAY' or text()='OVO']]"
                        )

                        index = random.randint(0, 4)
                        brand = brands[index]
                        brand.click()

                        x = random.randint(1234567890, 9999999999)
                        index = random.randint(0, 4)
                        prefix = ["083", "087", "085", "081", "0881"]

                        number_form = driver.find_element(By.XPATH, "//div[@id='use_wa']//input[@type='number']")
                        number_form.send_keys(f"{prefix[index]}{x}")

                        buy_button = driver.find_element(By.XPATH, "//button[normalize-space()='Beli Sekarang']")
                        buy_button.click()

                        web_requests = driver.requests
                        for r in web_requests:
                            if r.url == "https://topup.co.id/validasi?op=freefire":
                                cred = {}
                                cookies = r.headers.get("Cookie")
                                xrsf_token = r.headers.get('X-Xsrf-Token')

                                cred["cookies"] = cookies
                                cred["xrsf_token"] = xrsf_token

                                with open(self.cred_path, "wb") as f:
                                    pickle.dump(cred, f)

                                is_api_intercepted = True
                                print("Successfully intercepting https://topup.co.id/validasi?op=freefire")
                                return f"Successfully intercepting https://topup.co.id/validasi?op=freefire"
                            else:
                                print(f"request: {r.url}")

                    except TimeoutException as e:
                        print(
                            f"Timeout intercepting https://topup.co.id/validasi?op=freefire ({max_retries + 1}/3 retries)")
                        max_retries += 1
                        driver.refresh()

                    except NoSuchElementException as e:
                        print("Element not found:", e)
                        max_retries += 1
                        driver.refresh()

                    except ElementClickInterceptedException as e:
                        print("Element click intercepted:", e)
                        max_retries += 1
                        driver.refresh()

                    except Exception as e:
                        print("Unexpected error:", e)
                        max_retries += 1
                        driver.refresh()
                else:
                    print("Failed to intercept https://topup.co.id/validasi?op=freefire due to maximum retries")
                    return "Failed to intercept https://topup.co.id/validasi?op=freefire due to maximum retries"

            return "Timeout contacting topup.co.id/id/free-fire"

    def request(self, user_id: str) -> requests.Response:
        with open(self.cred_path, "rb") as f:
            cred = pickle.load(f)

        cookies = cred.get("cookies")
        xrsf_token = cred.get("xrsf_token")

        url = "https://topup.co.id/validasi?op=freefire"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Cookie": cookies,
            "User-Agent": UserAgent().random,
            "X-Xsrf-Token": xrsf_token
        }
        payload = {
            "user_id": user_id,
            "zone_id": "",
            "cek_validasi": "freefire"
        }
        response = requests.post(url=url, headers=headers, json=payload)
        return response

    def start_request(self, user_id: str) -> str:
        response = self.request(user_id)
        if response.status_code == 200:
            status = response.json().get("status")
            if status == 0:
                print(response.text)
                return response.text
            else:
                nickname = response.json().get("data").get("username")
                print(f"Nickname: {nickname} - TopUp")
                return f"Nickname={nickname}"
        elif response.status_code == 419:
            self.get_cred(user_id)


class TokoGame:
    def __init__(self):
        self.cred_path = os.path.join(os.getcwd(), "cred", "tokogame_cred.pkl")

        if not os.path.exists(self.cred_path):
            self.get_cred(str(random.randint(1000000000, 9999999999)))

    def check_url(self, driver) -> str:
        max_retries = 0
        is_page_loaded = False
        while not is_page_loaded and max_retries < 3:
            try:
                driver.set_page_load_timeout(6)
                driver.get("https://www.tokogame.com/id-id/digital/free-fire-promo")
                if driver.current_url == "https://www.tokogame.com/id-id/digital/free-fire-promo":
                    is_page_loaded = True
                    return "Page Loaded"
            except TimeoutException as e:
                print(f"Timeout loading page ({max_retries + 1}/3 retries)")
                max_retries += 1
        else:
            print("Timeout contacting www.tokogame.com/id-id/digital/free-fire-promo")
            return "Timeout contacting www.tokogame.com/id-id/digital/free-fire-promo"

    def get_cred(self, user_id: str) -> str:
        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument('--headless')
        driver_options.add_argument('--no-sandbox')
        driver_options.add_argument('--ignore-certificate-errors-spki-list')
        driver_options.add_argument('--ignore-ssl-errors')
        driver = webdriver.Chrome(options=driver_options)

        url = self.check_url(driver)

        if url == "Page Loaded":
            max_retries = 0
            is_api_intercepted = False
            while not is_api_intercepted and max_retries < 3:
                try:
                    username_form = driver.find_element(By.NAME, "userid")
                    check_button = driver.find_element(By.CSS_SELECTOR, "div.sc-abbc6fcb-13")

                    username_form.send_keys(f"{user_id}")
                    check_button.click()

                    validate_order_request = driver.wait_for_request(
                        "https://api.tokogame.com/core/v1/orders/validate-order", timeout=30
                    )

                    if validate_order_request:
                        is_api_intercepted = True
                        x_secret_id = validate_order_request.headers.get('x-secret-id')
                        x_request_id = validate_order_request.headers.get('x-request-id')
                        cred = f"x-secret-id={x_secret_id}|x-request-id={x_request_id}"
                        with open(self.cred_path, "wb") as f:
                            pickle.dump(cred, f)
                        print(
                            "Successfully intercepting https://api.tokogame.com/core/v1/orders/validate-order")
                        driver.quit()
                        return f"Successfully intercepting https://api.tokogame.com/core/v1/orders/validate-order"
                    else:
                        print("https://api.tokogame.com/core/v1/orders/validate-order not found")
                        return "https://api.tokogame.com/core/v1/orders/validate-order not found"

                except TimeoutException as e:
                    print(
                        f"Timeout intercepting https://api.tokogame.com/core/v1/orders/validate-order ({max_retries + 1}/3 retries)")
                    max_retries += 1
                    driver.refresh()
                except NoSuchElementException as e:
                    print("Element not found:", e)
                    max_retries += 1
                    driver.refresh()
                except Exception as e:
                    print("Unexpected error:", e)
                    max_retries += 1
                    driver.refresh()
            else:
                print("Can't Intercept https://api.tokogame.com/core/v1/orders/validate-order")
                driver.quit()
                return "Can't Intercept https://api.tokogame.com/core/v1/orders/validate-order"
        else:
            driver.quit()
            return "Timeout contacting www.tokogame.com/id-id/digital/free-fire-promo"

    def request(self, user_id: str) -> requests.Response:
        with open(self.cred_path, "rb") as f:
            cred = str(pickle.load(f))

        x_secret_id = cred.split("|")[0].split("=")[1]
        x_request_id = cred.split("|")[1].split("=")[1]

        url = "https://api.tokogame.com/core/v1/orders/validate-order"
        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "user-agent": UserAgent().random,
            "x-request-id": x_request_id,
            "x-secret-id": x_secret_id
        }
        payload = {
            "productId": "644359b1f61740160ca158ca",
            "questionnaireAnswers": [
                {
                    "questionnaire": {
                        "code": "userid",
                        "inputType": "STRING",
                        "translations": [
                            {
                                "language": "ID",
                                "question": "Masukkan User ID",
                                "description": "User ID",
                                "choices": []
                            }
                        ]
                    },
                    "answer": user_id
                }
            ]
        }
        response = requests.post(url=url, headers=headers, json=payload)
        return response

    def start_request(self, user_id: str):
        response = self.request(user_id)

        if response.status_code == 200:
            nickname = response.json().get("data")["username"]
            print(f"Nickname: {nickname} - TokoGame")
            return f"Nickname={nickname}"

        elif response.status_code == 401:
            print("Tokogame cred expired. otw intercepting api...")
            self.get_cred(user_id)

        elif response.status_code == 204:
            print("Tujuan Salah - TokoGame")
            return "Tujuan Salah"

        else:
            print(f"{response.status_code} - {response.text} - TokoGame")


class RozezShop:
    def __init__(self):
        pass

    def start_request(self, user_id: str) -> str:
        url = f"https://rozezshop.com/api/v1/order/prepare/FREEFIRE?userId={user_id}&zoneId=undefined"

        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "User-Agent": UserAgent().random,
        }

        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            nickname = response.json().get("data")
            if nickname:
                print(f"Nickname: {nickname} - RozezShop")
                return f"Nickname={nickname}"
        else:
            print(f"{response.status_code} - {response.text} - RozezShop")
            return response.text
