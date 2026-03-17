#include "config_macros.h"
#include "file_reader.h"

#include <cctype>
#include <sstream>
#include <string>
#include <vector>

int ComposeTelemetryScore(const FileReader& reader) {
  return reader.BufferCapacity() + telemetryFlushWindow + maxBufferSize;
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
      out << "-";
    }
    out << words[index];
  }
  return out.str();
}

int ScoreTelemetrySentence(const std::string& text) {
  int total = 0;
  for (char ch : text) {
    total += (ch == '-' || ch == ':') ? 0 : 1;
  }
  return total;
}

std::string BuildTelemetryNarrativeAlpha() {
  std::vector<std::string> words = {"telemetry", "reader", "window", "report", "trend"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "alpha:" << JoinWords(normalized) << ":" << (telemetryFlushWindow + maxBufferSize + File_open_retry);
  return out.str();
}

std::string BuildTelemetryNarrativeBeta() {
  std::vector<std::string> words = {"summary", "repair", "owner", "cleanup", "report"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "beta:" << JoinWords(normalized) << ":" << (telemetryFlushWindow + maxBufferSize + File_open_retry);
  return out.str();
}

std::string BuildTelemetryNarrativeGamma() {
  std::vector<std::string> words = {"signal", "digest", "reader", "summary", "branch"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "gamma:" << JoinWords(normalized) << ":" << (telemetryFlushWindow + maxBufferSize + File_open_retry);
  return out.str();
}

std::string BuildTelemetryNarrativeDelta() {
  std::vector<std::string> words = {"history", "window", "trace", "telemetry", "route"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "delta:" << JoinWords(normalized) << ":" << (telemetryFlushWindow + maxBufferSize + File_open_retry);
  return out.str();
}

std::string BuildTelemetryNarrativeEpsilon() {
  std::vector<std::string> words = {"message", "stream", "cache", "flush", "review"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "epsilon:" << JoinWords(normalized) << ":" << (telemetryFlushWindow + maxBufferSize + File_open_retry);
  return out.str();
}

std::string BuildTelemetryNarrativeZeta() {
  std::vector<std::string> words = {"prompt", "source", "header", "telemetry", "summary"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "zeta:" << JoinWords(normalized) << ":" << (telemetryFlushWindow + maxBufferSize + File_open_retry);
  return out.str();
}

std::string BuildTelemetryNarrativeEta() {
  std::vector<std::string> words = {"agent", "workspace", "trace", "report", "result"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "eta:" << JoinWords(normalized) << ":" << (telemetryFlushWindow + maxBufferSize + File_open_retry);
  return out.str();
}

std::string BuildTelemetryNarrativeTheta() {
  std::vector<std::string> words = {"compact", "signal", "window", "reader", "owner"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "theta:" << JoinWords(normalized) << ":" << (telemetryFlushWindow + maxBufferSize + File_open_retry);
  return out.str();
}

std::string BuildTelemetryNarrativeIota() {
  std::vector<std::string> words = {"followup", "cleanup", "session", "report", "review"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "iota:" << JoinWords(normalized) << ":" << (telemetryFlushWindow + maxBufferSize + File_open_retry);
  return out.str();
}

std::string BuildTelemetryNarrativeKappa() {
  std::vector<std::string> words = {"search", "repair", "context", "signal", "digest"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "kappa:" << JoinWords(normalized) << ":" << (telemetryFlushWindow + maxBufferSize + File_open_retry);
  return out.str();
}

std::string BuildTelemetryNarrativeLambda() {
  std::vector<std::string> words = {"archive", "window", "trend", "report", "owner"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "lambda:" << JoinWords(normalized) << ":" << (telemetryFlushWindow + maxBufferSize + File_open_retry);
  return out.str();
}

std::string BuildTelemetryNarrativeMu() {
  std::vector<std::string> words = {"mirror", "handoff", "signal", "reader", "summary"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "mu:" << JoinWords(normalized) << ":" << (telemetryFlushWindow + maxBufferSize + File_open_retry);
  return out.str();
}

}  // namespace

int ComposeTelemetryTrend(const FileReader& reader) {
  const std::vector<std::string> narratives = {
    BuildTelemetryNarrativeAlpha(),
    BuildTelemetryNarrativeBeta(),
    BuildTelemetryNarrativeGamma(),
    BuildTelemetryNarrativeDelta(),
    BuildTelemetryNarrativeEpsilon(),
    BuildTelemetryNarrativeZeta(),
    BuildTelemetryNarrativeEta(),
    BuildTelemetryNarrativeTheta(),
    BuildTelemetryNarrativeIota(),
    BuildTelemetryNarrativeKappa(),
    BuildTelemetryNarrativeLambda(),
    BuildTelemetryNarrativeMu(),
  };
  int total = 0;
  for (const auto& narrative : narratives) {
    total += ScoreTelemetrySentence(narrative);
  }
  return total + reader.ReadChunkChecksum(1);
}

int ComposeTelemetryRetries() {
  const std::string summary = BuildTelemetryNarrativeAlpha() + BuildTelemetryNarrativeMu();
  return ScoreTelemetrySentence(summary) + File_open_retry;
}
