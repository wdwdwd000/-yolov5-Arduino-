### -yolov5-Arduino-(heu大一学生水引导型立项的项目)
极其简单地用yolov5与Arduino来进行垃圾分类任务，最适合想入门yolo的小白体质！
几分钟教会从未学过yolo的小白完成一个最简单的yolo目标检测任务

数据集网盘下载：链接: https://pan.baidu.com/s/1Xk3x9Oi2txGenUMFX4n4vg?pwd=1234 提取码: 1234
请在运行项目之前提前下载好合适的CUDA，若使用显卡请下载对应的驱动，当然也可以使用cpu进行训练

## 运行步骤：
# 一、下载数据集进行训练（可选，也可以用自定义yolo格式的数据集）
1、检查garbage.yaml文件的数据集文件路径(若使用自定义数据集，请更换自定义数据集文件路径)
2、可修改yolov5-6.0/data/hyps/hyp.scratch.yaml来改变训练过程中的超参数 (可选)
3、打开项目所在文件夹目录的终端：
  3.1 pip install -r requirements.txt  (配置环境)
  3.2 cd yolov5-6.0
  3.3 python train.py --data garbage.yaml --weights yolov5s.pt --img 640

# 二、开始启动识别程序
# 打开Arduino
1、将arduino程序烧录进Arduino开发板中
2、连上摄像头(也可使用电脑默认摄像头)与四个舵机
3、在项目文件夹终端上：
  3.1、cd yolov5-6.0
  3.2 python detect_arduino.py --weights best.pt --source 0 --arduino COM3 --img-size 640 --conf-thres 0.4   (参数的详细说明请参考detect_arduino.py最顶上的注释)
