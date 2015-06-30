#!/bin/bash

function run4lw()
{
    exec 5<>/dev/tcp/$2/$3;echo $1 >&5;cat <&5 | egrep "Mode: "
}

function srvr()
{
    run4lw srvr $1 $2 2> /dev/null
}


echo "localhost:2181 $(srvr localhost 2181)"


echo "localhost:2182 $(srvr localhost 2182)"


echo "localhost:2183 $(srvr localhost 2183)"


echo "localhost:2184 $(srvr localhost 2184)"


echo "localhost:2185 $(srvr localhost 2185)"

