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
	cava
	wlogout
    hyprmon-bin
    rose-pine-cursor
    xwaylandvideobridge
    ttf-ms-fonts
)
sudo -u "$USER_NAME" yay -S --needed --noconfirm "${YAY_APPS[@]}"

# Install additional packages
echo "Installing additional packages..."
APPS=(
    stow
	firefox
    fastfetch
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
    jq
    grim
    slurp
    wl-clipboard
    xdg-desktop-portal-hyprland
    adw-gtk-theme
    man
    pcmanfm
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
    otf-font-awesome
    noto-fonts-emoji
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
echo "Copying dotfiles..."

DOTFILES_DIR="/home/$USER_NAME/Dotfiles"

mkdir -p "$DOTFILES_DIR"
cp -r . "$DOTFILES_DIR/"

chown -R "$USER_NAME:$USER_NAME" "$DOTFILES_DIR"

sudo -u "$USER_NAME" mkdir -p "/home/$USER_NAME/Pictures"
sudo -u "$USER_NAME" ln -s "$DOTFILES_DIR/wallpapers" "/home/$USER_NAME/Pictures/wallpapers"

# Symlink dotfiles with stow
echo "Symlinking dotfiles with stow..."
sudo -u "$USER_NAME" bash <<EOF
    cd "$DOTFILES_DIR"
    rm -f ~/.bashrc
    stow -vt ~ .
EOF

# Add execute permission to scripts
echo "Adding execute permissions to scripts..."
find "$DOTFILES_DIR" -name "*.sh" -exec chmod +x {} \;

# Cleanup
echo "Cleaning up..."
rm "$SUDOERS_FILE"

echo "Setup complete! OwO"
echo "Please reboot uwu"
