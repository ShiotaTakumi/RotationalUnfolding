CXX = g++
CXXFLAGS = -O3 -std=c++17 -I../../include/

TARGET = a.out
SRC = test.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC)

clean:
	rm -f $(TARGET)
