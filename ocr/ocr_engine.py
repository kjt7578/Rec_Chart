import pytesseract
from PIL import Image
import cv2
import numpy as np


def image_to_text(pil_img, lang='eng'):
    """
    PIL 이미지를 받아 pytesseract로 텍스트를 추출합니다.
    """
    # PIL 이미지를 OpenCV 이미지로 변환
    cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    # 전처리(선택적): 그레이스케일, threshold 등
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    # threshold 적용 (노이즈 제거 및 명확한 문자 추출)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # 다시 PIL 이미지로 변환
    proc_img = Image.fromarray(thresh)
    # pytesseract로 텍스트 추출
    text = pytesseract.image_to_string(proc_img, lang=lang)
    return text.strip() 