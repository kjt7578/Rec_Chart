import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
import cv2
import re

class OCREngine:
    """고급 OCR 엔진 클래스"""
    
    def __init__(self, settings):
        """
        OCR 엔진 초기화
        
        Args:
            settings (dict): OCR 설정
        """
        self.settings = settings
        self.language = settings['ocr']['language']
        self.confidence = max(70, settings['ocr']['confidence'])  # 최소 70% 신뢰도
        self.last_valid_text = ""  # 마지막 유효한 텍스트 저장
        
    def preprocess_image(self, image):
        """
        OCR을 위한 이미지 전처리 강화
        
        Args:
            image (PIL.Image): 원본 이미지
            
        Returns:
            PIL.Image: 전처리된 이미지
        """
        try:
            # PIL에서 OpenCV로 변환
            img_array = np.array(image)
            
            # 그레이스케일 변환
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # 1. 노이즈 제거
            denoised = cv2.medianBlur(gray, 3)
            
            # 2. 대비 향상 (CLAHE - 적응적 히스토그램 평활화)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # 3. 이진화 (적응적 임계값)
            binary = cv2.adaptiveThreshold(
                enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # 4. 모폴로지 연산으로 텍스트 정리
            kernel = np.ones((1,1), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # 5. 크기 확대 (2배)
            height, width = cleaned.shape
            enlarged = cv2.resize(cleaned, (width*2, height*2), interpolation=cv2.INTER_CUBIC)
            
            # OpenCV에서 PIL로 변환
            processed_image = Image.fromarray(enlarged)
            
            return processed_image
            
        except Exception as e:
            print(f"[OCR] 이미지 전처리 실패: {e}")
            return image
        
    def extract_text(self, image):
        """
        이미지에서 텍스트 추출 (레이아웃 보존, 필터링 없음)
        
        Args:
            image (PIL.Image): 처리할 이미지
            
        Returns:
            dict: {'text': str, 'confidence': float} 형식의 결과
        """
        try:
            # 1. 이미지 전처리
            processed_image = self.preprocess_image(image)
            
            # 2. OCR 설정 (PSM 4: 가변 크기의 단일 텍스트 열로 가정)
            custom_config = r'--oem 3 --psm 4' 
            
            # 3. OCR 수행 (image_to_string 사용으로 레이아웃 보존)
            text = pytesseract.image_to_string(
                processed_image, 
                lang=self.language,
                config=custom_config
            ).strip()
            
            # 4. 텍스트가 없으면 즉시 반환
            if not text:
                return {'text': "", 'confidence': 0}

            # 5. 신뢰도 계산
            conf_data = pytesseract.image_to_data(
                processed_image, 
                lang=self.language,
                config=custom_config,
                output_type=pytesseract.Output.DICT
            )
            confidences = [int(c) for c in conf_data['conf'] if int(c) >= 0] # -1은 제외
            avg_confidence = np.mean(confidences) if confidences else 0
            
            # 6. 간단한 후처리만 수행
            processed_text = self.advanced_text_processing(text)
            
            print(f"[OCR] 텍스트 추출 (No Filtering): {len(processed_text)}자 (평균 {avg_confidence:.1f}%)")
            return {'text': processed_text, 'confidence': avg_confidence}

        except Exception as e:
            print(f"[OCR] 텍스트 추출 실패: {e}")
            return {'text': "", 'confidence': 0}
    
    def advanced_text_processing(self, text):
        """
        고급 텍스트 후처리 (대화 형식 유지)
        
        Args:
            text (str): 원본 텍스트
            
        Returns:
            str: 후처리된 텍스트
        """
        if not text:
            return ""

        # 1. 화자 이름 앞에 줄바꿈 추가 (e.g., "great! JT: I'm...")
        # `\s`는 공백, `([A-Za-z]+:)`는 'JT:' 같은 화자 태그를 캡처.
        text = re.sub(r'\s([A-Za-z]+:)', r'\n\1', text)

        # 2. OCR 오류 패턴 수정
        corrections = {
            r'\b0\b': 'O',
            r'\b1\b': 'I',
            r'\bℓ\b': 'l',
            r'\b5\b': 'S',
            r'rn\b': 'm',
            r'\bvv\b': 'w',
            r'①②③④⑤⑥⑦⑧⑨⑩': '',
            r'[◆■□▲▼★☆]': '',
        }
        
        for pattern, replacement in corrections.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # 3. 줄 단위로 정리
        lines = text.splitlines()
        processed_lines = []
        for line in lines:
            # 3.1. 불필요한 문자 제거
            line = re.sub(r'[^\w\s가-힣.,!?:;()[\]{}"\'/-]', '', line)
            
            # 3.2. 연속된 같은 문자 정리
            line = re.sub(r'([a-zA-Z가-힣])\1{3,}', r'\1', line)
            
            # 3.3. 앞뒤 공백 제거
            line = line.strip()

            if line:
                processed_lines.append(line)
        
        # 4. 최종적으로 정리된 문장들을 다시 합침
        return "\n".join(processed_lines)
    
    def is_valid_text(self, text):
        """
        텍스트 품질 검증
        
        Args:
            text (str): 검증할 텍스트
            
        Returns:
            bool: 유효한 텍스트 여부
        """
        if not text or len(text) < 5:
            return False
        
        # 1. 의미있는 문자 비율 체크
        meaningful_chars = len(re.findall(r'[a-zA-Z가-힣0-9]', text))
        total_chars = len(text)
        
        if meaningful_chars / total_chars < 0.7:  # 70% 이상이 의미있는 문자여야 함
            return False
        
        # 2. 반복 패턴 체크
        if len(set(text)) < len(text) * 0.3:  # 너무 많은 반복 문자
            return False
        
        # 3. 최소 단어 수 체크
        words = text.split()
        if len(words) < 2:  # 최소 2개 단어
            return False
        
        return True
    
    def is_valid_text_relaxed(self, text):
        """
        텍스트 품질 검증 (실시간 인터뷰용 완화 버전)
        
        Args:
            text (str): 검증할 텍스트
            
        Returns:
            bool: 유효한 텍스트 여부
        """
        if not text or len(text) < 3:  # 최소 3글자 (기존 5글자에서 완화)
            return False
        
        # 1. 의미있는 문자 비율 체크 (완화)
        meaningful_chars = len(re.findall(r'[a-zA-Z가-힣0-9]', text))
        total_chars = len(text)
        
        if meaningful_chars / total_chars < 0.5:  # 50% 이상 (기존 70%에서 완화)
            return False
        
        # 2. 최소 단어 수 체크 (완화)
        words = text.split()
        if len(words) < 1:  # 최소 1개 단어 (기존 2개에서 완화)
            return False
        
        # 3. 키워드 기반 추가 검증 (인터뷰 관련 단어가 있으면 허용)
        interview_keywords = [
            'experience', 'work', 'project', 'team', 'skill', 'years',
            '경험', '업무', '프로젝트', '팀', '기술', '년', '회사', '담당',
            'I', 'my', 'we', 'our', 'the', 'and', 'with', 'for'
        ]
        
        text_lower = text.lower()
        for keyword in interview_keywords:
            if keyword.lower() in text_lower:
                print(f"[OCR] 키워드 '{keyword}' 발견으로 텍스트 승인")
                return True
        
        # 4. 반복 패턴 체크 (기존 유지)
        if len(set(text)) < len(text) * 0.2:  # 너무 많은 반복 문자 (30%→20%로 완화)
            return False
        
        return True
        
    def set_language(self, language):
        """OCR 언어 설정"""
        self.language = language
        
    def set_confidence(self, confidence):
        """최소 신뢰도 설정"""
        self.confidence = max(30, confidence)  # 최소 30%로 완화 (기존 70%)

def image_to_text(image):
    """
    이미지에서 텍스트 추출 (호환성 유지)
    
    Args:
        image: PIL Image 객체
        
    Returns:
        str: 추출된 텍스트
    """
    try:
        # 기본 OCR 설정
        settings = {
            'ocr': {
                'language': 'kor+eng',
                'confidence': 75
            }
        }
        
        ocr = OCREngine(settings)
        return ocr.extract_text(image)
        
    except Exception as e:
        print(f"[OCR] 텍스트 추출 실패: {e}")
        return ""

def preprocess_text(text):
    """
    OCR로 추출된 텍스트 전처리 (호환성 유지)
    
    Args:
        text (str): 원본 텍스트
        
    Returns:
        str: 전처리된 텍스트
    """
    if not text:
        return ""
    
    # 기본 정리
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def text_to_sentences(text):
    """
    텍스트를 문장 단위로 분할 (개선된 버전)
    
    Args:
        text (str): 입력 텍스트
        
    Returns:
        list: 문장 리스트
    """
    if not text:
        return []
    
    # 1. 문장 구분자 기준으로 분할 (개선)
    # 문장 끝을 나타내는 패턴들
    sentence_patterns = [
        r'[.!?]+\s+',  # 마침표, 느낌표, 물음표 + 공백
        r'[.!?]+$',    # 문장 끝의 마침표, 느낌표, 물음표
        r'\n+',        # 줄바꿈
        r'[.!?]+(?=[A-Z가-힣])',  # 마침표 다음에 대문자나 한글이 오는 경우
    ]
    
    # 임시 구분자로 분할
    temp_text = text
    for pattern in sentence_patterns:
        temp_text = re.sub(pattern, '|||SPLIT|||', temp_text)
    
    # 분할된 문장들 정리
    sentences = temp_text.split('|||SPLIT|||')
    
    # 2. 문장 정리 및 필터링
    cleaned_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        
        # 유효한 문장인지 검사
        if (len(sentence) >= 5 and  # 최소 5글자
            len(sentence.split()) >= 2 and  # 최소 2단어
            not re.match(r'^[^a-zA-Z가-힣]*$', sentence)):  # 의미있는 문자 포함
            
            # 문장 부호 정리
            sentence = re.sub(r'[.!?]+$', '', sentence)  # 끝의 문장부호 제거
            cleaned_sentences.append(sentence)
    
    # 3. 중복 제거 (유사한 문장)
    unique_sentences = []
    for sentence in cleaned_sentences:
        is_duplicate = False
        for existing in unique_sentences:
            # 80% 이상 유사하면 중복으로 간주
            similarity = len(set(sentence.split()) & set(existing.split())) / max(len(sentence.split()), len(existing.split()))
            if similarity > 0.8:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_sentences.append(sentence)
    
    return unique_sentences

def format_sentences_output(sentences):
    """
    문장들을 출력 형식으로 포맷팅
    
    Args:
        sentences (list): 문장 리스트
        
    Returns:
        str: 포맷팅된 텍스트
    """
    if not sentences:
        return ""
    
    # 각 문장을 번호와 함께 출력
    formatted_text = ""
    for i, sentence in enumerate(sentences, 1):
        formatted_text += f"{i}. {sentence}\n"
    
    return formatted_text 