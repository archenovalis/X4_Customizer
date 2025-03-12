@echo off
py "Framework\Main.py" Cat_Unpack -argpass %* -include * -exclude *.dds *.xmf *.sig *.ani *.jcs *.ogg *.wav *.gz *.xpm *.xsm *.xac *.f *.psb *.ogl *.h *.v *.abc *.jpg *.dtd *.pk *.comp *.vh *.fh *.tcs *.tes *.peb *.dae *.bgp *.bgf *.bsg *.amw
pause