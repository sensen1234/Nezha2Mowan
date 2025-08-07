import time
import sys

def play_ascii_movie(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 读取头部信息
    header = lines[0].strip().split(',')
    width, height, fps = int(header[0]), int(header[1]), int(header[2])
    frame_delay = 1.0 / fps
    
    # 读取帧数据
    frames = [line.strip() for line in lines[1:] if line.strip()]
    
    print(f"播放参数: {width}x{height}, {fps}FPS")
    input("按回车开始播放...")
    
    try:
        for i, frame in enumerate(frames):
            # 清屏并显示帧
            print('\033[2J\033[H')  # ANSI清屏
            print(f"帧 {i+1}/{len(frames)}")
            # 重新格式化帧数据
            chars_per_row = width + 1  # 包含分隔符
            for j in range(height):
                start = j * chars_per_row
                end = start + width
                if start < len(frame):
                    print(frame[start:end])
            time.sleep(frame_delay)
    except KeyboardInterrupt:
        print("\n播放结束")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        play_ascii_movie(sys.argv[1])
    else:
        print("使用方法: python play_ascii.py result.txt")