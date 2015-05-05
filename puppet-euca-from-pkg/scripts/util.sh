#
# Utility functions
#

######################################################################
# Parse command line options
# Globals:
#	CC_PART
#	RIAKCS_KEY
#	RIAKCS_SECRET
#	PRIMARY_HEAD
#	SECONDARY_HEAD
# Arguments:
#	none
# Returns:
#	none
######################################################################

#TODO: EUCA_NODES

parse_args() {
	EUCA_NODES=()
	while getopts ":c:n:k:s:p:q:d" opt; do
		case "$opt" in
			n)
				EUCA_NODES+=("$OPTARG")
				;;
			c)
				CC_PART="$OPTARG"
				pdebug "CC_PART=$CC_PART"
				;;
			k)
				RIAKCS_KEY="$OPTARG"
				pdebug "RIAKCS_KEY=$RIAKCS_KEY"
				;;
			s)
				RIAKCS_SECRET="$OPTARG"
				pdebug "RIAKCS_SECRET=$RIAKCS_SECRET"
				;;
			p)
				PRIMARY_HEAD="$OPTARG"
				pdebug "PRIMARY_HEAD=$PRIMARY_HEAD"
				;;
			q)
				SECONDARY_HEAD="$OPTARG"
				pdebug "SECONDARY_HEAD=$SECONDARY_HEAD"
				;;
			d)
				DEBUG="TRUE"
				;;
		esac
	done

	HOSTNAME="$(hostname -f)"
	pdebug "HOSTNAME=$HOSTNAME"
	NODENAME="${HOSTNAME%%.*}"
	pdebug "NODENAME=$NODENAME"
	PUBLIC_IP="$(get_inet_addr eth0)"
	pdebug "PUBLIC_IP=$PUBLIC_IP"
	PRIVATE_IP="$(get_inet_addr br0)"
	pdebug "PRIVATE_IP=$PRIVATE_IP"
}

######################################################################
# Print a debug message to stderr
# Globals:
#	none
# Arguments:
#	text to print
# Returns:
#	none
######################################################################

pdebug() {
	if [[ "$DEBUG" == "TRUE" ]]; then
		echo "DEBUG: $@" >&2
	fi
}

######################################################################
# Print an error message to stderr
# Globals:
#	none
# Arguments:
#	text to print
# Returns:
#	none
######################################################################

perror() {
	echo "ERROR: $@" >&2
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

get_eucalytpus_credentials() {
	local start_dir
	start_dir="$PWD"
	rm -rf /root/cred/*
	cd /root/cred/
	euca_conf --get-credentials=admin.zip
	unzip admin.zip
	source eucarc
	cd $start_dir
}


