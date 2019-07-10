from sys import byteorder
from array import array
from struct import pack
from time import clock, time, sleep
import pyaudio
import wave
import struct
import threading
import os.path, os
import numpy as np
import math
import logging
from time import sleep
from threading import Thread, Event
from tafkit.taf.drivers.dialog.util import getcustom_logger
import audioop

DEBUG_AUDIO_CONTROL2 = True
ACTIVE_SOUND_RMS = 100
import re
import thread


def wavRead(fileN):
    waveFile = wave.open(fileN, 'r')
    NbChanels = waveFile.getnchannels()
    data = []
    for x in range(NbChanels):
        data.append([])
    for i in range(0, waveFile.getnframes()):
        waveData = waveFile.readframes(1)
        data[i % (NbChanels)].append(int(struct.unpack("<h", waveData)[0]))

    RetAR = []
    BitDebth = waveFile.getsampwidth() * 8
    for x in range(NbChanels):
        RetAR.append(np.array(data[x]))
        RetAR[-1] = RetAR[-1] / float(pow(2, (BitDebth - 1)))

    fs = waveFile.getframerate()
    return RetAR, fs


class CWinSoundControl:
    def __init__(self):
        self.p = pyaudio.PyAudio()

        # Settings per audio device.
        self.InputDevices = {}
        self.OutputDevices = {}
        self.stream = []
        self.active = []
        self.abort = []
        self.toneFreq = []
        self.toneAmp = []

        # Python Event for enabling Pause and resume action.
        self.AudioPaused = Event()
        self.AudioPaused.set()
        self.AudioPlaying = False
        self.RecordingRMSArray = []
        self.callbacksoundfunc = None

        # In case of an Unpause route music to a newly generated stream.
        self.routeMusicToNewStream = False

        # Notify stream issue for routing music.
        self.streamUnavailable = False

        # Default device the music should be routed to, -1 indicates
        # music output to window's default selection.
        self.defaultDeviceIndex = -1

        # Default device to record music from.
        # -1 indicated PC's default choosen Microphone.
        self.defaultMicrophoneIndex = -1

        #         self.logger = getcustom_logger('logging.conf','test.ucTest')
        self.setUpAudioDevices()

    def resetPyAudio(self):
        # Necessary to terminate older Pyaudio instance, otherwise portaudio returns
        # stale configurations.
        self.p.terminate()
        self.p = None

        self.p = pyaudio.PyAudio()

    def setUpAudioDevices(self):
        max_devs = self.p.get_device_count()

        for i in range(max_devs):
            self.stream.append(None)
            self.active.append(False)
            self.abort.append(False)
            self.toneFreq.append(440.0)
            self.toneAmp.append(0.25)

            devinfo = self.p.get_device_info_by_index(i)
            if devinfo["maxOutputChannels"] > 0:
                self.OutputDevices[i] = devinfo["name"]
            if devinfo["maxInputChannels"] > 0:
                self.InputDevices[i] = devinfo["name"]

    def __del__(self):
        self.InputDevices = None
        self.OutputDevices = None
        self.stream = None
        self.toneFreq = None
        self.toneAmp = None

    def deleteInstance(self):
        self.p.terminate()

    def callbackOnsound(self, func):
        self.callbacksoundfunc = func

    def recordToFile_int(self, path, duration=20, dev=None, Srate=16000, FORMAT=pyaudio.paInt16, CHUNK_SIZE=1024):
        self.logger.info("Audio Control2 : Initiated recording")

        p = pyaudio.PyAudio()
        if dev == None:
            if self.defaultMicrophoneIndex == -1:
                # self.logger.info(" Audio Control2 - Recording on default device")
                dev = p.get_default_input_device_info()['index']

            else:
                # self.logger.info(" Audio Control2 - Recording on Non-default Device")
                dev = self.defaultMicrophoneIndex
                devinfo = self.p.get_device_info_by_index(dev)
                self.logger.info("Device info %s", devinfo)

        self.active[dev] = True
        self.abort[dev] = False
        stream = p.open(format=FORMAT, channels=1, rate=Srate,
                        input=True, output=True,
                        input_device_index=dev,
                        frames_per_buffer=CHUNK_SIZE)
        r = array('h')
        start = clock()
        self.logger.info(" Begin recording at %s " % str(time()))
        while clock() < start + duration and not self.abort[dev]:
            # little endian, signed short
            stream_data = stream.read(CHUNK_SIZE)
            snd_data = array('h', stream_data)

            # Store the RMS value of input signal in an array
            rms = audioop.rms(snd_data, 2)

            if self.callbacksoundfunc and rms > ACTIVE_SOUND_RMS:
                currentTime = time()
                self.callbacksoundfunc(rms, currentTime)
                self.callbacksoundfunc = None

            self.RecordingRMSArray.append(rms)
            if byteorder == 'big':
                snd_data.byteswap()
            r.extend(snd_data)

        sample_width = p.get_sample_size(FORMAT)
        stream.stop_stream()
        stream.close()
        p.terminate()

        data = pack('<' + ('h' * len(r)), *r)
        wf = wave.open(path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(sample_width)
        wf.setframerate(Srate)
        wf.writeframes(data)
        wf.close()
        self.active[dev] = False
        # self.logger.info(" Stopped recording ")

    def recordToFile(self, path, duration=10, dev=None, Srate=16000, FORMAT=pyaudio.paInt16, CHUNK_SIZE=1024):
        self.stopRecord(dev)

        if os.path.isfile(path):
            # print " Recording File already present, deleting it"
            os.remove(path)

        th = threading.Thread(target=self.recordToFile_int, args=(path, duration, dev, Srate, FORMAT, CHUNK_SIZE,))

        # Reset the previously recorded RMS value data
        self.RecordingRMSArray = []

        # th.setDaemon(True)
        th.start()

    def setAudioPlaying(self):
        self.AudioPlaying = True

    def unsetAudioPlaying(self):
        self.AudioPlaying = False

    def logCurrentAudioStatus(self, funcName):
        debugStr = "Audio " + ("" if self.AudioPlaying else "not ") + "playing and " + \
                   "Audio " + ("not " if self.AudioPaused.isSet() else "") + "paused"

    #         self.logger.debug( " Audio Control2 : " + funcName + " " + debugStr )

    def pauseAudio(self):
        # Audio was playing but wan not already paused.
        if self.AudioPlaying and self.AudioPaused.isSet():
            self.AudioPaused.clear()
            self.logger.debug("Audio Control2 : Pausing the Audio")
        else:
            self.logCurrentAudioStatus("pauseAudio")

    def resumeAudio(self):
        # Audio was playing and is in paused state.
        if self.AudioPlaying and not self.AudioPaused.isSet():
            self.AudioPaused.set()
            self.logger.debug("Audio Control2 : Resuming the Audio")
        else:
            self.logCurrentAudioStatus("resumeAudio")

    def routeMusicToNewStreamProcess(self):
        # Call this when a new output device has been inserted in windows.
        # Setting this flag forces play_int to Get new default device stream to play music.
        self.routeMusicToNewStream = True

    def getConnectedAudioDevicesDetails(self):
        # Re - initialize Py audio in case any new device added.
        self.resetPyAudio()
        self.setUpAudioDevices()

        deviceCount = int(self.p.get_device_count())

        OutputDevices = {}
        InputDevices = {}

        for devIndex in range(deviceCount):
            devinfo = self.p.get_device_info_by_index(devIndex)

            if devinfo["maxOutputChannels"] > 0:
                OutputDevices[devIndex] = devinfo["name"]

            if devinfo["maxInputChannels"] > 0:
                InputDevices[devIndex] = devinfo["name"]

        # [ {0:Microsoft Sound Mapper - Input, }, {}]
        return [OutputDevices, InputDevices]

    def PlayBackOnDevice(self, devIndex):
        """
        Specify preferred device for playing audio in windows PC.
        """
        # Maybe a new audio device is included, so create new pyaudio instance.
        self.resetPyAudio()
        self.setUpAudioDevices()

        self.defaultDeviceIndex = devIndex

        if DEBUG_AUDIO_CONTROL2 and devIndex != -1:
            devinfo = self.p.get_device_info_by_index(devIndex)

    #             self.logger.debug("Audio Control2 : PlayBackOnDevice - Selected device %s" %devinfo)

    def getPlayBackDeviceIndex(self):
        if self.defaultDeviceIndex == -1:
            dev = self.p.get_default_output_device_info()['index']
        else:
            dev = self.defaultDeviceIndex

        if DEBUG_AUDIO_CONTROL2 and dev != -1:
            devinfo = self.p.get_device_info_by_index(dev)
        #             self.logger.debug("Audio Control2 : getPlayBackDeviceIndex - Selected device %s" %devinfo)

        return dev

    def getMicrophoneDeviceIndex(self):
        if self.defaultMicrophoneIndex == -1:
            dev = self.p.get_default_input_device_info()['index']

        else:
            dev = self.defaultMicrophoneIndex

        if DEBUG_AUDIO_CONTROL2 and dev != -1:
            devinfo = self.p.get_device_info_by_index(dev)
            self.logger.debug("Audio Control2 : getMicrophoneDeviceIndex - Selected device %s" % devinfo)

        return dev

    def SelectMicrophoneDevice(self, devIndex):
        """
        Specify a Microphone device for recording audio.
        """

        # Maybe a new audio device is included, so create new pyaudio instance.
        self.resetPyAudio()
        self.setUpAudioDevices()

        self.defaultMicrophoneIndex = devIndex

        if DEBUG_AUDIO_CONTROL2 and devIndex != -1:
            devinfo = self.p.get_device_info_by_index(devIndex)
            self.logger.debug("Audio Control2 : SelectMicrophoneDevice - Selected device %s" % devinfo)

    def play_int(self, myfile, repeat=1, duration=5000, dev=None, CHUNK_SIZE=1024):
        """ Init audio stream """
        self.routeMusicToNewStream = False
        self.streamUnavailable = False
        wf = wave.open(myfile, 'rb')
        # p = pyaudio.PyAudio()

        # Get Audio device to play music.
        dev = self.getPlayBackDeviceIndex()

        self.active[dev] = True
        self.abort[dev] = False
        stream = self.p.open(
            format=self.p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output_device_index=dev,
            output=True
        )

        # Update this stream.
        self.stream[dev] = stream

        """ Play entire file """
        self.setAudioPlaying()
        start = clock()
        data = wf.readframes(CHUNK_SIZE)

        self.logCurrentAudioStatus("Audio Control2 : Playing ")

        while repeat and clock() < start + duration and not self.abort[dev]:
            while data != '' and not self.abort[dev] and clock() < start + duration:
                # Check whether audio is requested to be paused by other threads.
                # Pause i.e. AudioPaused event has been cleared and following call waits till setting.
                self.AudioPaused.wait()

                # self.logger.info(" Playing audio now --- ")
                try:
                    stream.write(data)
                # Stream has been closed, this can be caused by USB removal.
                # Proceed with new sink to play music.
                except IOError as error:
                    self.logCurrentAudioStatus("play_int (stream.write) stopped with - %s" % error)
                    self.routeMusicToNewStream = True
                    self.streamUnavailable = True

                # Music interrrupted on current device/ rerouted to new audio device.
                if self.routeMusicToNewStream:
                    if self.streamUnavailable:
                        # Search for a default device to keep playing music.
                        _, dev = self.getDefaultDevices()
                        if DEBUG_AUDIO_CONTROL2:
                            self.logger.info("Audio Control2 : Re-routing music to default device")
                    else:
                        # Get new device stream to play music. Hoping you have chosen correct device.
                        dev = self.getPlayBackDeviceIndex()

                    stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                                         channels=wf.getnchannels(),
                                         rate=wf.getframerate(),
                                         output_device_index=dev,
                                         output=True)

                    # Mark new device as active and update it's stream.
                    self.active[dev] = True
                    self.abort[dev] = False
                    self.stream[dev] = stream

                    self.routeMusicToNewStream = False
                    self.streamUnavailable = False

                data = wf.readframes(CHUNK_SIZE)
            wf.rewind()
            data = wf.readframes(CHUNK_SIZE)

        """ Graceful shutdown """
        self.unsetAudioPlaying()
        stream.close()
        # p.terminate()
        self.active[dev] = False

        # self.logCurrentAudioStatus("Audio Control 1 : play_int stopping")

    def play(self, file, repeat=0, duration=300, dev=None, CHUNK_SIZE=1024):
        # self.logger.debug(" Audio Control : play ")
        self.stopPlayback(dev)
        if os.path.isfile(file):
            th = threading.Thread(target=self.play_int, args=(file, repeat, duration, dev, CHUNK_SIZE,))
            th.setDaemon(True)
            th.start()

    def playTone_int(self, Freq=440, amplitude=1.0, duration=1000, dev=None, CHUNK_SIZE=16):
        """ Init audio stream """
        if dev == None:
            dev = self.getPlayBackDeviceIndex()

        self.active[dev] = True
        self.abort[dev] = False

        self.stream[dev] = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=48000,
            output_device_index=dev,
            output=True)

        """ Play entire file """
        self.setAudioPlaying()

        rate = 48000.0
        start = clock()
        counter = 0
        phase = 0.0
        t2 = 0.0
        while clock() < start + duration:
            t = np.arange(float(counter * CHUNK_SIZE), float((counter + 1) * CHUNK_SIZE))
            dat = []
            for x in range(CHUNK_SIZE):
                factor2 = (t2 * float(Freq) * (math.pi * 2.0) / rate)
                factor2 = np.sin(factor2)
                dat.append(factor2 * amplitude)
                t2 += 1.0
            data = np.array(dat)
            try:
                self.stream[dev].write(data.astype(np.float32).tostring())
            except Exception as e:
                if "Stream is stopped" in e:
                    self.logger.debug("Stream is stopped")
                elif "Unanticipated host error" in e:
                    self.logger.debug("USB Cable may have been detached")
                else:
                    self.logger.debug("play_api failed")
                    self.logger.debug("ErrorCode: %s" % e)
                break
            counter += 1

        self.logger.debug("playTone_int end")

        """ Graceful Shutdown """
        self.unsetAudioPlaying()
        self.active[dev] = False

    def playTone(self, Freq=440, amplitude=1.0, duration=1000, dev=None, CHUNK_SIZE=1024):

        self.logger.debug("Audio Control : PlayTone")
        self.stopPlayback(dev)

        th = threading.Thread(target=self.playTone_int, args=(Freq, amplitude, duration, dev, CHUNK_SIZE,))
        th.setDaemon(True)
        th.start()

    def setTonePar(self, Freq=None, Amp=None, dev=None):
        if dev == None:
            p = pyaudio.PyAudio()
            dev = p.get_default_output_device_info()['index']
            p.terminate()
        if Freq != None:
            self.toneFreq[dev] = Freq
        if Amp != None:
            self.toneAmp[dev] = Amp

    def stopPlayback(self, dev=None):
        # self.logger.info(" Audio COntrol2 : stopPlayback")
        if dev == None:
            # dev = self.p.get_default_output_device_info()['index']
            if self.defaultDeviceIndex == -1:
                dev = self.p.get_default_output_device_info()['index']
            else:
                dev = self.defaultDeviceIndex

        if (self.stream[dev] != None):
            try:
                self.abort[dev] = True
                self.AudioPaused.set()
                self.AudioPlaying = False
                sleep(1)
                self.stream[dev].stop_stream()
                # self.logger.debug( "Audio Control2 : Stopping the Audio" )
            except Exception as e:
                if "Stream not open" in e:
                    self.logger.debug("Stream is not open or already closed")
                else:
                    self.logger.debug("stop_stream failed")
                    self.logger.debug("ErrorCode: %s" % e)
            sleep(1)
            self.stream[dev].close()
            self.stream[dev] = None

    def stopRecord(self, dev=None):
        if dev == None:
            p = pyaudio.PyAudio()
            if self.defaultMicrophoneIndex == -1:
                dev = p.get_default_input_device_info()['index']
            else:
                dev = self.defaultMicrophoneIndex
            p.terminate()
        while self.active[dev]:
            self.abort[dev] = True

    def getDefaultDevices(self):
        dev0 = self.p.get_default_input_device_info()['index']
        dev1 = self.p.get_default_output_device_info()['index']
        return dev0, dev1

    def GetRMSArrayOfRecording(self):
        return self.RecordingRMSArray


filePath = "plays.wav"
mf = os.path.abspath(filePath)
first = CWinSoundControl()
devices = first.getConnectedAudioDevicesDetails()[0]
# print(devices)
# print(devices.values())
dev = [{i: devices[i]} for i in devices if "Headset Earphone" in devices[i]]
print(dev)
devIndex = dev[0].keys()[0]
print(devIndex)
devIndex_2 = dev[1].keys()[0]
first.PlayBackOnDevice(devIndex)
playThread = Thread(target=first.play_int, args=(mf,))
playThread.start()

second = CWinSoundControl()
devices = second.getConnectedAudioDevicesDetails()[0]
# print(devices)
# print(devices.values())
dev = [{i: devices[i]} for i in devices if "Headset Earphone" in devices[i]]
devIndex_2 = dev[1].keys()[0]
print("mani", dev)
print("mani", devIndex_2)
devIndex_2 = dev[1].keys()[0]
second.PlayBackOnDevice(devIndex_2)
pt = Thread(target=second.play_int, args=(mf,))
pt.start()
