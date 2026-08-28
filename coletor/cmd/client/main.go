package main

import (
	"fmt"

	"github.com/pion/mediadevices"
	"github.com/pion/mediadevices/pkg/codec/x264"
	"github.com/pion/mediadevices/pkg/frame"
	"github.com/pion/mediadevices/pkg/prop"
	"github.com/pion/webrtc/v4"

	_ "github.com/pion/mediadevices/pkg/driver/camera"
)

func main() {
	pc, err := webrtc.NewPeerConnection(webrtc.Configuration{
		ICEServers: []webrtc.ICEServer{webrtc.ICEServer{URLs: []string{"stun:stun.l.google.com:19302"}}},
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

	stream.GetVideoTracks()[0].(*mediadevices.VideoTrack).NewReader(false).Read()

	panic(pc)
}
