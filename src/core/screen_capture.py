import mss
import numpy as np
from PIL import Image
from PyQt6.QtWidgets import QApplication, QRubberBand, QWidget, QLabel
from PyQt6.QtCore import Qt, QRect, QPoint, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QScreen, QPixmap, QFont
import threading

class RegionSelector(QWidget):
    """영역 선택을 위한 오버레이 위젯"""
    
    def __init__(self):
        super().__init__()
        self.setupUI()
        
        self.start_point = None
        self.end_point = None
        self.selected_region = None
        self.is_selecting = False
        
    def setupUI(self):
        """UI 설정"""
        # 윈도우 플래그 설정
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # 속성 설정
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        # 전체 화면으로 설정
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            self.setGeometry(geometry)
            
        # 배경 설정
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 30);
            }
        """)
        
        # 안내 텍스트
        self.instruction_label = QLabel("마우스를 드래그하여 캡처할 영역을 선택하세요. ESC키로 취소", self)
        self.instruction_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 150);
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        self.instruction_label.move(50, 50)
        self.instruction_label.adjustSize()
        
        # 커서 설정
        self.setCursor(Qt.CursorShape.CrossCursor)
        
        print("[RegionSelector] 초기화 완료")
        
    def showEvent(self, event):
        """위젯이 표시될 때"""
        print("[RegionSelector] 표시됨")
        super().showEvent(event)
        
        # 전체 화면으로 다시 설정
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())
            
        # 포커스 설정
        self.setFocus()
        self.raise_()
        self.activateWindow()
        
    def keyPressEvent(self, event):
        """키 입력 처리"""
        if event.key() == Qt.Key.Key_Escape:
            print("[RegionSelector] ESC 키로 취소")
            self.selected_region = None
            self.close()
        super().keyPressEvent(event)
        
    def mousePressEvent(self, event):
        """마우스 클릭 시작"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.position().toPoint()
            self.is_selecting = True
            print(f"[RegionSelector] 선택 시작: {self.start_point}")
            
    def mouseMoveEvent(self, event):
        """마우스 드래그"""
        if self.is_selecting and self.start_point:
            self.end_point = event.position().toPoint()
            self.update()  # 화면 다시 그리기
            
    def mouseReleaseEvent(self, event):
        """마우스 클릭 끝"""
        if event.button() == Qt.MouseButton.LeftButton and self.start_point and self.end_point:
            # 선택된 영역 계산
            x1, y1 = self.start_point.x(), self.start_point.y()
            x2, y2 = self.end_point.x(), self.end_point.y()
            
            x = min(x1, x2)
            y = min(y1, y2)
            w = abs(x2 - x1)
            h = abs(y2 - y1)
            
            # 최소 크기 체크
            if w > 10 and h > 10:
                self.selected_region = (x, y, w, h)
                print(f"[RegionSelector] 영역 선택 완료: {self.selected_region}")
            else:
                print("[RegionSelector] 영역이 너무 작음")
                self.selected_region = None
                
            self.close()
            
    def paintEvent(self, event):
        """그리기 이벤트"""
        painter = QPainter(self)
        
        # 반투명 배경
        painter.fillRect(self.rect(), QColor(0, 0, 0, 30))
        
        # 선택 영역 그리기
        if self.start_point and self.end_point:
            # 선택 사각형
            rect = QRect(self.start_point, self.end_point)
            
            # 선택 영역 하이라이트 (투명하게)
            painter.fillRect(rect, QColor(255, 0, 0, 50))
            
            # 선택 영역 테두리
            pen = QPen(QColor(255, 0, 0), 2)
            painter.setPen(pen)
            painter.drawRect(rect)
            
            # 크기 정보 텍스트
            size_text = f"{rect.width()} x {rect.height()}"
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(rect.bottomRight() + QPoint(5, 5), size_text)

class ScreenCapture:
    """화면 캡처 클래스 (다중 모니터 대응)"""
    
    def __init__(self):
        self._local = threading.local()

    @property
    def sct(self):
        """스레드별로 mss 인스턴스 생성 또는 반환"""
        if not hasattr(self._local, 'sct_instance'):
            self._local.sct_instance = mss.mss()
        return self._local.sct_instance

    @property
    def monitors(self):
        """스레드-안전한 모니터 정보 반환"""
        return self.sct.monitors
        
    def select_region(self):
        """
        사용자가 마우스로 영역을 선택할 수 있는 인터페이스 제공
        
        Returns:
            tuple: (x, y, width, height) 형식의 선택된 영역, 취소시 None
        """
        print("[ScreenCapture] 영역 선택 시작")
        
        app = QApplication.instance()
        if app is None:
            print("[ScreenCapture] QApplication 인스턴스 없음")
            return None
        
        # 기존 selector가 있다면 닫기
        for widget in app.allWidgets():
            if isinstance(widget, RegionSelector):
                widget.close()
                
        selector = RegionSelector()
        
        # 강제로 표시
        selector.show()
        selector.showFullScreen()
        selector.raise_()
        selector.activateWindow()
        
        print("[ScreenCapture] RegionSelector 표시됨")
        
        # 이벤트 루프 실행 (모달 방식)
        while selector.isVisible():
            app.processEvents()
            QTimer.singleShot(10, lambda: None)  # 10ms 대기
            
        result = selector.selected_region
        print(f"[ScreenCapture] 영역 선택 결과: {result}")
        
        return result
    
    def capture_screen(self, region=None):
        """화면 캡처 (전체 또는 지정 영역)"""
        try:
            if region is None:
                # 전체 화면 캡처 (모든 모니터 포함)
                monitor = self.monitors[0]  # 모든 모니터를 포함하는 가상 모니터
                screenshot = self.sct.grab(monitor)
                
                # PIL Image로 변환
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                return img
            else:
                # 지정된 영역 캡처
                return self.capture(region)
            
        except Exception as e:
            print(f"[ScreenCapture] 화면 캡처 실패: {e}")
            return None
        
    def capture_region(self, region):
        """
        지정된 영역을 캡처하여 PIL 이미지로 반환
        
        Args:
            region (tuple): (x, y, width, height) 형식의 캡처 영역
            
        Returns:
            PIL.Image: 캡처된 이미지
        """
        return self.capture(region)
        
    def capture(self, region):
        """
        지정된 영역을 캡처하여 PIL 이미지로 반환
        
        Args:
            region (tuple): (x, y, width, height) 형식의 캡처 영역
            
        Returns:
            PIL.Image: 캡처된 이미지
        """
        x, y, width, height = region
        
        # 선택한 좌표가 어느 모니터에 속하는지 판별
        monitor_idx = self._find_monitor(x, y)
        if monitor_idx is None:
            # 못 찾으면 전체 화면에서 캡처
            monitor = {"top": y, "left": x, "width": width, "height": height}
        else:
            mon = self.monitors[monitor_idx]
            # 선택 영역을 해당 모니터 기준 상대좌표로 변환
            rel_x = x - mon["left"]
            rel_y = y - mon["top"]
            monitor = {
                "top": mon["top"] + rel_y,
                "left": mon["left"] + rel_x,
                "width": width,
                "height": height
            }
        
        # 화면 캡처
        sct_img = self.sct.grab(monitor)
        
        # PIL 이미지로 변환
        img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
        
        return img
        
    def _find_monitor(self, x, y):
        # [1]부터 각 모니터의 영역을 확인
        for idx, mon in enumerate(self.monitors[1:], 1):
            if (mon["left"] <= x < mon["left"] + mon["width"] and
                mon["top"] <= y < mon["top"] + mon["height"]):
                return idx
        return None

    def __del__(self):
        """소멸자"""
        self.sct.close() 