#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SMALL_PROJECT_SRC = ROOT / "fixtures" / "project"
SMALL_SIGNAL_SRC = ROOT / "fixtures" / "static-signals" / "small-findings.json"
LARGE_SIGNAL_SRC = ROOT / "fixtures" / "static-signals" / "large-findings.json"
PROJECT_DST = ROOT / "workspace" / "project"
SIGNAL_DST = ROOT / "workspace" / "static-signals" / "current-findings.json"


def _write_files(base: Path, files: dict[str, str]) -> None:
    for rel_path, content in files.items():
        path = base / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def _scenario_lines(
    *,
    function_name: str,
    words: list[str],
    label: str,
    macro_expression: str,
) -> list[str]:
    quoted_words = ", ".join(f'"{word}"' for word in words)
    return [
        f"std::string {function_name}() {{",
        f"  std::vector<std::string> words = {{{quoted_words}}};",
        "  std::vector<std::string> normalized;",
        "  normalized.reserve(words.size());",
        "  for (const auto& word : words) {",
        "    normalized.push_back(NormalizeWord(word));",
        "  }",
        "  std::ostringstream out;",
        f'  out << "{label}:" << JoinWords(normalized) << ":" << ({macro_expression});',
        "  return out.str();",
        "}",
        "",
    ]


def _large_project_files() -> dict[str, str]:
    config_macros = "\n".join(
        [
            "#ifndef CONFIG_MACROS_H",
            "#define CONFIG_MACROS_H",
            "",
            "#define maxBufferSize 256",
            "#define File_open_retry 3",
            "#define telemetryFlushWindow 12",
            "#define Cache_line_size 64",
            "",
            "#endif",
            "",
        ]
    )

    file_reader_h = "\n".join(
        [
            "#ifndef FILE_READER_H",
            "#define FILE_READER_H",
            "",
            "#include <cstdio>",
            "#include <string>",
            "#include <vector>",
            "",
            "struct ReaderDigest {",
            "  int visibleCharacters;",
            "  int uppercaseCharacters;",
            "  int lowercaseCharacters;",
            "  int punctuationCharacters;",
            "};",
            "",
            "class FileReader {",
            "public:",
            "  explicit FileReader(const std::string& path);",
            "  std::string ReadLine();",
            "  bool IsOpen() const;",
            "  int ReadChunkChecksum(int chunk) const;",
            "  int RetryBudget() const;",
            "  int BufferCapacity() const;",
            "  std::string DescribeWindow() const;",
            "  ReaderDigest InspectText(const std::string& text) const;",
            "",
            "private:",
            "  FILE* file_;",
            "  std::string path_;",
            "  int cached_window_;",
            "  std::vector<std::string> startup_notes_;",
            "};",
            "",
            "#endif",
            "",
        ]
    )

    file_reader_cpp_lines = [
        '#include "file_reader.h"',
        "",
        "#include <array>",
        "#include <cctype>",
        "#include <sstream>",
        "",
        'FileReader::FileReader(const std::string& path) : file_(std::fopen(path.c_str(), "r")), path_(path), cached_window_(0), startup_notes_{} {}',
        "",
        "namespace {",
        "std::string NormalizeWord(const std::string& text) {",
        "  std::string out;",
        "  out.reserve(text.size());",
        "  for (char ch : text) {",
        "    if (std::isalnum(static_cast<unsigned char>(ch))) {",
        "      out.push_back(static_cast<char>(std::tolower(static_cast<unsigned char>(ch))));",
        "    }",
        "  }",
        "  return out;",
        "}",
        "",
        "std::string JoinWords(const std::vector<std::string>& words) {",
        "  std::ostringstream out;",
        "  for (std::size_t index = 0; index < words.size(); ++index) {",
        "    if (index != 0) {",
        '      out << ",";',
        "    }",
        "    out << words[index];",
        "  }",
        "  return out.str();",
        "}",
        "",
        "int CountVisibleCharacters(const std::string& text) {",
        "  int total = 0;",
        "  for (char ch : text) {",
        "    if (!std::isspace(static_cast<unsigned char>(ch))) {",
        "      ++total;",
        "    }",
        "  }",
        "  return total;",
        "}",
        "",
        "int CountUppercaseCharacters(const std::string& text) {",
        "  int total = 0;",
        "  for (char ch : text) {",
        "    if (std::isupper(static_cast<unsigned char>(ch))) {",
        "      ++total;",
        "    }",
        "  }",
        "  return total;",
        "}",
        "",
        "int CountLowercaseCharacters(const std::string& text) {",
        "  int total = 0;",
        "  for (char ch : text) {",
        "    if (std::islower(static_cast<unsigned char>(ch))) {",
        "      ++total;",
        "    }",
        "  }",
        "  return total;",
        "}",
        "",
        "int CountPunctuationCharacters(const std::string& text) {",
        "  int total = 0;",
        "  for (char ch : text) {",
        "    if (std::ispunct(static_cast<unsigned char>(ch))) {",
        "      ++total;",
        "    }",
        "  }",
        "  return total;",
        "}",
        "",
    ]
    reader_notes = [
        ("BuildReaderNarrativeAlpha", ["ingest", "window", "reader", "sample", "handoff"], "alpha"),
        ("BuildReaderNarrativeBeta", ["buffer", "handoff", "summary", "sample", "journal"], "beta"),
        ("BuildReaderNarrativeGamma", ["persist", "cursor", "archive", "snapshot", "delta"], "gamma"),
        ("BuildReaderNarrativeDelta", ["render", "window", "cache", "merge", "outline"], "delta"),
        ("BuildReaderNarrativeEpsilon", ["repair", "report", "history", "branch", "search"], "epsilon"),
        ("BuildReaderNarrativeZeta", ["header", "source", "owner", "cleanup", "review"], "zeta"),
        ("BuildReaderNarrativeEta", ["stream", "record", "digest", "checkpoint", "staging"], "eta"),
        ("BuildReaderNarrativeTheta", ["message", "signal", "context", "trace", "session"], "theta"),
        ("BuildReaderNarrativeIota", ["throttle", "cursor", "ledger", "handoff", "mirror"], "iota"),
        ("BuildReaderNarrativeKappa", ["verify", "sample", "result", "window", "reader"], "kappa"),
        ("BuildReaderNarrativeLambda", ["line", "parse", "normalize", "compact", "summary"], "lambda"),
        ("BuildReaderNarrativeMu", ["token", "state", "followup", "ownership", "cleanup"], "mu"),
    ]
    for function_name, words, label in reader_notes:
        file_reader_cpp_lines.extend(
            _scenario_lines(
                function_name=function_name,
                words=words,
                label=label,
                macro_expression="static_cast<int>(JoinWords(normalized).size())",
            )
        )
    file_reader_cpp_lines.extend(
        [
            "}  // namespace",
            "",
            "std::string FileReader::ReadLine() {",
            "  if (file_ == nullptr) {",
            "    return {};",
            "  }",
            "",
            "  std::array<char, 256> buffer{};",
            "  if (std::fgets(buffer.data(), static_cast<int>(buffer.size()), file_) == nullptr) {",
            "    return {};",
            "  }",
            "  return std::string(buffer.data());",
            "}",
            "",
            "bool FileReader::IsOpen() const {",
            "  return file_ != nullptr;",
            "}",
            "",
            "int FileReader::ReadChunkChecksum(int chunk) const {",
            "  const std::vector<std::string> narratives = {",
            "    BuildReaderNarrativeAlpha(),",
            "    BuildReaderNarrativeBeta(),",
            "    BuildReaderNarrativeGamma(),",
            "    BuildReaderNarrativeDelta(),",
            "    BuildReaderNarrativeEpsilon(),",
            "    BuildReaderNarrativeZeta(),",
            "    BuildReaderNarrativeEta(),",
            "    BuildReaderNarrativeTheta(),",
            "    BuildReaderNarrativeIota(),",
            "    BuildReaderNarrativeKappa(),",
            "    BuildReaderNarrativeLambda(),",
            "    BuildReaderNarrativeMu(),",
            "  };",
            "  int total = 0;",
            "  for (const auto& narrative : narratives) {",
            "    total += CountVisibleCharacters(narrative) + chunk;",
            "  }",
            "  return total + cached_window_;",
            "}",
            "",
            "int FileReader::RetryBudget() const {",
            "  return static_cast<int>(startup_notes_.size()) + 3;",
            "}",
            "",
            "int FileReader::BufferCapacity() const {",
            "  return 256 + cached_window_;",
            "}",
            "",
            "std::string FileReader::DescribeWindow() const {",
            "  std::vector<std::string> words = {",
            '    "reader",',
            '    "window",',
            '    "digest",',
            '    "handoff",',
            '    "summary",',
            "  };",
            '  return path_ + ":window=" + JoinWords(words) + ":" + std::to_string(ReadChunkChecksum(2));',
            "}",
            "",
            "ReaderDigest FileReader::InspectText(const std::string& text) const {",
            "  return ReaderDigest{",
            "    CountVisibleCharacters(text),",
            "    CountUppercaseCharacters(text),",
            "    CountLowercaseCharacters(text),",
            "    CountPunctuationCharacters(text),",
            "  };",
            "}",
            "",
        ]
    )
    file_reader_cpp = "\n".join(file_reader_cpp_lines)

    config_usage_lines = [
        '#include "config_macros.h"',
        "",
        "#include <algorithm>",
        "#include <cctype>",
        "#include <sstream>",
        "#include <string>",
        "#include <vector>",
        "",
        "int GetBufferBudget() {",
        "  return maxBufferSize * File_open_retry + telemetryFlushWindow;",
        "}",
        "",
        "namespace {",
        "std::string NormalizeWord(const std::string& text) {",
        "  std::string out;",
        "  out.reserve(text.size());",
        "  for (char ch : text) {",
        "    if (ch != ' ' && ch != '_' && ch != '-') {",
        "      out.push_back(static_cast<char>(std::tolower(static_cast<unsigned char>(ch))));",
        "    }",
        "  }",
        "  return out;",
        "}",
        "",
        "std::string JoinWords(const std::vector<std::string>& words) {",
        "  std::ostringstream out;",
        "  for (std::size_t index = 0; index < words.size(); ++index) {",
        "    if (index != 0) {",
        '      out << " ";',
        "    }",
        "    out << words[index];",
        "  }",
        "  return out.str();",
        "}",
        "",
        "int ScoreNarrative(const std::string& text) {",
        "  int total = 0;",
        "  for (char ch : text) {",
        "    total += std::isalpha(static_cast<unsigned char>(ch)) ? 1 : 0;",
        "  }",
        "  return total;",
        "}",
        "",
    ]
    budget_scenarios = [
        ("BuildBudgetNarrativeAlpha", ["pipeline", "buffer", "handoff", "budget", "window"], "alpha"),
        ("BuildBudgetNarrativeBeta", ["reader", "retry", "message", "fallback", "branch"], "beta"),
        ("BuildBudgetNarrativeGamma", ["telemetry", "cache", "line", "pressure", "report"], "gamma"),
        ("BuildBudgetNarrativeDelta", ["session", "summary", "signal", "history", "cursor"], "delta"),
        ("BuildBudgetNarrativeEpsilon", ["review", "repair", "owner", "cleanup", "followup"], "epsilon"),
        ("BuildBudgetNarrativeZeta", ["prompt", "workspace", "header", "source", "trace"], "zeta"),
        ("BuildBudgetNarrativeEta", ["context", "agent", "budget", "report", "summary"], "eta"),
        ("BuildBudgetNarrativeTheta", ["signal", "branch", "route", "memo", "window"], "theta"),
        ("BuildBudgetNarrativeIota", ["cache", "stride", "reader", "budget", "review"], "iota"),
        ("BuildBudgetNarrativeKappa", ["handoff", "digest", "owner", "result", "mirror"], "kappa"),
        ("BuildBudgetNarrativeLambda", ["sample", "staging", "window", "report", "budget"], "lambda"),
        ("BuildBudgetNarrativeMu", ["cleanup", "followup", "signal", "compact", "session"], "mu"),
    ]
    for function_name, words, label in budget_scenarios:
        config_usage_lines.extend(
            _scenario_lines(
                function_name=function_name,
                words=words,
                label=label,
                macro_expression="maxBufferSize + File_open_retry + telemetryFlushWindow",
            )
        )
    config_usage_lines.extend(
        [
            "}  // namespace",
            "",
            "int ComputeBudgetTelemetryMix() {",
            "  const std::vector<std::string> narratives = {",
            "    BuildBudgetNarrativeAlpha(),",
            "    BuildBudgetNarrativeBeta(),",
            "    BuildBudgetNarrativeGamma(),",
            "    BuildBudgetNarrativeDelta(),",
            "    BuildBudgetNarrativeEpsilon(),",
            "    BuildBudgetNarrativeZeta(),",
            "    BuildBudgetNarrativeEta(),",
            "    BuildBudgetNarrativeTheta(),",
            "    BuildBudgetNarrativeIota(),",
            "    BuildBudgetNarrativeKappa(),",
            "    BuildBudgetNarrativeLambda(),",
            "    BuildBudgetNarrativeMu(),",
            "  };",
            "  int total = 0;",
            "  for (const auto& narrative : narratives) {",
            "    total += ScoreNarrative(narrative);",
            "  }",
            "  return total + maxBufferSize + telemetryFlushWindow;",
            "}",
            "",
            "int ComputeRetryWindowBudget() {",
            "  const std::string summary =",
            "    BuildBudgetNarrativeAlpha() + BuildBudgetNarrativeGamma() + BuildBudgetNarrativeMu();",
            "  return File_open_retry * telemetryFlushWindow + (ScoreNarrative(summary) % maxBufferSize);",
            "}",
            "",
        ]
    )
    config_usage_cpp = "\n".join(config_usage_lines)

    cache_pipeline_lines = [
        '#include "config_macros.h"',
        "",
        "#include <cctype>",
        "#include <sstream>",
        "#include <string>",
        "#include <vector>",
        "",
        "int ComputeCacheStride() {",
        "  return Cache_line_size + telemetryFlushWindow;",
        "}",
        "",
        "namespace {",
        "std::string NormalizeWord(const std::string& text) {",
        "  std::string out;",
        "  for (char ch : text) {",
        "    if (std::isalpha(static_cast<unsigned char>(ch))) {",
          "      out.push_back(static_cast<char>(std::tolower(static_cast<unsigned char>(ch))));",
        "    }",
        "  }",
        "  return out;",
        "}",
        "",
        "std::string JoinWords(const std::vector<std::string>& words) {",
        "  std::ostringstream out;",
        "  for (std::size_t index = 0; index < words.size(); ++index) {",
        "    if (index != 0) {",
        '      out << "/";',
        "    }",
        "    out << words[index];",
        "  }",
        "  return out.str();",
        "}",
        "",
        "int ScoreCacheSentence(const std::string& text) {",
        "  int total = 0;",
        "  for (char ch : text) {",
        "    total += std::isalpha(static_cast<unsigned char>(ch)) ? 2 : 0;",
        "  }",
        "  return total;",
        "}",
        "",
    ]
    cache_scenarios = [
        ("BuildCacheNarrativeAlpha", ["cache", "stride", "handoff", "window", "pipeline"], "alpha"),
        ("BuildCacheNarrativeBeta", ["buffer", "segment", "reader", "cache", "report"], "beta"),
        ("BuildCacheNarrativeGamma", ["context", "flush", "window", "signal", "owner"], "gamma"),
        ("BuildCacheNarrativeDelta", ["thread", "staging", "render", "route", "review"], "delta"),
        ("BuildCacheNarrativeEpsilon", ["compact", "memo", "cursor", "cache", "branch"], "epsilon"),
        ("BuildCacheNarrativeZeta", ["archive", "cache", "signal", "window", "repair"], "zeta"),
        ("BuildCacheNarrativeEta", ["search", "filter", "window", "cache", "summary"], "eta"),
        ("BuildCacheNarrativeTheta", ["layout", "reader", "stride", "cache", "message"], "theta"),
        ("BuildCacheNarrativeIota", ["ledger", "digest", "stream", "cache", "followup"], "iota"),
        ("BuildCacheNarrativeKappa", ["mirror", "handoff", "route", "cache", "status"], "kappa"),
        ("BuildCacheNarrativeLambda", ["owner", "cleanup", "flush", "cache", "review"], "lambda"),
        ("BuildCacheNarrativeMu", ["trace", "context", "reader", "cache", "summary"], "mu"),
    ]
    for function_name, words, label in cache_scenarios:
        cache_pipeline_lines.extend(
            _scenario_lines(
                function_name=function_name,
                words=words,
                label=label,
                macro_expression="Cache_line_size + telemetryFlushWindow",
            )
        )
    cache_pipeline_lines.extend(
        [
            "}  // namespace",
            "",
            "int ComputeCachePressure() {",
            "  const std::vector<std::string> narratives = {",
            "    BuildCacheNarrativeAlpha(),",
            "    BuildCacheNarrativeBeta(),",
            "    BuildCacheNarrativeGamma(),",
            "    BuildCacheNarrativeDelta(),",
            "    BuildCacheNarrativeEpsilon(),",
            "    BuildCacheNarrativeZeta(),",
            "    BuildCacheNarrativeEta(),",
            "    BuildCacheNarrativeTheta(),",
            "    BuildCacheNarrativeIota(),",
            "    BuildCacheNarrativeKappa(),",
            "    BuildCacheNarrativeLambda(),",
            "    BuildCacheNarrativeMu(),",
            "  };",
            "  int total = 0;",
            "  for (const auto& narrative : narratives) {",
            "    total += ScoreCacheSentence(narrative);",
            "  }",
            "  return total + Cache_line_size + maxBufferSize;",
            "}",
            "",
            "int ComputeCacheFlushAllowance() {",
            "  const std::string summary = BuildCacheNarrativeAlpha() + BuildCacheNarrativeMu();",
            "  return ScoreCacheSentence(summary) + telemetryFlushWindow;",
            "}",
            "",
        ]
    )
    cache_pipeline_cpp = "\n".join(cache_pipeline_lines)

    telemetry_report_lines = [
        '#include "config_macros.h"',
        '#include "file_reader.h"',
        "",
        "#include <cctype>",
        "#include <sstream>",
        "#include <string>",
        "#include <vector>",
        "",
        "int ComposeTelemetryScore(const FileReader& reader) {",
        "  return reader.BufferCapacity() + telemetryFlushWindow + maxBufferSize;",
        "}",
        "",
        "namespace {",
        "std::string NormalizeWord(const std::string& text) {",
        "  std::string out;",
        "  out.reserve(text.size());",
        "  for (char ch : text) {",
        "    if (std::isalnum(static_cast<unsigned char>(ch))) {",
        "      out.push_back(static_cast<char>(std::tolower(static_cast<unsigned char>(ch))));",
        "    }",
        "  }",
        "  return out;",
        "}",
        "",
        "std::string JoinWords(const std::vector<std::string>& words) {",
        "  std::ostringstream out;",
        "  for (std::size_t index = 0; index < words.size(); ++index) {",
        "    if (index != 0) {",
        '      out << "-";',
        "    }",
        "    out << words[index];",
        "  }",
        "  return out.str();",
        "}",
        "",
        "int ScoreTelemetrySentence(const std::string& text) {",
        "  int total = 0;",
        "  for (char ch : text) {",
        "    total += (ch == '-' || ch == ':') ? 0 : 1;",
        "  }",
        "  return total;",
        "}",
        "",
    ]
    telemetry_scenarios = [
        ("BuildTelemetryNarrativeAlpha", ["telemetry", "reader", "window", "report", "trend"], "alpha"),
        ("BuildTelemetryNarrativeBeta", ["summary", "repair", "owner", "cleanup", "report"], "beta"),
        ("BuildTelemetryNarrativeGamma", ["signal", "digest", "reader", "summary", "branch"], "gamma"),
        ("BuildTelemetryNarrativeDelta", ["history", "window", "trace", "telemetry", "route"], "delta"),
        ("BuildTelemetryNarrativeEpsilon", ["message", "stream", "cache", "flush", "review"], "epsilon"),
        ("BuildTelemetryNarrativeZeta", ["prompt", "source", "header", "telemetry", "summary"], "zeta"),
        ("BuildTelemetryNarrativeEta", ["agent", "workspace", "trace", "report", "result"], "eta"),
        ("BuildTelemetryNarrativeTheta", ["compact", "signal", "window", "reader", "owner"], "theta"),
        ("BuildTelemetryNarrativeIota", ["followup", "cleanup", "session", "report", "review"], "iota"),
        ("BuildTelemetryNarrativeKappa", ["search", "repair", "context", "signal", "digest"], "kappa"),
        ("BuildTelemetryNarrativeLambda", ["archive", "window", "trend", "report", "owner"], "lambda"),
        ("BuildTelemetryNarrativeMu", ["mirror", "handoff", "signal", "reader", "summary"], "mu"),
    ]
    for function_name, words, label in telemetry_scenarios:
        telemetry_report_lines.extend(
            _scenario_lines(
                function_name=function_name,
                words=words,
                label=label,
                macro_expression="telemetryFlushWindow + maxBufferSize + File_open_retry",
            )
        )
    telemetry_report_lines.extend(
        [
            "}  // namespace",
            "",
            "int ComposeTelemetryTrend(const FileReader& reader) {",
            "  const std::vector<std::string> narratives = {",
            "    BuildTelemetryNarrativeAlpha(),",
            "    BuildTelemetryNarrativeBeta(),",
            "    BuildTelemetryNarrativeGamma(),",
            "    BuildTelemetryNarrativeDelta(),",
            "    BuildTelemetryNarrativeEpsilon(),",
            "    BuildTelemetryNarrativeZeta(),",
            "    BuildTelemetryNarrativeEta(),",
            "    BuildTelemetryNarrativeTheta(),",
            "    BuildTelemetryNarrativeIota(),",
            "    BuildTelemetryNarrativeKappa(),",
            "    BuildTelemetryNarrativeLambda(),",
            "    BuildTelemetryNarrativeMu(),",
            "  };",
            "  int total = 0;",
            "  for (const auto& narrative : narratives) {",
            "    total += ScoreTelemetrySentence(narrative);",
            "  }",
            "  return total + reader.ReadChunkChecksum(1);",
            "}",
            "",
            "int ComposeTelemetryRetries() {",
            "  const std::string summary = BuildTelemetryNarrativeAlpha() + BuildTelemetryNarrativeMu();",
            "  return ScoreTelemetrySentence(summary) + File_open_retry;",
            "}",
            "",
        ]
    )
    telemetry_report_cpp = "\n".join(telemetry_report_lines)

    main_lines = [
        '#include "config_macros.h"',
        '#include "file_reader.h"',
        "",
        "#include <cctype>",
        "#include <iostream>",
        "#include <sstream>",
        "#include <string>",
        "#include <vector>",
        "",
        "int GetBufferBudget();",
        "int ComputeBudgetTelemetryMix();",
        "int ComputeRetryWindowBudget();",
        "int ComputeCacheStride();",
        "int ComputeCachePressure();",
        "int ComputeCacheFlushAllowance();",
        "int ComposeTelemetryScore(const FileReader& reader);",
        "int ComposeTelemetryTrend(const FileReader& reader);",
        "int ComposeTelemetryRetries();",
        "namespace {",
        "int BuildStartupTraceChecksum();",
        "std::string BuildStartupNarrativeAlpha();",
        "std::string BuildStartupNarrativeBeta();",
        "std::string BuildStartupNarrativeGamma();",
        "std::string BuildStartupNarrativeDelta();",
        "std::string BuildStartupNarrativeEpsilon();",
        "std::string BuildStartupNarrativeZeta();",
        "std::string BuildStartupNarrativeEta();",
        "std::string BuildStartupNarrativeTheta();",
        "std::string BuildStartupNarrativeIota();",
        "std::string BuildStartupNarrativeKappa();",
        "std::string BuildStartupNarrativeLambda();",
        "std::string BuildStartupNarrativeMu();",
        "}",
        "",
        "int main() {",
        '  FileReader reader("data/sample.txt");',
        "  if (!reader.IsOpen()) {",
        '    std::cerr << "failed to open sample file after " << File_open_retry << " retries\\n";',
        "    return 1;",
        "  }",
        "",
        '  std::cout << "budget=" << GetBufferBudget()',
        '            << " mix=" << ComputeBudgetTelemetryMix()',
        '            << " retry-window=" << ComputeRetryWindowBudget()',
        '            << " cache-stride=" << ComputeCacheStride()',
        '            << " cache-pressure=" << ComputeCachePressure()',
        '            << " cache-flush=" << ComputeCacheFlushAllowance()',
        '            << " telemetry-score=" << ComposeTelemetryScore(reader)',
        '            << " telemetry-trend=" << ComposeTelemetryTrend(reader)',
        '            << " telemetry-retries=" << ComposeTelemetryRetries()',
        '            << " startup-trace=" << BuildStartupTraceChecksum()',
        '            << " max=" << maxBufferSize',
        '            << " cache-line=" << Cache_line_size',
        '            << " line=" << reader.ReadLine();',
        "  return 0;",
        "}",
        "",
        "namespace {",
        "std::string NormalizeWord(const std::string& text) {",
        "  std::string out;",
        "  out.reserve(text.size());",
        "  for (char ch : text) {",
        "    if (std::isalnum(static_cast<unsigned char>(ch))) {",
        "      out.push_back(static_cast<char>(std::tolower(static_cast<unsigned char>(ch))));",
        "    }",
        "  }",
        "  return out;",
        "}",
        "",
        "std::string JoinWords(const std::vector<std::string>& words) {",
        "  std::ostringstream out;",
        "  for (std::size_t index = 0; index < words.size(); ++index) {",
        "    if (index != 0) {",
        '      out << "|";',
        "    }",
        "    out << words[index];",
        "  }",
        "  return out.str();",
        "}",
        "",
    ]
    startup_scenarios = [
        ("BuildStartupNarrativeAlpha", ["startup", "reader", "window", "budget", "report"], "alpha"),
        ("BuildStartupNarrativeBeta", ["context", "handoff", "signal", "cache", "owner"], "beta"),
        ("BuildStartupNarrativeGamma", ["stream", "summary", "repair", "branch", "result"], "gamma"),
        ("BuildStartupNarrativeDelta", ["telemetry", "route", "review", "session", "trace"], "delta"),
        ("BuildStartupNarrativeEpsilon", ["workspace", "header", "source", "cleanup", "owner"], "epsilon"),
        ("BuildStartupNarrativeZeta", ["prompt", "context", "window", "reader", "digest"], "zeta"),
        ("BuildStartupNarrativeEta", ["followup", "message", "compact", "signal", "owner"], "eta"),
        ("BuildStartupNarrativeTheta", ["archive", "repair", "result", "cache", "summary"], "theta"),
        ("BuildStartupNarrativeIota", ["owner", "cleanup", "branch", "review", "trend"], "iota"),
        ("BuildStartupNarrativeKappa", ["history", "window", "search", "reader", "report"], "kappa"),
        ("BuildStartupNarrativeLambda", ["signal", "mirror", "handoff", "summary", "cache"], "lambda"),
        ("BuildStartupNarrativeMu", ["result", "window", "context", "report", "owner"], "mu"),
    ]
    for function_name, words, label in startup_scenarios:
        main_lines.extend(
            _scenario_lines(
                function_name=function_name,
                words=words,
                label=label,
                macro_expression="maxBufferSize + Cache_line_size + telemetryFlushWindow",
            )
        )
    main_lines.extend(
        [
            "int BuildStartupTraceChecksum() {",
            "  const std::vector<std::string> narratives = {",
            "    BuildStartupNarrativeAlpha(),",
            "    BuildStartupNarrativeBeta(),",
            "    BuildStartupNarrativeGamma(),",
            "    BuildStartupNarrativeDelta(),",
            "    BuildStartupNarrativeEpsilon(),",
            "    BuildStartupNarrativeZeta(),",
            "    BuildStartupNarrativeEta(),",
            "    BuildStartupNarrativeTheta(),",
            "    BuildStartupNarrativeIota(),",
            "    BuildStartupNarrativeKappa(),",
            "    BuildStartupNarrativeLambda(),",
            "    BuildStartupNarrativeMu(),",
            "  };",
            "  int total = 0;",
            "  for (const auto& narrative : narratives) {",
            "    total += static_cast<int>(narrative.size() % 97);",
            "  }",
            "  return total;",
            "}",
            "",
            "}  // namespace",
            "",
        ]
    )
    main_cpp = "\n".join(main_lines)

    return {
        "data/sample.txt": "hello-from-large-demo\nsecond-line-for-large-demo\n",
        "include/config_macros.h": config_macros,
        "include/file_reader.h": file_reader_h,
        "src/file_reader.cpp": file_reader_cpp,
        "src/config_usage.cpp": config_usage_cpp,
        "src/cache_pipeline.cpp": cache_pipeline_cpp,
        "src/telemetry_report.cpp": telemetry_report_cpp,
        "src/main.cpp": main_cpp,
    }


def _line_number(text: str, snippet: str) -> int:
    for index, line in enumerate(text.splitlines(), start=1):
        if snippet in line:
            return index
    raise ValueError(f"snippet not found: {snippet}")


def _large_signal_payload(files: dict[str, str]) -> dict:
    macros = files["include/config_macros.h"]
    file_reader_h = files["include/file_reader.h"]
    file_reader_cpp = files["src/file_reader.cpp"]
    config_usage = files["src/config_usage.cpp"]
    cache_pipeline = files["src/cache_pipeline.cpp"]
    telemetry_report = files["src/telemetry_report.cpp"]
    main_cpp = files["src/main.cpp"]

    return {
        "workspace": "workspace/project",
        "tool": "mock-static-check",
        "scenario": "large",
        "findings": [
            {
                "id": "macro-naming-1",
                "ruleId": "macro-naming",
                "severity": "warning",
                "message": "macro maxBufferSize does not match SCREAMING_SNAKE_CASE",
                "symbol": "maxBufferSize",
                "category": "macro-naming",
                "primaryLocation": {
                    "file": "include/config_macros.h",
                    "line": _line_number(macros, "#define maxBufferSize"),
                    "column": 9,
                },
                "relatedLocations": [
                    {
                        "file": "src/config_usage.cpp",
                        "line": _line_number(config_usage, "return maxBufferSize * File_open_retry + telemetryFlushWindow;"),
                        "column": 10,
                        "message": "macro reference",
                    },
                    {
                        "file": "src/telemetry_report.cpp",
                        "line": _line_number(telemetry_report, "return reader.BufferCapacity() + telemetryFlushWindow + maxBufferSize;"),
                        "column": 46,
                        "message": "macro reference",
                    },
                    {
                        "file": "src/main.cpp",
                        "line": _line_number(main_cpp, '<< " max=" << maxBufferSize'),
                        "column": 26,
                        "message": "macro reference",
                    },
                ],
            },
            {
                "id": "macro-naming-2",
                "ruleId": "macro-naming",
                "severity": "warning",
                "message": "macro File_open_retry does not match SCREAMING_SNAKE_CASE",
                "symbol": "File_open_retry",
                "category": "macro-naming",
                "primaryLocation": {
                    "file": "include/config_macros.h",
                    "line": _line_number(macros, "#define File_open_retry"),
                    "column": 9,
                },
                "relatedLocations": [
                    {
                        "file": "src/config_usage.cpp",
                        "line": _line_number(config_usage, "return maxBufferSize * File_open_retry + telemetryFlushWindow;"),
                        "column": 28,
                        "message": "macro reference",
                    },
                    {
                        "file": "src/telemetry_report.cpp",
                        "line": _line_number(telemetry_report, "  return ScoreTelemetrySentence(summary) + File_open_retry;"),
                        "column": 42,
                        "message": "macro reference",
                    },
                    {
                        "file": "src/main.cpp",
                        "line": _line_number(main_cpp, '<< "failed to open sample file after " << File_open_retry'),
                        "column": 56,
                        "message": "macro reference",
                    },
                ],
            },
            {
                "id": "macro-naming-3",
                "ruleId": "macro-naming",
                "severity": "warning",
                "message": "macro telemetryFlushWindow does not match SCREAMING_SNAKE_CASE",
                "symbol": "telemetryFlushWindow",
                "category": "macro-naming",
                "primaryLocation": {
                    "file": "include/config_macros.h",
                    "line": _line_number(macros, "#define telemetryFlushWindow"),
                    "column": 9,
                },
                "relatedLocations": [
                    {
                        "file": "src/config_usage.cpp",
                        "line": _line_number(config_usage, "return maxBufferSize * File_open_retry + telemetryFlushWindow;"),
                        "column": 43,
                        "message": "macro reference",
                    },
                    {
                        "file": "src/cache_pipeline.cpp",
                        "line": _line_number(cache_pipeline, "  return Cache_line_size + telemetryFlushWindow;"),
                        "column": 30,
                        "message": "macro reference",
                    },
                    {
                        "file": "src/telemetry_report.cpp",
                        "line": _line_number(telemetry_report, "return reader.BufferCapacity() + telemetryFlushWindow + maxBufferSize;"),
                        "column": 41,
                        "message": "macro reference",
                    },
                    {
                        "file": "src/main.cpp",
                        "line": _line_number(main_cpp, "out << \"alpha:\" << JoinWords(normalized) << \":\" << (maxBufferSize + Cache_line_size + telemetryFlushWindow);"),
                        "column": 78,
                        "message": "macro reference",
                    },
                ],
            },
            {
                "id": "macro-naming-4",
                "ruleId": "macro-naming",
                "severity": "warning",
                "message": "macro Cache_line_size does not match SCREAMING_SNAKE_CASE",
                "symbol": "Cache_line_size",
                "category": "macro-naming",
                "primaryLocation": {
                    "file": "include/config_macros.h",
                    "line": _line_number(macros, "#define Cache_line_size"),
                    "column": 9,
                },
                "relatedLocations": [
                    {
                        "file": "src/cache_pipeline.cpp",
                        "line": _line_number(cache_pipeline, "  return Cache_line_size + telemetryFlushWindow;"),
                        "column": 10,
                        "message": "macro reference",
                    },
                    {
                        "file": "src/main.cpp",
                        "line": _line_number(main_cpp, '<< " cache-line=" << Cache_line_size'),
                        "column": 33,
                        "message": "macro reference",
                    },
                ],
            },
            {
                "id": "resource-leak-1",
                "ruleId": "resource-leak",
                "severity": "error",
                "message": "FILE handle opened by fopen is not released on object teardown",
                "symbol": "file_",
                "category": "resource-leak",
                "primaryLocation": {
                    "file": "src/file_reader.cpp",
                    "line": _line_number(file_reader_cpp, 'std::fopen(path.c_str(), "r")'),
                    "column": 54,
                },
                "relatedLocations": [
                    {
                        "file": "include/file_reader.h",
                        "line": _line_number(file_reader_h, "FILE* file_;"),
                        "column": 3,
                        "message": "class-owned FILE* member",
                    }
                ],
                "trace": [
                    {
                        "file": "src/file_reader.cpp",
                        "line": _line_number(file_reader_cpp, 'std::fopen(path.c_str(), "r")'),
                        "column": 54,
                        "event": "resource acquired by fopen",
                    },
                    {
                        "file": "include/file_reader.h",
                        "line": _line_number(file_reader_h, "FILE* file_;"),
                        "column": 3,
                        "event": "resource stored in owning member",
                    },
                    {
                        "file": "include/file_reader.h",
                        "line": _line_number(file_reader_h, "class FileReader {"),
                        "column": 7,
                        "event": "class has no destructor declaration",
                    },
                ],
            },
        ],
    }


def _reset_small() -> None:
    if PROJECT_DST.exists():
        shutil.rmtree(PROJECT_DST)
    shutil.copytree(SMALL_PROJECT_SRC, PROJECT_DST)
    SIGNAL_DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SMALL_SIGNAL_SRC, SIGNAL_DST)


def _reset_large() -> None:
    if PROJECT_DST.exists():
        shutil.rmtree(PROJECT_DST)
    files = _large_project_files()
    _write_files(PROJECT_DST, files)
    payload = _large_signal_payload(files)
    LARGE_SIGNAL_SRC.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    SIGNAL_DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(LARGE_SIGNAL_SRC, SIGNAL_DST)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["small", "large"], default="large")
    args = parser.parse_args()

    if args.scenario == "small":
        _reset_small()
    else:
        _reset_large()

    print(f"reset workspace: {PROJECT_DST}")
    print(f"reset static signals: {SIGNAL_DST}")
    print(f"scenario: {args.scenario}")


if __name__ == "__main__":
    main()
