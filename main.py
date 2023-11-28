from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re
import time


# 인원수 추출 및 범위 확장 함수
def extract_and_expand_numbers(de):
    matches = re.findall(r'\d+(?=인용)', de)
    if len(matches) > 1 and '~' in de:
        start, end = int(matches[0]), int(matches[-1])
        return [str(i) for i in range(start, end + 1)]
    else:
        return matches


# WebDriver 설정
driver = webdriver.Chrome()

# 웹사이트 접속
driver.get("https://prod.danawa.com/list/?cate=132437")

# 제품 정보를 저장할 리스트
product_info = []

try:
    for a in range(1, 6):
        # 브랜드 선택
        brand_xpath = f'/html/body/div[2]/div[3]/div[5]/div[2]/div[3]/form/div[2]/div[2]/div[1]/div[2]/div/div/dl[1]/dd/ul[1]/li[{a}]/label/input'
        driver.find_element(By.XPATH, brand_xpath).click()
        time.sleep(3)

        current_page = 1
        last_page = None

        while True:
            scroll = driver.find_element(By.CLASS_NAME, 'num')
            scroll.location_once_scrolled_into_view

            # 현재 페이지의 제품 정보 수집
            tents = driver.find_elements(By.CLASS_NAME, 'prod_main_info')
            for tent in tents:
                try:
                    name = tent.find_element(By.NAME, 'productName').text
                    price_text = tent.find_element(By.CLASS_NAME, 'price_sect').find_element(By.TAG_NAME, 'a').text
                    price_numbers = re.findall(r'\d+', price_text)
                    price = ''.join(price_numbers)
                    detail = tent.find_element(By.CLASS_NAME, 'spec_list').text
                    people = extract_and_expand_numbers(detail)

                    product_info.append({'name': name, 'price': price, 'people': people})
                except NoSuchElementException:
                    # 데이터가 없는 요소는 무시하고 계속 진행
                    continue

            # 페이지 처리
            if current_page == last_page:
                break

            try:
                page_numbers = driver.find_elements(By.CLASS_NAME, 'num')
                if page_numbers:
                    if last_page is None:
                        last_page = int(page_numbers[-1].text)  # 마지막 페이지 번호 저장

                    if current_page < last_page:
                        page_numbers[current_page].click()  # 다음 페이지로 이동
                        current_page += 1
                        time.sleep(3)
                    else:
                        break  # 마지막 페이지에 도달
                else:
                    break  # 페이지 번호가 없으면 종료
            except NoSuchElementException:
                break  # 페이지 번호가 없으면 종료

        # 브랜드 선택 해제
        driver.find_element(By.XPATH, brand_xpath).click()

except Exception as e:
    print(f"오류 발생: {e}")

finally:
    driver.quit()

# 수집한 데이터 출력
for info in product_info:
    print(info)

import csv
with open('danawa.csv', 'w', newline='') as file:
    fieldnames = ['NAME', 'PRICE', 'PEOPLE']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    
    for i in range(len(product_info)):
        
        if product_info[i]['price'] == '' or len(product_info[i]['people']) == 0:
            continue
        
        people = len(product_info[i]['people'])
        
        if people >= 2: # n >= 2
            for _ in range(people):
                writer.writerow({'NAME':product_info[i]['name'], 'PRICE':int(product_info[i]['price']), 'PEOPLE':product_info[i]['people'].pop(0)})
                
        elif people == 1: # n = 1
            writer.writerow({'NAME':product_info[i]['name'], 'PRICE':int(product_info[i]['price']), 'PEOPLE':product_info[i]['people'].pop()})

