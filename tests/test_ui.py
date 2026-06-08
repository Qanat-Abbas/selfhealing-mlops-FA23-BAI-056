import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "http://localhost:5000"


def test_frontend_sentiment():
    """Selenium headless test: submit text and verify result output."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)

    try:
        # Load the frontend
        driver.get(BASE_URL)

        # Find the text input by its fixed element ID and enter test sentence
        text_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "text-input"))
        )
        text_input.clear()
        text_input.send_keys(
            "Spotlessly clean rooms with attentive staff and superb amenities throughout"
        )

        # Click the submit button
        submit_btn = driver.find_element(By.ID, "submit-btn")
        submit_btn.click()

        # Wait for result-output to be populated
        result_output = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "result-output"))
        )

        # Wait until the result text is non-empty
        WebDriverWait(driver, 15).until(
            lambda d: d.find_element(By.ID, "result-output").text.strip() != ""
        )

        result_text = result_output.text.strip()

        # Assert result is non-empty and contains expected keywords
        assert result_text != "", "result-output should not be empty"
        assert any(keyword in result_text for keyword in ["POSITIVE", "NEGATIVE", "Confidence"]), \
            f"Unexpected result text: {result_text}"

    finally:
        driver.quit()
