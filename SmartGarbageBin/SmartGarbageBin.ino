//引导型立项：智能分类垃圾桶
//作者：庞奕豪、陈永愽、王卓
/*
 * ********************************************************

 * 舵机映射：
 * 舵机1 (Pin 9)  - 可回收物
 * 舵机2 (Pin 10) - 有害垃圾  
 * 舵机3 (Pin 11) - 厨余垃圾
 * 舵机4 (Pin 12) - 其他垃圾

***********************************************************

 * 字节通信协议：
 * 发送 0x01 - 打开可回收物垃圾桶
 * 发送 0x02 - 打开有害垃圾桶
 * 发送 0x03 - 打开厨余垃圾桶
 * 发送 0x04 - 打开其他垃圾桶
 * 发送 0x00 - 关闭所有垃圾桶（检测到未知垃圾时）
*/

#include <Servo.h>

// 定义舵机对象
Servo servo1;  // 可回收物
Servo servo2;  // 有害垃圾
Servo servo3;  // 厨余垃圾
Servo servo4;  // 其他垃圾

// 定义舵机引脚
const int SERVO1_PIN = 9;   
const int SERVO2_PIN = 10;
const int SERVO3_PIN = 11;
const int SERVO4_PIN = 12;

// 定义舵机角度
const int SERVO_CLOSED_ANGLE = 0;    // 关闭角度
const int SERVO_OPEN_ANGLE = 90;     // 打开角度
const int SERVO_DELAY_MS = 1000;     // 舵机动作延时(毫秒)

// 定义通信协议
const byte CMD_OPEN_BIN1 = 0x01;    
const byte CMD_OPEN_BIN2 = 0x02;   
const byte CMD_OPEN_BIN3 = 0x03;    
const byte CMD_OPEN_BIN4 = 0x04; 
const byte CMD_CLOSE_ALL = 0x00;   


//函数声明区
void openBin(int binNumber, String binName);  //打开垃圾桶的指令函数
void closeAllBins();  // 初始化所有舵机为关闭状态


void setup() 
{
  Serial.begin(9600);

  // 初始化舵机
  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);
  servo3.attach(SERVO3_PIN);
  servo4.attach(SERVO4_PIN);

  // 初始化所有舵机为关闭状态
  closeAllBins();
}

void loop() 
{
  byte command=0x00;
  
  // 检查并获取终端向串口发送的数据
  if (Serial.available() > 0) 
  {
    command = Serial.read(); //只获取串口缓冲区中的第一个字节数据
    // 清除串口缓冲区
    while (Serial.available() > 0)  //在这个while循环中其他数据相当于被遗弃
    {
      Serial.read(); 
    }
  }

  // 处理指令
    switch (command)
    {
      case CMD_OPEN_BIN1:
        openBin(1, "可回收物");
        break;
        
      case CMD_OPEN_BIN2:
        openBin(2, "有害垃圾");
        break;
        
      case CMD_OPEN_BIN3:
        openBin(3, "厨余垃圾");
        break;
        
      case CMD_OPEN_BIN4:
        openBin(4, "其他垃圾");
        break;
        
      case CMD_CLOSE_ALL:
        closeAllBins();
        break;

      //未知指令直接扔掉
      default:
        break;
    }

  // 等待指定时间后自动关闭
  delay(SERVO_DELAY_MS);
  closeAllBins();

}


//打开垃圾桶的指令函数
void openBin(int binNumber, String binName) 
{
  closeAllBins(); // 先关闭所有垃圾桶
  delay(200);  // 短暂延时确保关闭动作完成
  
  // 打开指定垃圾桶
  switch (binNumber) 
  {
    case 1:
      servo1.write(SERVO_OPEN_ANGLE);
      break;
      
    case 2:
      servo2.write(SERVO_OPEN_ANGLE);
      break;
      
    case 3:
      servo3.write(SERVO_OPEN_ANGLE);
      break;
      
    case 4:
      servo4.write(SERVO_OPEN_ANGLE);
      break;
  }
  
}


// 初始化所有舵机为关闭状态
void closeAllBins() 
{
  servo1.write(SERVO_CLOSED_ANGLE);
  servo2.write(SERVO_CLOSED_ANGLE);
  servo3.write(SERVO_CLOSED_ANGLE);
  servo4.write(SERVO_CLOSED_ANGLE);
    

}
