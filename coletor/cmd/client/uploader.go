package main

import (
	"fmt"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
)
func uploadRecording(outDir string, serverAddr string) error {
	files, err := os.ReadDir(outDir)
	if err != nil {
		return fmt.Errorf("read outDir: %w", err)
	}

	for _, f := range files {
		if f.IsDir() {
			continue
		}
		if err := uploadFile(filepath.Join(outDir, f.Name()), f.Name(), serverAddr); err != nil {
			return fmt.Errorf("upload  %s: %w", f.Name(), err)
		}
		fmt.Println("sended:", f.Name())
	}

	return nil
}

func uploadFile(path string, filename string, serverAddr string) error {
	file, err := os.Open(path)
	if err != nil {
		return err
	}
	defer file.Close()

	pr, pw, err := os.Pipe()
	if err != nil {
		return err
	} 
	mw := multipart.NewWriter(pw)

	go func() {
		defer pw.Close()
		defer mw.Close()

		part, err := mw.CreateFormFile("file", filename)
		if err != nil {
			return
		}
		if _, err := file.WriteTo(part); err != nil {
			fmt.Println("error copying archive to multipart:", err)
		}
	}()

	req, err := http.NewRequest(http.MethodPost, fmt.Sprintf("%s/upload", serverAddr), pr)
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", mw.FormDataContentType())
	req.Header.Set("X-Session-Id", sessionID)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("server response status %d", resp.StatusCode)
	}

	return nil
}