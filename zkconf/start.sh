#!/bin/bash

if [ ! -f ./localhost:2181/zookeeper_server.pid ] ; then
	java $ZKCONF_START_ZKOPTS -cp ./*:. org.apache.zookeeper.server.quorum.QuorumPeerMain ./localhost:2181/zoo.cfg > ./localhost:2181/zoo.log 2>&1 &
	echo -n $! > ./localhost:2181/zookeeper_server.pid
else
	PID=`cat ./localhost:2181/zookeeper_server.pid`
	echo "Server localhost:2181 already started as PID ${PID}"
fi

if [ ! -f ./localhost:2182/zookeeper_server.pid ] ; then
	java $ZKCONF_START_ZKOPTS -cp ./*:. org.apache.zookeeper.server.quorum.QuorumPeerMain ./localhost:2182/zoo.cfg > ./localhost:2182/zoo.log 2>&1 &
	echo -n $! > ./localhost:2182/zookeeper_server.pid
else
	PID=`cat ./localhost:2182/zookeeper_server.pid`
	echo "Server localhost:2182 already started as PID ${PID}"
fi

if [ ! -f ./localhost:2183/zookeeper_server.pid ] ; then
	java $ZKCONF_START_ZKOPTS -cp ./*:. org.apache.zookeeper.server.quorum.QuorumPeerMain ./localhost:2183/zoo.cfg > ./localhost:2183/zoo.log 2>&1 &
	echo -n $! > ./localhost:2183/zookeeper_server.pid
else
	PID=`cat ./localhost:2183/zookeeper_server.pid`
	echo "Server localhost:2183 already started as PID ${PID}"
fi

if [ ! -f ./localhost:2184/zookeeper_server.pid ] ; then
	java $ZKCONF_START_ZKOPTS -cp ./*:. org.apache.zookeeper.server.quorum.QuorumPeerMain ./localhost:2184/zoo.cfg > ./localhost:2184/zoo.log 2>&1 &
	echo -n $! > ./localhost:2184/zookeeper_server.pid
else
	PID=`cat ./localhost:2184/zookeeper_server.pid`
	echo "Server localhost:2184 already started as PID ${PID}"
fi

if [ ! -f ./localhost:2185/zookeeper_server.pid ] ; then
	java $ZKCONF_START_ZKOPTS -cp ./*:. org.apache.zookeeper.server.quorum.QuorumPeerMain ./localhost:2185/zoo.cfg > ./localhost:2185/zoo.log 2>&1 &
	echo -n $! > ./localhost:2185/zookeeper_server.pid
else
	PID=`cat ./localhost:2185/zookeeper_server.pid`
	echo "Server localhost:2185 already started as PID ${PID}"
fi

