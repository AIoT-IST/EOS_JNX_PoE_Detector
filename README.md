# EOS_JNX_PoE_Detector
Detect PoE Power and connect or not

## Install required package
$ sudo apt-get install qt5-default qttools5-dev-tools
$ sudo apt-get update
$ sudo apt-get install python3-pip
$. pip3 install --upgrade pip
$ pip3 install pyqt5

## Run sample
$ sudo python3 PoE_Detector.py  

## Edit UI
$ designer
### Open "PoE_Detector_UI.ui"

### Reflash UI after editing
$ pyuic5 PoE_Detector_UI.ui -o PoE_Detector_UI.py


