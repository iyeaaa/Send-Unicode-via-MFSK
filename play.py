import math
import pyaudio
import wave
import struct
import scipy.fftpack
import numpy as np


rules = {
    'START': 512,
    '0': 768, '1': 896, '2': 1024,
    '3': 1152, '4': 1280, '5': 1408,
    '6': 1536, '7': 1664, '8': 1792,
    '9': 1920, 'A': 2048, 'B': 2176,
    'C': 2304, 'D': 2432, 'E': 2560,
    'F': 2688,
    'END': 2944}


def audio2file(audio, filename):
    with wave.open(filename, 'wb') as w:
        w.setnchannels(1)  # 채널 수
        w.setsampwidth(2)  # 샘플 너비 (바이트)
        w.setframerate(48000)  # 프레임 레이트
        for a in audio:
            w.writeframes(struct.pack('<h', a))


def send(text):
    INTMAX = 2 ** (16 - 1) - 1
    channels = 1
    unit = 0.1
    samplerate = 48000
    string_hex = text.encode('utf-8').hex().upper()
    audio = []

    # 시작 신호 생성
    for i in range(int(unit * samplerate * 2)):
        audio.append(int(INTMAX * math.sin(2 * math.pi * rules['START'] * i / samplerate)))

    # 문자열에 대한 신호 생성
    for s in string_hex:
        for i in range(int(unit * samplerate * 1)):
            audio.append(int(INTMAX * math.sin(2 * math.pi * rules[s] * i / samplerate)))

    # 종료 신호 생성
    for i in range(int(unit * samplerate * 2)):
        audio.append(int(INTMAX * math.sin(2 * math.pi * rules['END'] * i / samplerate)))

    # PyAudio 초기화 및 스트림 설정
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=samplerate,
                    output=True)

    audio2file(audio, filename="output.wav")

    # 오디오 청크 처리 및 스트림으로 출력
    chunk_size = 1024
    for i in range(0, len(audio), chunk_size):
        chunk = audio[i:i + chunk_size]
        stream.write(struct.pack('<' + ('h' * len(chunk)), *chunk))


def receive():
    unit = 0.1  # 각 신호의 지속 시간(초)
    samplerate = 48000  # 샘플링 레이트, 초당 샘플의 수
    chunk_size = 1024  # 한 번에 처리할 오디오 데이터의 양
    padding = 20  # 주파수 판정 시 허용 오차 범위
    sound_start = False  # 소리 시작 플래그
    audio = []  # 오디오 데이터를 저장할 리스트
    tuning = False  # 소음이 아닌 데이터 인식 시작 여부
    hex_string = ''  # 인식된 헥스 문자열을 저장
    end_cnt = 0  # 종료 신호를 센 횟수
    start_cnt = 0  # 시작 신호를 센 횟수

    p = pyaudio.PyAudio()  # PyAudio 객체 생성
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=samplerate,
                    input=True)  # 오디오 스트림 열기

    while True:
        codeData = stream.read(chunk_size)  # 오디오 데이터 읽기
        data = struct.unpack('<' + ('h' * chunk_size), codeData)  # 바이트 데이터를 정수로 변환

        for entry in data:
            if abs(entry) > 5000:
                audio.append(entry)  # 오디오 데이터 저장
                tuning = True
            elif tuning:
                audio.append(entry)

            if len(audio) == 4800:
                freq = scipy.fftpack.fftfreq(len(audio), d=1 / samplerate)
                fourier = scipy.fftpack.fft(audio)  # FFT(고속 푸리에 변환) 실행
                top = freq[np.argmax(abs(fourier))]  # 가장 높은 주파수 성분 찾기

                for k, v in rules.items():
                    if v - padding <= top <= v + padding:
                        if k == "START":
                            start_cnt += 1
                            if start_cnt == 2:  # 시작 신호 2회 인식 시
                                print("START")
                                sound_start = True
                        elif not sound_start:
                            pass
                        elif k == "END":
                            end_cnt += 1
                            if end_cnt == 2:  # 종료 신호 2회 인식 시
                                print("\nEND")
                                print(f'입력한 값: {bytes.fromhex(hex_string).decode('utf-8')}')  # 헥스 문자열을 디코드하여 출력
                                exit(0)
                        else:
                            hex_string += k  # 인식된 키를 문자열에 추가
                            print(k, end='')
                        break

                audio.clear()  # 오디오 데이터 초기화
