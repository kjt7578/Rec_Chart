import json
import os
from pathlib import Path

DEFAULT_SETTINGS = {
    "capture": {
        "interval": 2.0,  # 캡처 간격 (초)
        "auto_save": True,  # 자동 저장 여부
        "save_interval": 300,  # 자동 저장 간격 (초)
    },
    "ocr": {
        "language": "kor+eng",  # OCR 언어 설정
        "confidence": 60,  # 최소 신뢰도 (%)
    },
    "gpt": {
        "model": "gpt-3.5-turbo",  # GPT 모델
        "temperature": 0.7,  # 생성 온도
        "max_tokens": 1000,  # 최대 토큰 수
    },
    "ui": {
        "theme": "light",  # UI 테마
        "font_size": 12,  # 기본 폰트 크기
    }
}

def get_config_path():
    """설정 파일 경로 반환"""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    return config_dir / "settings.json"

def load_settings():
    """설정 파일 로드"""
    config_path = get_config_path()
    
    if not config_path.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return settings
    except Exception as e:
        print(f"설정 파일 로드 중 오류 발생: {e}")
        return DEFAULT_SETTINGS

def save_settings(settings):
    """Save settings file"""
    config_path = get_config_path()
    
    try:
        # Try saving with UTF-8 BOM
        try:
            with open(config_path, 'w', encoding='utf-8-sig', errors='replace') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except UnicodeEncodeError:
            # If UTF-8 fails, retry with CP949
            with open(config_path, 'w', encoding='cp949', errors='replace') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving settings file: {e}")
        return False 