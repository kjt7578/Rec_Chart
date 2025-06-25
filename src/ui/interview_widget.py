# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QGroupBox, QScrollArea, QFrame, QSplitter,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCharFormat, QTextCursor, QTextDocument
import json
import os
from datetime import datetime

class AutoResizeTextEdit(QTextEdit):
    """텍스트 양에 따라 자동으로 높이가 조절되는 TextEdit"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textChanged.connect(self.adjust_height)
        self.setMinimumHeight(50)  # 최소 높이
        self.setMaximumHeight(300) # 최대 높이 제한
        
    def adjust_height(self):
        """텍스트 내용에 따라 높이 자동 조절"""
        # 문서 높이 계산
        doc = self.document()
        doc.setTextWidth(self.viewport().width())
        height = doc.size().height() + 10  # 여백 추가
        
        # 최소/최대 높이 제한 적용
        height = max(50, min(300, int(height)))
        self.setFixedHeight(height)
        
    def resizeEvent(self, event):
        """크기 변경 시 높이 재조정"""
        super().resizeEvent(event)
        self.adjust_height()

class CategoryNoteWidget(QFrame):
    """개별 카테고리 노트 위젯"""
    
    content_changed = pyqtSignal(str, bool)  # 카테고리명, 내용 있음/없음 신호
    
    def __init__(self, category_name, parent=None):
        super().__init__(parent)
        self.category_name = category_name
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #dee2e6;
                border-radius: 3px;
                margin: 1px;
                background-color: white;
                padding: 2px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 3, 4, 3)  # 여백 최소화
        layout.setSpacing(2)  # 간격 최소화
        
        # 카테고리 제목 (볼드체, 눈에 잘 띄게)
        self.title_label = QLabel(f"{self.category_name}")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #2c3e50;
                background-color: #f8f9fa;
                padding: 6px 8px;
                border-radius: 4px;
                border: 1px solid #dee2e6;
            }
        """)
        layout.addWidget(self.title_label)
        
        # 노트 내용 - 자동 높이 조절
        self.content_edit = AutoResizeTextEdit()
        self.content_edit.setPlaceholderText(f"{self.category_name}에 대한 정보가 여기에 자동으로 기록됩니다...")
        self.content_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Malgun Gothic', sans-serif;
                font-size: 12px;
                background-color: #ffffff;
                line-height: 1.4;
            }
        """)
        self.content_edit.textChanged.connect(self.on_content_changed)
        layout.addWidget(self.content_edit)
        
    def on_content_changed(self):
        """내용 변경 시 신호 발생"""
        has_content = bool(self.content_edit.toPlainText().strip())
        self.content_changed.emit(self.category_name, has_content)
        
    def add_content(self, content):
        """새 내용 추가 (중복 체크 포함)"""
        if content and content.strip():
            # 중복 체크
            if not self._is_duplicate_content(content.strip()):
                current = self.content_edit.toPlainText()
                if current:
                    # 기존 내용과 새 내용을 병합하여 중복 제거
                    merged_content = self._merge_similar_content(current + "\n" + content.strip())
                    self.content_edit.setPlainText(merged_content)
                else:
                    self.content_edit.setPlainText(content.strip())
                self.content_edit.adjust_height()
                self.on_content_changed()
            else:
                print(f"[중복 제거] '{self.category_name}' 카테고리: 유사한 내용 이미 존재")
    
    def _is_duplicate_content(self, new_content):
        """중복 내용 검사 (개선된 버전)"""
        existing_content = self.content_edit.toPlainText()
        if not existing_content:
            return False
        
        # 1. 완전 일치 검사
        if new_content in existing_content:
            print(f"[중복 제거] 완전 일치 발견: '{new_content[:50]}...'")
            return True
        
        # 2. 라인별 중복 검사 (기존 내용의 각 라인과 비교)
        existing_lines = [line.strip() for line in existing_content.split('\n') if line.strip()]
        for existing_line in existing_lines:
            # 핵심 키워드 기반 유사도 검사 (임계값 낮춤: 70% → 50%)
            similarity = self._calculate_similarity(new_content, existing_line)
            if similarity > 0.5:  # 50% 이상 유사하면 중복으로 판단
                print(f"[중복 제거] 유사도 {similarity:.1%} 발견:")
                print(f"  기존: '{existing_line[:50]}...'")
                print(f"  신규: '{new_content[:50]}...'")
                return True
        
        # 3. 숫자 정보 중복 검사 (예: "3 HR staff", "70 employees")
        if self._has_overlapping_numbers(new_content, existing_content):
            print(f"[중복 제거] 숫자 정보 중복 발견: '{new_content[:50]}...'")
            return True
            
        return False

    def _calculate_similarity(self, text1, text2):
        """두 텍스트 간 유사도 계산 (개선된 버전)"""
        import re
        
        # 주요 단어들 추출 (2글자 이상 영어 단어 + 숫자)
        words1 = set(re.findall(r'\b(?:[a-zA-Z]{2,}|\d+)\b', text1.lower()))
        words2 = set(re.findall(r'\b(?:[a-zA-Z]{2,}|\d+)\b', text2.lower()))
        
        if not words1 or not words2:
            return 0
        
        # 교집합 비율 계산 (더 관대한 방식)
        intersection = len(words1 & words2)
        smaller_set = min(len(words1), len(words2))
        
        # 작은 집합 기준으로 유사도 계산 (더 민감한 중복 검사)
        return intersection / smaller_set if smaller_set > 0 else 0

    def _has_overlapping_numbers(self, new_content, existing_content):
        """숫자 정보 중복 검사 (예: 직원 수, 사이트 수 등)"""
        import re
        
        # 숫자와 관련 단어 패턴 추출
        number_patterns = [
            r'(\d+)\s*(?:employees?|staff|people|members?)',
            r'(\d+)\s*(?:sites?|locations?|offices?)',
            r'(\d+)\s*(?:years?|months?)',
            r'\$?(\d+)K?\s*(?:salary|compensation|base)',
            r'(\d+)[-\s]*(?:week|month)\s*(?:notice|timeline)',
            r'(\d+)\s*(?:direct\s+)?(?:reports?|staff)'
        ]
        
        for pattern in number_patterns:
            new_numbers = re.findall(pattern, new_content, re.IGNORECASE)
            existing_numbers = re.findall(pattern, existing_content, re.IGNORECASE)
            
            # 같은 패턴의 숫자가 이미 존재하면서 값이 다르면 충돌 상황
            if new_numbers and existing_numbers and new_numbers != existing_numbers:
                print(f"[데이터 충돌] 패턴: {pattern}")
                print(f"  기존: {existing_numbers} <- '{existing_content}'")
                print(f"  신규: {new_numbers} <- '{new_content}'")
                # GPT 검증으로 더 정확한 정보 선택
                self._resolve_conflicting_data(new_content, existing_content, pattern)
                return True  # 충돌 처리 완료로 중복 판정
                
        return False

    def _resolve_conflicting_data(self, new_content, existing_content, pattern):
        """충돌하는 데이터 해결 (GPT 기반 검증)"""
        try:
            # GPT Summarizer 가져오기
            current_widget = self
            level = 0
            main_window = None
            
            while current_widget and level < 5:
                if hasattr(current_widget, 'gpt_summarizer'):
                    main_window = current_widget
                    break
                current_widget = current_widget.parent()
                level += 1
            
            if not main_window or not hasattr(main_window, 'gpt_summarizer'):
                print(f"[데이터 검증] GPT 분석기 없음 - 자동 검증 불가")
                return existing_content  # 기존 내용 유지
            
            gpt = main_window.gpt_summarizer
            
            # 데이터 검증 프롬프트
            validation_prompt = f"""
Two conflicting pieces of information detected about numerical data:

Existing: {existing_content}
New: {new_content}

Choose the most reliable statement based on:
1. More specific and detailed context
2. Completeness of information
3. Internal consistency
4. Clarity and precision

Important: If one mentions "$120K" and another "$12K", choose the more reasonable salary amount.
If one mentions "700 employees" and another "7 employees", choose based on company context.

Return ONLY the most accurate statement in resume bullet point format (no subjects like "he/she/candidate").
"""
            
            response = gpt.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a data validation expert. Choose the most accurate information from conflicting data points."},
                    {"role": "user", "content": validation_prompt}
                ],
                temperature=0.1,
                max_tokens=150
            )
            
            verified_content = response.choices[0].message.content.strip()
            print(f"[데이터 검증] GPT 검증 완료:")
            print(f"  기존: '{existing_content}'")
            print(f"  신규: '{new_content}'")
            print(f"  선택: '{verified_content}'")
            
            # 검증된 내용으로 기존 내용 업데이트
            current_text = self.content_edit.toPlainText()
            updated_text = current_text.replace(existing_content, verified_content)
            self.content_edit.setPlainText(updated_text)
            
            return verified_content
            
        except Exception as e:
            print(f"[데이터 검증] GPT 검증 실패: {e}")
            return existing_content  # 오류 시 기존 내용 유지

    def _merge_similar_content(self, content):
        """유사한 내용들을 병합하여 중복 제거 (개선된 버전)"""
        lines = content.strip().split('\n')
        unique_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 기존 라인들과 유사도 체크 (임계값 낮춤: 80% → 60%)
            is_similar = False
            for i, existing_line in enumerate(unique_lines):
                similarity = self._calculate_similarity(line, existing_line)
                if similarity > 0.6:  # 60% 이상 유사하면 병합
                    # 더 구체적이고 긴 문장으로 교체
                    if len(line) > len(existing_line):
                        print(f"[병합] 더 상세한 내용으로 교체:")
                        print(f"  기존: '{existing_line}'")
                        print(f"  신규: '{line}'")
                        unique_lines[i] = line
                    else:
                        print(f"[병합] 기존 내용 유지: '{existing_line}'")
                    is_similar = True
                    break
            
            if not is_similar:
                unique_lines.append(line)
        
        return '\n'.join(unique_lines)
        
    def get_content(self):
        """현재 노트 내용 반환"""
        return self.content_edit.toPlainText()
        
    def set_content(self, content):
        """노트 내용 설정"""
        # ** 마크다운 제거
        clean_content = content.replace("**", "")
        self.content_edit.setPlainText(clean_content)

class InterviewWidget(QWidget):
    """템플릿 기반 실시간 인터뷰 위젯"""
    
    def __init__(self, template, settings, parent=None):
        super().__init__(parent)
        self.template = template
        self.settings = settings
        self.category_widgets = {}
        self.category_status_labels = {}  # 카테고리 상태 라벨들
        self.other_notes = []
        
        # 누적 분석을 위한 버퍼 추가
        self.pending_analysis_buffer = ""  # 분석 대기 중인 텍스트 누적
        self.min_analysis_length = 150    # 최소 분석 길이 (글자 수)
        self.max_buffer_size = 1000      # 최대 버퍼 크기
        
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)  # 여백 최소화
        layout.setSpacing(3)  # 간격 최소화
        
        # 최상단: 카테고리 체크리스트 (미니멀)
        self.create_minimal_checklist(layout)
        
        # 중간: 스크리닝 노트 (메인 영역)
        screening_notes_panel = self.create_screening_notes_panel()
        layout.addWidget(screening_notes_panel)
        
        # 하단: 실시간 대화 + 컨트롤 버튼들 (모두 한 줄로 배치)
        bottom_layout = self.create_bottom_panel()
        layout.addWidget(bottom_layout)
        
    def create_bottom_panel(self):
        """하단 패널 - 실시간 대화 + 컨트롤 버튼들을 한 줄로 배치"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                margin: 1px;
                padding: 3px;
            }
        """)
        frame.setMaximumHeight(50)  # 높이 제한
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(5, 3, 5, 3)
        layout.setSpacing(8)
        
        # 1. 실시간 대화 텍스트 박스 (가장 큰 비율)
        self.live_text_edit = QTextEdit()
        self.live_text_edit.setMaximumHeight(35)
        self.live_text_edit.setPlaceholderText("실시간 대화 내용...")
        self.live_text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 2px;
                padding: 3px;
                font-family: 'Malgun Gothic', sans-serif;
                font-size: 10px;
                background-color: white;
            }
        """)
        layout.addWidget(self.live_text_edit, 60)  # 60% 비율
        
        # 2. 구분선
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        separator1.setStyleSheet("color: #dee2e6;")
        layout.addWidget(separator1)
        
        # 3. 컨트롤 버튼들
        button_style = """
            QPushButton {
                font-size: 9px;
                font-weight: bold;
                padding: 1px 4px;
                border: none;
                border-radius: 2px;
                min-width: 50px;
                min-height: 25px;
                max-height: 25px;
            }
        """
        
        self.test_capture_btn = QPushButton("🧪 테스트")
        self.test_capture_btn.clicked.connect(self.test_capture)
        self.test_capture_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #17a2b8;
                color: white;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        layout.addWidget(self.test_capture_btn)
        
        self.process_btn = QPushButton("🔄 분석")
        self.process_btn.clicked.connect(self.manual_process)
        self.process_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #f39c12;
                color: white;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        layout.addWidget(self.process_btn)
        
        # 4. 구분선
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setStyleSheet("color: #dee2e6;")
        layout.addWidget(separator2)
        
        # 5. 캡처 범위 버튼
        self.capture_range_btn = QPushButton("📐 범위")
        self.capture_range_btn.clicked.connect(self.select_capture_range)
        self.capture_range_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #6c757d;
                color: white;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        layout.addWidget(self.capture_range_btn)
        
        # 6. 구분선
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.Shape.VLine)
        separator3.setStyleSheet("color: #dee2e6;")
        layout.addWidget(separator3)
        
        # 7. 템플릿 편집 버튼
        self.template_edit_btn = QPushButton("📝 템플릿")
        self.template_edit_btn.clicked.connect(self.edit_template)
        self.template_edit_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(self.template_edit_btn)
        
        # 8. 저장 버튼
        self.export_btn = QPushButton("💾 저장")
        self.export_btn.clicked.connect(self.export_screening_notes)
        self.export_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #3498db;
                color: white;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(self.export_btn)
        
        # 9. 구분선
        separator4 = QFrame()
        separator4.setFrameShape(QFrame.Shape.VLine)
        separator4.setStyleSheet("color: #dee2e6;")
        layout.addWidget(separator4)
        
        # 10. 요약 완성 버튼
        self.summary_btn = QPushButton("📋 요약완성")
        self.summary_btn.clicked.connect(self.go_to_summary)
        self.summary_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #17a2b8;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        layout.addWidget(self.summary_btn)
        
        return frame
        
    def create_minimal_checklist(self, parent_layout):
        """최상단 미니멀 체크리스트 생성"""
        checklist_frame = QFrame()
        checklist_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                margin: 1px;
                padding: 3px;
            }
        """)
        checklist_frame.setMaximumHeight(35)  # 높이 제한
        
        layout = QHBoxLayout(checklist_frame)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(15)  # 카테고리 간 간격
        
        # 제목
        title_label = QLabel("📋")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        layout.addWidget(title_label)
        
        # 카테고리들을 한 줄로 배치
        all_categories = self.template["screening_categories"] + ["기타"]
        
        for category in all_categories:
            display_name = "기타" if category == "기타" else category
            
            status_label = QLabel(f"• {display_name}")
            status_label.setStyleSheet("""
                QLabel {
                    font-size: 10px;
                    font-weight: bold;
                    color: #e74c3c;
                    padding: 1px 3px;
                }
            """)
            
            # 카테고리명을 키로 저장
            key = "Other" if category == "기타" else category
            self.category_status_labels[key] = status_label
            
            layout.addWidget(status_label)
        
        layout.addStretch()  # 남은 공간을 오른쪽으로 밀어냄
        parent_layout.addWidget(checklist_frame)
        
    def select_capture_range(self):
        """캡처 범위 선택"""
        try:
            # 부모 위젯에서 캡처 범위 선택 기능 호출
            if hasattr(self.parent(), 'show_capture_widget'):
                self.parent().show_capture_widget()
            else:
                QMessageBox.information(self, "알림", "캡처 범위 선택 기능을 준비 중입니다.")
        except Exception as e:
            QMessageBox.warning(self, "오류", f"캡처 범위 선택 중 오류: {str(e)}")
            
    def edit_template(self):
        """템플릿 편집 팝업"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QDialogButtonBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("템플릿 편집")
            dialog.setModal(True)
            dialog.resize(400, 500)
            
            layout = QVBoxLayout(dialog)
            
            # 후보자 정보 섹션
            info_group = QGroupBox("후보자 정보")
            info_layout = QVBoxLayout(info_group)
            
            # 기존 정보 표시 및 편집
            self.name_edit = QLineEdit(self.template.get("candidate_name", ""))
            self.name_edit.setPlaceholderText("후보자 이름")
            info_layout.addWidget(QLabel("이름:"))
            info_layout.addWidget(self.name_edit)
            
            self.position_edit = QLineEdit(self.template.get("position", ""))
            self.position_edit.setPlaceholderText("지원 포지션")
            info_layout.addWidget(QLabel("포지션:"))
            info_layout.addWidget(self.position_edit)
            
            layout.addWidget(info_group)
            
            # 스크리닝 카테고리 섹션
            category_group = QGroupBox("스크리닝 카테고리")
            category_layout = QVBoxLayout(category_group)
            
            self.category_list = QListWidget()
            for category in self.template["screening_categories"]:
                item = QListWidgetItem(category)
                self.category_list.addItem(item)
            category_layout.addWidget(self.category_list)
            
            # 카테고리 추가/삭제 버튼
            category_btn_layout = QHBoxLayout()
            
            add_btn = QPushButton("+ 추가")
            add_btn.clicked.connect(self.add_category)
            category_btn_layout.addWidget(add_btn)
            
            remove_btn = QPushButton("- 삭제")
            remove_btn.clicked.connect(self.remove_category)
            category_btn_layout.addWidget(remove_btn)
            
            category_layout.addLayout(category_btn_layout)
            layout.addWidget(category_group)
            
            # 대화상자 버튼
            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            button_box.accepted.connect(self.save_template_changes)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "오류", f"템플릿 편집 중 오류: {str(e)}")
            
    def add_category(self):
        """카테고리 추가"""
        from PyQt6.QtWidgets import QInputDialog
        
        text, ok = QInputDialog.getText(self, "카테고리 추가", "새 카테고리 이름:")
        if ok and text.strip():
            item = QListWidgetItem(text.strip())
            self.category_list.addItem(item)
            
    def remove_category(self):
        """선택된 카테고리 삭제"""
        current_item = self.category_list.currentItem()
        if current_item:
            self.category_list.takeItem(self.category_list.row(current_item))
            
    def save_template_changes(self):
        """템플릿 변경사항 저장"""
        try:
            # 후보자 정보 업데이트
            self.template["candidate_name"] = self.name_edit.text().strip()
            self.template["position"] = self.position_edit.text().strip()
            
            # 카테고리 목록 업데이트
            new_categories = []
            for i in range(self.category_list.count()):
                item = self.category_list.item(i)
                new_categories.append(item.text())
            
            self.template["screening_categories"] = new_categories
            
            # UI 새로고침
            self.refresh_ui()
            
            QMessageBox.information(self, "저장 완료", "템플릿이 성공적으로 업데이트되었습니다.")
            
        except Exception as e:
            QMessageBox.critical(self, "저장 오류", f"템플릿 저장 중 오류: {str(e)}")
            
    def refresh_ui(self):
        """UI 새로고침 (템플릿 변경 후)"""
        try:
            # 체크리스트 새로고침
            self.category_status_labels.clear()
            
            # 카테고리 위젯들 새로고침
            old_widgets = list(self.category_widgets.keys())
            for category in old_widgets:
                if category not in self.template["screening_categories"] and category != "Other":
                    del self.category_widgets[category]
            
            # 새 카테고리 위젯 추가는 부모 위젯에서 처리하도록 신호 전달
            if hasattr(self.parent(), 'refresh_interview_widget'):
                self.parent().refresh_interview_widget()
                
        except Exception as e:
            print(f"UI 새로고침 중 오류: {e}")
        
    def create_screening_notes_panel(self):
        """스크리닝 노트 패널 - 메인 영역 (미니멀)"""
        group = QGroupBox("📝 스크리닝 노트")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #e74c3c;
                border-radius: 4px;
                margin-top: 2px;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
                color: #e74c3c;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setContentsMargins(5, 3, 5, 3)  # 여백 최소화
        
        # 스크롤 영역 (스크리닝 노트만, 체크리스트 제거)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # 스크롤 컨텐츠 위젯
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(6)  # 간격 조정
        scroll_layout.setContentsMargins(2, 2, 2, 2)  # 여백 최소화
        
        # 2열 구조 메인 컨테이너
        main_grid = QHBoxLayout()
        main_grid.setSpacing(8)
        
        # 좌측 열
        left_column = QVBoxLayout()
        left_column.setSpacing(6)
        
        # 우측 열
        right_column = QVBoxLayout()
        right_column.setSpacing(6)
        
        # 카테고리들을 2열로 분배
        all_categories = self.template["screening_categories"] + ["🔍 기타 중요 정보"]
        
        for i, category in enumerate(all_categories):
            if category == "🔍 기타 중요 정보":
                category_widget = CategoryNoteWidget("🔍 기타 중요 정보")
                self.other_widget = category_widget
                self.category_widgets["Other"] = category_widget
            else:
                category_widget = CategoryNoteWidget(category)
                self.category_widgets[category] = category_widget
            
            category_widget.content_changed.connect(self.update_category_status)
            
            # 좌우 교대로 배치
            if i % 2 == 0:
                left_column.addWidget(category_widget)
            else:
                right_column.addWidget(category_widget)
        
        # 좌우 균형 맞추기 (빈 공간 추가)
        left_column.addStretch()
        right_column.addStretch()
        
        # 좌우 열을 메인 그리드에 추가
        main_grid.addLayout(left_column)
        main_grid.addLayout(right_column)
        
        scroll_layout.addLayout(main_grid)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        return group
        
    def create_category_checklist(self, parent_layout):
        """카테고리 체크리스트 생성"""
        checklist_frame = QFrame()
        checklist_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                margin-bottom: 10px;
            }
        """)
        
        checklist_layout = QVBoxLayout(checklist_frame)
        checklist_layout.setContentsMargins(10, 8, 10, 8)
        checklist_layout.setSpacing(5)
        
        # 체크리스트 제목
        title_label = QLabel("📋 스크리닝 체크리스트")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 8px;
            }
        """)
        checklist_layout.addWidget(title_label)
        
        # 카테고리 상태 표시 (2열 그리드로 배치)
        grid_layout = QHBoxLayout()
        
        # 왼쪽 열
        left_column = QVBoxLayout()
        left_column.setSpacing(3)
        
        # 오른쪽 열  
        right_column = QVBoxLayout()
        right_column.setSpacing(3)
        
        all_categories = self.template["screening_categories"] + ["기타 중요 정보"]
        
        for i, category in enumerate(all_categories):
            display_name = "🔍 기타 중요 정보" if category == "기타 중요 정보" else category
            
            status_label = QLabel(f"• {display_name}")
            status_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    font-weight: bold;
                    color: #e74c3c;
                    padding: 2px 5px;
                }
            """)
            
            # 카테고리명을 키로 저장 (일관성 유지)
            key = "Other" if category == "기타 중요 정보" else category
            self.category_status_labels[key] = status_label
            
            # 좌우 교대로 배치
            if i % 2 == 0:
                left_column.addWidget(status_label)
            else:
                right_column.addWidget(status_label)
        
        grid_layout.addLayout(left_column)
        grid_layout.addLayout(right_column)
        grid_layout.addStretch()
        
        checklist_layout.addLayout(grid_layout)
        parent_layout.addWidget(checklist_frame)
        
    def update_category_status(self, category_name, has_content):
        """카테고리 상태 업데이트 (미니멀 체크리스트용)"""
        key = "Other" if category_name == "🔍 기타 중요 정보" else category_name
        
        if key in self.category_status_labels:
            label = self.category_status_labels[key]
            
            if has_content:
                # 내용이 있으면 완료 상태로 변경
                display_name = "기타" if key == "Other" else category_name
                label.setText(f"✅ {display_name}")
                label.setStyleSheet("""
                    QLabel {
                        font-size: 10px;
                        font-weight: normal;
                        color: #27ae60;
                        padding: 1px 3px;
                        background-color: #d5f4e6;
                        border-radius: 2px;
                    }
                """)
            else:
                # 내용이 없으면 대기 상태로 변경
                display_name = "기타" if key == "Other" else category_name
                label.setText(f"• {display_name}")
                label.setStyleSheet("""
                    QLabel {
                        font-size: 10px;
                        font-weight: bold;
                        color: #e74c3c;
                        padding: 1px 3px;
                    }
                """)

    def test_capture(self):
        """테스트 캡처 기능 - 실제 화면 캡처만 수행"""
        try:
            # MainWindow 찾기 - 위젯 계층을 따라 올라가며 capture_screen을 찾음
            current_widget = self
            main_window = None
            level = 0
            
            while current_widget and level < 10:  # 최대 10단계까지만 탐색
                if hasattr(current_widget, 'capture_screen'):
                    main_window = current_widget
                    print(f"[테스트] capture_screen 발견! Level {level}: {type(main_window)}")
                    break
                
                current_widget = current_widget.parent()
                level += 1
            
            if main_window and hasattr(main_window, 'capture_screen'):
                captured_text = main_window.capture_screen()
                if captured_text and captured_text.strip():
                    # 캡처된 텍스트를 실시간 영역에 표시
                    self.update_live_text(captured_text)
                    
                    # AI 분석 진행
                    self.process_text_for_categories(captured_text)
                    
                    QMessageBox.information(self, "테스트 완료", f"캡처 및 분석이 완료되었습니다!\n\n추출된 텍스트: {len(captured_text)}글자")
                else:
                    QMessageBox.warning(self, "캡처 실패", "화면에서 텍스트를 추출하지 못했습니다.\n\n• 캡처 범위에 텍스트가 있는지 확인하세요\n• OCR이 인식할 수 있는 텍스트인지 확인하세요")
            else:
                QMessageBox.critical(self, "기능 오류", "화면 캡처 기능을 찾을 수 없습니다.\n시스템 오류일 가능성이 있습니다.")
                
        except Exception as e:
            print(f"[ERROR] 테스트 캡처 중 오류: {e}")
            QMessageBox.critical(self, "오류", f"테스트 캡처 중 오류가 발생했습니다:\n{str(e)}")
    
    def update_live_text(self, new_text):
        """실시간 텍스트 업데이트"""
        if new_text:
            # ** 마크다운 제거
            clean_text = new_text.replace("**", "")
            
            current_text = self.live_text_edit.toPlainText()
            if current_text:
                updated_text = current_text + "\n\n" + clean_text
            else:
                updated_text = clean_text
                
            self.live_text_edit.setPlainText(updated_text)
            
            # 스크롤을 맨 아래로 이동
            cursor = self.live_text_edit.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.live_text_edit.setTextCursor(cursor)
    
    def process_text_for_categories(self, text):
        """텍스트를 카테고리별로 분석하여 자동 분류 (누적 분석 방식)"""
        try:
            print(f"[스크리닝] 텍스트 분석 시작 (길이: {len(text)})")
            
            # MainWindow 찾기 - 위젯 계층을 따라 올라가며 gpt_summarizer를 찾음
            current_widget = self
            main_window = None
            level = 0
            
            while current_widget and level < 10:  # 최대 10단계까지만 탐색
                print(f"[스크리닝] Level {level}: {type(current_widget)}")
                
                if hasattr(current_widget, 'gpt_summarizer'):
                    main_window = current_widget
                    print(f"[스크리닝] gpt_summarizer 발견! Level {level}: {type(main_window)}")
                    break
                
                current_widget = current_widget.parent()
                level += 1
            
            if main_window and hasattr(main_window, 'gpt_summarizer'):
                print(f"[스크리닝] GPT 분석기 연결됨: {type(main_window.gpt_summarizer)}")
                gpt = main_window.gpt_summarizer
                
                # 새 텍스트를 버퍼에 추가
                if self.pending_analysis_buffer:
                    self.pending_analysis_buffer += "\n" + text
                else:
                    self.pending_analysis_buffer = text
                
                # 버퍼 크기 제한
                if len(self.pending_analysis_buffer) > self.max_buffer_size:
                    # 앞부분 잘라내기 (최근 텍스트 유지)
                    lines = self.pending_analysis_buffer.split('\n')
                    self.pending_analysis_buffer = '\n'.join(lines[-10:])  # 최근 10줄만 유지
                    print(f"[스크리닝] 버퍼 크기 초과로 정리됨 (현재 길이: {len(self.pending_analysis_buffer)})")
                
                print(f"[스크리닝] 누적 버퍼 길이: {len(self.pending_analysis_buffer)}")
                
                # 충분한 양이 누적되었거나 의미있는 키워드가 있을 때만 분석
                should_analyze = (
                    len(self.pending_analysis_buffer) >= self.min_analysis_length or
                    self._has_meaningful_content(self.pending_analysis_buffer)
                )
                
                if should_analyze:
                    print(f"[스크리닝] 누적 분석 시작 (버퍼 길이: {len(self.pending_analysis_buffer)})")
                    
                    # 빠른 카테고리 분류 사용 (Enhanced Analyzer 대신)
                    categories = list(self.template.get("screening_categories", []))
                    if "Other" not in categories:
                        categories.append("Other")
                    
                    categorized_result = gpt.quick_categorize_text(self.pending_analysis_buffer, categories)
                    
                    if categorized_result:
                        print(f"[스크리닝] 빠른 분석 완료: {len(categorized_result)}개 카테고리")
                        
                        # 분석 결과를 각 카테고리에 추가
                        for category, analysis_data in categorized_result.items():
                            if category in self.category_widgets:
                                # assessment 리스트에서 내용 추출
                                if isinstance(analysis_data, dict) and "assessment" in analysis_data:
                                    assessment_list = analysis_data["assessment"]
                                    if isinstance(assessment_list, list):
                                        valid_items = []
                                        for item in assessment_list:
                                            if self._is_meaningful_assessment(item):
                                                valid_items.append(item)
                                                self.category_widgets[category].add_content(item)
                                        if valid_items:
                                            print(f"[스크리닝] '{category}' 카테고리에 {len(valid_items)}개 항목 추가")
                                        else:
                                            print(f"[스크리닝] '{category}' 카테고리: 의미있는 내용 없음, 추가하지 않음")
                                    else:
                                        if self._is_meaningful_assessment(str(assessment_list)):
                                            self.category_widgets[category].add_content(str(assessment_list))
                                            print(f"[스크리닝] '{category}' 카테고리에 내용 추가")
                                        else:
                                            print(f"[스크리닝] '{category}' 카테고리: 의미있는 내용 없음, 추가하지 않음")
                                else:
                                    if self._is_meaningful_assessment(str(analysis_data.get("assessment", analysis_data))):
                                        self.category_widgets[category].add_content(str(analysis_data.get("assessment", analysis_data)))
                                        print(f"[스크리닝] '{category}' 카테고리에 내용 추가")
                                    else:
                                        print(f"[스크리닝] '{category}' 카테고리: 의미있는 내용 없음, 추가하지 않음")
                            else:
                                # 매칭되지 않는 카테고리는 GPT에게 재분류 요청
                                if category != "Other":
                                    # GPT에게 더 적절한 카테고리 찾기 요청
                                    reassigned_category = self._reassign_category_with_gpt(
                                        category, analysis_data, list(self.template.get("screening_categories", []))
                                    )
                                    
                                    if reassigned_category and reassigned_category in self.category_widgets:
                                        # 재분류 성공 시 해당 카테고리에 추가
                                        if isinstance(analysis_data, dict) and "assessment" in analysis_data:
                                            assessment_list = analysis_data["assessment"]
                                            if isinstance(assessment_list, list):
                                                for item in assessment_list:
                                                    if self._is_meaningful_assessment(item):
                                                        self.category_widgets[reassigned_category].add_content(item)
                                                        print(f"[스크리닝] '{category}' → '{reassigned_category}'로 GPT 재분류")
                                            else:
                                                if self._is_meaningful_assessment(str(assessment_list)):
                                                    self.category_widgets[reassigned_category].add_content(str(assessment_list))
                                                    print(f"[스크리닝] '{category}' → '{reassigned_category}'로 GPT 재분류")
                                        else:
                                            content_str = str(analysis_data)
                                            if self._is_meaningful_assessment(content_str):
                                                self.category_widgets[reassigned_category].add_content(content_str)
                                                print(f"[스크리닝] '{category}' → '{reassigned_category}'로 GPT 재분류")
                                    else:
                                        # 재분류 실패 시에만 Other에 추가 (원시 카테고리 태그 없이)
                                        if "Other" in self.category_widgets:
                                            if isinstance(analysis_data, dict) and "assessment" in analysis_data:
                                                assessment_list = analysis_data["assessment"]
                                                if isinstance(assessment_list, list):
                                                    for item in assessment_list:
                                                        if self._is_meaningful_assessment(item):
                                                            self.category_widgets["Other"].add_content(item)  # 태그 제거
                                                            print(f"[스크리닝] '{category}' → '기타'로 분류됨 (재분류 실패)")
                                                else:
                                                    if self._is_meaningful_assessment(str(assessment_list)):
                                                        self.category_widgets["Other"].add_content(str(assessment_list))  # 태그 제거
                                                        print(f"[스크리닝] '{category}' → '기타'로 분류됨 (재분류 실패)")
                                            else:
                                                content_str = str(analysis_data)
                                                if self._is_meaningful_assessment(content_str):
                                                    self.category_widgets["Other"].add_content(content_str)  # 태그 제거
                                                    print(f"[스크리닝] '{category}' → '기타'로 분류됨 (재분류 실패)")
                                else:
                                    # Other 카테고리 자체는 그대로 처리
                                    if "Other" in self.category_widgets:
                                        if isinstance(analysis_data, dict) and "assessment" in analysis_data:
                                            assessment_list = analysis_data["assessment"]
                                            if isinstance(assessment_list, list):
                                                for item in assessment_list:
                                                    if self._is_meaningful_assessment(item):
                                                        self.category_widgets["Other"].add_content(item)
                                                        print(f"[스크리닝] 'Other' 카테고리에 직접 추가")
                                            else:
                                                if self._is_meaningful_assessment(str(assessment_list)):
                                                    self.category_widgets["Other"].add_content(str(assessment_list))
                                                    print(f"[스크리닝] 'Other' 카테고리에 직접 추가")
                                        else:
                                            content_str = str(analysis_data)
                                            if self._is_meaningful_assessment(content_str):
                                                self.category_widgets["Other"].add_content(content_str)
                                                print(f"[스크리닝] 'Other' 카테고리에 직접 추가")
                        
                        # 분석 완료 후 버퍼 비우기
                        self.pending_analysis_buffer = ""
                        print(f"[스크리닝] 빠른 분석 완료, 버퍼 초기화")
                        
                    else:
                        print(f"[스크리닝] 빠른 분석 결과 없음 - 계속 누적")
                else:
                    print(f"[스크리닝] 충분하지 않은 내용 - 계속 누적 (현재 {len(self.pending_analysis_buffer)}/{self.min_analysis_length})")
                        
            else:
                print(f"[스크리닝] GPT 분석기 없음 - 원본 텍스트를 기타에 저장")
                if "Other" in self.category_widgets:
                    self.category_widgets["Other"].add_content(text)
                    
        except Exception as e:
            print(f"[ERROR] 스크리닝 분석 실패: {e}")
            import traceback
            traceback.print_exc()
            # 오류 발생 시에도 원본 텍스트를 기타에 추가
            try:
                if "Other" in self.category_widgets:
                    self.category_widgets["Other"].add_content(f"[분석 오류] {text}")
            except:
                pass
    
    def _has_meaningful_content(self, text):
        """텍스트에 의미있는 내용이 있는지 확인"""
        # 인터뷰에서 중요한 키워드들
        meaningful_keywords = [
            # 직업/경력 관련
            "manager", "director", "experience", "years", "company", "work", "job", "position", "role",
            # 기술/스킬 관련
            "skills", "technical", "project", "system", "tools", "software", "certification",
            # 교육/자격 관련
            "education", "degree", "university", "college", "training", "certification",
            # 급여/조건 관련
            "salary", "compensation", "benefits", "location", "relocate", "remote", "onsite",
            # 한국어 키워드들
            "경험", "회사", "연봉", "기술", "프로젝트", "관리", "팀", "업무", "담당", "개발"
        ]
        
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in meaningful_keywords if keyword in text_lower)
        
        # 키워드가 2개 이상 있거나, 텍스트가 길면 분석할 가치가 있다고 판단
        return keyword_count >= 2 or len(text) >= 200
    
    def _is_meaningful_assessment(self, assessment_text):
        """분석 결과가 의미있는 내용인지 확인 (강화된 버전)"""
        if not assessment_text or not isinstance(assessment_text, str):
            return False
        
        assessment_lower = assessment_text.lower().strip()
        
        # 의미 없는 표준 문구들 (더 강화)
        meaningless_phrases = [
            "no specific information provided",
            "not provided in the transcript",
            "no information available",
            "information not specified",
            "details not mentioned",
            "not discussed in detail",
            "no relevant information",
            "information unavailable",
            "not covered in interview",
            "transcript does not contain",
            "no data available",
            "insufficient information",
            "candidate did not provide",
            "not applicable",
            "not relevant",
            "analysis error",
            "analysis failed",
            "processing failed",
            "[category_name]",
            "{'other':",
            "{\"other\":",
            "content not provided",
            "information was not mentioned",
            # 새로운 의미없는 패턴들 추가
            "briefly introduced himself",
            "mentioned his current role",
            "introduced herself", 
            "mentioned her current role",
            "candidate introduced",
            "mentioned their role",
            "general introduction",
            "basic introduction",
            "candidate briefly",
            "mentioned working at",
            "talked about their",
            "discussed their current",
            "provided general information",
            "gave an overview",
            "shared basic details",
            # 메타 코멘트 차단
            "interview text appears to be",
            "does not provide any meaningful information",
            "text appears garbled",
            "no meaningful information",
            "appears to be garbled",
            "does not provide meaningful",
            "text does not provide",
            "information appears to be",
            "content appears to be",
            "seems to be garbled",
            "analysis appears incomplete"
        ]
        
        # 의미 없는 문구가 포함되어 있으면 False
        for phrase in meaningless_phrases:
            if phrase in assessment_lower:
                print(f"[의미없는 내용 필터] 차단된 문구: '{phrase}' in '{assessment_text[:50]}...'")
                return False
        
        # 너무 짧은 내용도 의미 없음 (15자 미만으로 강화)
        if len(assessment_lower) < 15:
            print(f"[의미없는 내용 필터] 너무 짧은 내용: {len(assessment_lower)}자")
            return False
        
        # JSON 같은 원시 데이터 형태면 False
        if assessment_text.strip().startswith(("{", "[")):
            print(f"[의미없는 내용 필터] JSON 원시 데이터 형태")
            return False
        
        # 구체성 검사: 구체적인 정보가 포함되어야 함
        if not self._has_specific_information(assessment_text):
            print(f"[의미없는 내용 필터] 구체적 정보 부족: '{assessment_text[:50]}...'")
            return False
        
        return True

    def _has_specific_information(self, text):
        """텍스트에 구체적인 정보가 있는지 확인 (개선된 버전 - 감정/동기 포함)"""
        import re
        
        # 구체적 정보 패턴들 (감정/동기/가치관 추가)
        specific_patterns = [
            r'\d+',  # 숫자
            r'\$[\d,]+',  # 금액
            r'[A-Z][a-zA-Z\s&]+(Inc|Corp|LLC|Company|Solutions|Logistics|Group)',  # 회사명
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # 사람 이름 (First Last)
            r'\b(?:manager|director|analyst|specialist|coordinator|supervisor|lead|executive)\b',  # 직책
            r'\b(?:years?|months?)\s+(?:of\s+)?(?:experience|work)',  # 경험 기간
            r'\b(?:bachelor|master|mba|phd|degree|certification)\b',  # 학력/자격
            r'\b(?:payroll|HRIS|SAP|Oracle|Workday|SuccessFactors)\b',  # 시스템/도구
            r'\b(?:onsite|remote|hybrid|relocate|travel)\b',  # 근무 조건
            # HR 전문 용어
            r'\b(?:benefits|compensation|labor\s+relations|union|grievance|compliance|OSHA|FMLA|EEOC)\b',
            r'\b(?:recruitment|hiring|onboarding|training|performance|appraisal)\b',
            r'\b(?:policies|procedures|handbook|documentation|audit)\b',
            r'\b(?:coordination|administration|management|oversight|supervision)\b',
            r'\b(?:multi-state|multi-site|cross-functional|direct\s+reports)\b',
            r'\b(?:negotiation|contract|agreement|policy)\b',
            # 동작/행위 관련 구체적 표현
            r'\b(?:led|managed|coordinated|administered|supervised|implemented|developed|established)\b',
            r'\b(?:expertise|experience|proficient|skilled|knowledgeable)\b',
            
            # 🎯 감정/동기/가치관 패턴 추가
            r'\b(?:passionate|excited|motivated|enthusiastic|interested|drawn|attracted)\b',  # 감정 표현
            r'\b(?:believe|value|prioritize|focus|emphasize|commit)\b',  # 가치관/신념
            r'\b(?:goal|aspiration|vision|mission|purpose|objective)\b',  # 목표/비전
            r'\b(?:challenging|opportunity|growth|development|learning|improvement)\b',  # 성장 지향
            r'\b(?:culture|environment|team|collaboration|relationship|communication)\b',  # 문화적 적합성
            r'\b(?:innovation|creativity|problem-solving|solution|strategic)\b',  # 사고방식
            r'\b(?:leadership|responsibility|accountability|integrity|transparency)\b',  # 리더십 가치
            r'\b(?:work-life|balance|flexibility|autonomy|empowerment)\b',  # 근무 가치관
            
            # 감정 표현 구문 패턴
            r'(?:I\s+(?:am|feel|think|believe|want|hope|enjoy|love|prefer))',  # "I am passionate", "I believe" 등
            r'(?:what\s+(?:excites|motivates|drives|inspires)\s+me)',  # "What excites me"
            r'(?:(?:my|our)\s+(?:goal|mission|vision|approach|philosophy))',  # "My goal is"
            r'(?:looking\s+for|seeking|hoping\s+to|wanting\s+to)',  # 추구하는 것
            
            # 추가 구체적 정보 패턴 (스크립트 기반)
            r'\b(?:Savannah|Atlanta|Chicago|New York|Los Angeles|relocate|relocation)\b',  # 위치/이주 정보
            r'\b(?:notice|timeline|available|start|transition)\b',  # 타이밍 정보
            r'\b(?:Kenco|Hyundai|Glovis|automotive|manufacturing|packaging)\b',  # 회사/산업 정보
            r'\b\d+\s*(?:week|staff|member|direct\s+report)',  # 구체적 수치 정보
            r'\b(?:VP|General\s+Manager|Director|accessibility|diverse)',  # 리더십 정보
        ]
        
        text_lower = text.lower()
        specific_count = 0
        matched_patterns = []
        
        for pattern in specific_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                specific_count += len(matches)
                matched_patterns.append(pattern)
        
        # 임계값을 1개로 유지 (감정 표현도 중요한 정보)
        is_specific = specific_count >= 1
        
        if not is_specific:
            print(f"[구체성 검사] 구체적 정보 부족: {specific_count}개 발견")
            print(f"  텍스트: '{text[:60]}...'")
        else:
            print(f"[구체성 검사] 구체적 정보 충분: {specific_count}개 발견 (감정/동기 포함)")
            print(f"  매칭 패턴: {matched_patterns[:3]}...")  # 처음 3개만 표시
        
        return is_specific
    
    def _reassign_category_with_gpt(self, unknown_category, content_data, available_categories):
        """GPT를 사용하여 알 수 없는 카테고리를 적절한 카테고리로 재분류"""
        try:
            # GPT Summarizer 가져오기 (이미 위에서 확인했으므로 간단하게)
            current_widget = self
            level = 0
            main_window = None
            
            while current_widget and level < 5:
                if hasattr(current_widget, 'gpt_summarizer'):
                    main_window = current_widget
                    break
                current_widget = current_widget.parent()
                level += 1
            
            if not main_window or not hasattr(main_window, 'gpt_summarizer'):
                print(f"[재분류] GPT 분석기 없음 - 재분류 실패")
                return None
            
            gpt = main_window.gpt_summarizer
            
            # 내용 추출
            if isinstance(content_data, dict) and "assessment" in content_data:
                content_text = str(content_data["assessment"])
            else:
                content_text = str(content_data)
            
            # GPT 재분류 프롬프트
            reassign_prompt = f"""
Given the following content originally categorized as "{unknown_category}", determine the most appropriate category from the available options:

Available Categories: {', '.join(available_categories)}

Content: {content_text}

Return ONLY the most appropriate category name from the available list. If none fit well, return "Other".

Response format: [Category_Name]
"""
            
            response = gpt.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional content categorization expert. Return only the most appropriate category name."},
                    {"role": "user", "content": reassign_prompt}
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            result = response.choices[0].message.content.strip()
            
            # 결과에서 카테고리명 추출 (괄호 제거)
            if result.startswith('[') and result.endswith(']'):
                result = result[1:-1]
            
            # 유효한 카테고리인지 확인
            if result in available_categories:
                print(f"[재분류] GPT 추천: '{unknown_category}' → '{result}'")
                return result
            else:
                print(f"[재분류] GPT 결과 '{result}'가 유효하지 않음")
                return None
                
        except Exception as e:
            print(f"[재분류] GPT 재분류 실패: {e}")
            return None
    
    def manual_process(self):
        """수동 분석 버튼 클릭 - 현재 텍스트와 누적 버퍼 모두 처리 (빠른 분석)"""
        current_text = self.live_text_edit.toPlainText()
        
        # 현재 텍스트가 있으면 버퍼에 추가
        if current_text:
            if self.pending_analysis_buffer:
                self.pending_analysis_buffer += "\n" + current_text
            else:
                self.pending_analysis_buffer = current_text
        
        # 누적된 버퍼가 있으면 강제로 분석 실행
        if self.pending_analysis_buffer.strip():
            print(f"[수동분석] 빠른 분석 시작 (길이: {len(self.pending_analysis_buffer)})")
            
            # MainWindow에서 GPT 분석기 찾기
            current_widget = self
            main_window = None
            level = 0
            
            while current_widget and level < 10:
                if hasattr(current_widget, 'gpt_summarizer'):
                    main_window = current_widget
                    break
                current_widget = current_widget.parent()
                level += 1
            
            if main_window and hasattr(main_window, 'gpt_summarizer'):
                gpt = main_window.gpt_summarizer
                
                # 빠른 카테고리 분류 실행
                categories = list(self.template.get("screening_categories", []))
                if "Other" not in categories:
                    categories.append("Other")
                
                categorized_result = gpt.quick_categorize_text(self.pending_analysis_buffer, categories)
                
                if categorized_result:
                    print(f"[수동분석] 분석 완료: {len(categorized_result)}개 카테고리")
                    
                    # 분석 결과를 각 카테고리에 추가
                    for category, analysis_data in categorized_result.items():
                        if category in self.category_widgets:
                            if isinstance(analysis_data, dict) and "assessment" in analysis_data:
                                assessment_list = analysis_data["assessment"]
                                if isinstance(assessment_list, list):
                                    for item in assessment_list:
                                        if self._is_meaningful_assessment(item):
                                            self.category_widgets[category].add_content(item)
                                else:
                                    if self._is_meaningful_assessment(str(assessment_list)):
                                        self.category_widgets[category].add_content(str(assessment_list))
                    
                    # 버퍼 비우기
                    self.pending_analysis_buffer = ""
                    print(f"[수동분석] 완료, 버퍼 초기화")
                    
                    QMessageBox.information(self, "분석 완료", f"빠른 분석이 완료되었습니다!\n{len(categorized_result)}개 카테고리로 분류됨")
                else:
                    QMessageBox.warning(self, "분석 실패", "분석 결과를 가져올 수 없습니다.")
            else:
                QMessageBox.warning(self, "오류", "GPT 분석기를 찾을 수 없습니다.")
        else:
            QMessageBox.information(self, "알림", "분석할 텍스트가 없습니다.")
    
    def export_screening_notes(self):
        """스크리닝 노트를 파일로 저장"""
        try:
            # 파일 저장 위치 선택 - 영어 파일명
            candidate_name = self.template.get("candidate_name", "Participant")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"Interview_Screening_{candidate_name}_{timestamp}.txt"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Screening Results",
                default_filename,
                "Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                # 스크리닝 보고서 생성
                report_content = self.generate_screening_report()
                
                # 안전한 ASCII 인코딩으로 저장 (한글 문제 완전 회피)
                with open(file_path, 'w', encoding='ascii', errors='replace') as f:
                    f.write(report_content)
                
                QMessageBox.information(self, "Save Complete", f"Screening results saved successfully:\n{file_path}")
                
        except Exception as e:
            import traceback
            print(f"[ERROR] File save error: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "Save Error", f"An error occurred while saving the file: {str(e)}")
    
    def generate_screening_report(self):
        """스크리닝 보고서 생성 - 영어로 저장"""
        report_lines = []
        
        # 헤더
        report_lines.append("=" * 60)
        report_lines.append("Interview Screening Report")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # 후보자 정보
        report_lines.append("[Candidate Information]")
        report_lines.append(f"Name: {self.template.get('candidate_name', 'Not entered')}")
        report_lines.append(f"Position: {self.template.get('position', 'Not entered')}")
        report_lines.append(f"Location: {self.template.get('location', 'Not entered')}")
        report_lines.append(f"Education: {self.template.get('education', 'Not entered')}")
        report_lines.append(f"Experience: {self.template.get('experience', 'Not entered')}")
        report_lines.append(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # 스크리닝 결과
        report_lines.append("[Screening Assessment Results]")
        report_lines.append("")
        
        # 각 카테고리별 평가 (물음표 없이 깔끔하게)
        for category in self.template["screening_categories"]:
            if category in self.category_widgets:
                content = self.category_widgets[category].get_content()
                if content.strip():
                    report_lines.append(f"- {category}")
                    # 내용을 줄별로 정리
                    lines = content.strip().split('\n')
                    for line in lines:
                        if line.strip():
                            report_lines.append(f"  - {line}")
                    report_lines.append("")
        
        # 기타 정보 (내용이 있을 때만 표시)
        other_content = self.category_widgets["Other"].get_content()
        if other_content.strip():
            report_lines.append("- Other Important Information")
            lines = other_content.strip().split('\n')
            for line in lines:
                if line.strip():
                    report_lines.append(f"  - {line}")
            report_lines.append("")
        
        # 전체 요약
        summary = self.get_screening_summary()
        if summary:
            report_lines.append("[Overall Summary]")
            report_lines.append(summary)
            report_lines.append("")
        
        report_lines.append("=" * 60)
        
        return '\n'.join(report_lines)
    
    def get_screening_summary(self):
        """전체 스크리닝 요약 생성"""
        try:
            # 모든 카테고리의 내용 수집
            all_content = []
            
            for category in self.template["screening_categories"]:
                if category in self.category_widgets:
                    content = self.category_widgets[category].get_content()
                    if content.strip():
                        all_content.append(f"{category}: {content}")
            
            # 기타 정보도 포함
            other_content = self.category_widgets["Other"].get_content()
            if other_content.strip():
                all_content.append(f"Others: {other_content}")
            
            if all_content:
                combined_text = '\n'.join(all_content)
                
                # GPT를 통해 전체 요약 생성
                if hasattr(self.parent(), 'gpt_summarizer'):
                    gpt = self.parent().gpt_summarizer
                    return gpt.summarize_interview_screening(combined_text)
            
            return "No content to evaluate."
            
        except Exception as e:
            return f"Error occurred while generating summary: {str(e)}"
    
    def go_to_summary(self):
        """요약 완성 화면으로 이동 (구현예정)"""
        # (구현예정): 3번째 UI로 전환
        # 1. 현재 스크리닝 데이터 수집
        # 2. SummaryWidget으로 데이터 전달
        # 3. MainWindow에서 화면 전환
        
        try:
            # 현재 스크리닝 데이터 수집
            screening_data = {}
            for category in self.template["screening_categories"]:
                if category in self.category_widgets:
                    content = self.category_widgets[category].get_content()
                    if content.strip():
                        screening_data[category] = content
            
            # 기타 정보도 포함
            other_content = self.category_widgets["Other"].get_content()
            if other_content.strip():
                screening_data["Other"] = other_content
            
            # 부모 윈도우에서 요약 화면으로 전환
            # MainWindow에서 show_summary_widget 메서드를 구현해야 함
            if hasattr(self.parent(), 'show_summary_widget'):
                self.parent().show_summary_widget(self.template, screening_data)
            else:
                QMessageBox.information(
                    self, 
                    "Implementation Pending", 
                    "Summary completion feature will be implemented.\n"
                    f"Collected {len(screening_data)} categories of screening data."
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error switching to summary: {str(e)}") 