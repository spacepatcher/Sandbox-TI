# Sandbox-TI
Sandbox feed integration in ELK stack for threat intelligence operations

This service is designed for local storage and visualization of data feeds from public malware sandboxes:
* VxStream Sandbox (by Payload Security)
* Malwr (by Shadowserver)
* Metadefender (by OPSWAT)
* VirusTotal 

Each service is designed as a separate docker container. ELK stack is the base of data processing and visualizing.

Just run ```docker-compose up -d``` to start the service and do not forget to create ```app/key.json``` file with API-keys:

```
{
  "keys": {
    "virus-total": <your-secret-api-key>,
    "metadefender": <your-secret-api-key>,
  }
}
```

Enjoy!
