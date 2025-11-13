# KGMdeocder
decoder .kgm file using python and kivy  
一款用python和kivymd开发的安卓应用，可将酷狗音乐下载的被加密的音乐文件解码为通用格式音乐文件。  
会在原文件同目录下生成一个新的解码后的文件，后缀名由解码出来的数据决定，无法识别的格式会设置为默认的mp3  
解码部分完全转写自 [ghtz08](https://github.com/ghtz08) 的 [kugou-kgm-decoder](https://github.com/ghtz08/kugou-kgm-decoder)
注：虽然代码不长，但可能含有大量被注释的代码以及死代码，阅读时请注意  
待修改：文件选择器中文显示乱码，但暂时不会解决  
windows和linux桌面系统使用方法：
  1. 安装python
  2. 控制台输入命令 ```pip install kivy kivymd plyer filetype```
  3. 在main.py目录下执行 ```python main.py```
