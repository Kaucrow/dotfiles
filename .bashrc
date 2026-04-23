#======================================================
#
#
#   ██████╗  █████╗ ███████╗██╗  ██╗██████╗  ██████╗
#   ██╔══██╗██╔══██╗██╔════╝██║  ██║██╔══██╗██╔════╝
#   ██████╔╝███████║███████╗███████║██████╔╝██║
#   ██╔══██╗██╔══██║╚════██║██╔══██║██╔══██╗██║
#   ██████╔╝██║  ██║███████║██║  ██║██║  ██║╚██████╗
#   ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝
#		   		=== Kaucrow ===
#
#======================================================

# If not running interactively, don't do anything
[[ $- != *i* ]] && return
alias ls='ls --color=auto'
alias btop='btop -t'
alias neofetch='clear && neofetch --ascii ~/.config/neofetch/arch_small.txt --ascii_colors 7 1 3 2'
alias fastfetch='clear && fastfetch -c ~/.config/fastfetch/config.jsonc'
alias ncmp='ncmpcpp'
alias mpvmus='mpv --no-video --cache-secs=150'
export EDITOR='/usr/bin/nvim'
PS1='\[\033[1;36m\][\u@\W]\$\[\033[1;37m\] '
. "$HOME/.cargo/env"

# pnpm
export PNPM_HOME="/home/kaucrow/.local/share/pnpm"
case ":$PATH:" in
  *":$PNPM_HOME:"*) ;;
  *) export PATH="$PNPM_HOME:$PATH" ;;
esac
# pnpm end