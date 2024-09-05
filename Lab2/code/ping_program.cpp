#include <iostream>
#include <chrono>
#include <thread>

#ifdef _WIN32
#include <windows.h> // For PlaySound on Windows
#pragma comment(lib, "winmm.lib")
#endif

bool pingHost(const std::string& host) {
    std::string command;

#ifdef _WIN32
    command = "ping -n 1 " + host + " > nul";  // Windows command, ping once
#elif __APPLE__
    command = "ping -c 1 " + host + " > /dev/null";  // macOS command, ping once
#else
    command = "ping -c 1 " + host + " > /dev/null";  // Linux command, ping once
#endif

    // Execute the command and check the return value
    int result = system(command.c_str());
    return result == 0;  // 0 indicates success (host responded)
}

void playAlarm() {
#ifdef _WIN32
    PlaySound(TEXT("alarm.wav"), NULL, SND_FILENAME | SND_ASYNC);  // Play alarm sound on Windows
#elif __APPLE__
    system("afplay alarm.wav &");  // Play alarm sound on macOS using afplay
#else
    system("aplay alarm.wav &");  // Play alarm sound on Linux using aplay
#endif
}

int main() {
    const std::string host = "csce462.local";
    bool isConnected = false;
    auto startTime = std::chrono::steady_clock::now();

    while (true) {
        // Calculate the time elapsed since the program started searching
        auto currentTime = std::chrono::steady_clock::now();
        auto elapsedSeconds = std::chrono::duration_cast<std::chrono::seconds>(currentTime - startTime).count();

        // Print searching message in yellow
        std::cout << "\033[1;33mSearching... (" << elapsedSeconds << " seconds)\033[0m\r" << std::flush;

        if (pingHost(host)) {
            if (!isConnected) {
                std::cout << "\n\033[1;32mConnected!\033[0m" << std::endl;
                playAlarm();
                isConnected = true;
            }
        } else {
            if (isConnected) {
                std::cout << "\n\033[1;31mDisconnected\033[0m" << std::endl;
                break;  // Exit the loop and end the program if it disconnects
            }
        }

        // Wait for 5 seconds before the next ping
        std::this_thread::sleep_for(std::chrono::seconds(5));
    }

    return 0;
}
