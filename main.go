package main

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"

	"golang.org/x/oauth2"
	"golang.org/x/oauth2/google"
	"google.golang.org/api/dns/v1"
)

func main() {
	//var publicIp IPAddress = getPublicIp()

	//fmt.Println(getPublicIp())
	getDNSRecordSet()
}

//type IPAddress string
type IPAddress struct {
	Query string
}

func getPublicIp() string {
	req, err := http.Get("http://ip-api.com/json/")

	if err != nil {
		return err.Error()
	}

	defer req.Body.Close()

	body, err := ioutil.ReadAll(req.Body)

	if err != nil {
		return err.Error()
	}

	var publicip IPAddress

	json.Unmarshal(body, &publicip)

	return publicip.Query
}

func getDNSRecordSet() "google.golang.org/api/dns/v1".Service {
	client, err := google.DefaultClient(oauth2.NoContext,
		"https://www.googleapis.com/auth/cloud-platform")
	if err != nil {
		log.Fatal(err)
	}
	svc, err := dns.New(client)
	if err != nil {
		log.Fatal(err)
	}

	return svc
}
