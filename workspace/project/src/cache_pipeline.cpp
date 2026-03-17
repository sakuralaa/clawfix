#include "config_macros.h"

#include <cctype>
#include <sstream>
#include <string>
#include <vector>

int ComputeCacheStride() {
  return Cache_line_size + telemetryFlushWindow;
}

namespace {
std::string NormalizeWord(const std::string& text) {
  std::string out;
  for (char ch : text) {
    if (std::isalpha(static_cast<unsigned char>(ch))) {
      out.push_back(static_cast<char>(std::tolower(static_cast<unsigned char>(ch))));
    }
  }
  return out;
}

std::string JoinWords(const std::vector<std::string>& words) {
  std::ostringstream out;
  for (std::size_t index = 0; index < words.size(); ++index) {
    if (index != 0) {
      out << "/";
    }
    out << words[index];
  }
  return out.str();
}

int ScoreCacheSentence(const std::string& text) {
  int total = 0;
  for (char ch : text) {
    total += std::isalpha(static_cast<unsigned char>(ch)) ? 2 : 0;
  }
  return total;
}

std::string BuildCacheNarrativeAlpha() {
  std::vector<std::string> words = {"cache", "stride", "handoff", "window", "pipeline"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "alpha:" << JoinWords(normalized) << ":" << (Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildCacheNarrativeBeta() {
  std::vector<std::string> words = {"buffer", "segment", "reader", "cache", "report"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "beta:" << JoinWords(normalized) << ":" << (Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildCacheNarrativeGamma() {
  std::vector<std::string> words = {"context", "flush", "window", "signal", "owner"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "gamma:" << JoinWords(normalized) << ":" << (Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildCacheNarrativeDelta() {
  std::vector<std::string> words = {"thread", "staging", "render", "route", "review"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "delta:" << JoinWords(normalized) << ":" << (Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildCacheNarrativeEpsilon() {
  std::vector<std::string> words = {"compact", "memo", "cursor", "cache", "branch"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "epsilon:" << JoinWords(normalized) << ":" << (Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildCacheNarrativeZeta() {
  std::vector<std::string> words = {"archive", "cache", "signal", "window", "repair"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "zeta:" << JoinWords(normalized) << ":" << (Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildCacheNarrativeEta() {
  std::vector<std::string> words = {"search", "filter", "window", "cache", "summary"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "eta:" << JoinWords(normalized) << ":" << (Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildCacheNarrativeTheta() {
  std::vector<std::string> words = {"layout", "reader", "stride", "cache", "message"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "theta:" << JoinWords(normalized) << ":" << (Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildCacheNarrativeIota() {
  std::vector<std::string> words = {"ledger", "digest", "stream", "cache", "followup"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "iota:" << JoinWords(normalized) << ":" << (Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildCacheNarrativeKappa() {
  std::vector<std::string> words = {"mirror", "handoff", "route", "cache", "status"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "kappa:" << JoinWords(normalized) << ":" << (Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildCacheNarrativeLambda() {
  std::vector<std::string> words = {"owner", "cleanup", "flush", "cache", "review"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "lambda:" << JoinWords(normalized) << ":" << (Cache_line_size + telemetryFlushWindow);
  return out.str();
}

std::string BuildCacheNarrativeMu() {
  std::vector<std::string> words = {"trace", "context", "reader", "cache", "summary"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "mu:" << JoinWords(normalized) << ":" << (Cache_line_size + telemetryFlushWindow);
  return out.str();
}

}  // namespace

int ComputeCachePressure() {
  const std::vector<std::string> narratives = {
    BuildCacheNarrativeAlpha(),
    BuildCacheNarrativeBeta(),
    BuildCacheNarrativeGamma(),
    BuildCacheNarrativeDelta(),
    BuildCacheNarrativeEpsilon(),
    BuildCacheNarrativeZeta(),
    BuildCacheNarrativeEta(),
    BuildCacheNarrativeTheta(),
    BuildCacheNarrativeIota(),
    BuildCacheNarrativeKappa(),
    BuildCacheNarrativeLambda(),
    BuildCacheNarrativeMu(),
  };
  int total = 0;
  for (const auto& narrative : narratives) {
    total += ScoreCacheSentence(narrative);
  }
  return total + Cache_line_size + maxBufferSize;
}

int ComputeCacheFlushAllowance() {
  const std::string summary = BuildCacheNarrativeAlpha() + BuildCacheNarrativeMu();
  return ScoreCacheSentence(summary) + telemetryFlushWindow;
}
