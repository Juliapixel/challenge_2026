package main

import (
	"encoding/json"
	"io"
	"net/http"

	"github.com/pion/webrtc/v4"
)

func main() {
	http.HandleFunc("/sdp", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}
		sd := &webrtc.SessionDescription{}
		body, err := io.ReadAll(r.Body)
		if err != nil {
			panic(err)
		}
		err = json.Unmarshal(body, sd)
		if err != nil {
			panic(err)
		}
		pc, err := CreatePeerConection()
        if err != nil {
			panic(err)
			
		}
		pc.SetRemoteDescription(*sd)
			sigma := make(chan struct{})
		

		pc.OnICECandidate(func(i*webrtc.ICECandidate){
			if i == nil {
				sigma <- struct{}{}

			}
		})
		offer, err := pc.CreateAnswer(&webrtc.AnswerOptions{})
		if err != nil {
			panic(err)

		}
		offerJson, err := json.Marshal(offer)
		if err != nil {
			panic(err)

			
		}
		w.Write(offerJson)
	})
}
func CreatePeerConection() (*webrtc.PeerConnection, error) {
	mediaEngine := webrtc.MediaEngine{}
	
	err := mediaEngine.RegisterCodec(webrtc.RTPCodecParameters{
		RTPCodecCapability: webrtc.RTPCodecCapability{
			MimeType : webrtc.MimeTypeH264,
			ClockRate: 90000,
		},
		PayloadType: webrtc.PayloadType(96),
	}, webrtc.RTPCodecTypeVideo)
	if err != nil {
		return nil, err
	}

	api := webrtc.NewAPI(webrtc.WithMediaEngine(&mediaEngine))

	return	api.NewPeerConnection(webrtc.Configuration{ICEServers: []webrtc.ICEServer{webrtc.ICEServer{URLs: []string{"stun.stun.l.google.com:19302"}}},
	})
}