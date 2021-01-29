
# 비디오 공유 봇 :video_camera:
### :clipboard: 디스코드 서버에서 사용가능한 비디오 봇입니다.
:exclamation: 해당 봇을 실행하는 서버에 VLC 미디어 플레이어가 설치돼 있어야합니다.

<br>

### :closed_book: 사용전 필수 수정 사항
#### VideoBot.py 소스코드에서 

```

TOKEN = "Input your discord bot token" #디스코드 토큰 입력
BOT_PREFIX = "~" #명령어 prefix 설정
VLC_PATH = "E:/Programs/VLC/vlc.exe"  # VLC 미디어 플레이어 경로, 
DATABASE1 = ""  # 데이터베이스1 경로, 공유할 로컬 비디오 경로
DATABASE2 = ""  # 데이터베이스2 경로, 공유할 로컬 비디오 경로
DATABASE3 = ""  # 데이터베이스3 경로, 공유할 로컬 비디오 경로
SAVE_PATH = "" #다운로드한 유튜브 영상을 임시 저장할 경로

```

#### 해당 값을 자신의 환경에 맞게 변경하셔야합니다. :memo:

### :green_book: 사용방법
```

* 봇을 실행하는 서버는 디스코드 계정을 새롭게 개설한 뒤 비디오 봇이 있는 서버에 접속합니다.
* VLC 미디어 플레이어를 실행한 뒤 서버에 접속한 계정에서 창 공유를 실행, VLC를 선택합니다.
* 이로서 서버는 어떠한 영상도 실행중이지 않은 VLC 를 공유하게됩니다.
* 마지막으로 디스코드 서버에서 새롭게 채팅 채널을 생성하고 
* [~재설정] 명령어를 입력합니다. (만약 BOT_PREFIX 값을 수정하셨다면 알맞은 명령어를 입력합니다.)

```

#### :camera: 스냅샷

![6](https://user-images.githubusercontent.com/28488288/106223184-491e4f80-6224-11eb-90e5-d678c77e5799.png)
![1](https://user-images.githubusercontent.com/28488288/106223231-5f2c1000-6224-11eb-82b6-0028d04004e5.png)
![2](https://user-images.githubusercontent.com/28488288/106223233-605d3d00-6224-11eb-8f73-ebe1de0d2856.png)
![3](https://user-images.githubusercontent.com/28488288/106223238-60f5d380-6224-11eb-8e1f-05f84f576979.png)
![4](https://user-images.githubusercontent.com/28488288/106223239-62270080-6224-11eb-917a-338ce36da9f9.png)
![5](https://user-images.githubusercontent.com/28488288/106223241-62bf9700-6224-11eb-9839-0cf182164ea5.png)
