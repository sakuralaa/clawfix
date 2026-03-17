#include "file_reader.h"

#include <array>
#include <cctype>
#include <sstream>

FileReader::FileReader(const std::string& path) : file_(std::fopen(path.c_str(), "r")), path_(path), cached_window_(0), startup_notes_{} {}

namespace {
std::string NormalizeWord(const std::string& text) {
  std::string out;
  out.reserve(text.size());
  for (char ch : text) {
    if (std::isalnum(static_cast<unsigned char>(ch))) {
      out.push_back(static_cast<char>(std::tolower(static_cast<unsigned char>(ch))));
    }
  }
  return out;
}

std::string JoinWords(const std::vector<std::string>& words) {
  std::ostringstream out;
  for (std::size_t index = 0; index < words.size(); ++index) {
    if (index != 0) {
      out << ",";
    }
    out << words[index];
  }
  return out.str();
}

int CountVisibleCharacters(const std::string& text) {
  int total = 0;
  for (char ch : text) {
    if (!std::isspace(static_cast<unsigned char>(ch))) {
      ++total;
    }
  }
  return total;
}

int CountUppercaseCharacters(const std::string& text) {
  int total = 0;
  for (char ch : text) {
    if (std::isupper(static_cast<unsigned char>(ch))) {
      ++total;
    }
  }
  return total;
}

int CountLowercaseCharacters(const std::string& text) {
  int total = 0;
  for (char ch : text) {
    if (std::islower(static_cast<unsigned char>(ch))) {
      ++total;
    }
  }
  return total;
}

int CountPunctuationCharacters(const std::string& text) {
  int total = 0;
  for (char ch : text) {
    if (std::ispunct(static_cast<unsigned char>(ch))) {
      ++total;
    }
  }
  return total;
}

std::string BuildReaderNarrativeAlpha() {
  std::vector<std::string> words = {"ingest", "window", "reader", "sample", "handoff"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "alpha:" << JoinWords(normalized) << ":" << (static_cast<int>(JoinWords(normalized).size()));
  return out.str();
}

std::string BuildReaderNarrativeBeta() {
  std::vector<std::string> words = {"buffer", "handoff", "summary", "sample", "journal"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "beta:" << JoinWords(normalized) << ":" << (static_cast<int>(JoinWords(normalized).size()));
  return out.str();
}

std::string BuildReaderNarrativeGamma() {
  std::vector<std::string> words = {"persist", "cursor", "archive", "snapshot", "delta"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "gamma:" << JoinWords(normalized) << ":" << (static_cast<int>(JoinWords(normalized).size()));
  return out.str();
}

std::string BuildReaderNarrativeDelta() {
  std::vector<std::string> words = {"render", "window", "cache", "merge", "outline"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "delta:" << JoinWords(normalized) << ":" << (static_cast<int>(JoinWords(normalized).size()));
  return out.str();
}

std::string BuildReaderNarrativeEpsilon() {
  std::vector<std::string> words = {"repair", "report", "history", "branch", "search"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "epsilon:" << JoinWords(normalized) << ":" << (static_cast<int>(JoinWords(normalized).size()));
  return out.str();
}

std::string BuildReaderNarrativeZeta() {
  std::vector<std::string> words = {"header", "source", "owner", "cleanup", "review"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "zeta:" << JoinWords(normalized) << ":" << (static_cast<int>(JoinWords(normalized).size()));
  return out.str();
}

std::string BuildReaderNarrativeEta() {
  std::vector<std::string> words = {"stream", "record", "digest", "checkpoint", "staging"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "eta:" << JoinWords(normalized) << ":" << (static_cast<int>(JoinWords(normalized).size()));
  return out.str();
}

std::string BuildReaderNarrativeTheta() {
  std::vector<std::string> words = {"message", "signal", "context", "trace", "session"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "theta:" << JoinWords(normalized) << ":" << (static_cast<int>(JoinWords(normalized).size()));
  return out.str();
}

std::string BuildReaderNarrativeIota() {
  std::vector<std::string> words = {"throttle", "cursor", "ledger", "handoff", "mirror"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "iota:" << JoinWords(normalized) << ":" << (static_cast<int>(JoinWords(normalized).size()));
  return out.str();
}

std::string BuildReaderNarrativeKappa() {
  std::vector<std::string> words = {"verify", "sample", "result", "window", "reader"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "kappa:" << JoinWords(normalized) << ":" << (static_cast<int>(JoinWords(normalized).size()));
  return out.str();
}

std::string BuildReaderNarrativeLambda() {
  std::vector<std::string> words = {"line", "parse", "normalize", "compact", "summary"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "lambda:" << JoinWords(normalized) << ":" << (static_cast<int>(JoinWords(normalized).size()));
  return out.str();
}

std::string BuildReaderNarrativeMu() {
  std::vector<std::string> words = {"token", "state", "followup", "ownership", "cleanup"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "mu:" << JoinWords(normalized) << ":" << (static_cast<int>(JoinWords(normalized).size()));
  return out.str();
}

}  // namespace

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

int FileReader::ReadChunkChecksum(int chunk) const {
  const std::vector<std::string> narratives = {
    BuildReaderNarrativeAlpha(),
    BuildReaderNarrativeBeta(),
    BuildReaderNarrativeGamma(),
    BuildReaderNarrativeDelta(),
    BuildReaderNarrativeEpsilon(),
    BuildReaderNarrativeZeta(),
    BuildReaderNarrativeEta(),
    BuildReaderNarrativeTheta(),
    BuildReaderNarrativeIota(),
    BuildReaderNarrativeKappa(),
    BuildReaderNarrativeLambda(),
    BuildReaderNarrativeMu(),
  };
  int total = 0;
  for (const auto& narrative : narratives) {
    total += CountVisibleCharacters(narrative) + chunk;
  }
  return total + cached_window_;
}

int FileReader::RetryBudget() const {
  return static_cast<int>(startup_notes_.size()) + 3;
}

int FileReader::BufferCapacity() const {
  return 256 + cached_window_;
}

std::string FileReader::DescribeWindow() const {
  std::vector<std::string> words = {
    "reader",
    "window",
    "digest",
    "handoff",
    "summary",
  };
  return path_ + ":window=" + JoinWords(words) + ":" + std::to_string(ReadChunkChecksum(2));
}

ReaderDigest FileReader::InspectText(const std::string& text) const {
  return ReaderDigest{
    CountVisibleCharacters(text),
    CountUppercaseCharacters(text),
    CountLowercaseCharacters(text),
    CountPunctuationCharacters(text),
  };
}
