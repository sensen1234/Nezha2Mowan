import cv2
import numpy as np
import os
from concurrent.futures import ThreadPoolExecutor
import argparse
from tqdm import tqdm

class VideoAsciiCompressor:
    """
    视频转字符画压缩器
    支持多线程处理
    """
    def __init__(self, width=40, height=20, charset="█▓▒░■◆◇●◐◑◒◓◔◕◖◗⧝⧞⧟⧠⧡⧢⧣⧤⧥⧦⧧⧨⧩⧪⧫⧬⧭⧮⧯"):
        # 初始化参数
        self.w = width          # 输出宽度
        self.h = height         # 输出高度
        self.chars = charset    # 字符集
        self.n_chars = len(charset)  # 字符数量
        
    def _process_frame(self, frame):
        """
        将单帧视频转换为字符画
        """
        # 转换为灰度图
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 调整尺寸
        resized = cv2.resize(gray, (self.w, self.h), interpolation=cv2.INTER_NEAREST)
        
        # 计算字符索引
        indices = (resized.astype(np.float32) * (self.n_chars - 1) / 255).astype(int)
        indices = np.clip(indices, 0, self.n_chars - 1)
        
        # 映射到字符
        char_array = np.array(list(self.chars))
        ascii_chars = char_array[indices]
        # 格式化输出
        return '|'.join([''.join(row) for row in ascii_chars]) + '|'
    
    def compress(self, input_path, output_path, threads=4, max_frames=100):
        """
        压缩视频为字符画
        支持多线程处理
        """
        # 打开视频文件
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise IOError(f"无法打开视频文件: {input_path}")
        
        # 获取视频信息
        fps = min(5, cap.get(cv2.CAP_PROP_FPS))  # 限制最大帧率
        total = min(max_frames, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))  # 限制最大帧数
        
        # 读取帧数据
        frames = []
        count = 0
        
        with tqdm(total=total, desc="读取帧数据") as pbar:
            while count < total:
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)
                count += 1
                pbar.update(1)
        
        cap.release()
        
        # 多线程处理帧
        ascii_data = []
        with ThreadPoolExecutor(max_workers=threads) as executor:
            with tqdm(total=len(frames), desc="处理字符画") as pbar:
                futures = [executor.submit(self._process_frame, frame) for frame in frames]
                for future in futures:
                    ascii_data.append(future.result())
                    pbar.update(1)
        
        # 保存结果
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"{self.w},{self.h},{int(fps)},{self.chars}\n")
            for frame_data in ascii_data:
                f.write(frame_data + "\n")

def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser(description='视频转字符画压缩工具')
    parser.add_argument('input', help='输入视频文件')
    parser.add_argument('-o', '--output', default='output.txt', help='输出文件')
    parser.add_argument('-w', '--width', type=int, default=40, help='输出宽度')
    parser.add_argument('-H', '--height', type=int, default=20, help='输出高度')
    parser.add_argument('-f', '--frames', type=int, default=50, help='最大帧数')
    parser.add_argument('-t', '--threads', type=int, default=4, help='线程数')
    parser.add_argument('-c', '--charset', default='█▓▒░■◆◇●◐◑◒◓◔◕', help='字符集')
    
    args = parser.parse_args()
    
    # 检查输入文件
    if not os.path.exists(args.input):
        raise FileNotFoundError(f"输入文件不存在: {args.input}")
    
    try:
        # 创建压缩器实例
        compressor = VideoAsciiCompressor(
            width=args.width,
            height=args.height,
            charset=args.charset
        )
        
        # 执行压缩
        compressor.compress(
            args.input,
            args.output,
            threads=args.threads,
            max_frames=args.frames
        )
        
        print(f"压缩完成: {args.output}")
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()