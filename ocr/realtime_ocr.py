import threading
import queue
import time
from typing import Callable, Optional

from .screen_capture import capture_region
from .ocr_engine import image_to_text
from .text_detector import TextChangeDetector

class RealtimeOCR:
    def __init__(self, region: dict, callback: Callable[[str], None], interval: float = 2.0):
        """
        실시간 OCR 처리 클래스
        region: 캡처할 화면 영역
        callback: 텍스트 변화 감지 시 호출될 콜백 함수
        interval: 캡처 주기(초)
        """
        self.region = region
        self.callback = callback
        self.interval = interval
        self.text_detector = TextChangeDetector()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.queue = queue.Queue()

    def start(self):
        """OCR 처리 시작"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._process_loop)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """OCR 처리 중지"""
        self.running = False
        if self.thread:
            self.thread.join()
            self.thread = None

    def _process_loop(self):
        """OCR 처리 메인 루프"""
        for img in capture_region(self.region, self.interval):
            if not self.running:
                break
            
            try:
                # OCR 처리
                text = image_to_text(img)
                
                # 텍스트 변화 감지
                changed, new_text = self.text_detector.detect_change(text)
                
                if changed:
                    # 콜백 함수 호출
                    self.callback(new_text)
                    
            except Exception as e:
                print(f"OCR 처리 중 오류 발생: {e}")
                continue 