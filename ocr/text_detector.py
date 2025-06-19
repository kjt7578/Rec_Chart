from difflib import SequenceMatcher
import time
from typing import Optional, Tuple

class TextChangeDetector:
    def __init__(self, similarity_threshold: float = 0.8):
        """
        텍스트 변화를 감지하는 클래스
        similarity_threshold: 유사도 임계값 (0~1 사이, 높을수록 더 엄격한 변화 감지)
        """
        self.previous_text: Optional[str] = None
        self.similarity_threshold = similarity_threshold
        self.last_update_time = time.time()

    def detect_change(self, current_text: str) -> Tuple[bool, str]:
        """
        현재 텍스트와 이전 텍스트를 비교하여 변화를 감지
        Returns: (변화 감지 여부, 새로운 텍스트)
        """
        if not current_text.strip():
            return False, current_text

        if self.previous_text is None:
            self.previous_text = current_text
            return True, current_text

        # 텍스트 유사도 계산
        similarity = SequenceMatcher(None, self.previous_text, current_text).ratio()
        
        if similarity < self.similarity_threshold:
            self.previous_text = current_text
            self.last_update_time = time.time()
            return True, current_text
        
        return False, current_text

    def get_time_since_last_update(self) -> float:
        """마지막 업데이트로부터 경과 시간(초) 반환"""
        return time.time() - self.last_update_time 