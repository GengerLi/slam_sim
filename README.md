# Mid360雷达仿真搭建指南


## 1. 安装依赖
（注：依赖可能随环境差异有所不同，建议边运行边补充安装）

### 1.1 安装 Livox SDK2
自行克隆源码并编译安装：
```bash
# 克隆源码（需提前安装git）
git clone https://github.com/Livox-SDK/Livox-SDK2.git  
cd Livox-SDK2

# 编译安装
mkdir build && cd build
cmake .. && make -j$(nproc) 
sudo make install  
```

### 1.2 安装ROS 2及Gazebo相关依赖
```bash
sudo apt install \
  ros-humble-gazebo* \          
  ros-humble-ros2-control* \    
  ros-humble-robot-state-publisher \ 
  ros-humble-joint-state-publisher \ 
  ros-humble-xacro  
```


## 2. 环境配置

### 2.1 （可选）下载Gazebo官方模型库
```bash
#############################################
# 若Gazebo缺少基础模型，可手动克隆官方模型库
#############################################
cd ~/.gazebo/
git clone https://github.com/osrf/gazebo_models.git models


sudo chmod 777 ~/.gazebo/models
sudo chmod 777 ~/.gazebo/models/*
```


## 3. 编译项目
```bash
./build.sh  
```

## 4. 运行仿真
```bash
source install/setup.bash
ros2 launch ros2_livox_simulation livox_simulation.launch.py 
```
## 5. 启动里程计
```bash
source install/setup.bash 
ros2 launch fast_lio mapping.launch.py 
```
## 6.运行Nav2
```bash
source install/setup.bash
ros2 launch 