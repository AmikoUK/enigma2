from os import listdir
from boxbranding import getBoxType, getBrandOEM, getDisplayType, getHaveAVJACK, getHaveHDMIinFHD, getHaveHDMIinHD, getHaveRCA, getHaveSCART, getHaveSCARTYUV, getHaveYUV, getImageType, getMachineBrand, getMachineBuild, getMachineMtdRoot, getMachineName
from enigma import Misc_Options, eDVBCIInterfaces, eDVBResourceManager

from Components.About import getChipSetString
from Components.RcModel import rc_model
from Tools.BoxConfig import BoxConfig
from Tools.Directories import fileCheck, fileExists, fileHas, pathExists, isPluginInstalled
from Tools.HardwareInfo import HardwareInfo

SystemInfo = {}
SystemInfo["BoxInfo"] = BoxConfig()
SystemInfo["HasRootSubdir"] = False	# This needs to be here so it can be reset by getMultibootslots!
SystemInfo["RecoveryMode"] = False	# This needs to be here so it can be reset by getMultibootslots!
from Tools.Multiboot import GetCurrentImage, getMultibootslots  # This import needs to be here to avoid a SystemInfo load loop!
SystemInfo["HasHiSi"] = pathExists("/proc/hisi") and getBoxType() not in ("vipertwin", "viper4kv20", "viper4kv40")	# This needs to be for later checks
SystemInfo["canMultiBoot"] = getMultibootslots()	# SystemInfo["MBbootdevice"] set on call 
SystemInfo["MultiBootSlot"] = GetCurrentImage() if SystemInfo["canMultiBoot"] else False


def getNumVideoDecoders():
	numVideoDecoders = 0
	while fileExists("/dev/dvb/adapter0/video%d" % numVideoDecoders, "f"):
		numVideoDecoders += 1
	return numVideoDecoders


def countFrontpanelLEDs():
	numLeds = fileExists("/proc/stb/fp/led_set_pattern") and 1 or 0
	while fileExists("/proc/stb/fp/led%d_pattern" % numLeds):
		numLeds += 1
	return numLeds


def hasInitCam():
	for cam in listdir("/etc/init.d"):
		if cam.startswith("softcam.") and not cam.endswith("None"):
			return True
		else:
			pass
	return False


SystemInfo["HasInitCam"] = hasInitCam()
SystemInfo["MachineBrand"] = getMachineBrand()
SystemInfo["MachineName"] = getMachineName()
SystemInfo["DeveloperImage"] = getImageType().lower() != "release"
SystemInfo["CommonInterface"] = eDVBCIInterfaces.getInstance().getNumOfSlots()
SystemInfo["CommonInterfaceCIDelay"] = fileCheck("/proc/stb/tsmux/rmx_delay")
for cislot in range(0, SystemInfo["CommonInterface"]):
	SystemInfo["CI%dSupportsHighBitrates" % cislot] = fileCheck("/proc/stb/tsmux/ci%d_tsclk" % cislot)
	SystemInfo["CI%dRelevantPidsRoutingSupport" % cislot] = fileCheck("/proc/stb/tsmux/ci%d_relevant_pids_routing" % cislot)
SystemInfo["NumVideoDecoders"] = getNumVideoDecoders()
SystemInfo["Udev"] = not fileExists("/dev/.devfsd")
SystemInfo["HasFullHDSkinSupport"] = getBoxType() not in ("vipertwin",)
SystemInfo["PIPAvailable"] = getMachineBuild() not in ("i55plus") and SystemInfo["NumVideoDecoders"] > 1
SystemInfo["CanMeasureFrontendInputPower"] = eDVBResourceManager.getInstance().canMeasureFrontendInputPower()
SystemInfo["12V_Output"] = Misc_Options.getInstance().detected_12V_output()
SystemInfo["ZapMode"] = fileCheck("/proc/stb/video/zapmode") or fileCheck("/proc/stb/video/zapping_mode")
SystemInfo["NumFrontpanelLEDs"] = countFrontpanelLEDs()
SystemInfo["FrontpanelDisplay"] = fileExists("/dev/dbox/oled0") or fileExists("/dev/dbox/lcd0")
SystemInfo["7segment"] = getDisplayType() in ("7segment")
SystemInfo["ConfigDisplay"] = SystemInfo["FrontpanelDisplay"] and getDisplayType() not in ("7segment")
SystemInfo["LCDSKINSetup"] = pathExists("/usr/share/enigma2/display") and not SystemInfo["7segment"]
SystemInfo["OledDisplay"] = fileExists("/dev/dbox/oled0")
SystemInfo["LcdDisplay"] = fileExists("/dev/dbox/lcd0")
SystemInfo["LCDsymbol_hdd"] = getBoxType() in ("mutant51",) and fileCheck("/proc/stb/lcd/symbol_hdd")
SystemInfo["HasNoDisplay"] = getBoxType() in ("et4x00", "et5x00", "et6x00", "gb800se", "gb800solo", "gbx34k", "iqonios300hd", "mbmicro", "sf128", "sf138", "tmsingle", "tmnano2super", "tmnanose", "tmnanoseplus", "tmnanosem2", "tmnanosem2plus", "tmnanosecombo", "vusolo")
SystemInfo["DisplayLED"] = getBoxType() in ("gb800se", "gb800solo", "gbx1", "gbx2", "gbx3", "gbx3h")
SystemInfo["LEDButtons"] = False # getBoxType() == "vuultimo", For some reason this causes a cpp crash on vuultimo (which we no longer build). The cause needs investigating or the dead code in surrounding modules that this change causes should be removed.
SystemInfo["DeepstandbySupport"] = HardwareInfo().has_deepstandby()
SystemInfo["Fan"] = fileCheck("/proc/stb/fp/fan")
SystemInfo["FanPWM"] = SystemInfo["Fan"] and fileCheck("/proc/stb/fp/fan_pwm")
SystemInfo["PowerLED"] = fileExists("/proc/stb/power/powerled")
SystemInfo["PowerLED2"] = fileExists("/proc/stb/power/powerled2")
SystemInfo["StandbyLED"] = fileExists("/proc/stb/power/standbyled")
SystemInfo["SuspendLED"] = fileExists("/proc/stb/power/suspendled")
SystemInfo["LedPowerColor"] = fileExists("/proc/stb/fp/ledpowercolor")
SystemInfo["LedStandbyColor"] = fileExists("/proc/stb/fp/ledstandbycolor")
SystemInfo["LedSuspendColor"] = fileExists("/proc/stb/fp/ledsuspendledcolor")
SystemInfo["Power24x7On"] = fileExists("/proc/stb/fp/power4x7on")
SystemInfo["Power24x7Standby"] = fileExists("/proc/stb/fp/power4x7standby")
SystemInfo["Power24x7Suspend"] = fileExists("/proc/stb/fp/power4x7suspend")
SystemInfo["WakeOnLAN"] = getBoxType() not in ("et8000", "et10000") and fileCheck("/proc/stb/power/wol") or fileCheck("/proc/stb/fp/wol")
SystemInfo["hasHdmiCec"] = fileExists("/dev/hdmi_cec") or fileExists("/dev/misc/hdmi_cec0")
SystemInfo["HasExternalPIP"] = getMachineBuild() not in ("et9x00", "et6x00", "et5x00") and fileCheck("/proc/stb/vmpeg/1/external")
SystemInfo["VideoDestinationConfigurable"] = fileExists("/proc/stb/vmpeg/0/dst_left")
SystemInfo["hasPIPVisibleProc"] = fileCheck("/proc/stb/vmpeg/1/visible")
SystemInfo["VFD_scroll_repeats"] = not SystemInfo["7segment"] and getBoxType() not in ("et8500",) and fileCheck("/proc/stb/lcd/scroll_repeats")
SystemInfo["VFD_scroll_delay"] = not SystemInfo["7segment"] and getBoxType() not in ("et8500",) and fileCheck("/proc/stb/lcd/scroll_delay")
SystemInfo["VFD_initial_scroll_delay"] = not SystemInfo["7segment"] and getBoxType() not in ("et8500",) and fileCheck("/proc/stb/lcd/initial_scroll_delay")
SystemInfo["VFD_final_scroll_delay"] = not SystemInfo["7segment"] and getBoxType() not in ("et8500",) and fileCheck("/proc/stb/lcd/final_scroll_delay")
SystemInfo["LcdLiveTV"] = fileCheck("/proc/stb/fb/sd_detach") or fileCheck("/proc/stb/lcd/live_enable")
SystemInfo["LCDMiniTV"] = fileExists("/proc/stb/lcd/mode")
SystemInfo["LCDMiniTVPiP"] = SystemInfo["LCDMiniTV"] and getBoxType() != "gb800ueplus"
SystemInfo["LcdPowerOn"] = fileExists("/proc/stb/power/vfd")
SystemInfo["FastChannelChange"] = False
SystemInfo["3DMode"] = fileCheck("/proc/stb/fb/3dmode") or fileCheck("/proc/stb/fb/primary/3d")
SystemInfo["3DZNorm"] = fileCheck("/proc/stb/fb/znorm") or fileCheck("/proc/stb/fb/primary/zoffset")
SystemInfo["Blindscan_t2_available"] = fileCheck("/proc/stb/info/vumodel") and getBoxType().startswith("vu")
SystemInfo["HasTranscoding"] = pathExists("/proc/stb/encoder/0") or fileCheck("/dev/bcm_enc0")
SystemInfo["HasH265Encoder"] = fileHas("/proc/stb/encoder/0/vcodec_choices", "h265")
SystemInfo["CanNotDoSimultaneousTranscodeAndPIP"] = getBoxType() in ("vusolo4k", "gbquad4k", "gbue4k")
SystemInfo["hasXcoreVFD"] = getBoxType() in ("osmega", "spycat4k", "spycat4kmini", "spycat4kcomb") and fileCheck("/sys/module/brcmstb_%s/parameters/pt6302_cgram" % getBoxType())
SystemInfo["HasHDMIin"] = getHaveHDMIinHD() in ("True",) or getHaveHDMIinFHD() in ("True",)
SystemInfo["Has24hz"] = fileCheck("/proc/stb/video/videomode_24hz")
SystemInfo["AndroidMode"] = SystemInfo["RecoveryMode"] and getMachineBuild() in ("multibox",)
SystemInfo["canBackupEMC"] = getMachineBuild() in ("hd51", "h7") and ("disk.img", "%s" % SystemInfo["MBbootdevice"]) or getMachineBuild() in ("osmio4k", "osmio4kplus", "osmini4k") and ("emmc.img", "%s" % SystemInfo["MBbootdevice"]) or SystemInfo["HasHiSi"] and ("usb_update.bin", "none")
SystemInfo["canMode12"] = getMachineBuild() in ("hd51", "h7") and ("brcm_cma=440M@328M brcm_cma=192M@768M", "brcm_cma=520M@248M brcm_cma=200M@768M")
SystemInfo["HasMMC"] = fileHas("/proc/cmdline", "root=/dev/mmcblk") or "mmcblk" in getMachineMtdRoot()
SystemInfo["HasH9SD"] = getMachineBuild() in ("h9", "i55plus") and pathExists("/dev/mmcblk0p1")
SystemInfo["HasSDnomount"] = getMachineBuild() in ("h9", "i55plus") and (False, "none") or getMachineBuild() in ("multibox", "h9combo", "h9combose", "h9twin", "h9se") and (True, "mmcblk0")
SystemInfo["CanProc"] = SystemInfo["HasMMC"] and getBrandOEM() != "vuplus"
SystemInfo["Canaudiosource"] = fileCheck("/proc/stb/hdmi/audio_source")
SystemInfo["Can3DSurround"] = fileHas("/proc/stb/audio/3d_surround_choices", "none")
SystemInfo["Can3DSpeaker"] = fileHas("/proc/stb/audio/3d_surround_speaker_position_choices", "center")
SystemInfo["CanAutoVolume"] = fileHas("/proc/stb/audio/avl_choices", "none") or fileHas("/proc/stb/audio/avl_choices", "hdmi")
SystemInfo["supportPcmMultichannel"] = fileCheck("/proc/stb/audio/multichannel_pcm")
SystemInfo["CanDownmixAC3"] = fileHas("/proc/stb/audio/ac3_choices", "downmix")
SystemInfo["CanAC3Transcode"] = fileHas("/proc/stb/audio/ac3plus_choices", "force_ac3")
SystemInfo["CanDownmixDTS"] = fileHas("/proc/stb/audio/dts_choices", "downmix")
SystemInfo["CanDTSHD"] = fileHas("/proc/stb/audio/dtshd_choices", "downmix")
SystemInfo["CanDownmixAAC"] = fileHas("/proc/stb/audio/aac_choices", "downmix")
SystemInfo["CanDownmixAACPlus"] = fileHas("/proc/stb/audio/aacplus_choices", "downmix")
SystemInfo["CanAACTranscode"] = fileHas("/proc/stb/audio/aac_transcode_choices", "off")
SystemInfo["CanWMAPRO"] = fileHas("/proc/stb/audio/wmapro_choices", "downmix")
SystemInfo["CanBTAudio"] = fileHas("/proc/stb/audio/btaudio_choices", "off")
SystemInfo["CanBTAudioDelay"] = fileCheck("/proc/stb/audio/btaudio_delay") or fileCheck("/proc/stb/audio/btaudio_delay_pcm")
SystemInfo["havecolorspace"] = fileCheck("/proc/stb/video/hdmi_colorspace")
SystemInfo["havecolorspacechoices"] = fileCheck("/proc/stb/video/hdmi_colorspace_choices")
SystemInfo["havecolorimetry"] = fileCheck("/proc/stb/video/hdmi_colorimetry")
SystemInfo["havecolorimetrychoices"] = fileCheck("/proc/stb/video/hdmi_colorimetry_choices")
SystemInfo["havehdmicolordepth"] = fileCheck("/proc/stb/video/hdmi_colordepth")
SystemInfo["havehdmicolordepthchoices"] = fileCheck("/proc/stb/video/hdmi_colordepth_choices")
SystemInfo["havehdmihdrtype"] = fileExists("/proc/stb/video/hdmi_hdrtype")
SystemInfo["HDRSupport"] = fileExists("/proc/stb/hdmi/hlg_support_choices")
SystemInfo["Canedidchecking"] = fileCheck("/proc/stb/hdmi/bypass_edid_checking")
SystemInfo["haveboxmode"] = fileExists("/proc/stb/info/boxmode")
SystemInfo["HasScaler_sharpness"] = pathExists("/proc/stb/vmpeg/0/pep_scaler_sharpness")
SystemInfo["hasJack"] = getHaveAVJACK() in ('True',)
SystemInfo["hasRCA"] = getHaveRCA() in ('True',)
SystemInfo["hasScart"] = getHaveSCART() in ('True',)
SystemInfo["hasScartYUV"] = getHaveSCARTYUV() in ('True',)
SystemInfo["hasYUV"] = getHaveYUV() in ('True',)
SystemInfo["VideoModes"] = getChipSetString() in (  # 2160p and 1080p capable hardware...
	"5272s", "7251", "7251s", "7252", "7252s", "7278", "7366", "7376", "7444s", "72604", "3798mv200", "3798cv200", "hi3798mv200", "hi3798cv200"
) and (
	["720p", "1080p", "2160p", "1080i", "576p", "576i", "480p", "480i"],  # Normal modes.
	{"720p", "1080p", "2160p", "1080i"}  # Widescreen modes.
) or getChipSetString() in (  # 1080p capable hardware...
	"7241", "7356", "73565", "7358", "7362", "73625", "7424", "7425", "7552", "3716mv410"
) and (
	["720p", "1080p", "1080i", "576p", "576i", "480p", "480i"],  # Normal modes.
	{"720p", "1080p", "1080i"}  # Widescreen modes.
) or (  # Default modes (neither 2160p nor 1080p capable hardware)...
	["720p", "1080i", "576p", "576i", "480p", "480i"],  # Normal modes.
	{"720p", "1080i"}  # Widescreen modes.
)

SystemInfo["FbcTunerPowerAlwaysOn"] = getBoxType() in ("vusolo4k", "vuduo4k", "vuduo4kse", "vuultimo4k", "vuuno4k", "vuuno4kse", "gbquad4k", "gbue4k")
SystemInfo["HasPhysicalLoopthrough"] = ["Vuplus DVB-S NIM(AVL2108)", "GIGA DVB-S2 NIM (Internal)"]
SystemInfo["HasFBCtuner"] = ["Vuplus DVB-C NIM(BCM3158)", "Vuplus DVB-C NIM(BCM3148)", "Vuplus DVB-S NIM(7376 FBC)", "Vuplus DVB-S NIM(45308X FBC)", "Vuplus DVB-S NIM(45208 FBC)", "DVB-S NIM(45208 FBC)", "DVB-S2X NIM(45308X FBC)", "DVB-S2 NIM(45308 FBC)", "DVB-C NIM(3128 FBC)","BCM45208", "BCM45308X", "BCM3158"]

SystemInfo["rc_model"] = rc_model.getRcFolder()
SystemInfo["mapKeyInfoToEpgFunctions"] = SystemInfo["rc_model"] in ("vu", "vu2", "vu3", "vu4") # due to button limitations of the remote control
SystemInfo["toggleTvRadioButtonEvents"] = SystemInfo["rc_model"] in ("ax4", "beyonwiz1", "beyonwiz2", "gb0", "gb1", "gb2", "gb3", "gb4", "sf8008", "sf8008m", "uniboxhde") # due to button limitations of the remote control
