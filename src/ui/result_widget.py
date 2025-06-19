from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QComboBox, QFileDialog
)
from PyQt6.QtCore import Qt
from src.gpt.summarizer import GPTSummarizer
from src.utils.document_saver import DocumentSaver
import re

class ResultWidget(QWidget):
    """OCR 결과 및 요약 표시 위젯"""
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.current_text = ""
        self.current_summary = {}
        
        self.gpt_summarizer = GPTSummarizer(settings)
        self.document_saver = DocumentSaver()
        
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        
        # 텍스트 표시 영역
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        # 요약 표시 영역
        self.summary_edit = QTextEdit()
        self.summary_edit.setReadOnly(True)
        layout.addWidget(self.summary_edit)
        
        # 저장 컨트롤
        save_layout = QHBoxLayout()
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["TXT", "DOCX"])
        save_layout.addWidget(self.format_combo)
        
        self.save_button = QPushButton("저장")
        self.save_button.clicked.connect(self.save)
        save_layout.addWidget(self.save_button)
        
        layout.addLayout(save_layout)
        
    def update_text(self, text):
        """텍스트 업데이트"""
        print(f'[ResultWidget] update_text 호출됨, 텍스트 길이: {len(text)}')
        # OCR 결과 누적 (중복 방지)
        text = text.strip()
        if text and text not in self.current_text:
            if self.current_text:
                self.current_text += "\n" + text
            else:
                self.current_text = text
        # 문장 단위로 분리
        sentences = re.split(r'(?<=[.!?])\s+', self.current_text)
        pretty_text = '\n'.join([s.strip() for s in sentences if s.strip()])
        self.text_edit.setText(pretty_text)
        # GPT 요약 수행 (누적 텍스트 기준)
        self.current_summary = self.gpt_summarizer.summarize(self.current_text)
        self.update_summary()
        
    def update_summary(self):
        """요약 업데이트"""
        if not self.current_summary:
            return
            
        summary_text = "=== 요약 ===\n\n"
        
        if 'main_points' in self.current_summary:
            summary_text += "주요 포인트:\n"
            for point in self.current_summary['main_points']:
                summary_text += f"- {point}\n"
            summary_text += "\n"
            
        if 'keywords' in self.current_summary:
            summary_text += "키워드:\n"
            summary_text += ", ".join(self.current_summary['keywords'])
            summary_text += "\n\n"
            
        if 'summary' in self.current_summary:
            summary_text += "전체 요약:\n"
            summary_text += self.current_summary['summary']
            
        self.summary_edit.setText(summary_text)
        
    def save(self):
        """결과 저장"""
        if not self.current_text:
            return
            
        format_type = self.format_combo.currentText().lower()
        
        try:
            if format_type == 'docx':
                filepath = self.document_saver.save_docx(
                    self.current_text,
                    self.current_summary
                )
            else:
                filepath = self.document_saver.save_txt(
                    self.current_text,
                    self.current_summary
                )
                
            # 저장 성공 메시지
            self.text_edit.append(f"\n저장 완료: {filepath}")
            
        except Exception as e:
            self.text_edit.append(f"\n저장 실패: {str(e)}") 