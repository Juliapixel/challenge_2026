package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"sync"

	"github.com/google/uuid"
	"github.com/pion/webrtc/v4"
)
type session struct {
	pc         *webrtc.PeerConnection
}

var (
	sessionsMu sync.Mutex
	sessions   = map[string]*session{}
)

func main() {
	http.HandleFunc("/sdp", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}

		body, err := io.ReadAll(r.Body)
		if err != nil {
			panic(err)
		}

		offer := webrtc.SessionDescription{}
		if err = json.Unmarshal(body, &offer); err != nil{
			panic(err)
		}
		
		pc, err := createPeerConnection()
		if err != nil {
			panic(err)
		}

		sessionID := uuid.NewString()
		sessionsMu.Lock()
		sessions[sessionID] = &session{pc: pc}
		sessionsMu.Unlock()

		pc.OnTrack(func(track *webrtc.TrackRemote, receiver *webrtc.RTPReceiver){
			fmt.Printf("[%s] receiving track: %s %s \n",sessionID, track.Kind(), track.Codec().MimeType)
			buf := make([]byte, 1500)
			for {
				_, _, err := track.Read(buf)
				if err != nil {
					return
				}
				//gravar/encaminhar pacote rtp recebidos
			}
		})
		pc.OnICEConnectionStateChange(func(state webrtc.ICEConnectionState) {
			fmt.Printf("[%s] ICE state: %s \n", sessionID, state)
			if state == webrtc.ICEConnectionStateFailed {
				pc.Close()
				sessionsMu.Lock()
				delete(sessions, sessionID)
				sessionsMu.Unlock()
			}
		})

		if err := pc.SetRemoteDescription(offer); err != nil {
			panic(err)
		}

		answer, err := pc.CreateAnswer(nil)
		if err != nil {
			panic(err)
		}

		gatherComplete := webrtc.GatheringCompletePromise(pc)

		if err := pc.SetLocalDescription(answer); err != nil {
		panic(err)
		}
		<-gatherComplete

		if err := pc.SetLocalDescription(answer); err != nil {
			panic(err)
		}

		w.Header().Set("X-Session-Id", sessionID)
		answerJson, err := json.Marshal(pc.LocalDescription())
		if err != nil {
			panic(err)
		}
		w.Write(answerJson)
	})
	
	fmt.Println(" listening port: 8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		panic(err)
	}
}

func createPeerConnection() (*webrtc.PeerConnection, error) {
	mediaEngine := webrtc.MediaEngine{}

	err := mediaEngine.RegisterCodec(webrtc.RTPCodecParameters{
		RTPCodecCapability: webrtc.RTPCodecCapability{
			MimeType:  webrtc.MimeTypeH264,
			ClockRate: 90000,
		},
		PayloadType: webrtc.PayloadType(96),
	}, webrtc.RTPCodecTypeVideo)
	if err != nil {
		return nil, err
	}

	api := webrtc.NewAPI(webrtc.WithMediaEngine(&mediaEngine))
	
	return api.NewPeerConnection(webrtc.Configuration{
		ICEServers: []webrtc.ICEServer{{URLs: []string{"stun:stun.l.google.com:19302"}}},
	})
}
