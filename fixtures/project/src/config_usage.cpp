#include "config_macros.h"

int GetBufferBudget() {
  return maxBufferSize * File_open_retry;
}
