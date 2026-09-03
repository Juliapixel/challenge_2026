package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"time"

	"github.com/pion/mediadevices"
	"github.com/pion/mediadevices/pkg/codec/x264"
	"github.com/pion/mediadevices/pkg/frame"
	"github.com/pion/mediadevices/pkg/prop"
	"github.com/pion/webrtc/v4"

	_ "github.com/pion/mediadevices/pkg/driver/camera"
)

var sessionID string

func main() {if len(os.Args) != 2 {
	fmt.Printf("usage: %s <serverAddr> \n ", os.Args[0])
	return
	}

	serverAddr := os.Args[1]

	pc, err := webrtc.NewPeerConnection(webrtc.Configuration{
		ICEServers: []webrtc.ICEServer{{URLs: []string{"stun:stun.l.google.com:19302"}}},
	})
	if err != nil {
		panic(err)
	}

	params, err := x264.NewParams()
	if err != nil {
		panic(err)
	}
	params.BitRate = 1_000_000
	params.Preset = x264.PresetMedium

	for _, dev := range mediadevices.EnumerateDevices() {
		fmt.Println(dev)
	}

	stream, err := mediadevices.GetUserMedia(mediadevices.MediaStreamConstraints{
		Video: func(mtc *mediadevices.MediaTrackConstraints) {
			mtc.Width = prop.Int(1280)
			mtc.Height = prop.Int(720)

			mtc.FrameFormat = prop.FrameFormat(frame.FormatI420)
		},
		Codec: mediadevices.NewCodecSelector(mediadevices.WithVideoEncoders(&params)),
	})
	if err != nil {
		panic(err)
	}

	outDir := filepath.Join("recordings", time.Now().Format("2026-09-01_20-45-33"))

	pc.OnICEConnectionStateChange(func(state webrtc.ICEConnectionState) {
		fmt.Println("estado ICE:", state)
		switch state {
		case webrtc.ICEConnectionStateDisconnected:
			// add timer de espera 
		case webrtc.ICEConnectionStateFailed:
			if _, err := startCMAFRecording(stream, outDir); err != nil {
				fmt.Println("error inicializing record:", err)
			}
		case webrtc.ICEConnectionStateConnected:
			// add stopRecording e upload, se estava gravando
		}
	})
	stream.GetVideoTracks()[0].(*mediadevices.VideoTrack).NewReader(false).Read()

	videoTrack := stream.GetVideoTracks()[0]

	if _, err := pc.AddTrack(videoTrack.(*mediadevices.VideoTrack)); err != nil {
		panic(err)
	}

	offer, err := pc.CreateOffer(nil)
	if err != nil {
		panic(err)
	}
	gatherComplete := webrtc.GatheringCompletePromise(pc)

	if err := pc.SetLocalDescription(offer); err != nil {
		panic(err)
	}
	<-gatherComplete

	offerJson, err := json.Marshal(pc.LocalDescription())
	if err != nil {
		panic(err)
	}

	req, err := http.NewRequest(http.MethodPost, fmt.Sprintf("%s/sdp", serverAddr), bytes.NewReader(offerJson))
	if err != nil {
		panic(err)
	}

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	sessionID = resp.Header.Get("X-Session-Id")
	fmt.Println("Session created", sessionID)
	if err != nil {
		panic(err)
	}

	answerBody, err := io.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}

	answer := webrtc.SessionDescription{}
	if err := json.Unmarshal(answerBody, &answer); err != nil {
		panic(err)
	}
	if err := pc.SetRemoteDescription(answer); err != nil {
		panic(err)
	}
	fmt.Println("Connected, sending video :P")
}
