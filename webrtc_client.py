# webrtc_client.py
 
import asyncio
import time
import wave
import os 
from dotenv import load_dotenv

import aiohttp
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration
from aiortc.mediastreams import MediaStreamTrack

load_dotenv()

RTC_URL = os.environ.get('RTC_URL')
SDP_SERVER = os.environ.get('SDP_SERVER')
print(f'rtc_url={RTC_URL} sdp_server={SDP_SERVER}')
class AudioTrack(MediaStreamTrack):
    kind = "audio"
 
    def __init__(self):
        super().__init__()
        self.frames = []
 
    async def recv(self):
        frame = await super().recv()
        return frame
 
 
async def save_audio_to_file(frames, filename):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(44100)  # Sample rate
        print(frames.__sizeof__())
        print(print(type(frames)))
        for frame in frames:
            wf.writeframes(frame.tobytes())
        print(f"Saved {len(frames)} audio frames to {filename}.")
 
 
async def run_client():
    # 创建一个 WebRTC 连接
    rtc_conf = RTCConfiguration()
    rtc_conf.iceServers = []
    pc = RTCPeerConnection(rtc_conf)
    audio_track = AudioTrack()  # 创建音频轨道
    pc.addTrack(audio_track)  # 将音频轨道添加到连接中
    wav_file = wave.open("output.wav", "wb")
    wav_file.setnchannels(2)
    wav_file.setsampwidth(2)  
    wav_file.setframerate(48000)
 
    @pc.on("track")
    async def on_track(track):
        if track.kind == "audio":
            print("Receiving audio track")
            while True:
                frame = await track.recv()
                print(f"Received audio frame of size {len(frame.to_ndarray())}")
                audio_track.frames.append(frame)
                wav_file.writeframes(frame.to_ndarray())
 
    start_time = time.time()
    # 创建SDP Offer
    offer = await pc.createOffer()  # 创建 SDP Offer
    
    print("本地生成的SDP:", "offer.sdp")  # 打印本地 SDP
    offer_end_time = time.time()
    await pc.setLocalDescription(offer)  # 设置本地描述
    end_time = time.time()
 
    # 计算各个阶段的运行时长
    offer_duration = offer_end_time - start_time
    set_local_description_duration = end_time - offer_end_time
    total_duration = end_time - start_time
    print(f"创建 Offer 耗时: {offer_duration} 秒")
    print(f"设置本地描述耗时: {set_local_description_duration} 秒")
    print(f"总运行时长: {total_duration} 秒")
    
    data = {
        "api": SDP_SERVER,
        "streamurl": RTC_URL,
        "sdp": offer.sdp
    }
    print(f"sdp={offer.sdp}")
    async with aiohttp.ClientSession() as session:
       async with session.post(
                url=SDP_SERVER,
                json=data, 
                headers={"Content-Type": "application/json"} 
            ) as response:
                response_data = await response.json()
                print("对方的SDP:", response_data.get('sdp'))
                await pc.setRemoteDescription(RTCSessionDescription(sdp=response_data.get('sdp'), type='answer'))
    while True:
        await asyncio.sleep(0.1)
 
 
async def main():
    """主函数，启动客户端。"""
    await run_client()  
 
 
if __name__ == '__main__':
    asyncio.run(main()) 