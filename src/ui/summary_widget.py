from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QLabel, QSplitter, QFrame, QMessageBox,
                             QScrollArea, QGroupBox, QFileDialog, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime

class SummaryWidget(QWidget):
    """인터뷰 최종 요약 완성 위젯 - 통합 Cell 디자인"""
    
    back_to_interview = pyqtSignal()  # 인터뷰로 돌아가기 신호
    
    def __init__(self, template, screening_data, parent=None):
        super().__init__(parent)
        self.template = template
        self.screening_data = screening_data  # 인터뷰 위젯에서 넘어온 스크리닝 데이터
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
                padding: 0px;
            }
        """)
        
        # 그리드 레이아웃으로 효율적 공간 활용
        grid_layout = QGridLayout(container)
        grid_layout.setContentsMargins(20, 20, 20, 20)
        grid_layout.setSpacing(15)
        
        # Row 0: 헤더 (전체 너비)
        self.create_compact_header(grid_layout, 0, 0, 1, 3)
        
        # Row 1: 스크립트 입력 (좌측 2/3)
        self.create_script_section(grid_layout, 1, 0, 1, 2)
        
        # Row 1: 스크리닝 노트 (우측 1/3)
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
        header_frame.setFixedHeight(80)  # 높이 제한
        header_frame.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 8px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        header_layout.setSpacing(5)
        
        # 제목
        title_label = QLabel("📋 Interview Summary Completion")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
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
                font-size: 11px;
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
        script_layout.setContentsMargins(10, 10, 10, 10)
        script_layout.setSpacing(8)
        
        # 섹션 제목
        title_label = QLabel("📝 Complete Interview Script")
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 13px;
                color: #495057;
                padding: 2px;
            }
        """)
        script_layout.addWidget(title_label)
        
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
                font-size: 10px;
                background: white;
            }
            QTextEdit:focus {
                border-color: #667eea;
            }
        """)
        script_layout.addWidget(self.script_input)
        
        # 분석 버튼
        analyze_btn = QPushButton("🔍 Analyze Script")
        analyze_btn.setFixedHeight(32)
        analyze_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                border: none;
                padding: 6px 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        analyze_btn.clicked.connect(self.analyze_script)
        script_layout.addWidget(analyze_btn)
        
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
        screening_layout.setContentsMargins(10, 10, 10, 10)
        screening_layout.setSpacing(8)
        
        # 섹션 제목
        title_label = QLabel("📊 Screening Notes")
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 13px;
                color: #856404;
                padding: 2px;
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
                font-size: 9px;
                color: #495057;
            }
        """)
        screening_layout.addWidget(self.screening_display)
        
        grid_layout.addWidget(screening_frame, row, col, rowspan, colspan)
    
    def create_summary_section(self, grid_layout, row, col, rowspan, colspan):
        """최종 요약 섹션 - 2열 다중 박스 구조"""
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background: #e7f3ff;
                border: 1px solid #b3d9ff;
                border-radius: 8px;
            }
        """)
        
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(10, 10, 10, 10)
        summary_layout.setSpacing(6)
        
        # 섹션 제목과 저장 버튼을 한 줄에
        title_row = QHBoxLayout()
        
        title_label = QLabel("🎯 Final Summary")
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 13px;
                color: #0c5460;
                padding: 2px;
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
                border-radius: 5px;
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
        
        # 2열 다중 박스 구조 - 명확한 분할
        boxes_container = QHBoxLayout()
        boxes_container.setSpacing(15)  # 좌우 간격을 더 넓게
        
        # 좌측 열 (4개 박스) - 50% 너비
        left_column = QVBoxLayout()
        left_column.setSpacing(8)
        
        # 우측 열 (4개 박스) - 50% 너비  
        right_column = QVBoxLayout()
        right_column.setSpacing(8)
        
        # 요약 박스들 생성
        self.summary_boxes = {}
        
        # 좌측 박스들
        left_categories = [
            ("👤 Candidate Profile", "candidate_profile"),
            ("💼 Technical Skills", "technical_skills"), 
            ("🗣️ Communication", "communication"),
            ("🎯 Experience", "experience")
        ]
        
        for title, key in left_categories:
            box = self.create_summary_box(title, key)
            self.summary_boxes[key] = box
            left_column.addWidget(box)
        
        # 우측 박스들
        right_categories = [
            ("🤝 Cultural Fit", "cultural_fit"),
            ("⚡ Strengths", "strengths"),
            ("⚠️ Concerns", "concerns"), 
            ("📋 Recommendation", "recommendation")
        ]
        
        for title, key in right_categories:
            box = self.create_summary_box(title, key)
            self.summary_boxes[key] = box
            right_column.addWidget(box)
        
        boxes_container.addLayout(left_column)
        boxes_container.addLayout(right_column)
        
        summary_layout.addLayout(boxes_container)
        
        grid_layout.addWidget(summary_frame, row, col, rowspan, colspan)
    
    def create_summary_box(self, title, key):
        """개별 요약 박스 생성"""
        box_frame = QFrame()
        box_frame.setFixedHeight(120)  # 높이를 더 크게 설정
        box_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #74c0fc;
                border-radius: 8px;
                margin: 3px;
            }
        """)
        
        box_layout = QVBoxLayout(box_frame)
        box_layout.setContentsMargins(6, 4, 6, 4)
        box_layout.setSpacing(2)
        
        # 박스 제목
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 9px;
                color: #0c5460;
                background: transparent;
                padding: 1px;
            }
        """)
        box_layout.addWidget(title_label)
        
        # 내용 텍스트
        content_text = QTextEdit()
        content_text.setReadOnly(True)
        content_text.setPlaceholderText("Analysis result will appear here...")
        content_text.setStyleSheet("""
            QTextEdit {
                border: none;
                background: transparent;
                font-size: 8px;
                color: #495057;
                padding: 2px;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #f1f3f4;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                border-radius: 4px;
                min-height: 20px;
            }
        """)
        box_layout.addWidget(content_text)
        
        return box_frame
    
    def create_compact_controls(self, grid_layout, row, col, rowspan, colspan):
        """컴팩트한 컨트롤 버튼"""
        control_frame = QFrame()
        control_frame.setFixedHeight(50)
        control_frame.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border-top: 1px solid #dee2e6;
                border-radius: 0px 0px 8px 8px;
            }
        """)
        
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(15, 10, 15, 10)
        
        # 뒤로가기 버튼
        back_btn = QPushButton("⬅️ Back to Interview")
        back_btn.setFixedHeight(30)
        back_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
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
        new_interview_btn.setFixedHeight(30)
        new_interview_btn.setStyleSheet("""
            QPushButton {
                background: #17a2b8;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
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
        # (구현예정): 실제로는 screening_data에서 카테고리별 내용을 가져와서 표시
        placeholder_text = (
            "=== Screening Notes Summary ===\n\n"
            f"Candidate: {self.template.get('candidate_name', 'Unknown')}\n"
            f"Position: {self.template.get('position', 'N/A')}\n\n"
            "Technical Skills: (Implementation pending)\n"
            "Communication: (Implementation pending)\n"
            "Experience: (Implementation pending)\n"
            "Cultural Fit: (Implementation pending)\n\n"
            "Overall Assessment: (Implementation pending)"
        )
        self.screening_display.setPlainText(placeholder_text)
    
    def analyze_script(self):
        """인터뷰 스크립트 분석 - Enhanced Analyzer 사용"""
        script_text = self.script_input.toPlainText().strip()
        
        if not script_text:
            QMessageBox.warning(self, "Warning", "Please paste the interview script first.")
            return
        
        try:
            # 분석 시작 표시 - 모든 박스를 분석 중 상태로 설정
            self.set_all_boxes_analyzing()
            
            # 임시로 샘플 결과 표시 (실제 분석 로직은 추후 구현)
            self.display_sample_analysis()
            
            # 성공 메시지
            QMessageBox.information(
                self, 
                "Analysis Complete", 
                "✅ Analysis completed successfully!\n\nSample results displayed."
            )
                
        except Exception as e:
            print(f"[SummaryWidget] Analysis error: {e}")
            self.set_all_boxes_error(str(e))
    
    def set_all_boxes_analyzing(self):
        """모든 요약 박스를 분석 중 상태로 설정"""
        for key, box_frame in self.summary_boxes.items():
            content_text = box_frame.findChild(QTextEdit)
            if content_text:
                content_text.setPlainText("🔄 Analyzing...")
    
    def set_all_boxes_error(self, error_msg):
        """모든 요약 박스를 오류 상태로 설정"""
        for key, box_frame in self.summary_boxes.items():
            content_text = box_frame.findChild(QTextEdit)
            if content_text:
                content_text.setPlainText(f"❌ Error: {error_msg}")
    
    def display_sample_analysis(self):
        """샘플 분석 결과 표시"""
        sample_data = {
            "candidate_profile": "John Smith\nSenior Software Engineer\n5+ years experience\nPython, React, AWS",
            "technical_skills": "• Strong Python/Django background\n• Experience with React frontend\n• AWS cloud architecture\n• Agile development practices",
            "communication": "• Clear and articulate responses\n• Good active listening skills\n• Explains technical concepts well\n• Confident presentation style",
            "experience": "• 5 years software development\n• Led team of 3 developers\n• Managed full-stack projects\n• Startup to enterprise experience",
            "cultural_fit": "• Collaborative team player\n• Values work-life balance\n• Growth mindset\n• Aligns with company values",
            "strengths": "• Deep technical expertise\n• Leadership potential\n• Problem-solving skills\n• Adaptable to new technologies",
            "concerns": "• Limited experience in our domain\n• May need mentoring on processes\n• Salary expectations above budget",
            "recommendation": "🟢 STRONG HIRE\n\nExcellent technical candidate with leadership potential. Recommend proceeding to final round."
        }
        
        for key, content in sample_data.items():
            if key in self.summary_boxes:
                box_frame = self.summary_boxes[key]
                content_text = box_frame.findChild(QTextEdit)
                if content_text:
                    content_text.setPlainText(content)
    
    def display_comprehensive_analysis(self, analysis_result):
        """종합 분석 결과 표시"""
        try:
            candidate_profile = analysis_result.get('candidate_profile', {})
            comprehensive_analysis = analysis_result.get('comprehensive_analysis', {})
            improved_screening = analysis_result.get('improved_screening', {})
            
            # 결과 텍스트 구성
            output_parts = []
            
            # 1. 헤더
            output_parts.append("🎯 COMPREHENSIVE INTERVIEW ASSESSMENT")
            output_parts.append("=" * 70)
            output_parts.append("")
            
            # 2. 후보자 기본 정보
            output_parts.append("👤 CANDIDATE PROFILE")
            output_parts.append("-" * 50)
            output_parts.append(f"Name: {candidate_profile.get('candidate_name', 'Not specified')}")
            output_parts.append(f"Current Company: {candidate_profile.get('current_company', 'Not specified')}")
            output_parts.append(f"Current Position: {candidate_profile.get('current_position', 'Not specified')}")
            output_parts.append(f"Experience: {candidate_profile.get('experience_years', 'Not specified')}")
            output_parts.append(f"Target Position: {self.template.get('position', 'Not specified')}")
            output_parts.append(f"Salary Expectation: {candidate_profile.get('salary_expectation', 'Not specified')}")
            output_parts.append(f"Location Preference: {candidate_profile.get('location_preference', 'Not specified')}")
            output_parts.append("")
            
            # 3. 요약 평가
            if comprehensive_analysis.get('executive_summary'):
                output_parts.append("📋 EXECUTIVE SUMMARY")
                output_parts.append("-" * 50)
                output_parts.append(comprehensive_analysis['executive_summary'])
                output_parts.append("")
            
            # 4. 상세 분석 (주요 영역만)
            if comprehensive_analysis.get('detailed_analysis'):
                output_parts.append("📊 DETAILED ASSESSMENT")
                output_parts.append("-" * 50)
                for area, analysis in list(comprehensive_analysis['detailed_analysis'].items())[:4]:  # 상위 4개만
                    output_parts.append(f"▼ {area.replace('_', ' ').title()}")
                    output_parts.append(f"   Rating: {analysis.get('rating', 'N/A')}/5")
                    output_parts.append(f"   {analysis.get('assessment', 'No assessment provided')}")
                    output_parts.append("")
            
            # 5. 주요 강점
            if comprehensive_analysis.get('strengths'):
                output_parts.append("✅ KEY STRENGTHS")
                output_parts.append("-" * 50)
                for i, strength in enumerate(comprehensive_analysis['strengths'][:5], 1):
                    output_parts.append(f"{i}. {strength}")
                output_parts.append("")
            
            # 6. 우려사항
            if comprehensive_analysis.get('concerns'):
                output_parts.append("⚠️ AREAS OF CONCERN")
                output_parts.append("-" * 50)
                for i, concern in enumerate(comprehensive_analysis['concerns'][:3], 1):
                    output_parts.append(f"{i}. {concern}")
                output_parts.append("")
            
            # 7. 문화 적합성
            if comprehensive_analysis.get('cultural_fit'):
                cultural = comprehensive_analysis['cultural_fit']
                output_parts.append("🤝 CULTURAL FIT")
                output_parts.append("-" * 50)
                output_parts.append(f"Rating: {cultural.get('rating', 'N/A')}/5")
                output_parts.append(f"Assessment: {cultural.get('reasoning', 'No assessment provided')}")
                output_parts.append("")
            
            # 8. 최종 추천
            if comprehensive_analysis.get('recommendation'):
                rec = comprehensive_analysis['recommendation']
                output_parts.append("🎯 FINAL RECOMMENDATION")
                output_parts.append("-" * 50)
                output_parts.append(f"Decision: {rec.get('decision', 'Not specified')}")
                output_parts.append(f"Reasoning: {rec.get('reasoning', 'Not specified')}")
                output_parts.append(f"Next Steps: {rec.get('next_steps', 'Not specified')}")
                output_parts.append("")
            
            # 9. 스크리닝 노트 개선사항 (요약)
            if improved_screening.get('overall_improvement'):
                improvement = improved_screening['overall_improvement']
                output_parts.append("📈 SCREENING NOTES IMPROVEMENT")
                output_parts.append("-" * 50)
                output_parts.append(f"Completeness Score: {improvement.get('completeness_score', 'N/A')}/10")
                if improvement.get('key_improvements'):
                    output_parts.append("Key Improvements:")
                    for imp in improvement['key_improvements'][:3]:
                        output_parts.append(f"• {imp}")
                output_parts.append("")
            
            # 10. 푸터
            output_parts.append("=" * 70)
            output_parts.append(f"Analysis completed at {analysis_result.get('analysis_timestamp', 'Unknown time')}")
            output_parts.append("Generated by Rec Chart OCR - Enhanced Interview Analysis System")
            
            # 결과 표시
            self.final_summary.setPlainText('\n'.join(output_parts))
            
        except Exception as e:
            self.final_summary.setPlainText(f"❌ Error displaying analysis results: {str(e)}")
    
    def display_fallback_analysis(self, analysis_result):
        """폴백 분석 결과 표시"""
        fallback = analysis_result.get('fallback_analysis', {})
        
        output_parts = []
        output_parts.append("⚠️ BASIC ANALYSIS RESULTS")
        output_parts.append("(Enhanced analysis unavailable)")
        output_parts.append("=" * 70)
        output_parts.append("")
        output_parts.append(f"Error: {analysis_result.get('error', 'Unknown error')}")
        output_parts.append("")
        
        if fallback.get('summary'):
            output_parts.append("📝 BASIC SUMMARY:")
            output_parts.append(fallback['summary'])
            output_parts.append("")
        
        if fallback.get('screening_summary'):
            output_parts.append("📋 EXISTING SCREENING NOTES:")
            output_parts.append(fallback['screening_summary'])
            output_parts.append("")
        
        output_parts.append("💡 RECOMMENDATION:")
        output_parts.append("Please check Enhanced Analyzer configuration or OpenAI API key.")
        
        self.final_summary.setPlainText('\n'.join(output_parts))
    
    def basic_script_analysis(self, script_text):
        """기본 스크립트 분석 (Enhanced Analyzer 실패시)"""
        try:
            main_window = self.find_main_window()
            if main_window and hasattr(main_window, 'gpt_summarizer'):
                # 빠른 프로필 추출 시도
                profile = main_window.gpt_summarizer.quick_profile_extraction(script_text)
                
                output_parts = []
                output_parts.append("🔍 BASIC ANALYSIS RESULTS")
                output_parts.append("=" * 70)
                output_parts.append("")
                output_parts.append(f"Extracted Name: {profile.get('candidate_name', 'Not found')}")
                output_parts.append(f"Current Company: {profile.get('current_company', 'Not found')}")
                output_parts.append(f"Salary Information: {profile.get('salary_expectation', 'Not found')}")
                output_parts.append("")
                output_parts.append("📝 SCRIPT OVERVIEW:")
                output_parts.append(f"Total Length: {len(script_text)} characters")
                output_parts.append(f"Estimated Words: {len(script_text.split())} words")
                output_parts.append("")
                output_parts.append("⚠️ LIMITATIONS:")
                output_parts.append("Only basic analysis available. Enhanced Analyzer required for comprehensive assessment.")
                
                self.final_summary.setPlainText('\n'.join(output_parts))
            else:
                self.final_summary.setPlainText("❌ GPT analyzer not available.")
                
        except Exception as e:
            self.final_summary.setPlainText(f"❌ Basic analysis failed: {str(e)}")
    
    def find_main_window(self):
        """메인 윈도우 찾기"""
        current_widget = self
        level = 0
        
        while current_widget and level < 10:
            if hasattr(current_widget, 'gpt_summarizer'):
                return current_widget
            current_widget = current_widget.parent()
            level += 1
        
        return None
    
    def save_final_report(self):
        """최종 리포트 저장 - 다중 박스 결과 포함"""
        try:
            # 모든 박스의 내용을 수집
            final_content = self.collect_all_box_content()
            
            if not final_content or "will appear here" in final_content:
                QMessageBox.warning(
                    self, 
                    "No Analysis Available", 
                    "Please run the script analysis first to generate a comprehensive report."
                )
                return
            
            # 파일명 생성 (영어로)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            candidate_name = "Unknown_Candidate"
            
            # 후보자 이름 추출 시도
            if "Name: " in final_content:
                for line in final_content.split('\n'):
                    if line.startswith("Name: ") and "Not specified" not in line:
                        candidate_name = line.replace("Name: ", "").strip().replace(" ", "_")
                        break
            
            filename = f"Enhanced_Interview_Report_{candidate_name}_{timestamp}.txt"
            
            # 파일 저장
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Enhanced Interview Report",
                filename,
                "Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                # 리포트 헤더 추가
                report_header = f"""
============================================================
ENHANCED INTERVIEW ASSESSMENT REPORT
============================================================
Generated by: Rec Chart OCR - Enhanced Analysis System
Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Candidate: {candidate_name.replace('_', ' ')}
Position: {self.template.get('position', 'Not specified')}
============================================================

"""
                
                # 전체 내용 결합
                full_report = report_header + final_content
                
                # 인터뷰 스크립트도 추가 (옵션)
                script_content = self.script_input.toPlainText().strip()
                if script_content:
                    full_report += f"""

============================================================
FULL INTERVIEW TRANSCRIPT
============================================================

{script_content}

============================================================
END OF REPORT
============================================================
"""
                
                # 파일 저장 (영어 저장 방식)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(full_report)
                
                QMessageBox.information(
                    self, 
                    "Report Saved Successfully", 
                    f"Enhanced interview report saved successfully!\n\n"
                    f"File: {file_path}\n"
                    f"Size: {len(full_report)} characters\n"
                    f"Analysis Type: Enhanced AI Assessment\n"
                    f"Includes: Profile + Analysis + Full Transcript"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save the report:\n{str(e)}\n\n"
                f"Please check file permissions and try again."
            )
    
    def collect_all_box_content(self):
        """모든 요약 박스의 내용을 수집하여 하나의 텍스트로 반환"""
        report_parts = []
        report_parts.append("🎯 COMPREHENSIVE INTERVIEW ASSESSMENT")
        report_parts.append("=" * 70)
        report_parts.append("")
        
        # 각 박스의 내용을 순서대로 수집
        box_order = [
            ("candidate_profile", "👤 CANDIDATE PROFILE"),
            ("technical_skills", "💼 TECHNICAL SKILLS"),
            ("communication", "🗣️ COMMUNICATION"), 
            ("experience", "🎯 EXPERIENCE"),
            ("cultural_fit", "🤝 CULTURAL FIT"),
            ("strengths", "⚡ STRENGTHS"),
            ("concerns", "⚠️ CONCERNS"),
            ("recommendation", "📋 RECOMMENDATION")
        ]
        
        for key, title in box_order:
            if key in self.summary_boxes:
                box_frame = self.summary_boxes[key]
                content_text = box_frame.findChild(QTextEdit)
                if content_text:
                    content = content_text.toPlainText().strip()
                    if content and content != "Analysis result will appear here...":
                        report_parts.append(title)
                        report_parts.append("-" * 50)
                        report_parts.append(content)
                        report_parts.append("")
        
        return '\n'.join(report_parts)
    
    def start_new_interview(self):
        """새 인터뷰 시작 (구현예정)"""
        # (구현예정): 템플릿 에디터로 돌아가서 새 인터뷰 시작
        QMessageBox.information(
            self,
            "New Interview",
            "New interview functionality will be implemented.\n"
            "(Implementation pending: Reset to template editor)"
        ) 