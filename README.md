# hidsl-scripts
Setup and configuration scripts for the HOMEINFO Digital Signage Linux (HIDSL)

## hidsl-cfg
Provides 
* a systemd target, for HIDSL configuration mode, starting
* a systemd service to auto-login the configuration user's who than can launch
* a script to perform the actual configuration with limited sudo access to certain programs provided by
* a sudoers file

## hidsl-img
Script to create and restore HIDSL disk images
