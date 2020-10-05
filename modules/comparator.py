import pyautogui


def compare_screenshots(source, target):
    return pyautogui.locate(source, target, confidence=0.95)
