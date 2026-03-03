#ifndef FILE_READER_H
#define FILE_READER_H

#include <cstdio>
#include <string>

class FileReader {
public:
  explicit FileReader(const std::string& path);
  std::string ReadLine();
  bool IsOpen() const;

private:
  FILE* file_;
  std::string path_;
};

#endif
