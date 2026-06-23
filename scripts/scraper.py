import json
import time
import warnings
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

warnings.filterwarnings("ignore")

def start_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_question_links(driver, page):
    url = f"https://learn.microsoft.com/en-us/answers/tags/781/microsoft-edge?page={page}"
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/answers/questions/']")))
        elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/answers/questions/']")
        links = [el.get_attribute("href").split("?")[0] for el in elements if el.get_attribute("href")]
        return list(set([l for l in links if l.count("/") > 6]))
    except: return []

def expand_all_comments(driver):
    """Clica nos botões de expansão de comentários."""
    buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-bi-name='show-hide-comments'][aria-expanded='false']")
    for btn in buttons:
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            driver.execute_script("arguments[0].click();", btn)
        except:
            continue
    if buttons:
        
        time.sleep(1.5)

def get_comments_from_element(parent_element):
    """Extrai textos de comentários baseados na estrutura de lista do site."""
    comments_found = []
    comment_items = parent_element.find_elements(By.CSS_SELECTOR, "li[id^='comment-'], li[data-test-id^='comment-']")
    for li in comment_items:
        try:
            content_div = li.find_element(By.CSS_SELECTOR, ".content.font-size-sm")
            text = content_div.text.strip()
            if text:
                comments_found.append(text)
        except:
            continue
    return comments_found

def parse_question(driver, url):
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    data = {"url": url, "title": "", "question": {"text": "", "comments": []}, "answers": []}

    try:
        title_el = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        data["title"] = title_el.text.strip()

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(1)
        expand_all_comments(driver)

        # 1. Pergunta e Comentários da Pergunta
        try:
            q_container = driver.find_element(By.CSS_SELECTOR, "article.question, .question")
            q_text_el = q_container.find_element(By.CSS_SELECTOR, ".content, .post-body")
            data["question"]["text"] = q_text_el.text.strip()
            data["question"]["comments"] = get_comments_from_element(q_container)
        except: pass

        # 2. Respostas e Comentários das Respostas
        answer_elements = driver.find_elements(By.CSS_SELECTOR, ".answer, [id^='answer-']")
        for el in answer_elements:
            try:
                content = el.find_element(By.CSS_SELECTOR, ".content, .post-body, [itemprop='text']")
                text = content.text.strip()
                
                if text and text != data["question"]["text"]:
                    ai_indicator = el.find_elements(By.CSS_SELECTOR, "span.has-text-subtle.font-weight-semibold")
                    is_ai = any("Q&A Assist" in span.text for span in ai_indicator)
                    is_accepted = "is-accepted" in el.get_attribute("class") or "accepted-answer" in el.get_attribute("outerHTML")
                    
                    ans_comments = get_comments_from_element(el)

                    if text not in [a["text"] for a in data["answers"]]:
                        data["answers"].append({
                            "text": text,
                            "is_accepted": is_accepted,
                            "is_ai": is_ai,
                            "comments": ans_comments
                        })
            except: continue
    except Exception:
        pass

    return data

# ---------------- EXECUÇÃO COM FILTRO DE ALTA INTERAÇÃO ----------------
ROOT = Path(__file__).parent.parent
driver = start_driver()
dataset = []

try:
    for page in range(1, 4):
        links = get_question_links(driver, page)
        print(f"--- Analisando Página {page} ---")

        for link in links:
            item = parse_question(driver, link)
            
            # Contagem de comentários totais (na pergunta + em todas as respostas)
            total_comments = len(item["question"]["comments"]) + sum(len(a["comments"]) for a in item["answers"])
            total_answers = len(item["answers"])

            #  FILTRO DE ALTA INTERAÇÃO: Deve ter resposta E ter pelo menos um comentário
            if total_answers > 0 and total_comments > 0:
                dataset.append(item)
                print(f"✅ SALVO (Alta Interação): {item['title'][:40]}...")
                print(f"   ∟ {total_answers} Resposta(s) | {total_comments} Comentário(s) total")
            else:
                motivo = "Sem respostas" if total_answers == 0 else "Sem comentários"
                print(f"⏩ PULADO ({motivo}): {item['title'][:40]}...")
                
            time.sleep(0.5)
finally:
    driver.quit()

with open(ROOT / "data/raw/dataset_high_interaction.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print(f"\n Finalizado! Total de casos de alta interação salvos: {len(dataset)}")