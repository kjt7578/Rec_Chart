from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QLabel, QSplitter, QFrame, QMessageBox,
                             QScrollArea, QGroupBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime

class SummaryWidget(QWidget):
    """인터뷰 최종 요약 완성 위젯"""
    
    back_to_interview = pyqtSignal()  # 인터뷰로 돌아가기 신호
    
    def __init__(self, template, screening_data, parent=None):
        super().__init__(parent)
        self.template = template
        self.screening_data = screening_data  # 인터뷰 위젯에서 넘어온 스크리닝 데이터
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 상단 제목 영역
        self.create_header(layout)
        
        # 메인 컨텐츠 영역 (좌우 분할)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)
        
        # 좌측: 인터뷰 스크립트 입력 영역
        self.create_script_input_panel(main_splitter)
        
        # 우측: 기존 스크리닝 데이터 + 최종 요약 영역
        self.create_summary_panel(main_splitter)
        
        # 설정 비율 (좌측 60%, 우측 40%)
        main_splitter.setSizes([600, 400])
        
        # 하단 컨트롤 버튼
        self.create_bottom_controls(layout)
    
    def create_header(self, parent_layout):
        """상단 헤더 생성"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 8px;
                padding: 15px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        # 제목
        title_label = QLabel("📋 Interview Summary Completion")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: bold;
                background: transparent;
            }
        """)
        header_layout.addWidget(title_label)
        
        # 후보자 정보
        candidate_info = QLabel(f"Candidate: {self.template.get('candidate_name', 'Unknown')} | "
                               f"Position: {self.template.get('position', 'N/A')} | "
                               f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        candidate_info.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 12px;
                background: transparent;
            }
        """)
        header_layout.addWidget(candidate_info)
        
        parent_layout.addWidget(header_frame)
    
    def create_script_input_panel(self, parent_splitter):
        """좌측: 인터뷰 스크립트 입력 패널"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # 그룹박스로 영역 구분
        script_group = QGroupBox("📝 Complete Interview Script")
        script_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        script_layout = QVBoxLayout(script_group)
        
        # 안내 텍스트
        instruction_label = QLabel(
            "Please paste the complete interview transcript below.\n"
            "This will be combined with the screening notes to generate the final summary."
        )
        instruction_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
                padding: 5px;
                background: #f8f9fa;
                border-radius: 4px;
            }
        """)
        script_layout.addWidget(instruction_label)
        
        # 인터뷰 스크립트 입력창
        self.script_input = QTextEdit()
        self.script_input.setPlaceholderText(
            "Paste the complete interview transcript here...\n\n"
            "Example:\n"
            "Interviewer: Tell me about your background.\n"
            "Candidate: I have 5 years of experience in...\n"
            "Interviewer: What are your strengths?\n"
            "Candidate: My main strengths are..."
        )
        self.script_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border-color: #667eea;
            }
        """)
        script_layout.addWidget(self.script_input)
        
        # 스크립트 분석 버튼
        analyze_btn = QPushButton("🔍 Analyze Script")
        analyze_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #218838;
            }
            QPushButton:pressed {
                background: #1e7e34;
            }
        """)
        analyze_btn.clicked.connect(self.analyze_script)  # (구현예정)
        script_layout.addWidget(analyze_btn)
        
        left_layout.addWidget(script_group)
        parent_splitter.addWidget(left_widget)
    
    def create_summary_panel(self, parent_splitter):
        """우측: 기존 스크리닝 데이터 + 최종 요약 패널"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # 기존 스크리닝 데이터 영역
        screening_group = QGroupBox("📊 Screening Notes")
        screening_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        screening_layout = QVBoxLayout(screening_group)
        
        # 스크리닝 데이터 표시
        self.screening_display = QTextEdit()
        self.screening_display.setReadOnly(True)
        self.screening_display.setMaximumHeight(150)
        self.screening_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background: #f8f9fa;
                font-size: 10px;
            }
        """)
        screening_layout.addWidget(self.screening_display)
        
        right_layout.addWidget(screening_group)
        
        # 최종 요약 영역
        final_group = QGroupBox("🎯 Final Summary")
        final_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        final_layout = QVBoxLayout(final_group)
        
        # 최종 요약 결과
        self.final_summary = QTextEdit()
        self.final_summary.setPlaceholderText(
            "The final comprehensive summary will appear here after analyzing the complete interview script.\n\n"
            "(Implementation pending: AI-powered analysis combining screening notes with full transcript)"
        )
        self.final_summary.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                padding: 10px;
                font-size: 11px;
                line-height: 1.5;
            }
        """)
        final_layout.addWidget(self.final_summary)
        
        # 최종 저장 버튼
        save_final_btn = QPushButton("💾 Save Final Report")
        save_final_btn.setStyleSheet("""
            QPushButton {
                background: #007bff;
                color: white;
                border: none;
                padding: 10px 25px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #0056b3;
            }
            QPushButton:pressed {
                background: #004085;
            }
        """)
        save_final_btn.clicked.connect(self.save_final_report)  # (구현예정)
        final_layout.addWidget(save_final_btn)
        
        right_layout.addWidget(final_group)
        parent_splitter.addWidget(right_widget)
    
    def create_bottom_controls(self, parent_layout):
        """하단 컨트롤 버튼"""
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                border-top: 1px solid #ddd;
                padding: 10px;
                background: #f8f9fa;
            }
        """)
        control_layout = QHBoxLayout(control_frame)
        
        # 뒤로가기 버튼
        back_btn = QPushButton("⬅️ Back to Interview")
        back_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
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
        new_interview_btn.setStyleSheet("""
            QPushButton {
                background: #17a2b8;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #138496;
            }
        """)
        new_interview_btn.clicked.connect(self.start_new_interview)  # (구현예정)
        control_layout.addWidget(new_interview_btn)
        
        parent_layout.addWidget(control_frame)
        
        # 스크리닝 데이터 로드
        self.load_screening_data()
    
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
            # 분석 시작 표시
            self.final_summary.setPlainText("🔄 Enhanced AI Analysis in Progress...\n\nStep 1/4: Extracting candidate profile...")
            self.final_summary.repaint()
            
            # 메인 윈도우에서 GPT Summarizer 가져오기
            main_window = self.find_main_window()
            if not main_window or not hasattr(main_window, 'gpt_summarizer'):
                self.final_summary.setPlainText("❌ GPT Analyzer not found. Please check system configuration.")
                return
            
            gpt_summarizer = main_window.gpt_summarizer
            
            # Enhanced Analyzer를 통한 전체 분석 실행
            print("[SummaryWidget] Enhanced Analysis 시작")
            analysis_result = gpt_summarizer.analyze_complete_interview(
                interview_script=script_text,
                template=self.template,
                screening_data=self.screening_data
            )
            
            if analysis_result.get('error'):
                # 오류 발생시 폴백 분석 표시
                self.display_fallback_analysis(analysis_result)
            else:
                # 성공시 전체 분석 결과 표시
                self.display_comprehensive_analysis(analysis_result)
                
                # 성공 메시지
                QMessageBox.information(
                    self, 
                    "Analysis Complete", 
                    f"✅ Enhanced AI analysis completed successfully!\n\n"
                    f"Candidate: {analysis_result.get('candidate_profile', {}).get('candidate_name', 'Unknown')}\n"
                    f"Recommendation: {analysis_result.get('comprehensive_analysis', {}).get('recommendation', {}).get('decision', 'Not specified')}"
                )
                
        except Exception as e:
            print(f"[SummaryWidget] Analysis error: {e}")
            self.final_summary.setPlainText(f"❌ Analysis failed: {str(e)}\n\nTrying basic analysis...")
            # 기본 분석 시도
            self.basic_script_analysis(script_text)
    
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
        """최종 리포트 저장 - Enhanced 분석 결과 포함"""
        try:
            final_content = self.final_summary.toPlainText().strip()
            
            if not final_content or "Implementation pending" in final_content:
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
    
    def start_new_interview(self):
        """새 인터뷰 시작 (구현예정)"""
        # (구현예정): 템플릿 에디터로 돌아가서 새 인터뷰 시작
        QMessageBox.information(
            self,
            "New Interview",
            "New interview functionality will be implemented.\n"
            "(Implementation pending: Reset to template editor)"
        ) 