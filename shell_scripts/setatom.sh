#!/bin/bash

mkdir -p /app/dellboomi/Boomi_Atmosphere/Atom/Atom_DV_G1_A1_01/bin/
cd /app/dellboomi/Boomi_Atmosphere/Atom/Atom_DV_G1_A1_01/bin/
touch atom.sh
touch atom-status
touch log-atom

cat <<EOL > atom.sh
#!/bin/bash
script_file_path=/app/dellboomi/Boomi_Atmosphere/Atom/Atom_DV_G1_A1_01/bin/
if ! [ -f \$script_file_path/atom-status ]
then 
    touch \$script_file_path/atom-status
fi
case "\$1" in
    "start") sleep 5;echo "\$(date) atom is running." >> \$script_file_path/log-atom;echo "atom is running."|tee \$script_file_path/atom-status;;
    "stop") sleep 5;echo "\$(date) atom is offline." >> \$script_file_path/log-atom;echo "atom is offline."|tee \$script_file_path/atom-status;;
    "status") echo \$(cat \$script_file_path/atom-status);;
    *) echo "input invalid";;
esac
EOL
chmod +x atom.sh
chown root:root atom.sh
chown root:root atom-status
chown root:root log-atom
chmod 777 atom-status
chmod 777 log-atom
mv atom.sh atom
echo "atom is offline." > atom-status
