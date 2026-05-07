TARGET = foo
OBJS += lib/parse_trace.o
OBJS += lib/solve_mcf.o
OBJS += foo.o

CXX = g++
CXXFLAGS += -std=c++11
CXXFLAGS += -MMD -MP

# 1. 顯式加入 w64devkit 的路徑，確保 lemon 被優先找到
CXXFLAGS += -I"C:/w64devkit/include" -I.. -I ../../lib
CXXFLAGS += -O3 -ffast-math -march=native
# CXXFLAGS += -Wall -Werror
CXXFLAGS += -Wall


# 2. 定義要連結的 lemon 函式庫
LIBS += -llemon
# 3. 確保連結路徑正確
LDFLAGS += -L"C:/w64devkit/lib"

all: $(TARGET)

debug: CXXFLAGS += -ggdb -D_GLIBCXX_DEBUG
debug: $(TARGET)

# 注意：在 MinGW/GCC 中，$(LIBS) 必須放在 $^ (物件檔) 的後面
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS) $(LIBS)

%.o: %.c
	$(CXX) $(CXXFLAGS) -c -o $@ $<

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $<

DEPS = $(OBJS:%.o=%.d)
-include $(DEPS)

clean:
	-rm -f $(TARGET) $(OBJS) $(DEPS)
