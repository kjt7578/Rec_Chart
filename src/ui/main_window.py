from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QComboBox,
    QSpinBox, QCheckBox, QSystemTrayIcon, QMenu, QSplitter,
    QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QAction, QPixmap
from src.ui.template_editor import TemplateEditor
from src.ui.interview_widget import InterviewWidget
from src.ui.capture_widget import CaptureWidget
from src.ui.summary_widget import SummaryWidget

class MainWindow(QMainWindow):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.current_template = None
        self.interview_mode = False
        
        # GPT 요약기 초기화
        from src.gpt.summarizer import GPTSummarizer
        self.gpt_summarizer = GPTSummarizer(settings)
        
        # 화면 캡처 관련 초기화
        from src.core.screen_capture import ScreenCapture
        from src.core.ocr_engine import OCREngine
        self.screen_capture = ScreenCapture()
        self.ocr_engine = OCREngine(settings)
        self.capture_region = None
        
        self.init_ui()
        self.setup_tray()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("🎯 Rec Chart OCR - 실시간 인터뷰 스크리닝 시스템")
        self.setMinimumSize(1000, 800)
        self.resize(1400, 900)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 제목 및 모드 표시 (템플릿 모드에서만)
        self.header_widget = self.create_header()
        main_layout.addWidget(self.header_widget)
        
        # 스택 위젯 (템플릿 설정 모드 / 인터뷰 모드 전환)
        self.stacked_widget = QStackedWidget()
        
        # 1. 템플릿 설정 페이지
        self.template_editor = TemplateEditor()
        self.template_editor.template_changed.connect(self.start_interview_mode)
        self.stacked_widget.addWidget(self.template_editor)
        
        # 2. 인터뷰 페이지 (초기에는 None, 템플릿 설정 후 생성)
        self.interview_widget = None
        
        # 3. 요약 완성 페이지 (초기에는 None, 인터뷰 후 생성)
        self.summary_widget = None
        
        main_layout.addWidget(self.stacked_widget)
        
        # 하단 모드 전환 버튼
        self.control_widget = self.create_mode_controls()
        main_layout.addWidget(self.control_widget)
        
    def create_header(self):
        """헤더 섹션 생성 - 위젯으로 반환"""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)
        
        # 메인 제목
        title_label = QLabel("🎯 Rec Chart OCR - 실시간 인터뷰 스크리닝 시스템")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background-color: #ecf0f1;
                border-radius: 8px;
                margin-bottom: 5px;
            }
        """)
        header_layout.addWidget(title_label)
        
        # 현재 모드 표시
        self.mode_label = QLabel("📋 현재 모드: 템플릿 설정")
        self.mode_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #7f8c8d;
                padding: 8px 15px;
                background-color: #f8f9fa;
                border-radius: 4px;
            }
        """)
        header_layout.addWidget(self.mode_label)
        
        return header_widget
        
    def create_mode_controls(self):
        """모드 제어 버튼들 - 위젯으로 반환"""
        control_widget = QWidget()
        control_layout = QHBoxLayout(control_widget)
        control_layout.setContentsMargins(0, 10, 0, 0)
        control_layout.setSpacing(10)
        
        # 공통 버튼 스타일
        button_style = """
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                padding: 10px 16px;
                border: none;
                border-radius: 6px;
                min-width: 130px;
                min-height: 40px;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        
        # 템플릿 편집 모드로 돌아가기
        self.edit_template_btn = QPushButton("📝 템플릿 편집")
        self.edit_template_btn.clicked.connect(self.switch_to_template_mode)
        self.edit_template_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #95a5a6;
                color: white;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        control_layout.addWidget(self.edit_template_btn)
        
        # 캡처 범위 선택 버튼
        self.select_region_btn = QPushButton("📐 캡처 범위 선택")
        self.select_region_btn.clicked.connect(self.select_capture_region)
        self.select_region_btn.setEnabled(False)
        self.select_region_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #9C27B0;
                color: white;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        control_layout.addWidget(self.select_region_btn)
        
        # 전체 화면 캡처 버튼
        self.fullscreen_capture_btn = QPushButton("🖥️ 전체 화면")
        self.fullscreen_capture_btn.clicked.connect(self.set_fullscreen_capture)
        self.fullscreen_capture_btn.setEnabled(False)
        self.fullscreen_capture_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #607D8B;
                color: white;
            }
            QPushButton:hover {
                background-color: #455A64;
            }
        """)
        control_layout.addWidget(self.fullscreen_capture_btn)

        # OCR 캡처 시작/중지 (인터뷰 모드에서만 활성화)
        self.start_capture_btn = QPushButton("🎤 화면 캡처 시작")
        self.start_capture_btn.clicked.connect(self.start_ocr_capture)
        self.start_capture_btn.setEnabled(False)
        self.start_capture_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #27ae60;
                color: white;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        control_layout.addWidget(self.start_capture_btn)
        
        self.stop_capture_btn = QPushButton("⏹️ 캡처 중지")
        self.stop_capture_btn.clicked.connect(self.stop_ocr_capture)
        self.stop_capture_btn.setEnabled(False)
        self.stop_capture_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        control_layout.addWidget(self.stop_capture_btn)
        
        control_layout.addStretch()
        
        # 저장 버튼

        
        return control_widget
        
    def start_interview_mode(self, template):
        """인터뷰 모드 시작"""
        self.current_template = template
        self.interview_mode = True
        
        # 인터뷰 위젯 생성 (기존 것이 있으면 교체)
        if self.interview_widget:
            self.stacked_widget.removeWidget(self.interview_widget)
            self.interview_widget.deleteLater()
            
        self.interview_widget = InterviewWidget(template, self.settings, parent=self)
        self.stacked_widget.addWidget(self.interview_widget)
        
        # 인터뷰 모드로 전환
        self.stacked_widget.setCurrentWidget(self.interview_widget)
        
        # 헤더 숨기기 (인터뷰 모드에서는 불필요)
        self.header_widget.hide()
        
        # 버튼 상태 업데이트
        self.select_region_btn.setEnabled(True)
        self.fullscreen_capture_btn.setEnabled(True)
        self.start_capture_btn.setEnabled(True)
        
        print(f"[MainWindow] 인터뷰 모드 시작 - 카테고리: {template['screening_categories']}")
        
    def select_capture_region(self):
        """캡처 범위 선택"""
        if not self.interview_mode:
            print("[MainWindow] 인터뷰 모드가 아닙니다.")
            return
            
        try:
            from src.core.screen_capture import ScreenCapture
            screen_capture = ScreenCapture()
            
            print("[MainWindow] 캡처 범위 선택 시작...")
            region = screen_capture.select_region()
            
            if region:
                # CaptureWidget이 있으면 범위 설정
                if hasattr(self, 'capture_widget'):
                    self.capture_widget.capture_region = region
                    x, y, w, h = region
                    print(f"[MainWindow] 캡처 범위 설정됨: {w}x{h} at ({x}, {y})")
                else:
                    # CaptureWidget이 없으면 임시로 저장
                    self.temp_capture_region = region
                    x, y, w, h = region
                    print(f"[MainWindow] 캡처 범위 임시 저장됨: {w}x{h} at ({x}, {y})")
            else:
                print("[MainWindow] 캡처 범위 선택이 취소되었습니다.")
                
        except Exception as e:
            print(f"[MainWindow] 캡처 범위 선택 실패: {e}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "오류", f"캡처 범위 선택에 실패했습니다: {str(e)}")
        
    def set_fullscreen_capture(self):
        """전체 화면 캡처로 설정"""
        if not self.interview_mode:
            print("[MainWindow] 인터뷰 모드가 아닙니다.")
            return
            
        # CaptureWidget이 있으면 캡처 범위 초기화
        if hasattr(self, 'capture_widget'):
            self.capture_widget.capture_region = None
            print("[MainWindow] 전체 화면 캡처로 설정됨")
        else:
            # 임시 저장된 캡처 범위가 있으면 삭제
            if hasattr(self, 'temp_capture_region'):
                delattr(self, 'temp_capture_region')
            print("[MainWindow] 전체 화면 캡처로 설정됨 (임시)")
        
    def switch_to_template_mode(self):
        """템플릿 편집 모드로 전환"""
        self.interview_mode = False
        self.stacked_widget.setCurrentWidget(self.template_editor)
        
        # 헤더 다시 보이기
        self.header_widget.show()
        
        # UI 업데이트
        self.mode_label.setText("📋 현재 모드: 템플릿 설정")
        self.mode_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #7f8c8d;
                padding: 8px 15px;
                background-color: #f8f9fa;
                border-radius: 4px;
            }
        """)
        
        # 버튼 상태 업데이트
        self.select_region_btn.setEnabled(False)
        self.fullscreen_capture_btn.setEnabled(False)
        self.start_capture_btn.setEnabled(False)
        self.stop_capture_btn.setEnabled(False)
        
    def start_ocr_capture(self):
        """OCR 캡처 시작"""
        if not self.interview_mode or not self.interview_widget:
            print("[MainWindow] 인터뷰 모드가 아니거나 위젯이 없습니다.")
            return
            
        # 기존 CaptureWidget 기능을 InterviewWidget와 연동
        if not hasattr(self, 'capture_widget'):
            self.capture_widget = CaptureWidget(self.settings)
            # 캡처된 텍스트를 인터뷰 위젯으로 전달하는 연결
            self.capture_widget.text_captured.connect(self.on_text_captured)
            
            # 임시 저장된 캡처 범위가 있으면 적용
            if hasattr(self, 'temp_capture_region'):
                self.capture_widget.capture_region = self.temp_capture_region
                x, y, w, h = self.temp_capture_region
                print(f"[MainWindow] 저장된 캡처 범위 적용: {w}x{h} at ({x}, {y})")
                delattr(self, 'temp_capture_region')
            
        self.capture_widget.start_capture()
        
        # 버튼 상태 업데이트
        self.start_capture_btn.setEnabled(False)
        self.stop_capture_btn.setEnabled(True)
        
        print("[MainWindow] OCR 캡처 시작됨")
        
    def stop_ocr_capture(self):
        """OCR 캡처 중지 - 마지막 캡처 + 버퍼 정리"""
        if hasattr(self, 'capture_widget'):
            # 1. 마지막 캡처 한 번 더 수행
            print("[MainWindow] 마지막 캡처 수행 중...")
            try:
                self.capture_widget.perform_ocr()
                print("[MainWindow] 마지막 캡처 완료")
            except Exception as e:
                print(f"[MainWindow] 마지막 캡처 실패: {e}")
            
            # 2. 캡처 중지
            self.capture_widget.stop_capture()
            
        # 3. 인터뷰 위젯에서 버퍼 내용 마지막 정리
        if self.interview_widget and hasattr(self.interview_widget, 'pending_analysis_buffer'):
            if self.interview_widget.pending_analysis_buffer.strip():
                print("[MainWindow] 버퍼 내용 마지막 정리 중...")
                try:
                    self.interview_widget.manual_process()
                    print("[MainWindow] 버퍼 정리 완료")
                except Exception as e:
                    print(f"[MainWindow] 버퍼 정리 실패: {e}")
            
        # 버튼 상태 업데이트
        self.start_capture_btn.setEnabled(True)
        self.stop_capture_btn.setEnabled(False)
        
        print("[MainWindow] ✅ OCR 캡처 중지 완료 (마지막 캡처 + 버퍼 정리 포함)")
        
    def on_text_captured(self, text):
        """캡처된 텍스트 처리"""
        if self.interview_widget and text.strip():
            # 인터뷰 위젯에 실시간 텍스트 업데이트
            self.interview_widget.update_live_text(text)
            
            # 자동으로 카테고리별 분석 실행
            self.interview_widget.process_text_for_categories(text)
    
    def capture_screen(self, region=None):
        """화면 캡처 및 OCR 수행 (InterviewWidget에서 호출)"""
        try:
            print("[MainWindow] 화면 캡처 시작...")
            
            # 캡처 영역이 지정되어 있으면 해당 영역, 없으면 전체 화면
            if region:
                print(f"[MainWindow] 매개변수 영역으로 캡처: {region}")
                screenshot = self.screen_capture.capture_region(region)
            elif self.capture_region:
                print(f"[MainWindow] 설정된 영역으로 캡처: {self.capture_region}")
                screenshot = self.screen_capture.capture_region(self.capture_region)
            else:
                print("[MainWindow] 전체 화면 캡처")
                screenshot = self.screen_capture.capture_screen()
            
            if screenshot is None:
                print("[MainWindow] 스크린샷 캡처 실패")
                return ""
            
            print(f"[MainWindow] 스크린샷 캡처 성공 - 크기: {screenshot.size}")
            
            # OCR 수행
            print("[MainWindow] OCR 텍스트 추출 시작...")
            ocr_result = self.ocr_engine.extract_text(screenshot)
            
            if ocr_result and 'text' in ocr_result:
                extracted_text = ocr_result['text'].strip()
                confidence = ocr_result.get('confidence', 0)
                print(f"[MainWindow] OCR 성공 - {len(extracted_text)}글자 추출 (신뢰도: {confidence:.1f}%)")
                if len(extracted_text) > 100:
                    print(f"[MainWindow] 텍스트 샘플: {extracted_text[:100]}...")
                else:
                    print(f"[MainWindow] 전체 텍스트: {extracted_text}")
                return extracted_text
            else:
                print("[MainWindow] OCR 결과 없음 - 텍스트가 인식되지 않았습니다")
                return ""
                
        except Exception as e:
            print(f"[MainWindow] 화면 캡처 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return ""
            

            
    def setup_tray(self):
        """시스템 트레이 아이콘 설정"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("시스템 트레이를 사용할 수 없습니다.")
            return
            
        self.tray_icon = QSystemTrayIcon(self)
        
        # 기본 아이콘 생성
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.blue)
        icon = QIcon(pixmap)
        self.tray_icon.setIcon(icon)
        
        # 트레이 메뉴
        tray_menu = QMenu()
        
        show_action = QAction("보이기", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("종료", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def show_summary_widget(self, template, screening_data):
        """요약 완성 화면으로 전환 (구현예정)"""
        try:
            # SummaryWidget 생성 또는 업데이트
            if self.summary_widget is None:
                self.summary_widget = SummaryWidget(template, screening_data, parent=self)
                self.summary_widget.back_to_interview.connect(self.back_to_interview)
                self.stacked_widget.addWidget(self.summary_widget)
            else:
                # 기존 위젯 업데이트
                self.summary_widget.template = template
                self.summary_widget.screening_data = screening_data
                self.summary_widget.load_screening_data()
            
            # 화면 전환
            self.stacked_widget.setCurrentWidget(self.summary_widget)
            
            # 헤더 및 컨트롤 버튼 숨기기 (요약 모드에서는 불필요)
            self.header_widget.hide()
            self.control_widget.hide()
            
            print(f"[DEBUG] 요약 화면으로 전환 완료. 스크리닝 데이터: {len(screening_data)}개 카테고리")
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to switch to summary view: {str(e)}")
            print(f"[ERROR] 요약 화면 전환 실패: {e}")
    
    def back_to_interview(self):
        """요약 화면에서 인터뷰로 돌아가기 (구현예정)"""
        try:
            if self.interview_widget is not None:
                self.stacked_widget.setCurrentWidget(self.interview_widget)
                
                # 헤더 및 컨트롤 버튼 다시 표시
                self.header_widget.show()
                self.control_widget.show()
                
                print("[DEBUG] 인터뷰 화면으로 돌아가기 완료")
            else:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Warning", "No interview session available.")
                
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to return to interview: {str(e)}")
            print(f"[ERROR] 인터뷰 화면 돌아가기 실패: {e}")
    
    def closeEvent(self, event):
        """창 닫기 이벤트"""
        if hasattr(self, 'capture_widget'):
            self.capture_widget.stop_capture()
        event.accept() 