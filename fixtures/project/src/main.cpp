#include "config_macros.h"
#include "file_reader.h"

#include <iostream>

int GetBufferBudget();

int main() {
  FileReader reader("data/sample.txt");
  if (!reader.IsOpen()) {
    std::cerr << "failed to open sample file after " << File_open_retry << " retries\n";
    return 1;
  }

  std::cout << "budget=" << GetBufferBudget() << " first-line=" << reader.ReadLine();
  std::cout << " max=" << maxBufferSize << "\n";
  return 0;
}
