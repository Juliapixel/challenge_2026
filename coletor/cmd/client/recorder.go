package main

import (
	"fmt"
	"os"
	"io"
	"os/exec"
	"path/filepath"

	"github.com/pion/mediadevices"
)

func startCMAFRecording(stream mediadevices.MediaStream, outDir string) (stop func(), err error) {
	if err := os.MkdirAll(outDir, 0o755); err != nil {
		return nil, fmt.Errorf("create outDir: %w", err)
	}
	videoTrack := stream.GetVideoTracks()[0].(*mediadevices.VideoTrack)

	encodedReader, err := videoTrack.NewEncodedIOReader("h264")
	if err != nil {
		return nil, fmt.Errorf("encoded reader: %w", err)
	}
	cmd := exec.Command("ffmpeg",
	"-y",
	"-r", "30",
	"-f", "h264",
	"-i", "pipe:0",
	"-c:v", "copy",
	"-f", "mp4",
	"-movflags", "+frag_keyframe+empty_moov+default_base_moof",
	filepath.Join(outDir, "recording.mp4"),
	)
	cmd.Dir = outDir
	cmd.Stderr = os.Stderr

	stdin, err := cmd.StdinPipe()
	if err != nil {
		return nil, fmt.Errorf("stdin pipe: %w", err)
	}

	if err := cmd.Start(); err != nil {
		return nil, fmt.Errorf("start ffmpeg: %w", err)
	}

	done := make(chan struct{})
	go func() {
		defer close(done)
		defer stdin.Close()
		if _, err := io.Copy(stdin, encodedReader); err != nil {
			fmt.Println("error copying frames to ffmpeg:", err)
		}
	}()
	stop = func() {
		encodedReader.Close()
		<-done
		if err := cmd.Wait(); err != nil {
			fmt.Println("ffmpeg error:", err)
		}
	}
	return stop, nil
}