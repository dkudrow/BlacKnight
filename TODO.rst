To Do
=====

* Handle ZooKeeper connections: the client should continue to run and re-join the election when the connection is reset.
* Handle Stanchion failure
* Handle client started with no spec: don't allow client to run without spec (barrier + watcher on spec node?)
* Make sure watcher on children is correct! rihgt now roles are top level children!