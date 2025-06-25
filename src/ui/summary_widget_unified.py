from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QLabel, QFrame, QMessageBox,
                             QFileDialog, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime

class SummaryWidget(QWidget):
    """인터뷰 최종 요약 완성 위젯 - 통합 Cell 디자인"""
    
    back_to_interview = pyqtSignal()  # 인터뷰로 돌아가기 신호
    
    def __init__(self, template, screening_data, parent=None):
        super().__init__(parent)
        self.template = template
        self.screening_data = screening_data
        self.init_ui()
    
    def init_ui(self):
        """통합 Cell UI 초기화"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(0)  # 잉여 공간 최소화
        
        # 단일 통합 컨테이너 생성
        self.create_unified_container(main_layout)
    
    def create_unified_container(self, parent_layout):
        """모든 요소를 포함하는 단일 통합 컨테이너"""
        # 메인 컨테이너 프레임
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #e1e5e9;
                border-radius: 12px;
            }
        """)
        
        # 그리드 레이아웃으로 효율적 공간 활용
        grid_layout = QGridLayout(container)
        grid_layout.setContentsMargins(20, 20, 20, 20)
        grid_layout.setSpacing(12)
        
        # Row 0: 헤더 (전체 너비)
        self.create_compact_header(grid_layout, 0, 0, 1, 3)
        
        # Row 1: 스크립트 입력 (좌측 2/3) + 스크리닝 노트 (우측 1/3)
        self.create_script_section(grid_layout, 1, 0, 1, 2)
        self.create_screening_section(grid_layout, 1, 2, 1, 1)
        
        # Row 2: 최종 요약 (전체 너비)
        self.create_summary_section(grid_layout, 2, 0, 1, 3)
        
        # Row 3: 컨트롤 버튼 (전체 너비)
        self.create_compact_controls(grid_layout, 3, 0, 1, 3)
        
        parent_layout.addWidget(container)
        
        # 스크리닝 데이터 로드
        self.load_screening_data()
    
    def create_compact_header(self, grid_layout, row, col, rowspan, colspan):
        """컴팩트한 헤더"""
        header_frame = QFrame()
        header_frame.setFixedHeight(70)  # 높이 제한
        header_frame.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 8px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 8, 15, 8)
        header_layout.setSpacing(3)
        
        # 제목
        title_label = QLabel("📋 Interview Summary Completion")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
            }
        """)
        header_layout.addWidget(title_label)
        
        # 후보자 정보 (한 줄로 축약)
        info_text = f"👤 {self.template.get('candidate_name', 'Unknown')} | 💼 {self.template.get('position', 'N/A')} | 📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        candidate_info = QLabel(info_text)
        candidate_info.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 10px;
                background: transparent;
            }
        """)
        header_layout.addWidget(candidate_info)
        
        grid_layout.addWidget(header_frame, row, col, rowspan, colspan)
    
    def create_script_section(self, grid_layout, row, col, rowspan, colspan):
        """스크립트 입력 섹션"""
        script_frame = QFrame()
        script_frame.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
        """)
        
        script_layout = QVBoxLayout(script_frame)
        script_layout.setContentsMargins(12, 12, 12, 12)
        script_layout.setSpacing(8)
        
        # 섹션 제목과 분석 버튼을 한 줄에
        title_row = QHBoxLayout()
        
        title_label = QLabel("📝 Complete Interview Script")
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 12px;
                color: #495057;
            }
        """)
        title_row.addWidget(title_label)
        
        title_row.addStretch()
        
        analyze_btn = QPushButton("🔍 Analyze")
        analyze_btn.setFixedHeight(28)
        analyze_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        analyze_btn.clicked.connect(self.analyze_script)
        title_row.addWidget(analyze_btn)
        
        script_layout.addLayout(title_row)
        
        # 스크립트 입력창
        self.script_input = QTextEdit()
        self.script_input.setPlaceholderText(
            "Paste complete interview transcript here...\n\n"
            "Example:\n"
            "Interviewer: Tell me about your background.\n"
            "Candidate: I have 5 years of experience..."
        )
        self.script_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9px;
                background: white;
                line-height: 1.3;
            }
            QTextEdit:focus {
                border-color: #667eea;
            }
        """)
        script_layout.addWidget(self.script_input)
        
        grid_layout.addWidget(script_frame, row, col, rowspan, colspan)
    
    def create_screening_section(self, grid_layout, row, col, rowspan, colspan):
        """스크리닝 노트 섹션"""
        screening_frame = QFrame()
        screening_frame.setStyleSheet("""
            QFrame {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
            }
        """)
        
        screening_layout = QVBoxLayout(screening_frame)
        screening_layout.setContentsMargins(12, 12, 12, 12)
        screening_layout.setSpacing(8)
        
        # 섹션 제목
        title_label = QLabel("📊 Screening Notes")
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 12px;
                color: #856404;
            }
        """)
        screening_layout.addWidget(title_label)
        
        # 스크리닝 데이터 표시
        self.screening_display = QTextEdit()
        self.screening_display.setReadOnly(True)
        self.screening_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ffd60a;
                border-radius: 6px;
                padding: 8px;
                background: white;
                font-size: 8px;
                color: #495057;
                line-height: 1.3;
            }
        """)
        screening_layout.addWidget(self.screening_display)
        
        grid_layout.addWidget(screening_frame, row, col, rowspan, colspan)
    
    def create_summary_section(self, grid_layout, row, col, rowspan, colspan):
        """최종 요약 섹션"""
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background: #e7f3ff;
                border: 1px solid #b3d9ff;
                border-radius: 8px;
            }
        """)
        
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(12, 12, 12, 12)
        summary_layout.setSpacing(8)
        
        # 섹션 제목과 저장 버튼을 한 줄에
        title_row = QHBoxLayout()
        
        title_label = QLabel("🎯 Final Summary")
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 12px;
                color: #0c5460;
            }
        """)
        title_row.addWidget(title_label)
        
        title_row.addStretch()
        
        save_btn = QPushButton("💾 Save Report")
        save_btn.setFixedHeight(28)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #007bff;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background: #0056b3;
            }
        """)
        save_btn.clicked.connect(self.save_final_report)
        title_row.addWidget(save_btn)
        
        summary_layout.addLayout(title_row)
        
        # 최종 요약 결과
        self.final_summary = QTextEdit()
        self.final_summary.setMaximumHeight(100)  # 높이 제한으로 공간 절약
        self.final_summary.setPlaceholderText(
            "Final comprehensive summary will appear here after analyzing the complete interview script..."
        )
        self.final_summary.setStyleSheet("""
            QTextEdit {
                border: 1px solid #74c0fc;
                border-radius: 6px;
                padding: 8px;
                font-size: 9px;
                background: white;
                line-height: 1.3;
            }
        """)
        summary_layout.addWidget(self.final_summary)
        
        grid_layout.addWidget(summary_frame, row, col, rowspan, colspan)
    
    def create_compact_controls(self, grid_layout, row, col, rowspan, colspan):
        """컴팩트한 컨트롤 버튼"""
        control_frame = QFrame()
        control_frame.setFixedHeight(45)
        control_frame.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border-top: 1px solid #dee2e6;
                border-radius: 0px 0px 8px 8px;
            }
        """)
        
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(15, 8, 15, 8)
        
        # 뒤로가기 버튼
        back_btn = QPushButton("⬅️ Back to Interview")
        back_btn.setFixedHeight(28)
        back_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        back_btn.clicked.connect(self.back_to_interview.emit)
        control_layout.addWidget(back_btn)
        
        control_layout.addStretch()
        
        # 새 인터뷰 시작 버튼
        new_interview_btn = QPushButton("🆕 New Interview")
        new_interview_btn.setFixedHeight(28)
        new_interview_btn.setStyleSheet("""
            QPushButton {
                background: #17a2b8;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background: #138496;
            }
        """)
        new_interview_btn.clicked.connect(self.start_new_interview)
        control_layout.addWidget(new_interview_btn)
        
        grid_layout.addWidget(control_frame, row, col, rowspan, colspan)
    
    def load_screening_data(self):
        """스크리닝 데이터 로드 및 표시"""
        if self.screening_data:
            # 실제 스크리닝 데이터 표시
            display_text = f"=== Screening Notes ===\n\n"
            display_text += f"Candidate: {self.template.get('candidate_name', 'Unknown')}\n"
            display_text += f"Position: {self.template.get('position', 'N/A')}\n\n"
            
            # 카테고리별 내용 축약 표시
            for category, notes in self.screening_data.items():
                if notes:
                    display_text += f"• {category}:\n"
                    # 첫 2개 항목만 표시 (공간 절약)
                    for i, note in enumerate(notes[:2]):
                        display_text += f"  - {note[:80]}{'...' if len(note) > 80 else ''}\n"
                    if len(notes) > 2:
                        display_text += f"  (+{len(notes)-2} more items)\n"
                    display_text += "\n"
        else:
            # 플레이스홀더 텍스트
            display_text = (
                "=== Screening Notes ===\n\n"
                f"Candidate: {self.template.get('candidate_name', 'Unknown')}\n"
                f"Position: {self.template.get('position', 'N/A')}\n\n"
                "No screening data available.\n"
                "Please complete the interview first."
            )
        
        self.screening_display.setPlainText(display_text)
    
    def analyze_script(self):
        """인터뷰 스크립트 분석"""
        script_text = self.script_input.toPlainText().strip()
        
        if not script_text:
            QMessageBox.warning(self, "Warning", "Please paste the interview script first.")
            return
        
        # 분석 시작 표시
        self.final_summary.setPlainText("🔄 Analyzing interview script...\n\nPlease wait...")
        
        # 여기에 실제 분석 로직 구현 (기존 코드 참조)
        # 간단한 플레이스홀더로 대체
        import time
        QMessageBox.information(self, "Analysis", "Analysis feature will be implemented soon!")
        
        # 샘플 결과 표시
        sample_result = (
            "=== COMPREHENSIVE INTERVIEW ANALYSIS ===\n\n"
            "🎯 CANDIDATE PROFILE:\n"
            f"Name: {self.template.get('candidate_name', 'Unknown')}\n"
            f"Position: {self.template.get('position', 'N/A')}\n\n"
            "📊 ASSESSMENT SUMMARY:\n"
            "• Technical Skills: Strong background demonstrated\n"
            "• Communication: Clear and articulate responses\n"
            "• Cultural Fit: Good alignment with company values\n\n"
            "💡 RECOMMENDATION:\n"
            "Proceed to next round - positive assessment overall."
        )
        self.final_summary.setPlainText(sample_result)
    
    def save_final_report(self):
        """최종 리포트 저장"""
        content = self.final_summary.toPlainText()
        if not content or "will appear here" in content:
            QMessageBox.warning(self, "Warning", "No analysis results to save.")
            return
        
        # 파일 저장 다이얼로그
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Final Report",
            f"Final_Interview_Report_{self.template.get('candidate_name', 'Unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                QMessageBox.information(self, "Success", f"Report saved successfully!\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save report:\n{str(e)}")
    
    def start_new_interview(self):
        """새 인터뷰 시작"""
        reply = QMessageBox.question(
            self, "New Interview", 
            "Start a new interview? Current data will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 메인 윈도우로 신호 전송 (구현 필요)
            self.back_to_interview.emit() 