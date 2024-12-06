
import pjsua2 as pj
import time

ep=None
# Call class
class Call(pj.Call):
    """
    High level Python Call object, derived from pjsua2's Call object.
    """
    def __init__(self, acc, peer_uri='', chat=None, call_id = pj.PJSUA_INVALID_ID):
        pj.Call.__init__(self, acc, call_id)
        self.acc = acc

        self.aud_med=pj.AudioMedia

    def onCallState(self, prm):
        ci = self.getInfo()
        self.connected = ci.state == pj.PJSIP_INV_STATE_CONFIRMED
        self.recorder=None
        if(self.connected ==True):
            player=pj.AudioMediaPlayer()
            #Play welcome message
            player.createPlayer('audio/g711_a/steve.wav')

            self.recorder=pj.AudioMediaRecorder()
            i=0
            for media in ci.media:

                if (media.type == pj.PJMEDIA_TYPE_AUDIO):
                    self.aud_med = self.getMedia(i)
                    break
                i=i+1
            if self.aud_med!=None:
                mym= pj.AudioMedia.typecastFromMedia(self.aud_med)
                player.startTransmit( mym)
        if(ci.state==pj.PJSIP_INV_STATE_DISCONNECTED):
            print(">>>>>>>>>>>>>>>>>>>>>>> Call disconnected")

        raise Exception('onCallState done!')        

        if self.chat:
            self.chat.updateCallState(self, ci)

    def onCallMediaState(self, prm):
        ci = self.getInfo()
        for mi in ci.media:
            if mi.type == pj.PJMEDIA_TYPE_AUDIO and \
              (mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE or \
               mi.status == pj.PJSUA_CALL_MEDIA_REMOTE_HOLD):
                if mi.status == pj.PJSUA_CALL_MEDIA_REMOTE_HOLD and not self.onhold:
                    self.chat.addMessage(None, "'%s' sets call onhold" % (self.peerUri))
                    self._onhold_ = True
                elif mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE and self.onhold:
                    self.chat.addMessage(None, "'%s' sets call active" % (self.peerUri))
                    self._onhold_ = False
        raise Exception('onCallMediaState done!')        


class Account(pj.Account):
    """
    Subclass to extend the Account and get notifications etc.
    """
    def onRegState(self, prm):
        print ("***OnRegState: " + prm.reason)
    def onIncomingCall(self, prm):
        c = Call(self, call_id=prm.callId)
        call_prm = pj.CallOpParam()
        call_prm.statusCode = 180
        c.answer(call_prm)

        ci = c.getInfo()
        msg = "Incoming call  from  '%s'" % (ci.remoteUri)
        print(msg)
        call_prm.statusCode = 200
        c.answer(call_prm)
        raise Exception('onIncomingCall done!')


def receive_call_and_play():
    # Create and initialize the library
    ep_cfg = pj.EpConfig()
    ep_cfg.uaConfig.threadCnt = 0
    ep_cfg.uaConfig.mainThreadOnly = False
    ep = pj.Endpoint()
    ep.libCreate()
    ep.libInit(ep_cfg)
    ep.audDevManager().setNullDev()

    # Create SIP transport. Error handling sample is shown
    sipTpConfig = pj.TransportConfig()
    sipTpConfig.port = 12345
    tp=ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, sipTpConfig)
    # Start the library
    ep.libStart()

    acfg = pj.AccountConfig()


    acfg.idUri = "sip:5001@192.168.7.60"
    acfg.regConfig.registrarUri = "sip:192.168.7.60"
    cred = pj.AuthCredInfo("digest", "*", "5001", 0, "5001500150015001")
    acfg.sipConfig.authCreds.append(cred)

    # Create the account
    acc = Account()
    acc.create(acfg)


    while True:    
        ep.libHandleEvents(10)


    ep.libDestroy()
    del ep

#
# main()
#
if __name__ == "__main__":
    receive_call_and_play()