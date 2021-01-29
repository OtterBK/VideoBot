import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os
import time
import asyncio
import subprocess
import pyautogui
import youtube_dl

# 개발자 페이지에서 봇에 대한 토큰 텍스트를 가져온 뒤, TOKEN에 대입하자
TOKEN = "Input your discord bot's token"
BOT_PREFIX = "~"
VLC_PATH = "E:/Programs/VLC/vlc.exe"  # VLC 미디어 플레이어 경로
DATABASE1 = "G:/전현성/잡것들/RunAPI.dll/애니메이션/"  # 데이터베이스1 경로
DATABASE2 = "I:/전현성/잡것들/RunAPI.dll/애니메이션/"  # 데이터베이스2 경로
DATABASE3 = "F:/영화/"  # 데이터베이스3 경로

SAVE_PATH = "F:/비디오봇/download/" #유튜브 다운로드 임시경로

bot = commands.Bot(command_prefix=BOT_PREFIX)  # 봇 커맨드 설정

class DATABASE_TYPE(enumerate): #데이터베이스타입
    DATABASE1 = DATABASE1 #DB1
    DATABASE2 = DATABASE2 #DB2
    DATABASE3 = DATABASE3 #DB3

class EMOJI_BUTTON(enumerate): #버튼
    PAGE_PREV = "🔺"
    PAGE_NEXT = "🔻"
    PAGE_PARENT = "↩️"
    PLAY_LEFT = "⏪"
    PLAY_PAUSE_AND_RESUME = "⏯️"
    PLAY_STOP = "⏹️"
    PLAY_RIGHT = "⏩" 
    PLAY_SUB_FAST = "⬅️" 
    PLAY_SUB_SLOW = "➡️" 
    PLAY_AUDIO_FAST = "◀️" 
    PLAY_AUDIO_SLOW = "▶️" 

    

class PlayerData:
    def __init__(self):
        self.controlChannel = None #버튼 상호작용할 채널
        self.databaseType = None #선택한 데이터베이스
        self.nowPage = 0 #페이지 넘버
        self.playListMessage = None #비디오 선택 embed 메시지
        self.controllerMessage = None #리모컨 embed 메시지
        self.pageList = None #현재 표시된 비디오 목록
        self.maxPage = 0 #최대 페이지
        self.pathPoint = [] #경로 저장용
        self.nowPlaying = "없음" #현재 재생중인 파일
        self.subSync = 0 #자막 싱크
        self.audioSync = 0 #오디오 싱크
        self.guildName = ""
        self.channelName = ""
        self.status = 0 #재생 또는 중지, 종료 확인 0, 종료 1, 중지 2,재생
        self.lastPage = 0 #목록 페이지 저장용


#전역 저장 변수
playerData = PlayerData()

#상수
emojiNumberList = [ "0️⃣", "1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
ListPerPage = 9 #페이지 당 표시 개수
DATABASE_MAP = dict()
DATABASE_MAP["애니메이션 DB1"] = DATABASE_TYPE.DATABASE1
DATABASE_MAP["애니메이션 DB2"] = DATABASE_TYPE.DATABASE2
DATABASE_MAP["영화"] = DATABASE_TYPE.DATABASE3

async def loadData():
     try:
        f = open("channeldata.txt", 'r', encoding="utf-8" )
        line = f.readline()
        line = line.strip()
        playerData.guildName = line #길드이름


        line = f.readline()
        line = line.strip()
        playerData.channelName = line #채널

        line = f.readline()
        line = line.strip()
        playerData.controlChannel = line #채널id
        f.close()

        channel = discord.utils.get(bot.get_all_channels(), guild__name=str(playerData.guildName), name=str(playerData.channelName)) #채널 가져오기
        print("채널 : "+str(channel))
        print("정보 : "+str(playerData.guildName) + "," + str(playerData.channelName)+ str(playerData.controlChannel))

        print("gui 재구성")
        await clear(channel)
        await makeEmbed(channel)
     except:
         print("파일 로드 에러")

async def saveData(ctx):
    playerData.guildName = ctx.guild.name
    playerData.channelName = ctx.channel.name
    playerData.controlChannel = str(ctx.message.channel.id)
    
    f = open("channeldata.txt", 'w', encoding="utf-8" )
    f.write(str(playerData.guildName)+"\n")
    f.write(str(playerData.channelName)+"\n")
    f.write(str(playerData.controlChannel)+"\n")
    f.close()

async def clear(chatChannel):
    await chatChannel.purge(limit=100)

async def initSetting(ctx): #초기 설정
    await saveData(ctx) #데이터 저장
    await makeEmbed(ctx.channel) #GUI생성

async def makeEmbed(channel):
    await controlHelper(channel)

    playListEmbed = discord.Embed(
            title="[                                                비디오 선택                                               ]", url=None, description="\n▽", color=discord.Color.dark_magenta())
    playListEmbed.set_author(name=bot.user, url="",
                        icon_url=bot.user.avatar_url)


    playListMessage = await channel.send(embed=playListEmbed)

    await playListMessage.add_reaction(EMOJI_BUTTON.PAGE_PREV)
    i = 1
    while i < 10:
        await playListMessage.add_reaction(emojiNumberList[i])
        i += 1
    await playListMessage.add_reaction(EMOJI_BUTTON.PAGE_PARENT)
    await playListMessage.add_reaction(EMOJI_BUTTON.PAGE_NEXT)

    playerData.playListMessage = playListMessage
    #await setDatabase(DATABASE_TYPE.DATABASE1)
    await showSelectDatabase()

    controlEmbed = discord.Embed(
            title="[                         리모컨                         ]", url=None, description="\n▽", color=discord.Color.green())
    controlEmbed.set_author(name=bot.user, url="",
                        icon_url=bot.user.avatar_url)
    
    controllerMessage = await channel.send(embed=controlEmbed)
    playerData.controllerMessage = controllerMessage

    await controllerMessage.add_reaction(EMOJI_BUTTON.PLAY_LEFT)
    await controllerMessage.add_reaction(EMOJI_BUTTON.PLAY_PAUSE_AND_RESUME)
    await controllerMessage.add_reaction(EMOJI_BUTTON.PLAY_STOP)
    await controllerMessage.add_reaction(EMOJI_BUTTON.PLAY_RIGHT)
    await controllerMessage.add_reaction(EMOJI_BUTTON.PLAY_SUB_FAST)
    await controllerMessage.add_reaction(EMOJI_BUTTON.PLAY_SUB_SLOW)
    await controllerMessage.add_reaction(EMOJI_BUTTON.PLAY_AUDIO_FAST)
    await controllerMessage.add_reaction(EMOJI_BUTTON.PLAY_AUDIO_SLOW) 

    await updateController("")



async def controlHelper(channel): #도움말
    desc = EMOJI_BUTTON.PAGE_PREV+ "　　　　　[ 이전 페이지 ]\n"
    desc += "1️⃣ ~  9️⃣"+ "　　　[ 선택 ]\n"
    desc += EMOJI_BUTTON.PAGE_PARENT+ "　　　　　[ 돌아가기 ]\n"
    desc += EMOJI_BUTTON.PAGE_NEXT+ "　　　　　[ 다음 페이지 ]\n"
    desc += "　\n"
    desc += EMOJI_BUTTON.PLAY_LEFT + "　　　　　[ 10초 앞으로 ]\n"
    desc += EMOJI_BUTTON.PLAY_PAUSE_AND_RESUME + "　　　　　[ 일시중지/재생 ]\n"
    desc += EMOJI_BUTTON.PLAY_STOP + "　　　　　[ 비디오 중지 ]\n"
    desc += EMOJI_BUTTON.PLAY_RIGHT + "　　　　　[ 10초 뒤로 ]\n"
    desc += EMOJI_BUTTON.PLAY_SUB_FAST + "　　　　　[ 자막싱크 -0.05 ]\n"
    desc += EMOJI_BUTTON.PLAY_SUB_SLOW + "　　　　　[ 자막싱크 +0.05 ]\n"
    desc += EMOJI_BUTTON.PLAY_AUDIO_FAST + "　　　　　[ 오디오싱크 -0.05 ]\n"
    desc += EMOJI_BUTTON.PLAY_AUDIO_SLOW + "　　　　　[ 오디오싱크 +0.05 ]\n　\n"
    desc += "유튜브 시청" + "　　~y 유튜브주소\n"
    desc += "TV 껐다켜기" + "　　~재설정\n"
    

    helpEmbed = discord.Embed(
            title="[                                                사용 방법                                               ]", url=None, description="\n"+desc, color=discord.Color.dark_orange())
    helpEmbed.set_author(name=bot.user, url="",
                        icon_url=bot.user.avatar_url)

    await channel.send(embed=helpEmbed)
                    

async def control(button): #리모컨 동작
    isChanged = False

    errorMessage = ""
    if playerData.status == 0: #재생중이 아니면
        isChanged = True
        errorMessage = "먼저 비디오를 선택해주세요."
    elif button == EMOJI_BUTTON.PLAY_LEFT:
        pyautogui.press("f1")
        isChanged = True
    elif button == EMOJI_BUTTON.PLAY_PAUSE_AND_RESUME:
        pyautogui.press("f6")
        if playerData.status == 1: #중지 상태면
            playerData.status = 2  #재생으로
        else:
            playerData.status = 1 
        isChanged = True
    elif button == EMOJI_BUTTON.PLAY_STOP:
        pyautogui.press("f3")
        playerData.status = 0 
        playerData.nowPlaying = "없음"
        isChanged = True
    elif button == EMOJI_BUTTON.PLAY_RIGHT:
        pyautogui.press("f5")
        isChanged = True
    elif button == EMOJI_BUTTON.PLAY_SUB_FAST:
        for i in range(0, 10):
            pyautogui.press("f9")
        
        playerData.subSync -= 500
        isChanged = True
    elif button == EMOJI_BUTTON.PLAY_SUB_SLOW:
        for i in range(0, 10):
            pyautogui.press("f10")

        playerData.subSync += 500
        isChanged = True
    elif button == EMOJI_BUTTON.PLAY_AUDIO_FAST:
        pyautogui.press("f11")
        await asyncio.sleep(0.1)
        pyautogui.press("f11")
        playerData.audioSync -= 100
        isChanged = True
    elif button == EMOJI_BUTTON.PLAY_AUDIO_SLOW:
        pyautogui.press("f12")
        await asyncio.sleep(0.1)
        pyautogui.press("f12")
        playerData.audioSync += 100
        isChanged = True
    
    if isChanged:
        await updateController(errorMessage)

async def setDatabase(dbType):
    playerData.databaseType = dbType #데이터베이스 새로 설정

    playerData.nowPage = 0
    
    await updatePage()

def isVideo(fileName): #비디오 파일인지 확인
    fileName = fileName.lower()
    if fileName.endswith(".mp4") or fileName.endswith(".avi") or fileName.endswith(".mkv") or fileName.endswith(".wmv") or fileName.endswith("webm") or fileName.endswith("ts"):
        return True
    else:
        return False

async def getNowAbsolutePath(data):
    searchPath = "" #현재 경로

    i = 0
    while i < len(data.pathPoint):
        searchPath += data.pathPoint[i] + "/"
        i += 1
    
    allPath = data.databaseType + searchPath
    return allPath

def playVideo(videoPath):
    videoPath = videoPath.replace("/", "\\")
    videoPath = " \"" + videoPath + "\""

    #os.system('cmd /c '+VLC_PATH + videoPath)
    #subprocess.run(str(VLC_PATH + videoPath), close_fds=True,creationflags=DETACHED_PROCESS)

    subprocess.Popen(VLC_PATH + videoPath)
    print("play video : "+videoPath)

async def showSelectDatabase(): #데이터베이스 선택화면
    print("debug - "+"1")
    desc = "" #embed에 표시할 메시지

    DATABASE_LIST = list(DATABASE_MAP.keys()) #데이베이스 맵에서 이름만 꺼내기

    playerData.databaseType = None #선택한 데이터베이스
    playerData.pageList = [] #현재 표시된 파일 목록
    playerData.pathPoint = [] #경로 초기화
    playerData.nowPage = 0
    playerData.maxPage = (len(DATABASE_LIST) // 9) + 1
    print("debug - "+"2")
    i = 0
    while i < len(DATABASE_LIST): #데이터베이스 리스트 표시
        dbData = DATABASE_LIST[i]
        desc += emojiNumberList[i+1] + ". " + str(dbData) + "\n　\n"
        playerData.pageList.append(dbData)
        i += 1
    print("debug - "+"3")
    playListEmbed = discord.Embed(
            title="[                                                데이터베이스 선택                                               ]", url=None, description="\n"+desc, color=discord.Color.dark_magenta())
    playListEmbed.set_author(name=bot.user, url="",
                        icon_url=bot.user.avatar_url)

    playListEmbed.set_footer(text=("🅿️　"+str(playerData.nowPage+1)+" / "+str(playerData.maxPage)+"　　|　　📂 데이터베이스")) #페이지 표시

    await playerData.playListMessage.edit(embed=playListEmbed) #embed 메시지 수정
    print("debug - "+"4")


async def updateController(errorMessage):
    controllerDesc = "🎦\n현재 재생중인 비디오 : " + str(playerData.nowPlaying) + "\n　"

    controlEmbed = discord.Embed(
            title="[                         리모컨                         ]", url=None, description=controllerDesc, color=discord.Color.blue())
    controlEmbed.set_author(name=bot.user, url="",
                        icon_url=bot.user.avatar_url)

    status = ""
    if playerData.status == 0: 
        status = "종료"
    if playerData.status == 1: 
        status = "중지"
    if playerData.status == 2: 
        status = "재생"

    controlEmbed.add_field(
            name="[ 재생상태 ]", value=str(status), inline=True)  # 필드로 추가
    controlEmbed.add_field(
            name="[ 자막싱크 ]", value=str(playerData.subSync)+"ms", inline=True)  # 필드로 추가
    controlEmbed.add_field(
            name="[ 오디오싱크 ]", value=str(playerData.audioSync)+"ms", inline=True)  # 필드로 추가
    controlEmbed.set_footer(text=("❗　"+errorMessage)) #오류 표시용

    await playerData.controllerMessage.edit(embed=controlEmbed) #embed 메시지 수정


async def updatePage():
    if playerData.databaseType == None:
        return

    searchPath = "" #현재 경로

    i = 0
    while i < len(playerData.pathPoint):
        searchPath += playerData.pathPoint[i] + "/"
        i += 1
    
    allPath = playerData.databaseType + searchPath

    animeList = os.listdir(allPath) #현재 데이터베이스의 모든 비디오 폴더 긁어오기

    desc = "" #embed에 표시할 메시지
    playerData.pageList = [] #로컬 저장 목록 초기화
    i = 0

    tmpList = []
    for tmpFile in animeList: #쓸모없는 파일은 무시
        if not os.path.isdir(allPath+tmpFile): #폴더가 아닐때
            if not isVideo(tmpFile): #비디오 파일이 아니면
                continue #다음 파일로
        tmpList.append(tmpFile)

    playerData.maxPage = (len(tmpList) // ListPerPage) + 1 #최대 페이지 설정
    pageIndex = playerData.nowPage * ListPerPage #표시 시작할 인덱스

    while i < 9: #9개의 목록 표시
        fileIndex = pageIndex + i
        if fileIndex >= len(tmpList): #마지막 파일 도달하면 바로 break
            break
        animeData = tmpList[fileIndex]
        playerData.pageList.append(animeData) #저장 목록에 추가
        i += 1
        desc += emojiNumberList[i] + ". " + str(animeData) + "\n　\n"
    
    playListEmbed = discord.Embed(
            title="[                                                비디오 선택                                               ]", url=None, description="\n"+desc, color=discord.Color.dark_magenta())
    playListEmbed.set_author(name=bot.user, url="",
                        icon_url=bot.user.avatar_url)

    rootPath = ""
    if playerData.databaseType == DATABASE_TYPE.DATABASE1:
        rootPath = "애니메이션1/"
    elif playerData.databaseType == DATABASE_TYPE.DATABASE2:
        rootPath = "애니메이션2/"
    elif playerData.databaseType == DATABASE_TYPE.DATABASE3:
        rootPath = "영화/"

    playListEmbed.set_footer(text=("🅿️　"+str(playerData.nowPage+1)+" / "+str(playerData.maxPage)+"　　|　　📂 "+rootPath+searchPath)) #페이지 표시

    await playerData.playListMessage.edit(embed=playListEmbed) #embed 메시지 수정



async def somethingSelected(selectIndex):
        
    if selectIndex > len(playerData.pageList): #만약 선택 가능 범위를 넘으면 return
        return
    
    if playerData.databaseType == None: #데이터 베이스를 선택한 상태가 아니면
        databaseList = list(DATABASE_MAP.keys())
        dbName = databaseList[selectIndex-1]
        dbData = DATABASE_MAP[dbName]
        await setDatabase(dbData) #db 새롭게 설정
    else:
        allPath = await getNowAbsolutePath(playerData) #절대 경로 가져오기
        selectText = playerData.pageList[selectIndex-1] #선택한 텍스트 가져오기
        if not os.path.isdir(allPath+selectText): #폴더가 아닐때
            if isVideo(selectText): #선택한게 비디오 파일이면
                print("비디오 재생, "+allPath + selectText)
                playerData.subSync = 0
                playerData.audioSync = 0
                playerData.status = 2
                playerData.nowPlaying = selectText
                await updateController("")
                playVideo(allPath + selectText) #해당 비디오 실행
        else: #폴더면, 해당 폴더로 이동
            playerData.lastPage = playerData.nowPage
            playerData.pathPoint.append(selectText) #새로운 폴더가 새로고침 됐으니깐 nowPage도 0
            playerData.nowPage = 0

    await updatePage()

@bot.event
async def on_ready():
    print(f'{bot.user} 활성화됨')
    await bot.change_presence(status=discord.Status.online) #온라인
  #await client.change_presence(status=discord.Status.idle) #자리비움
  #await client.change_presence(status=discord.Status.dnd) #다른용무
  #await client.change_presence(status=discord.Status.offline) #오프라인
    await bot.change_presence(activity=discord.Game(name="정상 작동 중"))
    await loadData()
    print("봇 이름:",bot.user.name,"봇 아이디:",bot.user.id,"봇 버전:",discord.__version__)

@bot.command(pass_context=False, aliases=["재설정"])  # 초기설정 명령어 입력시
async def initSettingCommand(ctx):  # 조작 버튼 설정
    await initSetting(ctx)

    
    # if gameData._thumbnail != None:
    #     thumbnailFile = discord.File(str(gameData._thumbnail), filename="quizThumbnail.png")

    # embed.set_image(url="attachment://quizThumbnail.png")
    # await gameData._chatChannel.send(file=thumbnailFile, embed=embed)

@bot.command(pass_context=False, aliases=["y"])  # 초기설정 명령어 입력시
async def youtubeCommand(ctx, ytdUrl=None):  # 유튜브 재생
    if ytdUrl == None: #주소 미입력시
        await updateController("유효한 유튜브 동영상 주소를 입력해주세요.")
        return

    video_there = os.path.isfile(SAVE_PATH+"video.mp4") #song.mp4 파일의 존재여부
    try:
        if video_there: #존재하면
            await control(EMOJI_BUTTON.PLAY_STOP) #우선 현재 실행중인 비디오 중지 (삭제를 위해)
            os.remove(SAVE_PATH+"video.mp4") #삭제
            print("Removed old video file")
    except PermissionError: #권한 부족 에러 발생시
        print("Tring to delete video file, but it's being played") #이미 재생되는 중인 파일같다고 알려줌
        await updateController("기존 비디오 삭제실패, 비디오를 중지하고 시도하세요.")
        return

    voice = get(bot.voice_clients, guild=ctx.guild)

    #if voice == None:
       # await updateController("TV가 꺼져있습니다.")
        #return

    ydl_opt = {
        'format': 'best/best', #최상 품질의 비디오 형식 선택
        'outtmpl':SAVE_PATH + '%(title)s.%(ext)s', #다운 경로 설정
        'writesubtitles': 'best', # 자막 다운로드(자막이 없는 경우 다운로드 X)
        # 'writethumbnail': 'best',  # 영상 thumbnail 다운로드
        'writeautomaticsub': False, # 자동 생성된 자막 다운로드
        'noplaylist': True,
        'subtitleslangs': 'kr'  # 자막 언어가 영어인 경우(다른 언어로 변경 가능)
    }
    
    playBarEmbed = discord.Embed(title="[ 유튜브 시청 ]", url="", description="유튜브 영상 다운로드 중... 잠시만 기다리세요.", color=discord.Color.blue()) #재생바
    alarmMessage = await ctx.send(embed=playBarEmbed)
    await updateController("유튜브 영상 다운로드 중... 잠시만 기다리세요.")
    try:
        with youtube_dl.YoutubeDL(ydl_opt) as ydl: #with문을 사용해 파일입출력을 안전하게 as하여 outube_dl.YoutubeDL(ydl_opta) 값을 ydl로
            ydl.download({ytdUrl}) #ydl_opta 값을 적용한 유튜브 다운로더를 통해 url에서 파일을 다운로드한다. 경로는 소스경로
    except:
        await updateController("유튜브 영상 다운로드 실패")
        return

    title = ""
    for file in os.listdir(SAVE_PATH): #다운로드 경로 참조, 해당 디렉토리 모든 파일에 대해
        if isVideo(file): #파일 확장자가 비디오면, 다운로드한 파일일거임
            try: #찾았다면 아래 실행
                print(f"Renamed File: {file}\n")
                os.rename(SAVE_PATH+file, SAVE_PATH+"video.mp4") #파일명 변경 song.mp3로
                title = file #기존 파일명 저장
            except:
                await updateController("다운로드한 영상 찾기 실패.")

    await alarmMessage.delete()
    if title != "":
        playerData.nowPlaying = title
        playerData.subSync = 0
        playerData.audioSync = 0
        playerData.status = 2
        await updateController("유튜브 영상 실행 - " + str(ctx.message.author))
        playVideo(SAVE_PATH+"video.mp4") #유튜브 비디오 실행



@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user: #봇이 입력한거면
        return #건너뛰어

    channel = reaction.message.channel #반응 추가한 채널

    if playerData.controlChannel == str(channel.id): #비디오 콘트롤 있는 채널이면
        emoji = reaction.emoji # 반응한 이모지 가져오기
        print(str(user) + ", " + str(emoji)) #로그
        try:
            await reaction.remove(user) #이모지 삭제
        except:
            return

        isControl = True
        index = 0
        while index < len(emojiNumberList): #번호 이모지인지 확인
            if emojiNumberList[index] == emoji:
                await somethingSelected(index) #번호 이미지면 행동
                isControl = False
                break
            index += 1

        if emoji == EMOJI_BUTTON.PAGE_NEXT: #다음 페이지면
            isControl = False
            if playerData.nowPage < playerData.maxPage: #최대 페이지 미만이면
                playerData.nowPage += 1 #다음 페이지
        elif emoji == EMOJI_BUTTON.PAGE_PREV: #이전 페이지면
            isControl = False
            if playerData.nowPage > 0: #0보다 크면
                playerData.nowPage -= 1 #이전 페이지
        elif emoji == EMOJI_BUTTON.PAGE_PARENT: #되돌아가기면
            isControl = False
            if len(playerData.pathPoint) > 0: #부모 폴더가 있다면
                del playerData.pathPoint[len(playerData.pathPoint) - 1] #최하위 경로를 삭제함으로서 1단계 위로
            else: #부모 폴더가 없다면
                await showSelectDatabase()
        
        if isControl: #만약 컨트롤 버튼이면
            await control(emoji) #리모콘 동작

        

        await updatePage()


@bot.event
async def on_reaction_remove(reaction, user):
    if user == bot.user: #봇이 삭제한거면
        return #건너뛰어

    channel = reaction.message.channel #반응 삭제한 채널

    if playerData.controlChannel == str(channel.id): #비디오 콘트롤 있는 채널이면
        emoji = reaction.emoji # 반응한 이모지 가져오기
        await reaction.message.add_reaction(emoji=emoji) #다시 추가...


@bot.event
async def on_message(message):
    channel = message.channel #메시지 입력한 채널

    # 봇이 입력한 메시지라면 무시하고 넘어간다.
    if message.author == bot.user:
        #print("m - self")
        return
    elif playerData.controlChannel == str(channel.id): #비디오 콘트롤 있는 채널이면
        await message.delete() #메시지 삭제

    if message.content.startswith(BOT_PREFIX):  # 명령어면 실행
        #print("m - its command")
        await bot.process_commands(message)
    

bot.run(TOKEN)  # 봇 실행
