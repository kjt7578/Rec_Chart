from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox, QInputDialog
)
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QTextCursor
from src.core.screen_capture import ScreenCapture
from src.core.ocr_engine import OCREngine
from src.gpt.summarizer import GPTSummarizer
from difflib import SequenceMatcher
from datetime import datetime
import re

class CaptureWidget(QWidget):
    """화면 캡처 및 OCR 처리 위젯"""
    
    # 텍스트 캡처 시그널
    text_captured = pyqtSignal(str)
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.screen_capture = ScreenCapture()
        self.ocr_engine = OCREngine(settings)
        self.summarizer = GPTSummarizer(settings)
        
        # 캡처 상태 관리
        self.capturing = False
        self.extracted_text = ""    # 전체 대화 로그
        self.previous_text = ""
        self.capture_region = None  # 캡처 영역
        self.summary_buffer = ""    # 요약할 텍스트를 임시 저장하는 버퍼
        
        # 화자 구분 설정
        self.interviewer_name = "Interviewer"  # 기본값
        
        # 타이머 설정
        self.timer = QTimer()
        self.timer.timeout.connect(self.perform_ocr)
        
        self.summary_timer = QTimer()
        self.summary_timer.timeout.connect(self.perform_summary)
        
        # 문서 저장 유틸리티
        from src.utils.document_saver import DocumentSaver
        self.document_saver = DocumentSaver()
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 상단 버튼 행
        button_layout = QHBoxLayout()
        
        # Start/Stop 버튼 → Test Capture 버튼으로 변경
        self.test_capture_btn = QPushButton("🔍 Test Capture", self)
        self.test_capture_btn.clicked.connect(self.test_capture)
        self.test_capture_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        button_layout.addWidget(self.test_capture_btn)
        
        # Interviewer 이름 설정 버튼
        self.set_interviewer_btn = QPushButton("Set Interviewer Name", self)
        self.set_interviewer_btn.clicked.connect(self.set_interviewer_name)
        self.set_interviewer_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 12px;
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        button_layout.addWidget(self.set_interviewer_btn)
        
        # 캡처 영역 설정 버튼
        self.select_region_btn = QPushButton("Select Capture Area", self)
        self.select_region_btn.clicked.connect(self.select_capture_region)
        self.select_region_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 12px;
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        button_layout.addWidget(self.select_region_btn)
        
        layout.addLayout(button_layout)
        
        # Interviewer 이름 표시
        self.interviewer_label = QLabel(f"Interviewer: {self.interviewer_name}")
        self.interviewer_label.setStyleSheet("color: #666; padding: 5px; font-weight: bold;")
        layout.addWidget(self.interviewer_label)
        
        # 캡처 영역 상태 표시
        self.region_label = QLabel("Capture Area: Full Screen")
        self.region_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.region_label)
        
        # 현재 인식된 텍스트 표시
        current_text_label = QLabel("Current OCR Text:")
        layout.addWidget(current_text_label)
        
        self.current_text_display = QTextEdit(self)
        self.current_text_display.setMaximumHeight(150)
        self.current_text_display.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        layout.addWidget(self.current_text_display)
        
        # Screening Note (영어 인터뷰용) 표시
        screening_note_label = QLabel("Screening Note (English Interview - Guideline v2.0):")
        layout.addWidget(screening_note_label)
        
        self.summary_display = QTextEdit(self)
        self.summary_display.setMinimumHeight(300)
        self.summary_display.setStyleSheet("border: 1px solid #ccc; padding: 5px; background-color: #f9f9f9;")
        layout.addWidget(self.summary_display)
        
        # 저장 버튼
        self.save_btn = QPushButton("Save Screening Note", self)
        self.save_btn.clicked.connect(self.save_documents)
        self.save_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 12px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        layout.addWidget(self.save_btn)

        # 상태 표시
        self.status_label = QLabel("Status: Ready", self)
        self.status_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)
    
    def set_interviewer_name(self):
        """Interviewer 이름 설정"""
        name, ok = QInputDialog.getText(
            self, 
            'Set Interviewer Name', 
            'Enter interviewer name:',
            text=self.interviewer_name
        )
        
        if ok and name.strip():
            self.interviewer_name = name.strip()
            self.interviewer_label.setText(f"Interviewer: {self.interviewer_name}")
            print(f"Interviewer name set to: {self.interviewer_name}")
    
    def select_capture_region(self):
        """캡처 영역 선택"""
        try:
            region = self.screen_capture.select_region()
            if region:
                self.capture_region = region
                x, y, w, h = region
                self.region_label.setText(f"Capture Area: {w}x{h} at ({x}, {y})")
                print(f"Capture region set: {region}")
            else:
                print("Capture region selection cancelled")
        except Exception as e:
            print(f"Error selecting capture region: {e}")
            QMessageBox.warning(self, "Error", f"Failed to select capture region: {str(e)}")
    
    def parse_speaker_text(self, text):
        """화자 구분하여 텍스트 파싱"""
        lines = text.split('\n')
        parsed_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # "이름:" 패턴 감지
            speaker_match = re.match(r'^([^:]+):\s*(.+)', line)
            if speaker_match:
                speaker = speaker_match.group(1).strip()
                content = speaker_match.group(2).strip()
                
                # Interviewer인지 확인
                is_interviewer = (speaker.lower() == self.interviewer_name.lower())
                
                parsed_content.append({
                    'speaker': speaker,
                    'content': content,
                    'is_interviewer': is_interviewer
                })
            else:
                # 화자 구분이 없는 경우 후보자 발언으로 간주
                parsed_content.append({
                    'speaker': 'Candidate',
                    'content': line,
                    'is_interviewer': False
                })
        
        return parsed_content
    
    def format_conversation_for_ai(self, parsed_content):
        """AI를 위한 대화 포맷팅"""
        formatted_lines = []
        
        for item in parsed_content:
            speaker = item['speaker']
            content = item['content']
            
            if item['is_interviewer']:
                formatted_lines.append(f"{speaker} (Interviewer): {content}")
            else:
                formatted_lines.append(f"{speaker} (Candidate): {content}")
        
        return '\n'.join(formatted_lines)
    
    def is_duplicate_text(self, current_text):
        """중복 텍스트 확인"""
        if not self.previous_text:
            return False
        
        # 85% 이상 유사하면 중복으로 판단
        similarity = SequenceMatcher(None, self.previous_text, current_text).ratio()
        return similarity >= 0.85
    
    def extract_incremental_content(self, current_text):
        """증분 콘텐츠 추출 (스크롤 대응 알고리즘)"""
        if not self.previous_text:
            return current_text

        prev_lines = self.previous_text.splitlines()
        curr_lines = current_text.splitlines()

        if not prev_lines or not curr_lines:
            return current_text

        # 스크롤 감지를 위한 최적의 중첩 구간 탐색
        max_overlap = 0
        # 가능한 중첩 길이 (최소 1줄, 최대 텍스트 길이)로 반복
        for overlap_len in range(min(len(prev_lines), len(curr_lines)), 0, -1):
            # 이전 텍스트의 끝 부분과 현재 텍스트의 시작 부분
            prev_suffix = prev_lines[-overlap_len:]
            curr_prefix = curr_lines[:overlap_len]

            # 70% 이상 유사도를 보이면 신뢰할 수 있는 중첩으로 간주
            # OCR 오류나 약간의 수정에도 대응 가능
            if SequenceMatcher(None, prev_suffix, curr_prefix).ratio() > 0.7:
                max_overlap = overlap_len
                break
        
        # 중첩 구간을 찾았다면, 그 이후의 내용만 '새로운' 것으로 간주
        if max_overlap > 0:
            new_lines = curr_lines[max_overlap:]
            if new_lines:
                new_content = "\n".join(new_lines)
                print(f"[Incremental] Scroll detected. Overlap: {max_overlap} lines. New content: {len(new_lines)} lines.")
                return new_content
            else:
                # 새로운 줄이 없으면 (예: 위로 스크롤만 된 경우) 무시
                print("[Incremental] Scroll detected, but no new content.")
                return None
        else:
            # 중첩 구간이 없다면, 화면이 완전히 전환된 것으로 간주하고
            # 현재 텍스트 전체를 새로운 내용으로 처리
            print("[Incremental] No overlap found. Treating entire text as new.")
            return current_text
        
    def test_capture(self):
        """OCR 테스트용 한 번 캡처"""
        try:
            # 지정된 영역 또는 전체 스크린 캡처
            if self.capture_region:
                screenshot = self.screen_capture.capture_region(self.capture_region)
            else:
                screenshot = self.screen_capture.capture_screen()
            
            if not screenshot:
                self.status_label.setText("Status: Capture failed")
                return
            
            # OCR 수행
            ocr_result = self.ocr_engine.extract_text(screenshot)
            
            if not ocr_result or not ocr_result.get('text'):
                self.status_label.setText("Status: No text detected")
                return
                
            text = ocr_result['text'].strip()
            confidence = ocr_result.get('confidence', 0)
            
            # 결과 표시
            confidence_info = f"[Test - Confidence: {confidence:.1f}%] "
            display_text = confidence_info + text
            self.current_text_display.setText(display_text)
            
            # 상태 업데이트
            self.status_label.setText(f"Status: Test complete - {len(text)} chars detected")
            print(f"Test capture: {len(text)} characters, {confidence:.1f}% confidence")
            
        except Exception as e:
            print(f"Test capture error: {e}")
            self.status_label.setText(f"Status: Test error - {str(e)}")
        
    def toggle_capture(self):
        """캡처 시작/중지 토글 (메인윈도우에서 호출용)"""
        if not self.capturing:
            self.start_capture()
        else:
            self.stop_capture()
        
    def start_capture(self):
        """실제 인터뷰 캡처 시작"""
        self.capturing = True
        self.status_label.setText("Status: Interview capture started...")
        
        # 타이머 시작
        self.timer.start(2000)  # 2초마다 캡처
        self.summary_timer.start(4000)  # 4초마다 요약
        
    def stop_capture(self):
        """실제 인터뷰 캡처 중지"""
        self.capturing = False
        self.status_label.setText("Status: Interview capture stopped")
        
        # 타이머 중지
        self.timer.stop()
        self.summary_timer.stop()

    def perform_ocr(self):
        """OCR 수행"""
        if not self.capturing:
            return
            
        try:
            # 지정된 영역 또는 전체 스크린 캡처
            if self.capture_region:
                screenshot = self.screen_capture.capture_region(self.capture_region)
            else:
                screenshot = self.screen_capture.capture_screen()
            
            # OCR 수행
            ocr_result = self.ocr_engine.extract_text(screenshot)
            
            if not ocr_result or not ocr_result.get('text'):
                return
                
            current_text = ocr_result['text'].strip()
            confidence = ocr_result.get('confidence', 0)
            
            # confidence 정보 표시
            confidence_info = f"[Confidence: {confidence:.1f}%] "
            
            # OCR 신뢰도 정보만 로깅 (필터링하지 않음 - AI가 판단)
            print(f"[OCR] 신뢰도: {confidence:.1f}% - 모든 텍스트를 AI에게 전달")
            
            if current_text and len(current_text) >= 15:  # 최소 15자
                # 중복 체크
                if not self.is_duplicate_text(current_text):
                    # 증분 추출 (이전 텍스트를 넘어서는 새로운 부분만)
                    new_content = self.extract_incremental_content(current_text)
                    
                    if new_content and len(new_content) >= 15:  # 새 내용이 15자 이상
                        # 현재 텍스트 표시
                        display_text = confidence_info + current_text
                        self.current_text_display.setText(display_text)
                        
                        # 전체 로그에 증분 텍스트 축적
                        if self.extracted_text:
                            self.extracted_text += "\n" + new_content
                        else:
                            self.extracted_text = new_content
                        
                        # 요약 버퍼에 추가
                        if self.summary_buffer:
                            self.summary_buffer += "\n" + new_content
                        else:
                            self.summary_buffer = new_content

                        # 이전 텍스트 업데이트
                        self.previous_text = current_text
                        
                        # 새로운 텍스트 캡처 시그널 발생
                        self.text_captured.emit(new_content)
                        
                        print(f"New content added (Confidence: {confidence:.1f}%): {new_content.splitlines()[0]}")
                    else:
                        print(f"Incremental content too short or none (Confidence: {confidence:.1f}%)")
                else:
                    print(f"Duplicate text detected (Confidence: {confidence:.1f}%)")
            else:
                print(f"Text too short or empty (Confidence: {confidence:.1f}%)")
                
        except Exception as e:
            print(f"OCR Error: {e}")

    def perform_summary(self):
        """스크리닝 노트 생성 (증분 방식)"""
        # 버퍼에 내용이 없으면 실행하지 않음
        if not self.capturing or not self.summary_buffer.strip():
            return
        
        # 처리할 내용을 가져오고 버퍼를 즉시 비움
        text_to_process = self.summary_buffer
        self.summary_buffer = ""
            
        try:
            # 화자 구분 파싱 (새로운 청크만 처리)
            parsed_content = self.parse_speaker_text(text_to_process)
            
            # AI를 위한 포맷팅
            formatted_conversation = self.format_conversation_for_ai(parsed_content)
            
            # 요약 생성 (화자 구분된 대화 전달)
            result = self.summarizer.generate_screening_note_with_speaker(
                formatted_conversation, 
                self.interviewer_name
            )
            
            if result and isinstance(result, dict):
                category = result.get('category', 'Unknown')
                note = result.get('note', '')
                
                if category != 'Not Applicable' and note:
                    # 타임스탬프 추가
                    timestamp = datetime.now().strftime("[%H:%M:%S]")
                    formatted_note = f"{timestamp} **{category}**: {note}"
                    
                    # 스크리닝 노트에 추가
                    current_content = self.summary_display.toPlainText()
                    if current_content:
                        new_content = current_content + "\n\n" + formatted_note
                    else:
                        new_content = formatted_note
                    
                    self.summary_display.setText(new_content)
                    
                    # 스크롤을 최하단으로
                    cursor = self.summary_display.textCursor()
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                    self.summary_display.setTextCursor(cursor)
                    
                    print(f"Screening note added: [{category}] {note}")
                else:
                    print(f"Content not applicable or empty note: {category}")
                    
        except Exception as e:
            print(f"Screening note generation error: {e}")

    def save_documents(self):
        """문서 저장"""
        try:
            if not self.extracted_text and not self.summary_display.toPlainText():
                QMessageBox.warning(self, "Warning", "No content to save.")
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 원본 텍스트 저장
            if self.extracted_text:
                text_filename = f"extracted_text_{timestamp}.txt"
                self.document_saver.save_text(self.extracted_text, text_filename)
            
            # 스크리닝 노트 저장
            screening_note = self.summary_display.toPlainText()
            if screening_note:
                note_filename = f"screening_note_{timestamp}.txt"
                self.document_saver.save_text(screening_note, note_filename)
            
            # 성공 메시지
            QMessageBox.information(self, "Success", "Documents saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save documents: {str(e)}")

    def closeEvent(self, event):
        """위젯 종료 시 리소스 정리"""
        print("[CaptureWidget] 종료 중...")
        self.stop_capture()
        event.accept() 