#include <Servo.h>

unsigned char start01[] = {0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x80,0x40,0x20,0x10,0x08,0x04,0x02,0x01};
unsigned char front[] = {0x00,0x00,0x00,0x00,0x00,0x24,0x12,0x09,0x12,0x24,0x00,0x00,0x00,0x00,0x00,0x00};
unsigned char back[] = {0x00,0x00,0x00,0x00,0x00,0x24,0x48,0x90,0x48,0x24,0x00,0x00,0x00,0x00,0x00,0x00};
unsigned char left[] = {0x00,0x00,0x00,0x00,0x00,0x00,0x44,0x28,0x10,0x44,0x28,0x10,0x44,0x28,0x10,0x00};
unsigned char right[] = {0x00,0x10,0x28,0x44,0x10,0x28,0x44,0x10,0x28,0x44,0x00,0x00,0x00,0x00,0x00,0x00};
unsigned char STOP01[] = {0x2E,0x2A,0x3A,0x00,0x02,0x3E,0x02,0x00,0x3E,0x22,0x3E,0x00,0x3E,0x0A,0x0E,0x00};
unsigned char clear[] = {0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00};

Servo Servo1;

#define SCL_Pin  A5  
#define SDA_Pin  A4  
#define ML_Ctrl 13  
#define ML_PWM 11   
#define MR_Ctrl 12  
#define MR_PWM 3   
#define SERVO_Pin 9 

uint8_t transmit_destination=0;
uint8_t left_pwn=0;
uint8_t left_direction=0;
uint8_t right_pwn=0;
uint8_t right_direction=0;
uint8_t display_direction=0;
uint8_t read_count = 0;
uint8_t servo_angle = 0;

float duration, distance;


void setup(){
  Serial.begin(9600);
  Servo.attach(SERVO_Pin)
  
  pinMode(SCL_Pin,OUTPUT);
  pinMode(SDA_Pin,OUTPUT);
  pinMode(ML_Ctrl, OUTPUT);
  pinMode(ML_PWM, OUTPUT);
  pinMode(MR_Ctrl, OUTPUT);
  pinMode(MR_PWM, OUTPUT);

  matrix_display(clear);    
  matrix_display(start01); 

  analogWrite(ML_PWM,left_pwn); 
  analogWrite(MR_PWM,right_pwn);
  digitalWrite(ML_Ctrl,LOW);
  digitalWrite(MR_Ctrl,LOW);

  Servo1.write(servo_angle);

  while (Serial.available() > 0){
    char t = Serial.read();
  }
}

void loop(){
  if (left_direction > 1 || right_direction > 1 ){
    left_direction = 0;
    right_direction = 0;
    read_count = 0;
  }
  if (Serial.available())
  {
    switch(read_count){

      case 0:
        left_pwn = Serial.read();
        break;
      case 1:
        left_direction = Serial.read();
        break;
      case 2:
        right_pwn = Serial.read();
        break;
      case 3:
        right_direction = Serial.read();
        break;
      case 4:
        display_direction = Serial.read();
        break;
      case 5:
        servo_angle = Serial.read();
        break;
    }
    read_count++;
  } 
  if (read_count < 6){
    return;
  }

  read_count = 0;

  switch (display_direction) 
  {
     case 0:  
        matrix_display(front);  
        break;
     case 1:  
        matrix_display(back);  
        break;
     case 2:  
        matrix_display(left);  
        break;
     case 3:  
        matrix_display(right);  
       break;
     case 4:  
        matrix_display(STOP01);  
        break;
  }
  if (left_direction == 0){
    digitalWrite(ML_Ctrl,HIGH);
  } else {
    digitalWrite(ML_Ctrl,LOW);
  }
  if (right_direction == 0){
    digitalWrite(MR_Ctrl,HIGH);
  } else {
    digitalWrite(MR_Ctrl,LOW);
  }

  analogWrite(ML_PWM,left_pwn); 
  analogWrite(MR_PWM,right_pwn);

  Servo1.write(servo_angle);
  
}
void matrix_display(unsigned char matrix_value[])
{
  IIC_start();
  IIC_send(0xc0);  
  for(int i = 0;i < 16;i++) 
  {
     IIC_send(matrix_value[i]); 
  }
  IIC_end(); 
  IIC_start();
  IIC_send(0x8A);  
  IIC_end();
}
void IIC_start()
{
  digitalWrite(SCL_Pin,HIGH);
  delayMicroseconds(3);
  digitalWrite(SDA_Pin,HIGH);
  delayMicroseconds(3);
  digitalWrite(SDA_Pin,LOW);
  delayMicroseconds(3);
}
void IIC_send(unsigned char send_data)
{
  for(char i = 0;i < 8;i++)  
  {
      digitalWrite(SCL_Pin,LOW);        
      delayMicroseconds(3);
      if(send_data & 0x01)  
      {
        digitalWrite(SDA_Pin,HIGH);
      }
      else
      {
        digitalWrite(SDA_Pin,LOW);
      }
      delayMicroseconds(3);
      digitalWrite(SCL_Pin,HIGH); 
      delayMicroseconds(3);
      send_data = send_data >> 1;  
  }
}
void IIC_end()
{
  digitalWrite(SCL_Pin,LOW);
  delayMicroseconds(3);
  digitalWrite(SDA_Pin,LOW);
  delayMicroseconds(3);
  digitalWrite(SCL_Pin,HIGH);
  delayMicroseconds(3);
  digitalWrite(SDA_Pin,HIGH);
  delayMicroseconds(3);
}
