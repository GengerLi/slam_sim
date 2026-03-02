#ifndef ICP_REGISTRATION_FEATURE_EXTRACTOR_HPP
#define ICP_REGISTRATION_FEATURE_EXTRACTOR_HPP

#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/search/kdtree.h>
#include <pcl/features/normal_3d.h>
#include <pcl/features/fpfh.h>
#include <pcl/keypoints/iss_3d.h>
#include <vector>
#include <memory>

namespace icp {

// 特征点结构
struct FeaturePoint {
    pcl::PointXYZ position;
    std::vector<float> descriptor;
};

// 特征提取器类
class FeatureExtractor {
public:
    FeatureExtractor();
    ~FeatureExtractor() = default;
    
    // 配置参数
    void setISSRadius(double salient_radius, double non_max_radius);
    void setFPFHSearchRadius(double radius);
    void setMinNeighbors(int min_neighbors);
    
    // 特征提取主函数
    std::vector<FeaturePoint> extractFeatures(
        const pcl::PointCloud<pcl::PointXYZI>::Ptr& cloud);
    
    // 仅提取关键点
    pcl::PointCloud<pcl::PointXYZ>::Ptr extractKeypoints(
        const pcl::PointCloud<pcl::PointXYZI>::Ptr& cloud);
    
    // 仅计算特征描述子
    std::vector<std::vector<float>> computeDescriptors(
        const pcl::PointCloud<pcl::PointXYZI>::Ptr& cloud,
        const pcl::PointCloud<pcl::PointXYZ>::Ptr& keypoints);
    
private:
    // ISS关键点检测器
    pcl::ISSKeypoint3D<pcl::PointXYZI, pcl::PointXYZI> iss_detector_;
    
    // FPFH特征计算
    pcl::FPFHEstimation<pcl::PointXYZI, pcl::Normal, pcl::FPFHSignature33> fpfh_;
    
    // 搜索树
    pcl::search::KdTree<pcl::PointXYZI>::Ptr tree_;
    pcl::search::KdTree<pcl::PointXYZ>::Ptr keypoint_tree_;
    
    // 参数
    double iss_salient_radius_;
    double iss_non_max_radius_;
    double fpfh_search_radius_;
    int min_neighbors_;
    
    // 初始化
    void initializeISS();
    void initializeFPFH();
};

} // namespace icp

