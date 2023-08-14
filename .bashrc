#======================================================
#
#
#   ██████╗  █████╗ ███████╗██╗  ██╗██████╗  ██████╗
#   ██╔══██╗██╔══██╗██╔════╝██║  ██║██╔══██╗██╔════╝
#   ██████╔╝███████║███████╗███████║██████╔╝██║     
#   ██╔══██╗██╔══██║╚════██║██╔══██║██╔══██╗██║     
#   ██████╔╝██║  ██║███████║██║  ██║██║  ██║╚██████╗
#   ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝
#		   ===Kaucrow - gruvbox-material===
#
#======================================================

# If not running interactively, don't do anything
[[ $- != *i* ]] && return
clear
alias ls='ls --color=auto'
alias btop='btop -t'
alias neofetch='clear && neofetch --ascii ~/Pictures/Wallpapers/Rices/neofetch_ascii/arch_small.txt --ascii_colors 7 1 3 2'
alias ncmp='ncmpcpp'
alias mpvmus='mpv --no-video --cache-secs=150'
if [ "$TERM" = "linux" ]; then
	echo -en "\e]P0282828" # Black
	echo -en "\e]P1ea6962" # Red
	echo -en "\e]P2a8b762" # Green
	echo -en "\e]P3e78a4e" # Yellow
	echo -en "\e]P47daea3" # Blue
	echo -en "\e]P5d3869b" # Magenta
	echo -en "\e]P689b482" # Cyan
	echo -en "\e]P7dfbf8e" # White
	echo -en "\e]P8282828" # Black_bright
	echo -en "\e]P9ea6962" # Red_bright
	echo -en "\e]Paa8b762" # Green_bright
	echo -en "\e]Pbe78a4e" # Yellow_bright
	echo -en "\e]Pc7daea3" # Blue_bright
	echo -en "\e]Pdd3869b" # Magenta_bright
	echo -en "\e]Pe89b482" # Cyan_bright
	echo -en "\e]Pfdfbf8e" # White_bright
	clear # Clear artifacts
fi
export EDITOR='/usr/bin/nvim'
PS1='\[\033[1;36m\][\u@\W]\$\[\033[1;37m\] '
# PS1='[\u@\W]\$ '
