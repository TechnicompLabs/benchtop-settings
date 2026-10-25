# Technicomp Benchtop Linux: the user's own Homebrew (installed by /usr/bin/brew
# on first use) on the PATH of each login session, with its MANPATH and INFOPATH
if [ -z "${HOMEBREW_PREFIX-}" ] && [ "$(id -u)" -ne 0 ]; then
	for _tcbl_brew in "$HOME/.linuxbrew" "$HOME/.brew" /home/linuxbrew/.linuxbrew; do
		if [ -x "$_tcbl_brew/bin/brew" ]; then
			eval "$("$_tcbl_brew/bin/brew" shellenv)"
			break
		fi
	done
	unset _tcbl_brew
fi
