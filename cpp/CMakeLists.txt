cmake_minimum_required(VERSION 3.15)
project(RotationalUnfolding VERSION 1.0.0 LANGUAGES CXX)

# C++17 を要求
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# コンパイルオプション
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -Wall -Wextra")

# include ディレクトリの設定
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# 実行ファイルの生成
add_executable(rotunfold src/main.cpp)

# compile_commands.json の生成（clangd/LSP 用）
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
