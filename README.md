# SyncStream

## Installation
### Requirements
- python3
- python3-yaml
- tmux
- g++

### Setup

In `src/terminal_testbed` run

```bash
g++ -o a.out ./main.cpp
```

## Usage

1. Run `boot.sh`
2. Run `start_testbed.sh`

#### Network setup
The TesLAN Signposts and Crewpanel devices are set up for IPs `10.20.30.x`, with `x=signpost_id+1`, and listen on port 8888.