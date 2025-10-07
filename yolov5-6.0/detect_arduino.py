# 使用方法：
# python detect_arduino.py --weights best.pt --source 0 --arduino COM3 --img-size 640 --conf-thres 0.4
# 参数说明：
# --weights：模型权重文件路径
# --source：摄像头ID (0为默认摄像头)
# --arduino：Arduino串口端口
# --img-size：推理尺寸
# --conf-thresh：置信度阈值

import argparse
import cv2
import serial
import time
import torch
import numpy as np
from pathlib import Path
import os

# YOLOv5相关导入
from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression, scale_coords
from utils.plots import Annotator, colors
from utils.torch_utils import select_device

class ArduinoController:
    """Arduino串口控制器"""
    
    def __init__(self, port='COM3', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.last_trigger_time = 0
        self.trigger_cooldown = 2.0  # 2秒冷却时间
        self.last_triggered_class = None
        self.is_paused = False  # 检测暂停标志
        self.pause_start_time = 0  # 暂停开始时间
        self.pause_duration = 0.1  # 暂停持续时间（秒）
        self.connect()
        
        # 垃圾类别到指令的映射
        self.class_to_command = {
            '可回收物': 0x01,
            '有害垃圾': 0x02, 
            '厨余垃圾': 0x03,
            '其他垃圾': 0x04
        }
        

    def connect(self):
        """连接Arduino"""
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # 等待Arduino初始化
            command = 0x00  # 关闭所有的垃圾桶
            self.serial_conn.write(bytes([command]))
            print(f"成功连接到Arduino: {self.port}")
            return True
        except Exception as e:
            print(f"Arduino连接失败: {e}")
            return False
        
        
    def can_trigger(self, class_name):
        """检查是否可以触发舵机（防重复触发）"""
        current_time = time.time()
        
        # 检查是否在暂停期间
        if self.is_paused:
            if current_time - self.pause_start_time >= self.pause_duration:
                self.is_paused = False
                print("检测暂停结束，恢复检测")
            else:
                return False
        
        # 检查冷却时间
        if current_time - self.last_trigger_time < self.trigger_cooldown:
            return False
        
        # 检查是否是同一个类别（防止短时间内重复触发相同类别）
        if self.last_triggered_class == class_name and current_time - self.last_trigger_time < self.trigger_cooldown:
            return False
        
        return True
        
    
    def send_command(self, class_name):
        """发送指令到Arduino"""
        if not self.can_trigger(class_name):
            return False
        
        if class_name in self.class_to_command and self.serial_conn:
            command = self.class_to_command[class_name]
            try:
                self.serial_conn.write(bytes([command]))
                print(f"发送指令: {class_name} -> 0x{command:02X}")
                
                # 更新触发时间和类别
                self.last_trigger_time = time.time()
                self.last_triggered_class = class_name
                
                # 启动检测暂停
                self.is_paused = True
                self.pause_start_time = time.time()
                print(f"检测暂停 {self.pause_duration} 秒，防止Arduino无法响应")
                
                return True
            except Exception as e:
                print(f"发送失败: {e}")
                return False
        return False
    

def main(weights_path, source=0, arduino_port='COM3', img_size=640, conf_thresh=0.25):
    """主函数"""
    
    # 获取根目录路径
    root_path=os.getcwd()
    # 获取权重文件路径
    weights_path=os.path.join(root_path,weights_path)
    
    # 初始化设备
    device = select_device('')
    
    # 加载YOLOv5模型
    model = attempt_load(weights_path, map_location=device)
    stride = int(model.stride.max())
    img_size = check_img_size(img_size, s=stride)
    names = model.module.names if hasattr(model, 'module') else model.names
    
    # 初始化Arduino控制器
    arduino = ArduinoController(port=arduino_port)
    
    # 打开摄像头
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print("无法打开摄像头")
        return
    
    print("开始检测... 按 'q' 退出")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 预处理图像
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (img_size, img_size))
        img = img.transpose(2, 0, 1)  # HWC to CHW
        img = torch.from_numpy(img).to(device).float()
        img = img / 255.0  # 归一化
        img = img.unsqueeze(0)  # 添加batch维度
        
        # 推理
        pred = model(img)[0]
        pred = non_max_suppression(pred, conf_thresh, 0.45, classes=None, agnostic=False)
        
        # 处理检测结果
        annotator = Annotator(frame, line_width=2, example=str(names))
        detected_class = None
        max_conf = 0
        
        for det in pred:
            if len(det):
                # 还原坐标到原图尺寸
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], frame.shape).round()
                
                for *xyxy, conf, cls in det:
                    class_name = names[int(cls)]
                    confidence = float(conf)
                    
                    # 记录置信度最高的检测结果
                    if confidence > max_conf:
                        max_conf = confidence
                        detected_class = class_name
                    
                    # 绘制边界框和标签
                    label = f'{class_name} {confidence:.2f}'
                    annotator.box_label(xyxy, label, color=colors(int(cls), True))
        
        # 发送指令到Arduino
        if detected_class and arduino.serial_conn:
            arduino.send_command(detected_class)
        
        # 显示结果
        result_frame = annotator.result()
        cv2.imshow('垃圾分类检测', result_frame)
        
        # 退出条件
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # 清理资源
    cap.release()
    cv2.destroyAllWindows()
    if arduino.serial_conn:
        arduino.serial_conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', type=str, default='best.pt', help='模型名称')
    parser.add_argument('--source', type=int, default=0, help='摄像头ID (0为默认摄像头)')
    parser.add_argument('--arduino', type=str, default='COM3', help='Arduino串口端口')
    parser.add_argument('--img-size', type=int, default=640, help='推理尺寸')
    parser.add_argument('--conf-thres', type=float, default=0.4, help='置信度阈值')
    
    args = parser.parse_args()
    
    main(
        weights_path=args.weights,
        source=args.source,
        arduino_port=args.arduino,
        img_size=args.img_size,
        conf_thresh=args.conf_thres
    )