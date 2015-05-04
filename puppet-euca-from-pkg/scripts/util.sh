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
	while getopts ":cnkspq" opt; do
		case $opt in
			n)
				if [[ ! -v "$EUCA_NODES" ]]; then
					EUCA_NODES=()
				fi
				EUCA_NODES+=("$OPTARG")
				;;
			c)
				CC_PART="$OPTARG"
				;;
			k)
				RIAKCS_KEY="$OPTARG"
				;;
			s)
				RIAKCS_SECRET="$OPTARG"
				;;
			p)
				PRIMARY_HEAD="$OPTARG"
				;;
			q)
				SECONDARY_HEAD="$OPTARG"
				;;
		esac
	done

	NODENAME="$(hostname -f)"
	PUBLIC_IP="$(get_inet_addr eth0)"
	PRIVATE_IP="$(get_inet_addr br0)"
}

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


