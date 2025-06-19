import time
import mss
import numpy as np
from PIL import Image


def capture_region(region, interval=2):
    """
    지정된 화면 영역(region)을 interval(초)마다 캡처하여 PIL 이미지로 반환합니다.
    region: dict, 예시: {'top': 100, 'left': 100, 'width': 800, 'height': 300}
    interval: 캡처 주기(초)
    """
    with mss.mss() as sct:
        while True:
            sct_img = sct.grab(region)
            img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
            yield img
            time.sleep(interval)


def capture_once(region):
    """
    지정된 영역을 한 번만 캡처하여 PIL 이미지로 반환합니다.
    """
    with mss.mss() as sct:
        sct_img = sct.grab(region)
        img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
        return img 