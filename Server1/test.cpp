// 필요한 헤더 파일들을 포함
#include <iostream>        // 입출력을 위한 헤더
#include <sys/socket.h>    // 소켓 프로그래밍 관련 함수들
#include <netinet/in.h>    // 인터넷 프로토콜 관련 정의
#include <unistd.h>        // close() 함수 사용
#include <string.h>        // memset() 함수 사용

// 상수 정의
#define PORT 12345         // 서버가 사용할 포트 번호
#define BUFFER_SIZE 1024   // 메시지 버퍼 크기


int main() {
    // 소켓 생성
    int serverSocket = socket(AF_INET,     // IPv4 프로토콜
                            SOCK_STREAM,    // TCP 프로토콜
                            0);             // 프로토콜 자동 선택
    if (serverSocket == -1) {
        std::cerr << "소켓 생성 실패" << std::endl;
        return 1;
    }

    // 서버 주소 구조체 설정
    struct sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;           // IPv4 사용
    serverAddr.sin_port = htons(PORT);         // 포트 번호 설정 (네트워크 바이트 순서로 변환)
    serverAddr.sin_addr.s_addr = INADDR_ANY;   // 모든 네트워크 인터페이스에서 연결 수락

    // 소켓과 주소를 바인딩 (연결)
    if (bind(serverSocket, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
        std::cerr << "바인딩 실패" << std::endl;
        return 1;
    }

    // 연결 요청 대기열 생성
    if (listen(serverSocket, 3) < 0) {    // 최대 3개의 대기 연결 허용
        std::cerr << "리스닝 실패" << std::endl;
        return 1;
    }

    std::cout << "서버가 포트 " << PORT << "에서 시작되었습니다..." << std::endl;

    // 메인 서버 루프
    while (true) {
        struct sockaddr_in clientAddr;    // 클라이언트 주소 정보를 저장할 구조체
        socklen_t clientAddrLen = sizeof(clientAddr);

        // 클라이언트 연결 수락
        int clientSocket = accept(serverSocket, 
                                (struct sockaddr*)&clientAddr, 
                                &clientAddrLen);
        if (clientSocket < 0) {
            std::cerr << "연결 수락 실패" << std::endl;
            continue;
        }

        std::cout << "새로운 클라이언트가 연결되었습니다!" << std::endl;

        char buffer[BUFFER_SIZE];    // 메시지를 저장할 버퍼

        // 클라이언트와의 통신 루프
        while (true) {
            // 버퍼 초기화
            memset(buffer, 0, BUFFER_SIZE);

            // 클라이언트로부터 데이터 수신
            int bytesRead = recv(clientSocket, buffer, BUFFER_SIZE, 0);
            
            if (bytesRead <= 0) {
                if (bytesRead == 0) {
                    // 클라이언트가 정상적으로 연결을 종료
                    std::cout << "클라이언트가 연결을 종료했습니다." << std::endl;
                } else {
                    // 수신 중 오류 발생
                    std::cerr << "수신 오류" << std::endl;
                }
                break;
            }

            // 받은 메시지 출력
            std::cout << "받은 메시지: " << buffer << std::endl;

            // 받은 메시지를 그대로 클라이언트에게 다시 전송 (에코)
            send(clientSocket, buffer, bytesRead, 0);
        }

        // 클라이언트 소켓 닫기
        close(clientSocket);
    }

    // 서버 소켓 닫기
    close(serverSocket);
    return 0;
}