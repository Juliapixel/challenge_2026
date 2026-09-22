package main

import (
	"github.com/pion/mediadevices"

	"github.com/pion/mediadevices/pkg/prop"
	"github.com/pion/webrtc/v4"
)

func main() {
	pc, err := webrtc.NewPeerConnection(webrtc.Configuration{
		ICEServers: []webrtc.ICEServer{webrtc.ICEServer{URLs: []string{"stun:stun.l.google.com:19302"}}},
	})
	if err != nil {
		panic(err)
	}

	stream, err := mediadevices.GetUserMedia(mediadevices.MediaStreamConstraints{
		Video: func(mtc *mediadevices.MediaTrackConstraints) {
			mtc.Width = prop.Int(1280)
			mtc.Height = prop.Int(720)
			// mtc.FrameFormat = prop.FrameFormat(frame.FormatI420)

		},
	})
	if err != nil {
		panic(err)
	}

	panic(pc)
	panic(stream)
}
