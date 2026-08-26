cmake_minimum_required(VERSION 3.8)
project(sentinel_description)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch rviz urdf worlds
  DESTINATION share/${PROJECT_NAME}
)

ament_package()

