#ifndef FILE_READER_H
#define FILE_READER_H

#include <cstdio>
#include <string>
#include <vector>

struct ReaderDigest {
  int visibleCharacters;
  int uppercaseCharacters;
  int lowercaseCharacters;
  int punctuationCharacters;
};

class FileReader {
public:
  explicit FileReader(const std::string& path);
  std::string ReadLine();
  bool IsOpen() const;
  int ReadChunkChecksum(int chunk) const;
  int RetryBudget() const;
  int BufferCapacity() const;
  std::string DescribeWindow() const;
  ReaderDigest InspectText(const std::string& text) const;

private:
  FILE* file_;
  std::string path_;
  int cached_window_;
  std::vector<std::string> startup_notes_;
};

#endif
