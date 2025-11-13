# om kivy.app import App
from kivymd.uix.filemanager import MDFileManager
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooserListView
from plyer import filechooser
import os
import struct
import lzma
import threading
import filetype
from kivy.clock import Clock
from typing import List, Optional
from pathlib import Path
from android.permissions import request_permissions, Permission
from android import activity
from jnius import autoclass, cast
from android.runnable import run_on_ui_thread
from kivy.core.text import LabelBase
from kivymd.font_definitions import theme_font_styles
LabelBase.register(name="font_ch", fn_regular="simkai.ttf")
theme_font_styles.append('font_ch')
# from kivy.config import Config

def callback(request_code, result_code, intent):
    files = []
    if intent:
        # 支持多选
        if intent.getClipData():
            clip = cast('android.content.ClipData', intent.getClipData())
            for i in range(clip.getItemCount()):
                files.append(str(clip.getItemAt(i).getUri().toString()))
        elif intent.getData():
            files.append(str(intent.getData().toString()))
    print("Selected files:", files)

# Config.set('kivy', 'default_font', ['SimHei', 'Arial'])
activity.bind(on_activity_result=callback)
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Environment = autoclass('android.os.Environment')
Settings = autoclass('android.provider.Settings')
Intent = autoclass('android.content.Intent')
Uri = autoclass('android.net.Uri')

def has_all_files_permission():
    context = PythonActivity.mActivity
    if Environment.isExternalStorageManager():
        return True
    else:
        return False

def request_manage_all_files():
    activity = PythonActivity.mActivity
    uri = Uri.parse(f"package:{activity.getPackageName()}")
    intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION, uri)
    activity.startActivity(intent)

class KuGou:
    HEADER_LEN = 1024
    OWN_KEY_LEN = 17
    PUB_KEY_LEN = 1170494464
    PUB_KEY_LEN_MAGNIFICATION = 16
    MAGIC_HEADER = bytes([
        0x7c, 0xd5, 0x32, 0xeb, 0x86, 0x02, 0x7f, 0x4b, 0xa8, 0xaf, 0xa6, 0x8e, 0x0f, 0xff, 0x99,
        0x14, 0x00, 0x04, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
    ])
    
    PUB_KEY_MEND = bytes([
        0xB8, 0xD5, 0x3D, 0xB2, 0xE9, 0xAF, 0x78, 0x8C, 0x83, 0x33, 0x71, 0x51, 0x76, 0xA0,
        0xCD, 0x37, 0x2F, 0x3E, 0x35, 0x8D, 0xA9, 0xBE, 0x98, 0xB7, 0xE7, 0x8C, 0x22, 0xCE,
        0x5A, 0x61, 0xDF, 0x68, 0x69, 0x89, 0xFE, 0xA5, 0xB6, 0xDE, 0xA9, 0x77, 0xFC, 0xC8,
        0xBD, 0xBD, 0xE5, 0x6D, 0x3E, 0x5A, 0x36, 0xEF, 0x69, 0x4E, 0xBE, 0xE1, 0xE9, 0x66,
        0x1C, 0xF3, 0xD9, 0x02, 0xB6, 0xF2, 0x12, 0x9B, 0x44, 0xD0, 0x6F, 0xB9, 0x35, 0x89,
        0xB6, 0x46, 0x6D, 0x73, 0x82, 0x06, 0x69, 0xC1, 0xED, 0xD7, 0x85, 0xC2, 0x30, 0xDF,
        0xA2, 0x62, 0xBE, 0x79, 0x2D, 0x62, 0x62, 0x3D, 0x0D, 0x7E, 0xBE, 0x48, 0x89, 0x23,
        0x02, 0xA0, 0xE4, 0xD5, 0x75, 0x51, 0x32, 0x02, 0x53, 0xFD, 0x16, 0x3A, 0x21, 0x3B,
        0x16, 0x0F, 0xC3, 0xB2, 0xBB, 0xB3, 0xE2, 0xBA, 0x3A, 0x3D, 0x13, 0xEC, 0xF6, 0x01,
        0x45, 0x84, 0xA5, 0x70, 0x0F, 0x93, 0x49, 0x0C, 0x64, 0xCD, 0x31, 0xD5, 0xCC, 0x4C,
        0x07, 0x01, 0x9E, 0x00, 0x1A, 0x23, 0x90, 0xBF, 0x88, 0x1E, 0x3B, 0xAB, 0xA6, 0x3E,
        0xC4, 0x73, 0x47, 0x10, 0x7E, 0x3B, 0x5E, 0xBC, 0xE3, 0x00, 0x84, 0xFF, 0x09, 0xD4,
        0xE0, 0x89, 0x0F, 0x5B, 0x58, 0x70, 0x4F, 0xFB, 0x65, 0xD8, 0x5C, 0x53, 0x1B, 0xD3,
        0xC8, 0xC6, 0xBF, 0xEF, 0x98, 0xB0, 0x50, 0x4F, 0x0F, 0xEA, 0xE5, 0x83, 0x58, 0x8C,
        0x28, 0x2C, 0x84, 0x67, 0xCD, 0xD0, 0x9E, 0x47, 0xDB, 0x27, 0x50, 0xCA, 0xF4, 0x63,
        0x63, 0xE8, 0x97, 0x7F, 0x1B, 0x4B, 0x0C, 0xC2, 0xC1, 0x21, 0x4C, 0xCC, 0x58, 0xF5,
        0x94, 0x52, 0xA3, 0xF3, 0xD3, 0xE0, 0x68, 0xF4, 0x00, 0x23, 0xF3, 0x5E, 0x0A, 0x7B,
        0x93, 0xDD, 0xAB, 0x12, 0xB2, 0x13, 0xE8, 0x84, 0xD7, 0xA7, 0x9F, 0x0F, 0x32, 0x4C,
        0x55, 0x1D, 0x04, 0x36, 0x52, 0xDC, 0x03, 0xF3, 0xF9, 0x4E, 0x42, 0xE9, 0x3D, 0x61,
        0xEF, 0x7C, 0xB6, 0xB3, 0x93, 0x50,
    ])
    
    _keys_lock = threading.Lock()
    _keys = None

    @classmethod
    def _get_keys(cls):
        with cls._keys_lock:
            if cls._keys is None:
                with open('kugou_key.xz', 'rb') as f:
                    compressed_data = f.read()
                
                decompressed_size = cls.PUB_KEY_LEN // cls.PUB_KEY_LEN_MAGNIFICATION
                decompressed_data = lzma.decompress(compressed_data)
                
                if len(decompressed_data) != decompressed_size:
                    raise Exception("Failed to decode the KuGou key")
                
                cls._keys = decompressed_data
        return cls._keys

    def __init__(self, file_obj):
        header = file_obj.read(self.HEADER_LEN)
        if len(header) != self.HEADER_LEN or not header.startswith(self.MAGIC_HEADER):
            raise ValueError("Invalid KGM data")
        
        self.origin = file_obj
        self.own_key = bytearray(self.OWN_KEY_LEN)
        self.own_key[:16] = header[0x1c:0x2c]
        self.pos = 0

    def read(self, size=-1):
        if size == -1:
            data = self.origin.read()
        else:
            data = self.origin.read(size)
        
        if not data:
            return b''
        
        keys = self._get_keys()
        audio = bytearray(data)
        start_pos = self.pos
        
        for i in range(len(audio)):
            global_pos = start_pos + i
            
            own_key_byte = self.own_key[global_pos % self.OWN_KEY_LEN] ^ audio[i]
            own_key_byte ^= (own_key_byte & 0x0f) << 4
            
            key_index = global_pos // self.PUB_KEY_LEN_MAGNIFICATION
            pub_key_byte = self.PUB_KEY_MEND[global_pos % len(self.PUB_KEY_MEND)] ^ keys[key_index]
            pub_key_byte ^= (pub_key_byte & 0xf) << 4
            
            audio[i] = own_key_byte ^ pub_key_byte
        
        self.pos += len(audio)
        return bytes(audio)

def decode_files(files: List[Path]):
    """
    解码文件列表
    
    Args:
        files: 要解码的文件路径列表
        config: 配置字典，包含 'keep_file' 等选项
    
    Returns:
        成功解码的文件数量
    """
    count = 0
    buf_size = 16 * 1024  # 16KB 缓冲区
    
    for file_path in files:
        file_path = Path(file_path)
        try:
            with open(file_path, 'rb') as file_obj:
                try:
                    origin = KuGou(file_obj).read()
                except Exception:
                    raise Exception(f"Skip: \"{file_path}\", can't decode")
                    continue
        except FileNotFoundError:
            raise Exception(f'Skip: "{file_path}", file not found')
            continue
        
        original_ext = file_path.suffix
        if not original_ext:
            original_ext = '.mp3'
        else:
            original_ext = original_ext[1:]
        
        ext = original_ext
        
        # 使用文件类型推断
        head_buffer = bytearray(origin[:8192])
        try:
            kind = filetype.guess(head_buffer)
            if kind:
                ext = kind.extension
        except Exception:
            pass  # 如果类型推断失败，使用默认扩展名
        
        # 处理文件名
        stem_os = file_path.stem
        stem = stem_os.lower().removesuffix('.kgm') if stem_os.lower().endswith('.kgm') else stem_os
        
        out_path = file_path.parent / f"{stem}.{ext}"
        try:
            with open(out_path, 'wb') as audio_file:
                audio_file.write(origin)
        except Exception as err:
            raise Exception(f'Write error: "{file_path}" -> "{out_path}", {err}')
        
        print(f'Ok  : "{file_path}" -> "{out_path}"')
        count += 1
    return count

def decoder(file_list):
    try:
        count = decode_files(file_list)
        return True, f"success! process count {count}"
    except Exception as e:
        return False, f"decrypt failed: {str(e)}"


class FileSelectorApp(MDApp):
    def build(self):
        self.theme_cls.font_styles["font_ch"] = ["font_ch", 16, False, 0.15]
        # 主布局 - 垂直排列
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 选择文件按钮
        self.select_btn = Button(
            text='select file',
            size_hint=(1, 0.1),
            background_color=(0.2, 0.6, 0.8, 1)
        )
        self.select_btn.bind(on_press=self.select_files)
        main_layout.add_widget(self.select_btn)
        self.file_manager = MDFileManager(
            selector="multi",
            exit_manager=self.exit_manager,
            select_path=self.select_path
        )
        # 创建带滚动条的文本框
        scroll_view = ScrollView(size_hint=(1, 0.7))
        
        self.file_display = TextInput(
            text='select file...',
            font_name="font_ch",
            size_hint_y=None,
            readonly=True,
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.file_display.bind(minimum_height=self.file_display.setter('height'))
        
        scroll_view.add_widget(self.file_display)
        main_layout.add_widget(scroll_view)
        
        # 开始解密按钮
        self.decrypt_btn = Button(
            text='decrypt',
            size_hint=(1, 0.1),
            background_color=(0.8, 0.2, 0.2, 1)
        )
        self.decrypt_btn.bind(on_press=self.start_decryption)
        main_layout.add_widget(self.decrypt_btn)
        
        # 存储选择的文件列表
        self.selected_files = []
        
        return main_layout
    def select_files(self, instance):
        # 使用plyer选择多个文件
        external_storage_root = os.environ.get("EXTERNAL_STORAGE", "none")
        print(f'exter:{external_storage_root}')
        '''download_dir = os.path.join(external_storage_root, "testmkdir")
        os.makedirs(download_dir, exist_ok=True)
        file_name = "downloaded_file.txt"
        file_path = os.path.join(download_dir, file_name)

        with open(file_path, "w") as f:
                f.write("这是Kivy应用存储在共享外部存储的数据。\n")
                f.write("此文件需要WRITE_EXTERNAL_STORAGE权限。\n")
        print(f"文件已写入：{file_path}")'''
        self.file_manager.show(external_storage_root)
        '''def handle_selection(selection):
            if selection:
                display_text = "selected file:\n" + "\n".join([os.path.basename(f) for f in selection])
                print(f'selection files: {display_text}')
                self.file_display.text = display_text
        filechooser.open_file(multiple=True, on_selection=handle_selection)'''
    def select_path(self, path):
        self.selected_files = [path][0]  # 存成列表以保持兼容
        print(f'{self.selected_files}, type:{type(self.selected_files)}')
        display_text = "selected file:\n" + "\n".join([os.path.basename(f) for f in self.selected_files])
        self.file_display.text = display_text
        self.exit_manager()

    def exit_manager(self, *args):
        self.file_manager.close()
    def start_decryption(self, instance):
        """开始解密过程"""
        if not self.selected_files:
            self.file_display.text = "error: select file first!"
            return
        
        # 禁用按钮防止重复点击
        self.decrypt_btn.disabled = True
        self.file_display.text = self.decrypt_btn.text = "Decrypting... Please wait....."
        
        # 调用解密函数
        # success, message = decoder(self.selected_files)
        thread = threading.Thread(target=self._decrypt_in_thread)
        thread.daemon = True  # 设置为守护线程，这样主程序退出时线程也会退出
        thread.start()
        # 显示结果
        # result_text = f"{message}"
        
        # self.file_display.text = result_text
        # self.selected_files = []
        # self.decrypt_btn.disabled = False
        # self.decrypt_btn.text = "decrypt"
    def _decrypt_in_thread(self):
        """在后台线程中执行解密"""
        # 调用解密函数
        success, message = decoder(self.selected_files)

        # 使用Clock.schedule_once将更新UI的操作调度到主线程
        Clock.schedule_once(lambda dt: self._update_ui(success, message), 0)

    def _update_ui(self, success, message):
        """更新UI，这个函数会在主线程中执行"""
        result_text = f"{message}"
        self.file_display.text = result_text
        self.selected_files = []
        self.decrypt_btn.disabled = False
        self.decrypt_btn.text = "decrypt"

if __name__ == '__main__':
    # request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE, Permission.MANAGE_EXTERNAL_STORAGE])
    if not has_all_files_permission():
        print("No permission, requesting...")
        request_manage_all_files()
        if not has_all_files_permission():
           exit(1) 
    FileSelectorApp().run()


