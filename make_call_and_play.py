import pjsua2 as pj

import time
import logging

# Subclass to extend the Account and get notifications etc.
class Account(pj.Account):
    """
    Subclass to extend the Account.
    """
    def onRegState(self, prm):
        print("***OnRegState: " + prm.reason)




class Call(pj.Call):
    """
    High level Python Call object, derived from pjsua2's Call object.
    """
    def __init__(self, acc, call_id=pj.PJSUA_INVALID_ID):
        pj.Call.__init__(self, acc, call_id)
        self.player = None

    def onCallState(self, prm):

        ci = self.getInfo()



        if(ci.state==pj.PJSIP_INV_STATE_DISCONNECTED):
            print(">>>>>>>>>>>>>>>>>>>>>>> Call disconnected")

        raise Exception('onCallState done!')

    def onCallMediaState(self, prm):
        print("Call media state changed")
        ci = self.getInfo()
        if ci.state == pj.PJSIP_INV_STATE_CONFIRMED:
            print("Call is confirmed, starting audio playback")
            self.player = pj.AudioMediaPlayer()  # Use the class level attribute
            self.player.createPlayer("audio/steve.wav", pj.PJMEDIA_FILE_NO_LOOP)
            aud_med = self.getAudioMedia(-1)
            self.player.startTransmit(aud_med)
        raise Exception('onCallMediaState done!')

def make_call_and_play():
    # Create and initialize the library
    ep_cfg = pj.EpConfig()
    ep_cfg.medConfig.channelCount = 2
    ep = pj.Endpoint()
    ep.libCreate()
    ep.libInit(ep_cfg)

    # Create SIP transport. Error handling sample is shown
    sipTpConfig = pj.TransportConfig()
    sipTpConfig.port = 5060
    ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, sipTpConfig)
    # Start the library
    ep.libStart()
    pj.Endpoint.instance().audDevManager().setNullDev()

    acfg = pj.AccountConfig()

    acfg.idUri = "sip:5001@192.168.7.60"
    acfg.regConfig.registrarUri = "sip:192.168.7.60"
    cred = pj.AuthCredInfo("digest", "*", "5001", 0, "5001500150015001")
    acfg.sipConfig.authCreds.append(cred)


    # Create the account
    acc = Account()

    acc.create(acfg)
    time.sleep(4)

    call = Call(acc)
    call_prm = pj.CallOpParam(True)


    try:
        call.makeCall('sip:1402@192.168.7.60', call_prm)
    except Exception as e:
        print(e)
    while True:
        if call.isActive():
            time.sleep(2)
        else:
            break

    ep.libDestroy()
    del ep


#
# main()
#
if __name__ == "__main__":
    make_call_and_play()
