mkdir -p /workspace/.config/autostart


cat <<EOF > /workspace/.config/autostart/qgis.desktop 
[Desktop Entry]
Encoding=UTF-8
Version=0.9.4
Type=Application
Name=qgis
Comment=qgis
Exec=qgis
OnlyShowIn=XFCE;
RunHook=0
StartupNotify=false
Terminal=false
Hidden=false
EOF