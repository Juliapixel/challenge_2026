package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"sync"
	"path/filepath"
	"os"
	"os/exec"

	"gocv.io/x/gocv"
	
	"github.com/pion/webrtc/v4/pkg/media/h264writer"
	
	"github.com/google/uuid"
	"github.com/pion/webrtc/v4"
)
type session struct {
	pc         *webrtc.PeerConnection
}

var (
    pc *webrtc.PeerConnection
	sessionsMu sync.Mutex
	sessions   = map[string]*session{}
)
const (
	frameWidth  = 1280
	frameHeight = 720
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
		
		sessionID :=  r.Header.Get("X-Session-Id")
		sessionsMu.Lock()
		s, exists := sessions[sessionID]
		sessionsMu.Unlock()

		if exists {
			pc = s.pc
		}  else {
			pc, err = createPeerConnection() 
			if err != nil {
				panic(err)
			}
			sessionID = uuid.NewString()
			sessionsMu.Lock()
			sessions[sessionID] = &session{pc: pc}
			sessionsMu.Unlock()
		}

		pc.OnTrack(func(track *webrtc.TrackRemote, receiver *webrtc.RTPReceiver){
			fmt.Printf("[%s] receiving track: %s %s \n",sessionID, track.Kind(), track.Codec().MimeType)
			cmd := exec.Command("ffmpeg",
			"-f", "h264",
			"-i", "pipe:0",
			"-f", "rawvideo",
			"-pix_fmt", "bgr24",
			"pipe:1",
			)
			stdin, err := cmd.StdinPipe()
			if err != nil {
				fmt.Println("error creating stdin pipe:", err)
				return
			}
			stdout, err := cmd.StdoutPipe()
			if err != nil {
				fmt.Println("error creating stdout pipe:", err)
				return
			}
			if err := cmd.Start(); err != nil {
				fmt.Println("error initializing ffmpeg:", err)
				return
			}
			h264Writer := h264writer.NewWith(stdin)
			go func() {
				defer h264Writer.Close()
				for {
					pkt, _, readErr := track.ReadRTP()
					if readErr != nil {
						return
					}
					if err := h264Writer.WriteRTP(pkt); err != nil {
						fmt.Println("error writing RTP:", err)
						return
					}
				}
			}()
			go func() {
				buf := make([]byte, frameWidth*frameHeight*3)
				for {
				if _, err := io.ReadFull(stdout, buf); err != nil {
					fmt.Printf("[%s] end of stream: %v\n", sessionID, err)
					return
				}

			mat, err := gocv.NewMatFromBytes(frameHeight, frameWidth, gocv.MatTypeCV8UC3, buf)
			if err != nil {
				fmt.Println("error creating Mat:", err)
				continue
			}

			// cv

			mat.Close()
		}
	}()
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

		w.Header().Set("X-Session-Id", sessionID)
		answerJson, err := json.Marshal(pc.LocalDescription())
		if err != nil {
			panic(err)
		}
		w.Write(answerJson)
	})
	upload()

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
func upload() {
	http.HandleFunc("/upload", func(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	sessionID := r.Header.Get("X-Session-Id")

	if err := r.ParseMultipartForm(32 << 20); err != nil { 
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	file, header, err := r.FormFile("file")
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	defer file.Close()

	destDir := filepath.Join("uploads", sessionID)
	if err := os.MkdirAll(destDir, 0o755); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	destPath := filepath.Join(destDir, header.Filename)
	dest, err := os.Create(destPath)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer dest.Close()

	if _, err := io.Copy(dest, file); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	fmt.Printf("[%s] received: %s\n", sessionID, header.Filename)
	w.WriteHeader(http.StatusOK)
	})
}
