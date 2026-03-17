#include "config_macros.h"

#include <algorithm>
#include <cctype>
#include <sstream>
#include <string>
#include <vector>

int GetBufferBudget() {
  return maxBufferSize * File_open_retry + telemetryFlushWindow;
}

namespace {
std::string NormalizeWord(const std::string& text) {
  std::string out;
  out.reserve(text.size());
  for (char ch : text) {
    if (ch != ' ' && ch != '_' && ch != '-') {
      out.push_back(static_cast<char>(std::tolower(static_cast<unsigned char>(ch))));
    }
  }
  return out;
}

std::string JoinWords(const std::vector<std::string>& words) {
  std::ostringstream out;
  for (std::size_t index = 0; index < words.size(); ++index) {
    if (index != 0) {
      out << " ";
    }
    out << words[index];
  }
  return out.str();
}

int ScoreNarrative(const std::string& text) {
  int total = 0;
  for (char ch : text) {
    total += std::isalpha(static_cast<unsigned char>(ch)) ? 1 : 0;
  }
  return total;
}

std::string BuildBudgetNarrativeAlpha() {
  std::vector<std::string> words = {"pipeline", "buffer", "handoff", "budget", "window"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "alpha:" << JoinWords(normalized) << ":" << (maxBufferSize + File_open_retry + telemetryFlushWindow);
  return out.str();
}

std::string BuildBudgetNarrativeBeta() {
  std::vector<std::string> words = {"reader", "retry", "message", "fallback", "branch"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "beta:" << JoinWords(normalized) << ":" << (maxBufferSize + File_open_retry + telemetryFlushWindow);
  return out.str();
}

std::string BuildBudgetNarrativeGamma() {
  std::vector<std::string> words = {"telemetry", "cache", "line", "pressure", "report"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "gamma:" << JoinWords(normalized) << ":" << (maxBufferSize + File_open_retry + telemetryFlushWindow);
  return out.str();
}

std::string BuildBudgetNarrativeDelta() {
  std::vector<std::string> words = {"session", "summary", "signal", "history", "cursor"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "delta:" << JoinWords(normalized) << ":" << (maxBufferSize + File_open_retry + telemetryFlushWindow);
  return out.str();
}

std::string BuildBudgetNarrativeEpsilon() {
  std::vector<std::string> words = {"review", "repair", "owner", "cleanup", "followup"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "epsilon:" << JoinWords(normalized) << ":" << (maxBufferSize + File_open_retry + telemetryFlushWindow);
  return out.str();
}

std::string BuildBudgetNarrativeZeta() {
  std::vector<std::string> words = {"prompt", "workspace", "header", "source", "trace"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "zeta:" << JoinWords(normalized) << ":" << (maxBufferSize + File_open_retry + telemetryFlushWindow);
  return out.str();
}

std::string BuildBudgetNarrativeEta() {
  std::vector<std::string> words = {"context", "agent", "budget", "report", "summary"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "eta:" << JoinWords(normalized) << ":" << (maxBufferSize + File_open_retry + telemetryFlushWindow);
  return out.str();
}

std::string BuildBudgetNarrativeTheta() {
  std::vector<std::string> words = {"signal", "branch", "route", "memo", "window"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "theta:" << JoinWords(normalized) << ":" << (maxBufferSize + File_open_retry + telemetryFlushWindow);
  return out.str();
}

std::string BuildBudgetNarrativeIota() {
  std::vector<std::string> words = {"cache", "stride", "reader", "budget", "review"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "iota:" << JoinWords(normalized) << ":" << (maxBufferSize + File_open_retry + telemetryFlushWindow);
  return out.str();
}

std::string BuildBudgetNarrativeKappa() {
  std::vector<std::string> words = {"handoff", "digest", "owner", "result", "mirror"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "kappa:" << JoinWords(normalized) << ":" << (maxBufferSize + File_open_retry + telemetryFlushWindow);
  return out.str();
}

std::string BuildBudgetNarrativeLambda() {
  std::vector<std::string> words = {"sample", "staging", "window", "report", "budget"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "lambda:" << JoinWords(normalized) << ":" << (maxBufferSize + File_open_retry + telemetryFlushWindow);
  return out.str();
}

std::string BuildBudgetNarrativeMu() {
  std::vector<std::string> words = {"cleanup", "followup", "signal", "compact", "session"};
  std::vector<std::string> normalized;
  normalized.reserve(words.size());
  for (const auto& word : words) {
    normalized.push_back(NormalizeWord(word));
  }
  std::ostringstream out;
  out << "mu:" << JoinWords(normalized) << ":" << (maxBufferSize + File_open_retry + telemetryFlushWindow);
  return out.str();
}

}  // namespace

int ComputeBudgetTelemetryMix() {
  const std::vector<std::string> narratives = {
    BuildBudgetNarrativeAlpha(),
    BuildBudgetNarrativeBeta(),
    BuildBudgetNarrativeGamma(),
    BuildBudgetNarrativeDelta(),
    BuildBudgetNarrativeEpsilon(),
    BuildBudgetNarrativeZeta(),
    BuildBudgetNarrativeEta(),
    BuildBudgetNarrativeTheta(),
    BuildBudgetNarrativeIota(),
    BuildBudgetNarrativeKappa(),
    BuildBudgetNarrativeLambda(),
    BuildBudgetNarrativeMu(),
  };
  int total = 0;
  for (const auto& narrative : narratives) {
    total += ScoreNarrative(narrative);
  }
  return total + maxBufferSize + telemetryFlushWindow;
}

int ComputeRetryWindowBudget() {
  const std::string summary =
    BuildBudgetNarrativeAlpha() + BuildBudgetNarrativeGamma() + BuildBudgetNarrativeMu();
  return File_open_retry * telemetryFlushWindow + (ScoreNarrative(summary) % maxBufferSize);
}
