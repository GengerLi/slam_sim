## 1. 安装依赖

### 1.2 安装ROS 2及Gazebo相关依赖
```bash
sudo apt install \
  ros-humble-gazebo* \          
  ros-humble-ros2-control* \    
  ros-humble-robot-state-publisher \ 
  ros-humble-joint-state-publisher \ 
  ros-humble-xacro  
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
ros2 launch navigation2_sim navigation2.launch.py