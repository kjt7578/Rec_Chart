from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMessageBox,
    QGroupBox, QTextEdit, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import json

class TemplateEditor(QWidget):
    """스크리닝 노트 템플릿 편집 위젯"""
    
    template_changed = pyqtSignal(dict)  # 템플릿 변경 시그널
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_template = {
            "candidate_info": {
                "name": "",
                "position": "",
                "location": "",
                "education": "",
                "experience": ""
            },
            "screening_categories": [
                "Security Expertise",
                "Leadership",
                "Cultural Fluency", 
                "Salary Expectations"
            ]
        }
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 제목
        title_label = QLabel("📋 스크리닝 노트 템플릿 설정")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # 빠른 시작 섹션
        quick_start_section = self.create_quick_start_section()
        layout.addWidget(quick_start_section)
        
        # 구분선
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("QFrame { color: #bdc3c7; margin: 10px 0; }")
        layout.addWidget(separator)
        
        # 또는 라벨
        or_label = QLabel("또는 상세 템플릿 설정:")
        or_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #7f8c8d;
                text-align: center;
                margin: 10px 0;
            }
        """)
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(or_label)
        
        # 메인 스플리터 (좌우 분할)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 왼쪽: 후보자 기본 정보
        candidate_info_group = self.create_candidate_info_section()
        main_splitter.addWidget(candidate_info_group)
        
        # 오른쪽: 스크리닝 카테고리 관리
        category_group = self.create_category_section()
        main_splitter.addWidget(category_group)
        
        # 스플리터 비율 설정 (40:60)
        main_splitter.setStretchFactor(0, 40)
        main_splitter.setStretchFactor(1, 60)
        
        layout.addWidget(main_splitter)
        
        # 하단 버튼들
        button_layout = QHBoxLayout()
        
        self.load_template_btn = QPushButton("📁 템플릿 불러오기")
        self.load_template_btn.clicked.connect(self.load_template)
        button_layout.addWidget(self.load_template_btn)
        
        self.save_template_btn = QPushButton("💾 템플릿 저장")
        self.save_template_btn.clicked.connect(self.save_template)
        button_layout.addWidget(self.save_template_btn)
        
        button_layout.addStretch()
        
        self.apply_template_btn = QPushButton("✅ 템플릿 적용하고 인터뷰 시작")
        self.apply_template_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.apply_template_btn.clicked.connect(self.apply_template)
        button_layout.addWidget(self.apply_template_btn)
        
        layout.addLayout(button_layout)
        
    def create_quick_start_section(self):
        """빠른 시작 섹션 생성"""
        group = QGroupBox("🚀 빠른 시작")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #e74c3c;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #fdf2f2;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #e74c3c;
                background-color: #fdf2f2;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # 설명 텍스트
        desc_label = QLabel("별도 설정 없이 바로 인터뷰를 시작하고 싶다면:")
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #2c3e50;
                font-weight: normal;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(desc_label)
        
        # JUST TALK 버튼
        self.just_talk_btn = QPushButton("💬 JUST TALK")
        self.just_talk_btn.clicked.connect(self.start_just_talk_mode)
        self.just_talk_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                padding: 12px 25px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                border: none;
                border-radius: 8px;
                min-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ec7063, stop:1 #e74c3c);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #c0392b, stop:1 #a93226);
            }
        """)
        layout.addWidget(self.just_talk_btn)
        
        # 부가 설명
        note_label = QLabel("• 후보자 정보나 카테고리 설정 없이 즉시 시작\n• 모든 내용은 '자유 대화' 섹션에 자동 정리")
        note_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #7f8c8d;
                font-weight: normal;
                margin-top: 5px;
                line-height: 1.3;
            }
        """)
        layout.addWidget(note_label)
        
        return group
        
    def start_just_talk_mode(self):
        """JUST TALK 모드로 즉시 인터뷰 시작"""
        # 기본 템플릿 생성 (최소한의 정보만)
        template = {
            "candidate_info": {
                "name": "참가자",
                "position": "",
                "location": "",
                "education": "",
                "experience": ""
            },
            "screening_categories": ["자유 대화"]  # 하나의 카테고리만
        }
        
        print("[TemplateEditor] JUST TALK 모드 시작")
        self.template_changed.emit(template)
        
    def create_candidate_info_section(self):
        """후보자 기본 정보 섹션 생성"""
        group = QGroupBox("👤 후보자 기본 정보")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #3498db;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # 각 필드별 입력창
        self.candidate_fields = {}
        fields = [
            ("name", "이름"),
            ("position", "지원 포지션"),
            ("location", "위치/거주지"),
            ("education", "학력"),
            ("experience", "경력")
        ]
        
        for field_key, field_label in fields:
            field_layout = QVBoxLayout()
            
            label = QLabel(f"**{field_label}:**")
            label.setStyleSheet("font-weight: bold; color: #2c3e50;")
            field_layout.addWidget(label)
            
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"{field_label}을(를) 입력하세요...")
            line_edit.textChanged.connect(self.update_candidate_info)
            self.candidate_fields[field_key] = line_edit
            field_layout.addWidget(line_edit)
            
            layout.addLayout(field_layout)
            
        return group
        
    def create_category_section(self):
        """스크리닝 카테고리 섹션 생성"""
        group = QGroupBox("📝 스크리닝 노트 카테고리")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e74c3c;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #e74c3c;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # 카테고리 추가 섹션
        add_layout = QHBoxLayout()
        
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("새 카테고리명을 입력하세요 (예: Project Management Skills)")
        self.category_input.returnPressed.connect(self.add_category)
        add_layout.addWidget(self.category_input)
        
        self.add_category_btn = QPushButton("➕ 추가")
        self.add_category_btn.clicked.connect(self.add_category)
        add_layout.addWidget(self.add_category_btn)
        
        layout.addLayout(add_layout)
        
        # 현재 카테고리 목록
        categories_label = QLabel("**현재 스크리닝 카테고리:**")
        categories_label.setStyleSheet("font-weight: bold; color: #2c3e50; margin-top: 10px;")
        layout.addWidget(categories_label)
        
        self.categories_list = QListWidget()
        self.categories_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        layout.addWidget(self.categories_list)
        
        # 카테고리 관리 버튼
        category_buttons = QHBoxLayout()
        
        self.remove_category_btn = QPushButton("🗑️ 선택 삭제")
        self.remove_category_btn.clicked.connect(self.remove_category)
        category_buttons.addWidget(self.remove_category_btn)
        
        self.move_up_btn = QPushButton("⬆️ 위로")
        self.move_up_btn.clicked.connect(self.move_category_up)
        category_buttons.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("⬇️ 아래로")
        self.move_down_btn.clicked.connect(self.move_category_down)
        category_buttons.addWidget(self.move_down_btn)
        
        category_buttons.addStretch()
        
        layout.addLayout(category_buttons)
        
        # 기본 카테고리 로드
        self.load_default_categories()
        
        return group
        
    def load_default_categories(self):
        """기본 카테고리들을 목록에 로드"""
        self.categories_list.clear()
        for category in self.current_template["screening_categories"]:
            item = QListWidgetItem(f"📌 {category}")
            self.categories_list.addItem(item)
            
    def add_category(self):
        """새 카테고리 추가"""
        category_name = self.category_input.text().strip()
        if not category_name:
            QMessageBox.warning(self, "경고", "카테고리명을 입력해주세요.")
            return
            
        if category_name in self.current_template["screening_categories"]:
            QMessageBox.warning(self, "경고", "이미 존재하는 카테고리입니다.")
            return
            
        self.current_template["screening_categories"].append(category_name)
        item = QListWidgetItem(f"📌 {category_name}")
        self.categories_list.addItem(item)
        self.category_input.clear()
        
    def remove_category(self):
        """선택된 카테고리 삭제"""
        current_row = self.categories_list.currentRow()
        if current_row >= 0:
            self.current_template["screening_categories"].pop(current_row)
            self.categories_list.takeItem(current_row)
            
    def move_category_up(self):
        """선택된 카테고리를 위로 이동"""
        current_row = self.categories_list.currentRow()
        if current_row > 0:
            categories = self.current_template["screening_categories"]
            categories[current_row], categories[current_row-1] = categories[current_row-1], categories[current_row]
            self.load_default_categories()
            self.categories_list.setCurrentRow(current_row-1)
            
    def move_category_down(self):
        """선택된 카테고리를 아래로 이동"""
        current_row = self.categories_list.currentRow()
        if current_row >= 0 and current_row < len(self.current_template["screening_categories"]) - 1:
            categories = self.current_template["screening_categories"]
            categories[current_row], categories[current_row+1] = categories[current_row+1], categories[current_row]
            self.load_default_categories()
            self.categories_list.setCurrentRow(current_row+1)
            
    def update_candidate_info(self):
        """후보자 정보 업데이트"""
        for field_key, line_edit in self.candidate_fields.items():
            self.current_template["candidate_info"][field_key] = line_edit.text()
            
    def load_template(self):
        """저장된 템플릿 불러오기"""
        # TODO: 파일 다이얼로그로 JSON 템플릿 파일 로드
        pass
        
    def save_template(self):
        """현재 템플릿 저장"""
        # TODO: 파일 다이얼로그로 JSON 템플릿 파일 저장
        pass
        
    def apply_template(self):
        """템플릿 적용하고 인터뷰 시작"""
        self.update_candidate_info()
        self.template_changed.emit(self.current_template)
        
    def get_current_template(self):
        """현재 템플릿 반환"""
        self.update_candidate_info()
        return self.current_template.copy() 