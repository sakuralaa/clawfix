#include "config_macros.h"
#include "file_reader.h"

#include <cctype>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

int GetBufferBudget();
int ComputeBudgetTelemetryMix();
int ComputeRetryWindowBudget();
int ComputeCacheStride();
int ComputeCachePressure();
int ComputeCacheFlushAllowance();
int ComposeTelemetryScore(const FileReader& reader);
int ComposeTelemetryTrend(const FileReader& reader);
int ComposeTelemetryRetries();
namespace {
int BuildStartupTraceChecksum();
std::string BuildStartupNarrativeAlpha();
std::string BuildStartupNarrativeBeta();
std::string BuildStartupNarrativeGamma();
std::string BuildStartupNarrativeDelta();
std::string BuildStartupNarrativeEpsilon();
std::string BuildStartupNarrativeZeta();
std::string BuildStartupNarrativeEta();
std::string BuildStartupNarrativeTheta();
std::string BuildStartupNarrativeIota();
std::string BuildStartupNarrativeKappa();
std::string BuildStartupNarrativeLambda();
std::string BuildStartupNarrativeMu();
}

int main() {
  FileReader reader("data/sample.txt");
  if (!reader.IsOpen()) {
    std::cerr << "failed to open sample file after " << File_open_retry << " retries\n";
    return 1;
  }

  std::cout << "budget=" << GetBufferBudget()
            << " mix=" << ComputeBudgetTelemetryMix()
            << " retry-window=" << ComputeRetryWindowBudget()
            << " cache-stride=" << ComputeCacheStride()
            << " cache-pressure=" << ComputeCachePressure()
            << " cache-flush=" << ComputeCacheFlushAllowance()
            << " telemetry-score=" << ComposeTelemetryScore(reader)
            << " telemetry-trend=" << ComposeTelemetryTrend(reader)
            << " telemetry-retries=" << ComposeTelemetryRetries()
            << " startup-trace=" << BuildStartupTraceChecksum()
            << " max=" << maxBufferSize
            << " cache-line=" << Cache_line_size
            << " line=" << reader.ReadLine();
  return 0;
}

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
      out << "|";
    }
    out << words[index];
  }
  return out.str();
}

std::string BuildStartupNarrativeAlpha() {
  std::vector<std::string> words = {"startup", "reader", "window", "budget", "report"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "alpha:" << JoinWords(normalized) << ":" << (maxBufferSize + Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildStartupNarrativeBeta() {
  std::vector<std::string> words = {"context", "handoff", "signal", "cache", "owner"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "beta:" << JoinWords(normalized) << ":" << (maxBufferSize + Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildStartupNarrativeGamma() {
  std::vector<std::string> words = {"stream", "summary", "repair", "branch", "result"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "gamma:" << JoinWords(normalized) << ":" << (maxBufferSize + Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildStartupNarrativeDelta() {
  std::vector<std::string> words = {"telemetry", "route", "review", "session", "trace"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "delta:" << JoinWords(normalized) << ":" << (maxBufferSize + Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildStartupNarrativeEpsilon() {
  std::vector<std::string> words = {"workspace", "header", "source", "cleanup", "owner"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "epsilon:" << JoinWords(normalized) << ":" << (maxBufferSize + Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildStartupNarrativeZeta() {
  std::vector<std::string> words = {"prompt", "context", "window", "reader", "digest"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "zeta:" << JoinWords(normalized) << ":" << (maxBufferSize + Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildStartupNarrativeEta() {
  std::vector<std::string> words = {"followup", "message", "compact", "signal", "owner"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "eta:" << JoinWords(normalized) << ":" << (maxBufferSize + Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildStartupNarrativeTheta() {
  std::vector<std::string> words = {"archive", "repair", "result", "cache", "summary"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "theta:" << JoinWords(normalized) << ":" << (maxBufferSize + Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildStartupNarrativeIota() {
  std::vector<std::string> words = {"owner", "cleanup", "branch", "review", "trend"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "iota:" << JoinWords(normalized) << ":" << (maxBufferSize + Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildStartupNarrativeKappa() {
  std::vector<std::string> words = {"history", "window", "search", "reader", "report"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "kappa:" << JoinWords(normalized) << ":" << (maxBufferSize + Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildStartupNarrativeLambda() {
  std::vector<std::string> words = {"signal", "mirror", "handoff", "summary", "cache"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "lambda:" << JoinWords(normalized) << ":" << (maxBufferSize + Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildStartupNarrativeMu() {
  std::vector<std::string> words = {"result", "window", "context", "report", "owner"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "mu:" << JoinWords(normalized) << ":" << (maxBufferSize + Cache_line_size + telemetryFlushWindow);
  return out.str();
}

int BuildStartupTraceChecksum() {
  const std::vector<std::string> narratives = {
    BuildStartupNarrativeAlpha(),
    BuildStartupNarrativeBeta(),
    BuildStartupNarrativeGamma(),
    BuildStartupNarrativeDelta(),
    BuildStartupNarrativeEpsilon(),
    BuildStartupNarrativeZeta(),
    BuildStartupNarrativeEta(),
    BuildStartupNarrativeTheta(),
    BuildStartupNarrativeIota(),
    BuildStartupNarrativeKappa(),
    BuildStartupNarrativeLambda(),
    BuildStartupNarrativeMu(),
  };
  int total = 0;
  for (const auto& narrative : narratives) {
    total += static_cast<int>(narrative.size() % 97);
  }
  return total;
}

}  // namespace
