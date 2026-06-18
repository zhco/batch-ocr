"""
批量文字识别 - PaddleOCR 离线引擎
框架：KivyMD + RapidOCR (ONNX Runtime)
模型：ch_PP-OCRv4，约 8MB，离线可用
"""

import os
import threading
from pathlib import Path

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineListItem

KV = """
ScreenManager:
    MainScreen:

<MainScreen>:
    name: "main"
    MDTopAppBar:
        id: toolbar
        title: "批量OCR(Paddle)"
        pos_hint: {"top": 1}
        right_action_items: [["folder", lambda x: app.select_dir()]]

    MDFloatLayout:

        MDLabel:
            id: status_label
            text: "请点击右上角选择图片目录"
            halign: "center"
            pos_hint: {"center_x": 0.5, "y": 0.84}
            size_hint_x: 0.9
            font_style: "Subtitle1"

        MDLabel:
            id: dir_label
            text: ""
            halign: "center"
            pos_hint: {"center_x": 0.5, "y": 0.79}
            size_hint_x: 0.9
            font_style: "Caption"
            theme_text_color: "Hint"

        ScrollView:
            pos_hint: {"center_x": 0.5, "top": 0.76}
            size_hint: 0.95, 0.52
            MDList:
                id: file_list

        MDProgressBar:
            id: progress_bar
            pos_hint: {"center_x": 0.5, "y": 0.16}
            size_hint_x: 0.85
            max: 100
            value: 0
            type: "determinate"

        MDRaisedButton:
            id: run_button
            text: "开始识别"
            pos_hint: {"center_x": 0.5, "y": 0.06}
            on_release: app.start_ocr()
            md_bg_color: app.theme_cls.primary_color
            disabled: True
"""


class MainScreen(Screen):
    pass


class BatchOCRApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_dir = ""
        self.image_files = []
        self.engine = None
        self._lock = threading.Lock()

    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.theme_style = "Light"
        return Builder.load_string(KV)

    def select_dir(self):
        from kivymd.uix.textfield import MDTextField

        content = MDTextField(
            hint_text="输入图片所在目录路径",
            text=self.current_dir or "/sdcard/Pictures",
            mode="rectangle",
        )
        self.dialog = MDDialog(
            title="选择目录",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="取消", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(
                    text="确定",
                    on_release=lambda x: self._on_dir_selected(content.text),
                ),
            ],
        )
        self.dialog.open()

    def _on_dir_selected(self, path):
        self.dialog.dismiss()
        path = path.strip()
        if not os.path.isdir(path):
            self.show_dialog(f"目录不存在:\n{path}")
            return
        self.current_dir = path
        self._scan_images()

    def _scan_images(self):
        exts = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
        files = sorted([
            p for p in Path(self.current_dir).iterdir()
            if p.is_file() and p.suffix.lower() in exts
        ])
        self.image_files = [str(f) for f in files]

        screen = self.root.get_screen("main")
        screen.ids.dir_label.text = f"{self.current_dir}  ({len(self.image_files)} 张)"
        screen.ids.file_list.clear_widgets()

        if not self.image_files:
            screen.ids.status_label.text = "该目录下未找到图片"
            screen.ids.run_button.disabled = True
            return

        for f in self.image_files:
            screen.ids.file_list.add_widget(
                OneLineListItem(text=os.path.basename(f))
            )
        screen.ids.status_label.text = f"共 {len(self.image_files)} 张待识别"
        screen.ids.run_button.disabled = False

    def start_ocr(self):
        if not self.image_files:
            return
        screen = self.root.get_screen("main")
        screen.ids.run_button.disabled = True
        screen.ids.progress_bar.value = 0

        output_dir = os.path.join(
            os.path.dirname(self.current_dir) or "/sdcard/Documents",
            "ocr_output"
        )
        os.makedirs(output_dir, exist_ok=True)

        threading.Thread(
            target=self._run_ocr, args=(output_dir,), daemon=True
        ).start()

    def _init_engine(self):
        """初始化 RapidOCR 引擎（首次加载模型约 2-3 秒）"""
        from rapidocr_onnxruntime import RapidOCR
        self.engine = RapidOCR(
            text_score=0.5,
            det_use_cuda=False,
            cls_use_cuda=False,
            rec_use_cuda=False,
        )

    def _run_ocr(self, output_dir):
        with self._lock:
            if self.engine is None:
                Clock.schedule_once(
                    lambda dt: self._update_status("正在加载 PaddleOCR 模型...")
                )
                try:
                    self._init_engine()
                except Exception as e:
                    Clock.schedule_once(
                        lambda dt: self.show_dialog(
                            f"引擎加载失败:\n{e}\n\n"
                            "请确认已安装:\npip install rapidocr-onnxruntime"
                        )
                    )
                    Clock.schedule_once(lambda dt: self._enable_button())
                    return

            total = len(self.image_files)
            success = 0

            for idx, img_path in enumerate(self.image_files):
                name = os.path.basename(img_path)
                Clock.schedule_once(
                    lambda dt, i=idx, n=name: self._update_progress(i, total, n)
                )

                try:
                    result, _ = self.engine(img_path)

                    txt_name = Path(img_path).stem + ".txt"
                    txt_path = os.path.join(output_dir, txt_name)

                    if result:
                        lines = [item[1] for item in result if item[1]]
                        text = "\n".join(lines)
                    else:
                        text = ""

                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(text)

                    success += 1
                except Exception:
                    continue

            Clock.schedule_once(
                lambda dt: setattr(
                    self.root.get_screen("main").ids.progress_bar, "value", 100
                )
            )
            Clock.schedule_once(
                lambda dt: self._update_status(
                    f"完成！成功 {success}/{total}\n结果: {output_dir}"
                )
            )
            Clock.schedule_once(lambda dt: self._enable_button())

    def _update_status(self, msg):
        self.root.get_screen("main").ids.status_label.text = msg

    def _update_progress(self, idx, total, name):
        screen = self.root.get_screen("main")
        pct = int((idx + 1) / total * 100) if total else 0
        screen.ids.progress_bar.value = pct
        screen.ids.status_label.text = f"[{idx + 1}/{total}] {name}"

    def _enable_button(self):
        self.root.get_screen("main").ids.run_button.disabled = False

    def show_dialog(self, msg):
        self.dialog = MDDialog(
            text=msg,
            buttons=[MDFlatButton(text="确定", on_release=lambda x: self.dialog.dismiss())],
        )
        self.dialog.open()


if __name__ == "__main__":
    BatchOCRApp().run()
