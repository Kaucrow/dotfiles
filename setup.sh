#!/bin/bash

# Ensure the script runs as root
if [[ $EUID -ne 0 ]]; then
	echo "This script must be run as root"
	exit 1
fi

# Get the username and password
echo "Input the main user's data"
read -p "Username: " USER_NAME

while true; do
	read -sp "Password: " USER_PASS
	echo ""
	read -sp "Confirm password: " USER_PASS_CONFIRM
	echo ""

	if [[ "$USER_PASS" == "$USER_PASS_CONFIRM" ]]; then
		break
	else
		echo "Passwords do not match. Please try again."
	fi
done

# Create new user
echo "Creating new user..."
useradd -m -s /bin/bash "$USER_NAME"
echo "$USER_NAME:$USER_PASS" | chpasswd
usermod -aG wheel "$USER_NAME"
echo "User $USER_NAME has been created and added to the wheel group."

# Allow users in wheel to have sudo
sed -i 's/^# %wheel ALL=(ALL:ALL) ALL/%wheel ALL=(ALL:ALL) ALL/' /etc/sudoers

# Temporarily allow new user to execute yay without password
SUDOERS_FILE="/etc/sudoers.d/99-yay-tmp"
echo "$USER_NAME ALL=(ALL) NOPASSWD: /usr/bin/yay" | sudo tee "$SUDOERS_FILE" > /dev/null
chmod 0440 "$SUDOERS_FILE"

# Get the fastest package mirrors
echo "Getting package mirrors..."
pacman -S --needed --noconfirm reflector
reflector --latest 10 --protocol https --sort rate --save /etc/pacman.d/mirrorlist

# Update system
echo "Updating system..."
pacman -Syu --noconfirm

# Install base tools
echo "Installing base tools..."
pacman -S --needed --noconfirm base-devel git nvim networkmanager iwd

# Setup NetworkManager with iwd backend
echo "Configuring NetworkManager..."
mkdir -p /etc/NetworkManager/conf.d/
echo -e "[device]\nwifi.backend=iwd" > /etc/NetworkManager/conf.d/wifi_backend.conf
systemctl enable --now NetworkManager
systemctl enable --now iwd

# Setup audio
echo "Configuring audio..."
pacman -S --needed --noconfirm pipewire pipewire-pulse pipewire-alsa pipewire-jack wireplumber pavucontrol pamixer
systemctl --user enable --now pipewire
systemctl --user enable --now pipewire-pulse
systemctl --user enable --now wireplumber

# Setup yay
echo "Installing yay..."
sudo -u "$USER_NAME" bash <<EOF
	git clone https://aur.archlinux.org/yay.git /tmp/yay
	cd /tmp/yay
	makepkg -si --noconfirm
	cd ~
	rm -rf /tmp/yay
EOF

# Install yay packages
echo "Installing yay packages..."
YAY_APPS=(
	visual-studio-code-bin
	neofetch
	cava
	wlogout
    hyprmon-bin
    rose-pine-cursor
)
sudo -u "$USER_NAME" yay -S --needed --noconfirm "${YAY_APPS[@]}"

# Install additional packages
echo "Installing additional packages..."
APPS=(
	firefox
	htop
	network-manager-applet
	git
	discord
	telegram-desktop
	swaync
	matugen
    swww
	rofi
	kitty
	nwg-look
	papirus-icon-theme
	brightnessctl
	yazi
	zathura
	zathura-pdf-poppler
	tlp
	blueman
    imagemagick
    7zip
)
pacman -S --needed --noconfirm "${APPS[@]}"
systemctl enable --now tlp
systemctl enable --now bluetooth

# Prevent bluetooth from autoenabling on bootup
BT_CONFIG="/etc/bluetooth/main.conf"

if [ -f "$BT_CONFIG" ]; then
	echo "Setting AutoEnable=false in $BT_CONFIG..."
    	sed -i 's/^#AutoEnable=true/AutoEnable=false/' $BT_CONFIG
    	sed -i 's/^AutoEnable=true/AutoEnable=false/' $BT_CONFIG
fi

# Install fonts
echo "Installing fonts..."
FONTS=(
	ttf-jetbrains-mono-nerd
	noto-fonts-cjk
	ttf-dejavu
)
pacman -S --needed --noconfirm "${FONTS[@]}"

# Install wayland & hyprland
echo "Installing wayland & hyprland..."
pacman -S --needed --noconfirm hyprland xorg-xwayland waybar hyprlock hypridle hyprsunset

# Setup display manager
echo "Installing and configuring ly..."
pacman -S --needed --noconfirm ly
systemctl enable ly@tty2.service
systemctl disable getty@tty2.service

# Get dotfiles 
echo "Getting dotfiles..."
git clone https://github.com/Kaucrow/dotfiles.git /tmp/dotfiles
echo "Copying dotfiles..."
cp -r /tmp/dotfiles/.config /home/"$USER_NAME"/.config/.
cp -r /tmp/dotfiles/.scripts /home/"$USER_NAME"/.scripts
cp /tmp/dotfiles/.bashrc /home/"$USER_NAME"/.bashrc
mkdir -p /home/"$USER_NAME"/Pictures
cp -r /tmp/dotfiles/wallpapers /home/"$USER_NAME"/Pictures

# Setup dotfiles
echo "Finishing dotfiles setup..."
find /home/"$USER_NAME"/.scripts -name "*.sh" -exec chmod +x {} \;
chown -R "$USER_NAME":"$USER_NAME" /home/"$USER_NAME"/.config/
chown -R "$USER_NAME":"$USER_NAME" /home/"$USER_NAME"/.scripts
chown "$USER_NAME":"$USER_NAME" /home/"$USER_NAME"/.bashrc

# Cleanup
echo "Cleaning up..."
rm "$SUDOERS_FILE"

echo "Setup complete! OwO"
echo "Please reboot uwu"
