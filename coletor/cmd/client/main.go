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
	"log"

	"github.com/pion/mediadevices"
	"github.com/pion/mediadevices/pkg/codec/x264"
	"github.com/pion/mediadevices/pkg/frame"
	"github.com/pion/mediadevices/pkg/prop"
	"github.com/pion/webrtc/v4"

	_ "github.com/pion/mediadevices/pkg/driver/camera"
)

var (
	sessionID string
	stopRecordingFn func()
	isRecording     bool
	isReconnecting bool
)

func main() {
	if len(os.Args) != 2 {
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

	outDir := filepath.Join("recordings", time.Now().Format("2006-01-02_15-04-05"))

	pc.OnICEConnectionStateChange(func(state webrtc.ICEConnectionState) {
		fmt.Println(" ICE state:", state)
		switch state {
		case webrtc.ICEConnectionStateDisconnected:
			time.AfterFunc(5*time.Second, func() {
				if pc.ICEConnectionState() == webrtc.ICEConnectionStateDisconnected && !isRecording {
					outDir = newOutDir()
				stop, err := startRecording(stream, outDir)
				if err == nil {
					stopRecordingFn = stop
					isRecording = true
				}
			}
				if !isReconnecting {
				isReconnecting = true
				go func() {
					defer func() { isReconnecting = false }() 
					for state := pc.ICEConnectionState(); state == webrtc.ICEConnectionStateDisconnected || state == webrtc.ICEConnectionStateFailed; state = pc.ICEConnectionState() {
						fmt.Println("reconnection signaled successfully")
						if err := iceReconnection(pc, serverAddr); err == nil {
							break
						} else {
							fmt.Println("reconnection attempt failed:", err)
						}
						time.Sleep(5 * time.Second)
					}
				}()
			}
		})
		case webrtc.ICEConnectionStateFailed:
			if !isRecording {
			outDir = newOutDir()
			stop, err := startRecording(stream, outDir)
			if err != nil {
				fmt.Println("error initializing record:", err)
				return
			}
			stopRecordingFn = stop
			isRecording = true
		}

		case webrtc.ICEConnectionStateConnected:
			fmt.Printf("sending video :P \n")
			if stopRecordingFn != nil {
				stopRecordingFn()
				stopRecordingFn = nil
				go func() {
					if err := uploadRecording(outDir, serverAddr); err != nil {
					fmt.Println("upload error:", err)
				}
		}()
	}

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
	select{}
}

func iceReconnection(pc *webrtc.PeerConnection, serverAddr string) error {
	log.Println("initiating ICE Restart")
	offer, err := pc.CreateOffer(&webrtc.OfferOptions{ICERestart: true})
	if err != nil {
		return fmt.Errorf("failed to create offer for ICE restart: %w", err)
	}
	
	gatherComplete := webrtc.GatheringCompletePromise(pc)
	if err := pc.SetLocalDescription(offer); err != nil {
		return fmt.Errorf("failed to set local description during restart: %v", err)
	}

	<-gatherComplete

	offerJson, _ := json.Marshal(pc.LocalDescription())
	req, _ := http.NewRequest(http.MethodPost, fmt.Sprintf("%s/sdp", serverAddr), bytes.NewReader(offerJson))
	req.Header.Set("X-Session-Id", sessionID)
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		pc.SetLocalDescription(webrtc.SessionDescription{Type: webrtc.SDPTypeRollback})
		return fmt.Errorf("failed to send ICE restart offer to server: %v", err)
	}
	defer resp.Body.Close()

	sessionID = resp.Header.Get("X-Session-Id")

	answerBody, _ := io.ReadAll(resp.Body)
	answer := webrtc.SessionDescription{}
	if err := json.Unmarshal(answerBody, &answer); err != nil {
		pc.SetLocalDescription(webrtc.SessionDescription{Type: webrtc.SDPTypeRollback})
		return fmt.Errorf("failed to parse answer: %v", err)
	}

	if err := pc.SetRemoteDescription(answer); err != nil {
		pc.SetLocalDescription(webrtc.SessionDescription{Type: webrtc.SDPTypeRollback})
		return fmt.Errorf("failed to set remote answer during restart: %v", err)
	}
	return nil
}