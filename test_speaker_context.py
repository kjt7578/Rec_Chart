# -*- coding: utf-8 -*-
"""
화자 구분 및 컨텍스트 이해 테스트
사용자가 지적한 "Yes" 답변 상황을 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.gpt.summarizer import GPTSummarizer
from dotenv import load_dotenv

def test_short_answers():
    """짧은 답변에 대한 컨텍스트 이해 테스트"""
    
    # 설정 로드
    load_dotenv()
    
    settings = {
        'gpt': {
            'model': 'gpt-3.5-turbo',
            'temperature': 0.1,
            'max_tokens': 800
        }
    }
    
    summarizer = GPTSummarizer(settings)
    
    # 테스트 케이스 1: 이사 의향 - 짧은 답변
    test_case_1 = """Interviewer (Interviewer): Are you open to relocate?
Candidate (Candidate): Yes, absolutely"""

    print("=== 테스트 케이스 1: 이사 의향 짧은 답변 ===")
    print(f"입력: {test_case_1}")
    
    result_1 = summarizer.generate_screening_note_with_speaker(test_case_1, "Interviewer")
    print(f"결과: {result_1}")
    print()
    
    # 테스트 케이스 2: 급여 기대치 - 짧은 답변
    test_case_2 = """Interviewer (Interviewer): What is your salary expectation?
Candidate (Candidate): Around 120K would be ideal"""

    print("=== 테스트 케이스 2: 급여 기대치 ===")
    print(f"입력: {test_case_2}")
    
    result_2 = summarizer.generate_screening_note_with_speaker(test_case_2, "Interviewer")
    print(f"결과: {result_2}")
    print()
    
    # 테스트 케이스 3: 복합 대화 - 질문과 짧은 답변들
    test_case_3 = """Interviewer (Interviewer): Are you comfortable with onsite work?
Candidate (Candidate): Yes, definitely
Interviewer (Interviewer): What about overtime when needed?
Candidate (Candidate): No problem, I understand the demands"""

    print("=== 테스트 케이스 3: 복합 대화 ===")
    print(f"입력: {test_case_3}")
    
    result_3 = summarizer.generate_screening_note_with_speaker(test_case_3, "Interviewer")
    print(f"결과: {result_3}")
    print()
    
    # 테스트 케이스 4: 문제 상황 - 컨텍스트 없는 "Yes"
    test_case_4 = """Candidate (Candidate): Yes, absolutely"""

    print("=== 테스트 케이스 4: 컨텍스트 없는 답변 ===")
    print(f"입력: {test_case_4}")
    
    result_4 = summarizer.generate_screening_note_with_speaker(test_case_4, "Interviewer")
    print(f"결과: {result_4}")
    print()

if __name__ == "__main__":
    test_short_answers() 