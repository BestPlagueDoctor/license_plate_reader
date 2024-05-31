#!/usr/bin/env sh

# clone OID toolkit to gather images. this needs to be done on a full-size computer as the pi memory will not allow this to run
git clone https://github.com/EscVM/OIDv4_ToolKit.git
cd OIDv4_ToolKit
pip3 install -r requirements.txt
python3 main.py downloader --type_csv all --classes "Vehicle registration plate"
echo "license_plate" > classes.txt
python3 convert_annnotations.py
