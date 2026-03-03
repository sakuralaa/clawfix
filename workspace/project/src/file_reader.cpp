#include "file_reader.h"

#include <array>

FileReader::FileReader(const std::string& path) : file_(std::fopen(path.c_str(), "r")), path_(path) {}

std::string FileReader::ReadLine() {
  if (file_ == nullptr) {
    return {};
  }

  std::array<char, 256> buffer{};
  if (std::fgets(buffer.data(), static_cast<int>(buffer.size()), file_) == nullptr) {
    return {};
  }
  return std::string(buffer.data());
}

bool FileReader::IsOpen() const {
  return file_ != nullptr;
}
