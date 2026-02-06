CXX = g++
CXXFLAGS = -O3 -std=c++17 -Wall -Wextra -I./include
TARGET = rotunfold
SRC = src/main.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC)

clean:
	rm -f $(TARGET)

.PHONY: all clean
