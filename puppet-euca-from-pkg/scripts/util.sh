#
# Utility functions
#

######################################################################
# Print a message to stderr
# Globals:
#	none
# Arguments:
#	text to print
# Returns:
#	none
######################################################################

perror() {
	echo "$@" >&2
}

######################################################################
# Determine IP Address of interface
# Globals:
#	none
# Arguments:
#	name of interface
# Returns:
#	IP address of interface
######################################################################

get_inet_addr() {
	local result
	result=$(ifconfig "$1" \
		| grep 'inet addr' \
		| cut -d":" -f2 \
		| cut -d" " -f1)
	echo "$result" || return
}

######################################################################
# Fetch Eucalyptus credentials and export them
# Globals:
#	none
# Arguments:
#	none
# Returns:
#	none
######################################################################

get_euca_cred() {
	local start_dir
	start_dir="$PWD"
	rm -rf /root/cred/*
	cd /root/cred/
	euca_conf --get-credentials=admin.zip
	unzip admin.zip
	source eucarc
	cd $start_dir
}


